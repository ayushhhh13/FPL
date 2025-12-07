@echo off
REM Start script for Credit Card Assistant (Windows)

echo Starting Credit Card Assistant...

REM Check if .env exists
if not exist .env (
    echo .env file not found. Please create it from .env.example
    exit /b 1
)

REM Start Node.js backend
echo Starting Node.js API service...
start "Node.js API" cmd /k "cd nodejs_backend && node server.js"

REM Wait a bit
timeout /t 2 /nobreak >nul

REM Start Python backend
echo Starting Python backend...
start "Python Backend" cmd /k "cd python_backend && python app.py"

REM Wait a bit
timeout /t 3 /nobreak >nul

REM Start Streamlit UI
echo Starting Streamlit UI...
streamlit run ui/app.py

