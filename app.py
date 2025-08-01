# app.py

from flask import Flask, render_template, request, jsonify
from backend import AIContextManager

# Initialize the Flask app and the backend manager
app = Flask(__name__)
backend = AIContextManager()

# This is the route for the main webpage
@app.route('/')
def index():
    """Renders the main chat page."""
    return render_template('index.html')

# This is the route that handles chat messages
@app.route('/chat', methods=['POST'])
def chat():
    """Receives user input, processes it with the backend, and returns AI response."""
    data = request.get_json()
    topic = data.get('topic', 'general') # Default topic is 'general'
    user_prompt = data.get('prompt')

    if not user_prompt:
        return jsonify({'error': 'No prompt provided'}), 400

    try:
        # Call the backend to get the AI's response
        ai_response = backend.process_prompt(topic, user_prompt)
        return jsonify({'response': ai_response})
    except Exception as e:
        print(f"An error occurred: {e}")
        return jsonify({'error': str(e)}), 500