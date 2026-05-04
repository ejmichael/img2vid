# Base image with CUDA 12.1
FROM nvidia/cuda:12.1.1-runtime-ubuntu22.04

# Install system dependencies (Node.js for frontend build, no Redis needed)
RUN apt-get update && apt-get install -y \
    python3.10 \
    python3-pip \
    nodejs \
    npm \
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

# Upgrade AI libraries AFTER torch to prevent downgrades
RUN pip3 install -U diffusers transformers accelerate

# Copy and build frontend
COPY frontend/ ./frontend/
RUN cd frontend && npm ci && npm run build

# Copy backend and start script
COPY backend/ ./backend/
COPY start.sh ./
RUN chmod +x start.sh

# Environment
ENV PORT=8000
ENV PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
ENV HF_HUB_ENABLE_HF_TRANSFER=1

# RunPod HTTP proxy port
EXPOSE 8000

CMD ["./start.sh"]
