# backend.py

import google.generativeai as genai
import os
import chromadb
import uuid

class AIContextManager:
    def __init__(self):
        """Initializes the backend components."""
        # --- Configuration ---
        DB_DIR = "vectordb"
        self.client = chromadb.PersistentClient(path=DB_DIR)
        
        # --- Configure Gemini Models ---
        try:
            genai.configure(api_key=os.environ["GOOGLE_API_KEY"])
            self.text_model = genai.GenerativeModel('gemini-1.5-flash')
            # The embedding model is used for RAG
            self.embedding_model_name = 'models/embedding-001' 
        except KeyError:
            raise Exception("🚨 GOOGLE_API_KEY secret not found. Please set it in your Codespace secrets.")

    def _get_or_create_collection(self, topic: str):
        """Gets or creates a ChromaDB collection for a given topic."""
        collection_name = f"context_{topic.replace('-', '_')}" 
        return self.client.get_or_create_collection(name=collection_name)

    def _summarize_interaction(self, user_prompt: str, ai_response: str) -> str:
        """Uses the AI to summarize a single user/AI interaction."""
        summary_prompt = f"""
        Concisely summarize the following exchange in the third person.
        USER PROMPT: "{user_prompt}"
        AI RESPONSE: "{ai_response}"
        SUMMARY:"""
        
        summary_response = self.text_model.generate_content(summary_prompt)
        return summary_response.text.strip()

    def process_prompt(self, topic: str, user_prompt: str) -> str:
        """The main method to handle a user prompt and return an AI response."""
        collection = self._get_or_create_collection(topic)

        # 1. Load RELEVANT context by searching the DB
        relevant_context = "No previous context available."
        if collection.count() > 0:
            prompt_embedding = genai.embed_content(
                model=self.embedding_model_name,
                content=user_prompt,
                task_type="RETRIEVAL_QUERY"
            )['embedding']

            results = collection.query(
                query_embeddings=[prompt_embedding],
                n_results=min(3, collection.count()) 
            )
            relevant_context = "\n---\n".join(results['documents'][0])

        # 2. Get AI response based on relevant context
        full_prompt = f"### RELEVANT PAST CONVERSATION ###\n{relevant_context}\n\n### MY CURRENT QUESTION ###\n{user_prompt}"
        ai_response = self.text_model.generate_content(full_prompt).text
        
        # 3. Summarize and save the new interaction in the background
        interaction_summary = self._summarize_interaction(user_prompt, ai_response)
        
        document_embedding = genai.embed_content(
            model=self.embedding_model_name,
            content=interaction_summary,
            task_type="RETRIEVAL_DOCUMENT"
        )['embedding']
        
        collection.add(
            embeddings=[document_embedding],
            documents=[interaction_summary],
            ids=[str(uuid.uuid4())]
        )
        
        # 4. Return the direct AI response to the user
        return ai_response