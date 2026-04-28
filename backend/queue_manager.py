import os
from redis import Redis
from rq import Queue
from dotenv import load_dotenv

load_dotenv()

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")

# Connect to Redis
redis_conn = Redis.from_url(REDIS_URL)

# Create a queue
job_queue = Queue("image_to_video", connection=redis_conn)
