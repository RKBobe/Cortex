from flask import Flask, render_template, request, jsonify
from backend import AIContextManager
from werkzeug.utils import secure_filename
import traceback
import threading

# Initialize the Flask app and the backend manager
app = Flask(__name__)
backend = AIContextManager()

#
# --- Main Web Page Route ---
#
@app.route('/')
def index():
    """Renders the main chat page."""
    return render_template('index.html')

#
# --- Chat Endpoint ---
#
@app.route('/chat', methods=['POST'])
def chat():
    """Receives user input, processes it, and returns AI response."""
    data = request.get_json()
    user_id = data.get('user_id')
    topic = data.get('topic')
    user_prompt = data.get('prompt')

    if not all([user_id, topic, user_prompt]):
        return jsonify({'error': 'User ID, topic, and prompt are required'}), 400

    try:
        ai_response = backend.process_prompt(user_id, topic, user_prompt)
        return jsonify({'response': ai_response})
    except Exception as e:
        print(f"An error occurred in /chat: {e}")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

#
# --- File Upload Endpoint ---
#
@app.route('/upload', methods=['POST'])
def upload():
    """Receives an uploaded file and ingests its content."""
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    user_id = request.form.get('user_id')
    topic = request.form.get('topic')
    
    if file.filename == '' or not topic or not user_id:
        return jsonify({'error': 'User ID, topic, and a selected file are required'}), 400

    if file:
        try:
            filename = secure_filename(file.filename)
            content = file.read().decode('utf-8')
            
            backend.ingest_text(user_id, topic, content, filename)
            
            return jsonify({'message': f'Successfully ingested {filename}'})
        except Exception as e:
            print(f"An error occurred in /upload: {e}")
            traceback.print_exc()
            return jsonify({'error': str(e)}), 500

#
# --- GitHub Repo Ingestion Endpoint ---
#
@app.route('/ingest_repo', methods=['POST'])
def ingest_repo():
    """Receives a Git repo URL and starts the ingestion process in the background."""
    data = request.get_json()
    user_id = data.get('user_id')
    repo_url = data.get('repo_url')
    topic = data.get('topic')

    if not all([user_id, topic, repo_url]):
        return jsonify({'error': 'User ID, topic, and repository URL are required'}), 400
    
    # Run the long-running ingestion task in a background thread
    ingestion_thread = threading.Thread(
        target=backend.ingest_repo_from_url,
        args=(user_id, repo_url, topic)
    )
    ingestion_thread.start()

    return jsonify({'message': f'Started ingestion for {repo_url}. This may take several minutes.'})