#!/bin/bash

# Start the FastAPI Backend on port 8000
# The backend serves both the API and the built React frontend as static files.
cd /app/backend
python3 main.py
