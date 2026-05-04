import os
import uuid
<<<<<<< HEAD
import threading
from fastapi import FastAPI, UploadFile, File, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
=======
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from queue_manager import job_queue, redis_conn
from rq.job import Job
>>>>>>> acf77ad9603785ec6b875a72ef483968aa79d4f2
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="Image-to-Video AI API")

<<<<<<< HEAD
# Enable CORS for frontend dev server
=======
# Enable CORS for frontend
>>>>>>> acf77ad9603785ec6b875a72ef483968aa79d4f2
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ensure directories exist
os.makedirs("inputs", exist_ok=True)
os.makedirs("outputs", exist_ok=True)

# Serve output videos as static files
app.mount("/outputs", StaticFiles(directory="outputs"), name="outputs")

<<<<<<< HEAD
# In-memory job store (replaces Redis for local dev)
jobs: dict = {}

def _run_job(job_id: str, image_path: str, prompt: str):
    """Run AI generation in a background thread."""
    from model import model_instance
    jobs[job_id] = {"status": "processing"}
    try:
        model_instance.load_model()
        output_path = os.path.join("outputs", f"{job_id}.mp4")
        model_instance.generate(image_path, output_path, prompt=prompt)
        jobs[job_id] = {"status": "done", "video_url": f"/outputs/{job_id}.mp4"}
    except Exception as e:
        import traceback
        print(f"CRITICAL ERROR in job {job_id}:\n{traceback.format_exc()}")
        jobs[job_id] = {"status": "error", "message": str(e)}


@app.post("/generate")
async def generate_video(
    image: UploadFile = File(...),
    prompt: str = Form("cinematic motion, high quality")
):
=======
# NEW: Serve the built frontend
# We look for 'frontend-dist' (Docker) or '../frontend/dist' (Local/Git)
possible_paths = ["../frontend-dist", "../frontend/dist", "./frontend/dist", "frontend/dist"]
frontend_path = None

for p in possible_paths:
    abs_p = os.path.abspath(p)
    if os.path.exists(abs_p):
        frontend_path = abs_p
        print(f"Found frontend at: {frontend_path}")
        break

if frontend_path:
    app.mount("/", StaticFiles(directory=frontend_path, html=True), name="frontend")
else:
    print("WARNING: Frontend 'dist' folder NOT FOUND. Check your directory structure!")

@app.post("/generate")
async def generate_video(image: UploadFile = File(...)):
>>>>>>> acf77ad9603785ec6b875a72ef483968aa79d4f2
    # Validate file size (5MB limit)
    content = await image.read()
    if len(content) > 5 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File too large (max 5MB)")
<<<<<<< HEAD

    # Validate file type
    if not image.filename.lower().endswith((".png", ".jpg", ".jpeg")):
        raise HTTPException(status_code=400, detail="Invalid file type. Only PNG and JPG allowed.")

    job_id = str(uuid.uuid4())
    ext = os.path.splitext(image.filename)[1]
    image_path = os.path.join("inputs", f"{job_id}{ext}")

    # Save file
    with open(image_path, "wb") as f:
        f.write(content)

    # Register job as queued, then launch background thread
    jobs[job_id] = {"status": "queued"}
    t = threading.Thread(target=_run_job, args=(job_id, image_path, prompt), daemon=True)
    t.start()

    return {"job_id": job_id}


@app.get("/status/{job_id}")
async def get_status(job_id: str):
    job = jobs.get(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")
    return job


if __name__ == "__main__":
    import uvicorn

    # In Docker, frontend is built to /app/frontend/dist
    # Locally it may be at ../frontend/dist
    possible_paths = [
        "/app/frontend/dist",
        "../frontend/dist",
        "./frontend/dist",
    ]
    for p in possible_paths:
        abs_p = os.path.abspath(p)
        if os.path.exists(abs_p):
            print(f"Found frontend at: {abs_p}")
            app.mount("/", StaticFiles(directory=abs_p, html=True), name="frontend")
            break

    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
=======
    
    # Validate file type
    if not image.filename.lower().endswith((".png", ".jpg", ".jpeg")):
        raise HTTPException(status_code=400, detail="Invalid file type. Only PNG and JPG allowed.")
    
    job_id = str(uuid.uuid4())
    ext = os.path.splitext(image.filename)[1]
    image_path = os.path.join("inputs", f"{job_id}{ext}")
    
    # Save file
    with open(image_path, "wb") as f:
        f.write(content)
    
    # Add to queue
    # The function 'process_image_job' is imported from worker but we use string path for RQ if needed,
    # or just import it here.
    from worker import process_image_job
    job = job_queue.enqueue(process_image_job, image_path, job_id, job_id=job_id)
    
    return {"job_id": job_id}

@app.get("/status/{job_id}")
async def get_status(job_id: str):
    try:
        job = Job.fetch(job_id, connection=redis_conn)
    except Exception:
        raise HTTPException(status_code=404, detail="Job not found")
    
    if job.is_failed:
        return {"status": "error", "message": "Job failed"}
    elif job.is_finished:
        # Result from process_image_job
        result = job.result
        if result and result.get("status") == "done":
            video_url = f"/outputs/{job_id}.mp4"
            return {"status": "done", "video_url": video_url}
        else:
            return {"status": "error", "message": result.get("message") if result else "Unknown error"}
    elif job.is_started:
        return {"status": "processing"}
    else:
        return {"status": "queued"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
>>>>>>> acf77ad9603785ec6b875a72ef483968aa79d4f2
