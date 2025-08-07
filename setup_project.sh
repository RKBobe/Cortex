#!/bin/bash

# A script to set up a full backend/frontend monorepo structure.

# --- Configuration ---
# Add any other python-related files or directories you have.
BACKEND_FILES=("app.py" "requirements.txt" "models.py" "config.py") # Add your files here

# --- Script ---
echo "🚀 Starting full project setup..."

# 1. SETUP BACKEND
# ==================================
echo -e "\nSetting up backend..."

if [ -d "backend" ]; then
  echo "Directory 'backend' already exists. Skipping backend setup."
else
  mkdir backend
  echo "Created directory: backend/"

  for item in "${BACKEND_FILES[@]}"; do
    if [ -f "$item" ]; then
      echo "Moving '$item' to 'backend/'"
      mv "$item" backend/
    else
      # This check prevents warnings for files you might not have
      echo "Info: File '$item' not found, skipping."
    fi
  done
fi
echo "✅ Backend setup complete."


# 2. SETUP FRONTEND
# ==================================
echo -e "\nSetting up frontend..."

if [ -d "frontend" ]; then
  echo "Directory 'frontend' already exists. Skipping frontend setup."
else
  echo "Creating new Vite + React + TS project in 'frontend/'..."
  # The command creates the 'frontend' dir and installs the project in it.
  npm create vite@latest frontend -- --template react-ts

  if [ $? -eq 0 ]; then
    echo "✅ Frontend project created successfully."
  else
    echo "❌ Error: Failed to create Vite project. Please check for errors."
    exit 1
  fi
fi

echo -e "\n🎉 Project setup complete! Your directory structure is ready."
echo "Next steps:"
echo "1. cd backend"
echo "2. pip install -r requirements.txt (to set up your Python environment)"
echo "3. cd ../frontend"
echo "4. npm install (to install frontend dependencies)"