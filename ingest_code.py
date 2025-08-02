# ingest_code.py

import os
import argparse
import google.generativeai as genai
import chromadb
import uuid

# A list of common file extensions for source code
# Feel free to expand this list
SOURCE_CODE_EXTENSIONS = [
    ".py",
    ".js",
    ".ts",
    ".html",
    ".css",
    ".java",
    ".c",
    ".cpp",
    ".h",
    ".hpp",
    ".rs",
    ".go",
    ".php",
    ".rb",
    ".swift",
    ".kt",
    ".scala",
    ".md",
]

# Directories to ignore during ingestion
IGNORE_DIRS = ["__pycache__", "node_modules", ".git", ".vscode", "venv", ".idea"]


class CodeIngestor:
    def __init__(self):
        """Initializes the backend components for ingestion."""
        DB_DIR = "vectordb"
        self.client = chromadb.PersistentClient(path=DB_DIR)

        try:
            genai.configure(api_key=os.environ["GOOGLE_API_KEY"])
            self.embedding_model_name = "models/embedding-001"
        except KeyError:
            raise Exception("🚨 GOOGLE_API_KEY secret not found.")

    def ingest(self, repo_path: str, topic: str):
        """Walks through a directory, chunks files, and stores them in the DB."""
        collection_name = f"context_{topic.replace('-', '_')}"
        collection = self.client.get_or_create_collection(name=collection_name)

        print(f"🧹 Clearing any existing data for topic '{topic}'...")
        collection.delete(where={"topic": topic})

        print(f"🚀 Starting ingestion for '{repo_path}' into topic '{topic}'...")

        documents = []
        metadatas = []
        ids = []

        for root, dirs, files in os.walk(repo_path):
            # Remove ignored directories from traversal
            dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]

            for file in files:
                if any(file.endswith(ext) for ext in SOURCE_CODE_EXTENSIONS):
                    file_path = os.path.join(root, file)
                    relative_path = os.path.relpath(file_path, repo_path)

                    try:
                        with open(file_path, "r", encoding="utf-8") as f:
                            content = f.read()

                        # Simple chunking by splitting the file content
                        # For a more advanced version, you could use AST parsing
                        # But this is a very solid start.
                        chunk = f"--- File: {relative_path} ---\n\n{content}"

                        documents.append(chunk)
                        metadatas.append({"topic": topic, "file": relative_path})
                        ids.append(str(uuid.uuid4()))
                        print(f"  - Processing: {relative_path}")

                    except Exception as e:
                        print(f"  - ⚠️ Could not read file {file_path}: {e}")

        if not documents:
            print("No source code files found to ingest.")
            return

        print(f"\nEmbedding {len(documents)} document(s). This may take a moment...")
        embeddings = genai.embed_content(
            model=self.embedding_model_name,
            content=documents,
            task_type="RETRIEVAL_DOCUMENT",
        )["embedding"]

        # Add to collection in batches to avoid potential limits
        batch_size = 100
        for i in range(0, len(documents), batch_size):
            collection.add(
                ids=ids[i : i + batch_size],
                embeddings=embeddings[i : i + batch_size],
                documents=documents[i : i + batch_size],
                metadatas=metadatas[i : i + batch_size],
            )
            print(f"  - Added batch {i//batch_size + 1} to the database.")

        print(
            f"\n✅ Ingestion complete! {len(documents)} chunks from your codebase are now in the '{topic}' context."
        )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Ingest a codebase into the AI context model."
    )
    parser.add_argument(
        "--path", required=True, help="The local path to the code repository."
    )
    parser.add_argument(
        "--topic", required=True, help="The topic name to associate with this codebase."
    )
    args = parser.parse_args()

    ingestor = CodeIngestor()
    ingestor.ingest(args.path, args.topic)
