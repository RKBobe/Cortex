from flask import Flask, request, jsonify
from flask_cors import CORS
import threading
import tempfile
import git
from backend.ingest_code import CodeIngestor
from backend.context_chat import ChatAssistant
import os

# Initialize the Flask application
app = Flask(__name__)

# Global dictionary to store ingestion status
# Format: {user_id: {"status": "processing" | "completed" | "failed", "repo": "url", "error": "msg"}}
ingestion_status = {}

# Configure CORS (Cross-Origin Resource Sharing)
# This allows your frontend (running on a different port) to make requests to this backend.
CORS(app, resources={r"/*": {"origins": "http://localhost:5173"}}) # Adjust port if your frontend runs elsewhere

# --- API Endpoints ---

@app.route('/chat', methods=['POST'])
def chat():
    """
    Handles chat messages from the user.
    Receives a prompt and returns a mock AI response.
    """
    data = request.get_json()
    user_id = data.get('userId')
    topic = data.get('topic')
    prompt = data.get('prompt')

    if not all([user_id, topic, prompt]):
        return jsonify({"error": "Missing required fields: userId, topic, prompt"}), 400

    print(f"Received prompt: '{prompt}' for topic '{topic}' from user '{user_id}'")

    try:
        # Initialize the assistant (consider caching this instance or handling it per request)
        assistant = ChatAssistant()

        # Get the real AI response
        response_text = assistant.get_response(topic, prompt)

        response_payload = {
            "id": 123, # Placeholder ID
            "text": response_text,
            "sender": "ai"
        }
        return jsonify(response_payload)

    except Exception as e:
        print(f"Error in chat endpoint: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/upload', methods=['POST'])
def upload_file():
    """
    Handles file uploads for context ingestion.
    """
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    
    file = request.files['file']
    user_id = request.form.get('userId')
    
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    if file and user_id:
        print(f"Received file '{file.filename}' for user '{user_id}'")
        # TODO: Process and save the file, then ingest its content into the vector DB
        return jsonify({"message": f"File '{file.filename}' uploaded successfully."}), 200
    
    return jsonify({"error": "File or userId missing"}), 400


def run_ingestion_background(repo_url, user_id):
    """
    Background task to clone and ingest a repository.
    """
    global ingestion_status
    ingestion_status[user_id] = {"status": "processing", "repo": repo_url}

    try:
        # Extract repository name from URL (simple extraction)
        # e.g., https://github.com/user/repo.git -> repo
        repo_name = repo_url.rstrip('/').split('/')[-1]
        if repo_name.endswith('.git'):
            repo_name = repo_name[:-4]

        topic = f"{user_id}-{repo_name}"

        with tempfile.TemporaryDirectory() as temp_dir:
            print(f"Cloning '{repo_url}' into '{temp_dir}'...")
            git.Repo.clone_from(repo_url, temp_dir)

            print(f"Starting ingestion for topic '{topic}'...")
            ingestor = CodeIngestor()
            ingestor.ingest(temp_dir, topic)
            print(f"Ingestion for '{repo_url}' complete.")

        ingestion_status[user_id] = {"status": "completed", "repo": repo_url}

    except Exception as e:
        print(f"Error during ingestion of '{repo_url}': {e}")
        ingestion_status[user_id] = {"status": "failed", "repo": repo_url, "error": str(e)}


@app.route('/ingest_repo', methods=['POST'])
def ingest_repo():
    """
    Handles ingestion of a GitHub repository.
    """
    data = request.get_json()
    repo_url = data.get('repo_url')
    user_id = data.get('userId')

    if not all([repo_url, user_id]):
        return jsonify({"error": "Missing required fields: repo_url, userId"}), 400
        
    print(f"Ingesting repository '{repo_url}' for user '{user_id}'")
    
    # Start ingestion in a background thread
    thread = threading.Thread(target=run_ingestion_background, args=(repo_url, user_id), daemon=True)
    thread.start()

    return jsonify({"message": f"Repository '{repo_url}' ingestion started."}), 200


@app.route('/ingestion_status', methods=['GET'])
def get_ingestion_status():
    """
    Returns the current ingestion status for a user.
    """
    user_id = request.args.get('userId')
    if not user_id:
        return jsonify({"error": "userId parameter is required"}), 400

    status = ingestion_status.get(user_id, {"status": "idle"})
    return jsonify(status), 200


@app.route('/get_sources', methods=['GET'])
def get_sources():
    """
    Retrieves the list of ingested context sources for a user.
    """
    user_id = request.args.get('userId')

    if not user_id:
        return jsonify({"error": "userId parameter is required"}), 400

    print(f"Fetching sources for user '{user_id}'")
    
    # TODO: Replace with actual database