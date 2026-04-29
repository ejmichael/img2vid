# Image-to-Video AI Web App

A full-stack application that converts a single uploaded image into a short (2–4 second) animated video clip using AI.

## Architecture

- **Frontend**: React (Vite), Tailwind CSS, Axios.
- **Backend**: FastAPI, Uvicorn.
- **Worker**: RQ (Redis Queue) for background AI processing.
- **AI/ML**: PyTorch, Diffusers (Placeholder for Stable Video Diffusion / AnimateDiff).

## Setup Instructions

### 1. Prerequisites

- Python 3.10+
- Node.js & npm
- Redis server (running locally on default port 6379)

### 2. Backend Setup

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```
2. Create a virtual environment and activate it:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Ensure your `.env` file is configured (one is provided by default).

### 3. Start Redis

Make sure you have Redis installed and running:
```bash
redis-server
```

### 4. Run the Application

You will need three terminal windows:

**Window 1: Start the Backend (API)**
```bash
cd backend
python main.py
```

**Window 2: Start the Worker (AI Engine)**
```bash
cd backend
python worker.py
```

**Window 3: Start the Frontend**
```bash
cd frontend
npm install
npm run dev
```

## AI Model Customization

The model logic is encapsulated in `backend/model.py`. 
- By default, it uses a **Mock zoom effect** to demonstrate the end-to-end flow without requiring a high-end GPU or large model downloads.
- To use a real model:
  1. Uncomment the `StableVideoDiffusionPipeline` code in `model.py`.
  2. Ensure you have a GPU with sufficient VRAM (16GB+ recommended).
  3. Update `MODEL_ID` in `.env` if needed.

## Features

- Simple image upload (PNG/JPG, max 5MB).
- Real-time job status polling.
- MP4 video generation and browser playback.
- Clean, premium UI with smooth animations.
