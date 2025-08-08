# In app.py

from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token
import traceback
import threading
import os

# Import from our backend module
from backend import AIContextManager, db, bcrypt, User

# Initialize the Flask app
app = Flask(__name__)

# --- CONFIGURATION ---
# For the database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# For JWT --- IMPORTANT: Change this secret key!
app.config['JWT_SECRET_KEY'] = 'your-super-secret-key-change-me' 

# --- INITIALIZE EXTENSIONS ---
CORS(app)
db.init_app(app)
bcrypt.init_app(app)
jwt = JWTManager(app)

# Initialize the backend manager
backend = AIContextManager()

# --- API Endpoints ---

@app.route("/api/register", methods=["POST"])
def register_user():
    """
    Registers a new user.
    """
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"error": "Username and password are required"}), 400

    # Check if user already exists
    if User.query.filter_by(username=username).first():
        return jsonify({"error": "Username already exists"}), 409 # 409 Conflict

    try:
        new_user = User(username=username, password=password)
        db.session.add(new_user)
        db.session.commit()
        return jsonify({"message": f"User '{username}' created successfully"}), 201 # 201 Created
    except Exception as e:
        db.session.rollback()
        print(f"Error in /api/register: {e}")
        return jsonify({"error": "An internal error occurred."}), 500

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
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
    if "file" not in request.files:
        return jsonify({"error": "No file part"}), 400
    file = request.files["file"]
    user_id = request.form.get("userId")
    topic = request.form.get("topic")
    if file.filename == "" or not topic or not user_id:
        return jsonify({"error": "User ID, topic, and a selected file are required"}), 400
    if file:
        try:
            filename = file.filename # Note: werkzeug.utils.secure_filename is also an option
            content = file.read().decode("utf-8")
            backend.ingest_text(user_id, topic, content, filename)
            return jsonify({"message": f"Successfully ingested {filename}"})
        except Exception as e:
            print(f"An error occurred in /upload: {e}")
            traceback.print_exc()
            return jsonify({"error": "An internal error occurred."}), 500

@app.route("/ingest_repo", methods=["POST"])
def ingest_repo():
    data = request.get_json()
    user_id = data.get("user_id")
    repo_url = data.get("repo_url")
    topic = data.get("topic")
    if not all([user_id, topic, repo_url]):
        return jsonify({"error": "User ID, topic, and repository URL are required"}), 400
    
    # Run ingestion in a background thread to avoid HTTP timeouts
    ingestion_thread = threading.Thread(
        target=backend.ingest_repo_from_url, args=(user_id, repo_url, topic)
    )
    ingestion_thread.start()
    return jsonify({"message": f"Started ingestion for {repo_url}. This may take several minutes."})

@app.route('/get_sources', methods=['GET'])
def get_sources():
    user_id = request.args.get('userId')
    topic = request.args.get('topic')
    if not user_id or not topic:
        return jsonify({"error": "userId and topic parameters are required"}), 400
    try:
        source_list = backend.get_sources_for_topic(user_id, topic)
        formatted_sources = []
        for i, source_name in enumerate(source_list):
            source_type = "repo" if source_name.startswith("http") else "file"
            display_name = source_name
            if source_type == "repo":
                path_part = source_name.split("github.com/")[-1]
                if path_part:
                    display_name = path_part
            formatted_sources.append({
                "id": i + 1, "name": display_name, "type": source_type
            })
        return jsonify(formatted_sources)
    except Exception as e:
        print(f"An error occurred in /get_sources: {e}")
        traceback.print_exc()
        return jsonify({"error": "An internal error occurred."}), 500

@app.route("/api/topics", methods=["GET"])
def get_topics():
    try:
        collections = backend.client.list_collections()
        topic_names = set()
        for c in collections:
            parts = c.name.split("_topic_")
            if len(parts) > 1:
                topic_names.add(parts[1])
        if not topic_names:
            topic_names.add("general")
        return jsonify(sorted(list(topic_names)))
    except Exception as e:
        print(f"An error occurred in /api/topics: {e}")
        return jsonify({"error": "Could not retrieve topics."}), 500

@app.route("/api/login", methods=["POST"])
def login_user():
    """
    Logs in a user and returns a JWT access token.
    """
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"error": "Username and password are required"}), 400

    # Find the user in the database
    user = User.query.filter_by(username=username).first()

    # Check if the user exists and the password is correct
    if user and user.check_password(password):
        # Create a new token with the user's ID as the identity
        access_token = create_access_token(identity=user.id)
        return jsonify(access_token=access_token)

    # If credentials are bad, return an 'unauthorized' error
    return jsonify({"error": "Invalid username or password"}), 401