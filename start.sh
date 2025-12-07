#!/bin/bash

# Start script for Credit Card Assistant
# This script starts all required services

echo "🚀 Starting Credit Card Assistant..."

# Check if .env exists
if [ ! -f .env ]; then
    echo "⚠️  .env file not found. Running with default values."
    echo "   Some features may not work without proper API keys."
fi

# Start Node.js backend in background
echo "📡 Starting Node.js API service..."
cd nodejs_backend
node server.js &
NODE_PID=$!
cd ..

# Wait a bit for Node.js to start
sleep 2

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Start Python backend in background
echo "🐍 Starting Python backend..."
cd python_backend
python app.py &
PYTHON_PID=$!
cd ..

# Wait a bit for Python backend to start
sleep 3

# Start Streamlit UI
echo "🎨 Starting Streamlit UI..."
streamlit run ui/app.py

# Cleanup on exit
trap "kill $NODE_PID $PYTHON_PID 2>/dev/null" EXIT

