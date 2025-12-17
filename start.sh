#!/bin/bash
# ApoloCopilot Startup Script for Replit

echo "🚀 Starting ApoloCopilot Platform..."

# Create necessary directories
mkdir -p database uploads/documents uploads/avatars frontend

# Install dependencies if not installed
if [ ! -f ".dependencies_installed" ]; then
    echo "📦 Installing dependencies..."
    pip install -r requirements.txt
    touch .dependencies_installed
fi

# Initialize database
echo "📊 Initializing database..."
python init_database.py

# Start the server
echo "🌐 Starting server on port 8000..."
python -m uvicorn app_main:app --host 0.0.0.0 --port 8000 --reload
