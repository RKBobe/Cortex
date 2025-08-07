from flask import Flask, request, jsonify
from flask_cors import CORS

# Initialize the Flask application
app = Flask(__name__)

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

    # TODO: Replace with actual model inference logic
    mock_response = {
        "id": 123, # A unique ID for the message
        "text": f"This is a mock AI response to your message: '{prompt}'",
        "sender": "ai"
    }
    
    return jsonify(mock_response)


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
    
    # TODO: Implement repository cloning and ingestion logic
    return jsonify({"message": f"Repository '{repo_url}' ingestion started."}), 200


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