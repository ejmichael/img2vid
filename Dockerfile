# Base image with CUDA and Python
FROM nvidia/cuda:11.8.0-runtime-ubuntu22.04

# Install Python and Redis
RUN apt-get update && apt-get install -y \
    python3.10 \
    python3-pip \
    redis-server \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy and install backend dependencies
COPY backend/requirements.txt ./backend/
RUN pip3 install --no-cache-dir -r backend/requirements.txt

# Copy backend code
COPY backend/ ./backend/

# Copy frontend build (assuming it is built or we use static serve)
# We will serve the dist folder later
COPY frontend/dist/ ./frontend-dist/

# Copy start script
COPY start.sh ./
RUN chmod +x start.sh

# Set environment
ENV REDIS_URL=redis://localhost:6379

# Expose port (HF default)
EXPOSE 7860

# Run the unified start script
CMD ["./start.sh"]
