# app.py (Now a pure API)

from flask import Flask, request, jsonify
from flask_cors import CORS  # Import CORS
from backend import AIContextManager
from werkzeug.utils import secure_filename
import traceback
import threading

# Initialize the Flask app
app = Flask(__name__)

# --- NEW: Enable CORS ---
# This will allow the React frontend (running on a different port)
# to make requests to this Flask backend.
CORS(app)

# Initialize the backend manager
backend = AIContextManager()

# The route that used to serve index.html has been removed.
# The React app will now handle all UI.

#
# --- API Endpoints ---
# All your existing endpoints remain the same as they already handle JSON.
#

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    # ... (rest of the function is unchanged)
    user_id = data.get("user_id")
    topic = data.get("topic")
    user_prompt = data.get("prompt")
    if not all([user_id, topic, user_prompt]):
        return jsonify({"error": "User ID, topic, and prompt are required"}), 400
    try:
        ai_response = backend.process_prompt(user_id, topic, user_prompt)
        return jsonify({"response": ai_response})
    except Exception as e:
        print(f"An error occurred in /chat: {e}")
        traceback.print_exc()
        return jsonify({"error": "An internal error occurred."}), 500


@app.route("/upload", methods=["POST"])
def upload():
    # ... (rest of the function is unchanged)
    if "file" not in request.files:
        return jsonify({"error": "No file part"}), 400
    file = request.files["file"]
    user_id = request.form.get("user_id")
    topic = request.form.get("topic")
    if file.filename == "" or not topic or not user_id:
        return jsonify({"error": "User ID, topic, and a selected file are required"}), 400
    if file:
        try:
            filename = secure_filename(file.filename)
            content = file.read().decode("utf-8")
            backend.ingest_text(user_id, topic, content, filename)
            return jsonify({"message": f"Successfully ingested {filename}"})
        except Exception as e:
            print(f"An error occurred in /upload: {e}")
            traceback.print_exc()
            return jsonify({"error": "An internal error occurred."}), 500


@app.route("/ingest_repo", methods=["POST"])
def ingest_repo():
    # ... (rest of the function is unchanged)
    data = request.get_json()
    user_id = data.get("user_id")
    repo_url = data.get("repo_url")
    topic = data.get("topic")
    if not all([user_id, topic, repo_url]):
        return jsonify({"error": "User ID, topic, and repository URL are required"}), 400
    ingestion_thread = threading.Thread(
        target=backend.ingest_repo_from_url, args=(user_id, repo_url, topic)
    )
    ingestion_thread.start()
    return jsonify({"message": f"Started ingestion for {repo_url}. This may take several minutes."})


@app.route("/get_sources", methods=["POST"])
def get_sources():
    # ... (rest of the function is unchanged)
    data = request.get_json()
    user_id = data.get("user_id")
    topic = data.get("topic")
    if not user_id or not topic:
        return jsonify({"error": "User ID and topic are required"}), 400
    try:
        source_list = backend.get_sources_for_topic(user_id, topic)
        return jsonify({"sources": source_list})
    except Exception as e:
        print(f"An error occurred in /get_sources: {e}")
        traceback.print_exc()
        return jsonify({"error": "An internal error occurred."}), 500