#!/bin/bash

echo "🚀 Starting Casino-Club F2P Backend Server..."
echo "Working directory: $(pwd)"
echo "Python version: $(python --version)"
echo "Environment: ${APP_ENV:-development}"

# Change to application directory
cd /app

# Database auto-initialization
echo "📋 Database Auto-Initialization"
python db_auto_init.py

# Start the FastAPI server
echo "🔥 Starting FastAPI server..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
