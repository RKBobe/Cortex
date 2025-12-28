import google.generativeai as genai
import os
import argparse
import chromadb
import uuid

# --- Configuration ---
DB_DIR = "vectordb"

class ChatAssistant:
    def __init__(self):
        """Initializes the backend components for chat."""
        # Configure ChromaDB client
        self.client = chromadb.PersistentClient(path=DB_DIR)

        # Configure the Gemini API
        try:
            genai.configure(api_key=os.environ["GOOGLE_API_KEY"])
            self.text_model = genai.GenerativeModel("gemini-1.5-flash")
            self.embedding_model_name = "models/embedding-001"
        except KeyError:
            # We raise this so the caller knows the API key is missing
            raise Exception("🚨 GOOGLE_API_KEY secret not found.")

    def _get_or_create_collection(self, topic: str):
        """Gets or creates a ChromaDB collection for a given topic."""
        # ChromaDB collections must follow specific naming rules
        collection_name = f"context_{topic.replace('-', '_')}"
        return self.client.get_or_create_collection(name=collection_name)

    def _load_context(self, collection, user_prompt: str, n_results: int = 3) -> str:
        """Finds the most relevant historical context from the vector DB."""
        if collection.count() == 0:
            return "No previous context available."

        print(f"🔎 Searching for {n_results} most relevant conversation snippets...")

        # Create an embedding for the user's current prompt
        prompt_embedding = genai.embed_content(
            model=self.embedding_model_name,
            content=user_prompt,
            task_type="RETRIEVAL_QUERY"
        )["embedding"]

        # Query the collection for the most similar documents
        results = collection.query(
            query_embeddings=[prompt_embedding],
            n_results=min(n_results, collection.count()),
        )

        # Format the results into a string for the context
        if results["documents"] and results["documents"][0]:
            context_string = "\n---\n".join(results["documents"][0])
            return context_string
        return "No relevant context found."

    def _save_context(self, collection, interaction_summary: str):
        """Saves a new interaction summary to the vector DB."""
        print("💾 Saving interaction to vector memory...")

        document_embedding = genai.embed_content(
            model=self.embedding_model_name,
            content=interaction_summary,
            task_type="RETRIEVAL_DOCUMENT",
        )["embedding"]

        collection.add(
            embeddings=[document_embedding],
            documents=[interaction_summary],
            ids=[str(uuid.uuid4())],
        )

    def _get_ai_response(self, context: str, prompt: str) -> str:
        """Sends the context and prompt to the AI and gets a response."""
        full_prompt = f"### RELEVANT PAST CONVERSATION ###\n{context}\n\n### MY CURRENT QUESTION ###\n{prompt}"
        print("\n⏳ Sending to AI...")
        response = self.text_model.generate_content(full_prompt)
        return response.text

    def _summarize_interaction(self, user_prompt: str, ai_response: str) -> str:
        """Uses the AI to summarize a single user/AI interaction."""
        print("✍️  Summarizing interaction...")
        summary_prompt = f"""
        Concisely summarize the following exchange in the third person.
        USER PROMPT: "{user_prompt}"
        AI RESPONSE: "{ai_response}"
        SUMMARY:"""

        summary_response = self.text_model.generate_content(summary_prompt)
        return summary_response.text.strip()

    def get_response(self, topic: str, user_prompt: str) -> str:
        """Orchestrates the chat flow: Load Context -> Get Response -> Save Summary."""
        collection = self._get_or_create_collection(topic)

        # 1. Load RELEVANT context
        relevant_context = self._load_context(collection, user_prompt)

        # 2. Get AI response
        ai_response = self._get_ai_response(relevant_context, user_prompt)

        # 3. Summarize and save (optional: can be done async)
        interaction_summary = self._summarize_interaction(user_prompt, ai_response)
        self._save_context(collection, interaction_summary)

        return ai_response

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Chat with an AI with RAG-based context.")
    parser.add_argument("topic", help="The topic of the conversation.")
    args = parser.parse_args()

    topic = args.topic
    print(f"✅ Chatting about: {topic}")

    assistant = ChatAssistant()

    while True:
        user_prompt = input("\nYou: ")
        if user_prompt.lower() in ["exit", "quit"]:
            print("👋 Goodbye!")
            break

        response = assistant.get_response(topic, user_prompt)
        print(f"\nAI: {response}")
