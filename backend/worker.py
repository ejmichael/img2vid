import os
import time
import multiprocessing

# CRITICAL: This must be at the very top to fix the CUDA error
try:
    multiprocessing.set_start_method('spawn', force=True)
except RuntimeError:
    pass

from model import model_instance
from rq import Worker, Queue, SimpleWorker
from queue_manager import redis_conn

# Ensure directories exist
os.makedirs("inputs", exist_ok=True)
os.makedirs("outputs", exist_ok=True)

def process_image_job(image_path, job_id, prompt):
    """
    Function that runs inside the worker process to handle the generation.
    """
    # CRITICAL: Load model INSIDE the job to prevent CUDA Fork errors
    model_instance.load_model()
    
    print(f"Worker processing job: {job_id} for image: {image_path} with prompt: {prompt}")
    output_path = os.path.join("outputs", f"{job_id}.mp4")
    
    try:
        # Run the model generation
        model_instance.generate(image_path, output_path, prompt=prompt)
        return {"status": "done", "video_path": output_path}
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        print(f"CRITICAL ERROR in worker job {job_id}:\n{error_trace}")
        return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    print("Worker started. Listening for jobs on 'image_to_video'...")
    # ALWAYS use SimpleWorker on single-GPU servers to avoid CUDA fork issues
    worker = SimpleWorker(["image_to_video"], connection=redis_conn)
    worker.work()
