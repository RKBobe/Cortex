#!/bin/bash

# --- Safety Check: Ensure backend and frontend directories exist ---
if [ ! -d "backend" ] || [ ! -d "frontend" ]; then
  echo "❌ Error: 'backend' or 'frontend' directory not found. Please create them first."
  exit 1
fi

echo "🚀 Organizing project files..."

# --- Move Backend Files & Directories ---
# List all files and directories that should go into the 'backend' folder.
BACKEND_ITEMS=(
  "BHv3"
  "__pycache__"
  "backend.py"
  "context_chat.py"
  "contexts"
  "cortex_db"
  "ingest_code.py"
  "static"
  "templates"
  "vectordb"
  "venv"
)

for item in "${BACKEND_ITEMS[@]}"; do
  if [ -e "$item" ]; then
    echo "Moving '$item' to 'backend/'"
    mv "$item" backend/
  else
    echo "Info: '$item' not found, skipping."
  fi
done

# --- Move Root-Level Configuration Files ---
# These files typically live in the project root, not in the backend.
# The script will move them from 'backend' back out to the root if they were moved.
ROOT_ITEMS=(
  "Dockerfile"
  "fly.toml"
)

for item in "${ROOT_ITEMS[@]}"; do
    # This checks if the item ended up inside /backend and moves it out
    if [ -e "backend/$item" ]; then
        echo "Moving '$item' to project root."
        mv "backend/$item" .
    # This handles the case where the file is already in the right place
    elif [ -e "$item" ]; then
        echo "'$item' is already in the project root."
    fi
done


echo "✅ File organization complete!"