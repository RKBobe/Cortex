import os
import uuid
import chromadb
import google.generativeai as genai
import subprocess
import tempfile
import re
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

# This will be initialized from app.py
db = SQLAlchemy()
bcrypt = Bcrypt()

# Define the User database model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

    def __init__(self, username, password):
        self.username = username
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)

# ... your AIContextManager class definition follows ...


class AIContextManager:
    def __init__(self):
        """Initializes the backend components."""
        # UPDATED: Using a relative path for easier local development.
        # A 'cortex_db' folder will be created in your project directory.
        DB_DIR = "cortex_db" 
        self.client = chromadb.PersistentClient(path=DB_DIR)
        
        try:
            genai.configure(api_key=os.environ["GOOGLE_API_KEY"])
            self.text_model = genai.GenerativeModel("gemini-1.5-flash")
            self.embedding_model_name = "models/embedding-001"
        except KeyError:
            raise Exception("🚨 GOOGLE_API_KEY secret not found.")

    def _get_or_create_collection(self, user_id: str, topic: str):
        """Gets or creates a user-scoped ChromaDB collection."""
        sane_user_id = re.sub(r"[^a-zA-Z0-9_-]", "", user_id)
        sane_topic = re.sub(r"[^a-zA-Z0-9_-]", "", topic)

        collection_name = f"user_{sane_user_id}_topic_{sane_topic}"
        
        # Enforce ChromaDB's length limits
        if len(collection_name) > 63:
            collection_name = collection_name[:63]
            
        return self.client.get_or_create_collection(name=collection_name)

    def _summarize_interaction(self, user_prompt: str, ai_response: str) -> str:
        """Uses the AI to summarize a single user/AI interaction."""
        summary_prompt = f"Concisely summarize the following exchange in the third person.\nUSER: {user_prompt}\nAI: {ai_response}\nSUMMARY:"
        summary_response = self.text_model.generate_content(summary_prompt)
        return summary_response.text.strip()

    def ingest_text(self, user_id: str, topic: str, content: str, filename: str):
        """Ingests a single block of text content into a user's topic."""
        collection = self._get_or_create_collection(user_id, topic)
        print(f"Ingesting content from '{filename}' for user '{user_id}' into topic '{topic}'...")
        document = f"--- Content from file: {filename} ---\n\n{content}"

        doc_embedding = genai.embed_content(
            model=self.embedding_model_name,
            content=document,
            task_type="RETRIEVAL_DOCUMENT",
        )["embedding"]

        collection.add(
            embeddings=[doc_embedding], 
            documents=[document], 
            ids=[str(uuid.uuid4())],
            # UPDATED: Add metadata so we can retrieve the source name later
            metadatas=[{"source": filename}]
        )
        print("✅ Ingestion complete.")

    def ingest_repo_from_url(self, user_id: str, repo_url: str, topic: str):
        """Clones a Git repo into a temporary directory and ingests it for a specific user."""
        with tempfile.TemporaryDirectory() as temp_dir:
            try:
                print(f"Cloning {repo_url} for user '{user_id}'...")
                subprocess.run(
                    ["git", "clone", "--depth", "1", repo_url, temp_dir],
                    check=True,
                    capture_output=True,
                    text=True,
                )
                print("✅ Git clone successful.")
                self._ingest_directory(user_id, temp_dir, topic, repo_url)
            except subprocess.CalledProcessError as e:
                print(f"🚨 Failed to clone repository: {e.stderr}")
            except Exception as e:
                print(f"🚨 An error occurred during ingestion: {e}")

    def _ingest_directory(self, user_id: str, repo_path: str, topic: str, source_identifier: str):
        """Walks through a directory, chunks files, and stores them for a user's topic."""
        collection = self._get_or_create_collection(user_id, topic)
        
        SOURCE_CODE_EXTENSIONS = [".py", ".js", ".ts", ".html", ".css", ".java", ".c", ".cpp", ".rs", ".go", ".md"]
        IGNORE_DIRS = ["__pycache__", "node_modules", ".git", ".vscode", "venv"]

        documents, metadatas, ids = [], [], []

        for root, dirs, files in os.walk(repo_path):
            dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]
            for file in files:
                if any(file.endswith(ext) for ext in SOURCE_CODE_EXTENSIONS):
                    file_path = os.path.join(root, file)
                    relative_path = os.path.relpath(file_path, repo_path)
                    try:
                        with open(file_path, "r", encoding="utf-8") as f:
                            content = f.read()
                        chunk = f"--- File: {relative_path} from {source_identifier} ---\n\n{content}"
                        documents.append(chunk)
                        # UPDATED: Changed metadata key from "file" to "source" for consistency
                        metadatas.append({"source": f"{source_identifier}/{relative_path}"})
                        ids.append(str(uuid.uuid4()))
                    except Exception:
                        pass # Ignore files that can't be read

        if not documents:
            print("No source code files found to ingest.")
            return

        print(f"\nEmbedding {len(documents)} document(s) for user '{user_id}'...")
        embeddings = genai.embed_content(
            model=self.embedding_model_name,
            content=documents,
            task_type="RETRIEVAL_DOCUMENT",
        )["embedding"]

        batch_size = 100
        for i in range(0, len(documents), batch_size):
            collection.add(
                ids=ids[i : i + batch_size],
                embeddings=embeddings[i : i + batch_size],
                documents=documents[i : i + batch_size],
                metadatas=metadatas[i : i + batch_size],
            )
        print(f"✅ Ingestion complete for user '{user_id}', topic '{topic}'.")

    def process_prompt(self, user_id: str, topic: str, user_prompt: str) -> str:
        """Processes a user's prompt using the RAG pipeline."""
        collection = self._get_or_create_collection(user_id, topic)

        relevant_context = "No previous context available."
        if collection.count() > 0:
            prompt_embedding = genai.embed_content(
                model=self.embedding_model_name,
                content=user_prompt,
                task_type="RETRIEVAL_QUERY",
            )["embedding"]

            results = collection.query(
                query_embeddings=[prompt_embedding],
                n_results=min(3, collection.count()),
            )
            if results and results["documents"]:
                relevant_context = "\n---\n".join(results["documents"][0])

        full_prompt = f"""You are a helpful AI assistant with a persistent memory. Use the following context, which is composed of past conversation summaries or ingested file contents, to answer the user's question. If the context is not relevant, answer based on your general knowledge.

### RELEVANT CONTEXT ###
{relevant_context}

### USER'S QUESTION ###
{user_prompt}
"""
        ai_response = self.text_model.generate_content(full_prompt).text

        interaction_summary = self._summarize_interaction(user_prompt, ai_response)
        summary_embedding = genai.embed_content(
            model=self.embedding_model_name,
            content=interaction_summary,
            task_type="RETRIEVAL_DOCUMENT",
        )["embedding"]

        collection.add(
            embeddings=[summary_embedding],
            documents=[interaction_summary],
            ids=[str(uuid.uuid4())],
            # UPDATED: Added metadata to conversation snippets for better tracking
            metadatas=[{"source": "Conversation Summary"}], 
        )
        return ai_response

    # --- NEW METHOD ---
    def get_sources_for_topic(self, user_id: str, topic: str) -> list[str]:
        """
        Retrieves a list of unique source identifiers (filenames, repo URLs) 
        that have been ingested for a specific user and topic.
        """
        collection = self._get_or_create_collection(user_id, topic)
        results = collection.get(include=["metadatas"])

        if not results or not results["metadatas"]:
            return []

        unique_sources = set()
        for metadata in results["metadatas"]:
            if metadata and "source" in metadata:
                unique_sources.add(metadata["source"])
        
        return sorted(list(unique_sources))