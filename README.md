# Cortex
# Cortex 
persistant contextual memory for ai
# AI Context Tool 🧠

A web-based chat application that maintains a persistent, topic-specific memory for conversations with AI models. This tool uses a Retrieval-Augmented Generation (RAG) pipeline to provide relevant context from past conversations, ingested files, and even entire codebases, ensuring you never have to repeat yourself.

The application is built with multi-user support, providing each user with a completely isolated and private context database. It is designed for production deployment using Docker and Fly.io.

---

## ✨ Features

* **Persistent, Topic-Based Memory**: Conversations are saved and automatically recalled based on the topic you're discussing.
* **Retrieval-Augmented Generation (RAG)**: Instead of using the entire history, the app finds the most semantically relevant chunks of context for each new question, leading to more accurate and efficient responses.
* **Multi-User Isolation**: Each user has their own secure sandbox for topics and contexts, identified by a unique User ID.
* **Codebase Ingestion**: Ingest an entire public GitHub repository by providing its URL to make the AI contextually aware of your code.
* **File Ingestion**: Upload `.txt`, `.md`, or other text files to add specific documents to a topic's context.
* **Web-Based UI**: A clean, modern user interface built with Flask and Bootstrap.

---

## 🛠️ Tech Stack

* **Backend**: Python, Flask
* **AI**: Google Gemini API
* **Vector Database**: ChromaDB
* **Deployment**: Docker, Gunicorn, Fly.io

---

## 🚀 Local Setup and Development

1.  **Clone the Repository**:
    ```bash
    git clone [https://github.com/your-username/Cortex.git](https://github.com/your-username/Cortex.git)
    cd Cortex
    ```

2.  **Create a Virtual Environment**:
    ```bash
    python -m venv venv
    source venv/bin/activate
    ```

3.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

4.  **Set Environment Variable**: You need to set your Google AI API key.
    ```bash
    export GOOGLE_API_KEY="YOUR_API_KEY_HERE"
    ```

5.  **Run the Application**:
    ```bash
    flask run
    ```
    The app will be available at `http://127.0.0.1:5000`.

---

## ☁️ Deployment to Fly.io

This application is configured for deployment on Fly.io with a `Dockerfile` and `fly.toml`.

1.  **Install Fly.io CLI**:
    ```bash
    curl -L [https://fly.io/install.sh](https://fly.io/install.sh) | sh
    ```

2.  **Login and Launch**:
    ```bash
    fly auth login
    fly launch
    ```
    *(Follow the prompts, but do **not** set up a database or deploy immediately)*.

3.  **Create a Persistent Volume**:
    ```bash
    # Replace <your-app-name> with the name you chose during launch
    fly volumes create data --size 1 --app <your-app-name>
    ```

4.  **Set API Key Secret**:
    ```bash
    fly secrets set GOOGLE_API_KEY="YOUR_API_KEY_HERE"
    ```

5.  **Deploy**:
    ```bash
    fly deploy
    ```

---
## usage
The application is designed to be self-explanatory. Upon launching the web interface, you'll be prompted to enter a unique User ID. This ID ensures that all your topics and conversations are kept private.

Once you've set your User ID, you can start a new chat by typing a topic name into the "Topic" field. The application will automatically create a new context for this topic or load the existing one if you've discussed it before.

You can enhance a topic's context by using the "Ingest Content" section. This allows you to either upload a text file (like a `.txt` or `.md` document) or provide a URL to a public GitHub repository. The application will process this content, making the AI aware of the information within it when you chat about that specific topic.
