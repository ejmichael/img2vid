#!/bin/bash

# Start Redis in the background
redis-server --daemonize yes

# Wait for redis to start
sleep 2

# Start the Worker in the background
cd /app/backend
python3 worker.py &

# Start the FastAPI Backend (API + Frontend)
# Note: We use port 7860 as it is the default for Hugging Face Spaces
cd /app/backend
uvicorn main:app --host 0.0.0.0 --port 7860
