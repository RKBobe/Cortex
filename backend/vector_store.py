import chromadb

# Use the existing 'cortex_db' directory for persistent storage
CHROMA_PATH = "cortex_db" 

# Initialize the persistent Chroma client
# This will use the existing directory if it finds it, or create it.
client = chromadb.PersistentClient(path=CHROMA_PATH)

# Get or create the collection for our context
collection = client.get_or_create_collection(name="cortex_collection")

def get_chroma_collection():
    """Returns the singleton Chroma collection instance."""
    return collection