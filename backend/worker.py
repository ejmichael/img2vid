import os
import time
from model import model_instance
from rq import Worker, Queue, SimpleWorker
from queue_manager import redis_conn

# Ensure directories exist
os.makedirs("inputs", exist_ok=True)
os.makedirs("outputs", exist_ok=True)

def process_image_job(image_path, job_id):
    """
    Function that runs inside the worker process to handle the generation.
    """
    print(f"Worker processing job: {job_id} for image: {image_path}")
    output_path = os.path.join("outputs", f"{job_id}.mp4")
    
    try:
        # Run the model generation
        model_instance.generate(image_path, output_path)
        return {"status": "done", "video_path": output_path}
    except Exception as e:
        print(f"Error in worker job {job_id}: {e}")
        return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    # Load model once at startup
    model_instance.load_model()
    
    print("Worker started. Listening for jobs (Windows-compatible mode)...")
    worker = SimpleWorker(["image_to_video"], connection=redis_conn)
    worker.work()
