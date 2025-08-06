# Cortex - AI Context Chat 🧠

A web-based chat application that maintains a persistent, topic-specific memory for conversations with AI models. This tool uses a Retrieval-Augmented Generation (RAG) pipeline to provide relevant context from past conversations, ingested files, and even entire codebases, ensuring you never have to repeat yourself.

The application is built with multi-user support, providing each user with a completely isolated and private context database. It is designed for production deployment using Docker and Fly.io.

---

## ✨ Features

* **Persistent, Topic-Based Memory**: Conversations are saved and automatically recalled based on the topic you're discussing.
* **Retrieval-Augmented Generation (RAG)**: Finds the most semantically relevant chunks of context for each new question, leading to more accurate and efficient responses.
* **Multi-User Isolation**: Each user has their own secure sandbox for topics and contexts.
* **Codebase Ingestion**: Ingest an entire public GitHub repository by providing its URL.
* **File Ingestion**: Upload `.txt`, `.md`, or other text files to add specific documents to a topic's context.
* **NEW: Context Transparency**: View a list of all ingested files and sources for any given topic, so you always know what context the AI is using.
* **Web-Based UI**: A clean, modern user interface built with Flask and Bootstrap.

---

## 🛠️ Tech Stack

* **Backend**: Python, Flask, Gunicorn
* **AI**: Google Gemini API
* **Vector Database**: ChromaDB
* **Deployment**: Docker, Fly.io

---

## Usage

The application is designed to be self-explanatory. Upon launching the web interface, you'll be prompted to enter a unique User ID.

Once you've set your User ID, you can start a new chat by typing a topic name into the "Topic" field. You can enhance a topic's context by using the "Ingest Content" section to upload files or provide a GitHub repository URL.

To see what sources have been added to a topic's context, click the **"View Context"** button
