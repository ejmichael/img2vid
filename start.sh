#!/bin/bash

# 1. Start Redis in the background
redis-server --daemonize yes

# 2. Start the AI Worker in the background
cd /app/backend
python3 worker.py &

# 3. Start the FastAPI Backend (Port 7860 is required for Spaces)
# We run this in the foreground so the container doesn't exit
python3 main.py
