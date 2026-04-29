# Base image with CUDA 12.1 (Best for SVD)
FROM nvidia/cuda:12.1.1-runtime-ubuntu22.04

# Install System dependencies
RUN apt-get update && apt-get install -y \
    python3.10 \
    python3-pip \
    redis-server \
    ffmpeg \
    libsm6 \
    libxext6 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Ensure we use python3 as python
RUN ln -s /usr/bin/python3 /usr/bin/python

# Copy requirements and install
COPY backend/requirements.txt ./backend/
RUN pip3 install --no-cache-dir -r backend/requirements.txt

# Force install matching Torch version for CUDA 12.1
RUN pip3 install --force-reinstall torch==2.5.1 torchvision==0.20.1 --index-url https://download.pytorch.org/whl/cu121

# Copy project files
COPY backend/ ./backend/
COPY frontend/dist/ ./frontend-dist/
COPY start.sh ./
RUN chmod +x start.sh

# Environment
ENV REDIS_URL=redis://localhost:6379
ENV PORT=7860

# HF Spaces requires port 7860
EXPOSE 7860

CMD ["./start.sh"]
