import google.generativeai as genai
import os
import argparse
import chromadb # New import
import uuid # To create unique IDs for our entries

# --- Configuration ---
# Directory to store our vector database
DB_DIR = "vectordb"

# Configure ChromaDB client
client = chromadb.PersistentClient(path=DB_DIR)

# Configure the Gemini API
try:
    genai.configure(api_key=os.environ["GOOGLE_API_KEY"])
    text_model = genai.GenerativeModel('gemini-1.5-flash')
    # NEW: We need a dedicated model for creating embeddings
    embedding_model = genai.GenerativeModel('models/embedding-001')
except KeyError:
    print("🚨 GOOGLE_API_KEY secret not found or Codespace needs a restart.")
    exit()

# --- Core Functions ---

## MODIFIED ##
def get_or_create_collection(topic: str):
    """Gets or creates a ChromaDB collection for a given topic."""
    # ChromaDB collections must follow specific naming rules
    collection_name = f"context_{topic.replace('-', '_')}" 
    return client.get_or_create_collection(name=collection_name)

## MODIFIED ##
def load_context(collection, user_prompt: str, n_results: int = 3) -> str:
    """Finds the most relevant historical context from the vector DB."""
    if collection.count() == 0:
        return "No previous context available."

    print(f"🔎 Searching for {n_results} most relevant conversation snippets...")
    
    # Create an embedding for the user's current prompt
    prompt_embedding = genai.embed_content(
        model="models/embedding-001",
        content=user_prompt,
        task_type="RETRIEVAL_QUERY"
    )['embedding']

    # Query the collection for the most similar documents
    results = collection.query(
        query_embeddings=[prompt_embedding],
        n_results=min(n_results, collection.count()) # Ensure we don't ask for more results than exist
    )
    
    # Format the results into a string for the context
    context_string = "\n---\n".join(results['documents'][0])
    return context_string

## MODIFIED ##
def save_context(collection, interaction_summary: str):
    """Saves a new interaction summary to the vector DB."""
    print("💾 Saving interaction to vector memory...")
    
    # We need to create an embedding for the document we're storing
    document_embedding = genai.embed_content(
        model="models/embedding-001",
        content=interaction_summary,
        task_type="RETRIEVAL_DOCUMENT" # Different task type for storage
    )['embedding']
    
    collection.add(
        embeddings=[document_embedding],
        documents=[interaction_summary],
        ids=[str(uuid.uuid4())] # Each entry needs a unique ID
    )

def get_ai_response(context: str, prompt: str) -> str:
    """Sends the context and prompt to the AI and gets a response."""
    # The prompt structure is slightly different now
    full_prompt = f"### RELEVANT PAST CONVERSATION ###\n{context}\n\n### MY CURRENT QUESTION ###\n{prompt}"
    
    print("\n⏳ Sending to AI...")
    response = text_model.generate_content(full_prompt)
    return response.text

def summarize_interaction(user_prompt: str, ai_response: str) -> str:
    """Uses the AI to summarize a single user/AI interaction."""
    print("✍️  Summarizing interaction...")
    summary_prompt = f"""
    Concisely summarize the following exchange in the third person.
    USER PROMPT: "{user_prompt}"
    AI RESPONSE: "{ai_response}"
    SUMMARY:"""
    
    summary_response = text_model.generate_content(summary_prompt)
    return summary_response.text.strip()

# --- Main Execution Logic ---

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Chat with an AI with RAG-based context.")
    parser.add_argument("topic", help="The topic of the conversation.")
    args = parser.parse_args()

    topic = args.topic
    print(f"✅ Chatting about: {topic}")
    
    # Get or create the collection for this topic
    collection = get_or_create_collection(topic)

    while True:
        user_prompt = input("\nYou: ")
        if user_prompt.lower() in ['exit', 'quit']:
            print("👋 Goodbye!")
            break

        # 1. Load RELEVANT context by searching the DB
        relevant_context = load_context(collection, user_prompt)

        # 2. Get AI response
        ai_response = get_ai_response(relevant_context, user_prompt)
        print(f"\nAI: {ai_response}")

        # 3. Summarize and save the new interaction
        interaction_summary = summarize_interaction(user_prompt, ai_response)
        save_context(collection, interaction_summary)
        print("✅ Context updated in vector memory.")