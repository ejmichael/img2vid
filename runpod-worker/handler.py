import runpod
import torch
import base64
import io
import os
import tempfile
from pathlib import Path
from PIL import Image

MODEL_ID = os.environ.get("MODEL_ID", "Lightricks/LTX-Video-0.9.7-distilled")
MODEL_CACHE = "/workspace/models/ltx-video"

# Download model on first startup (persists on the worker's disk across warm invocations)
if not Path(MODEL_CACHE).exists():
    print(f"[startup] Downloading {MODEL_ID} — this only happens once per worker...")
    from huggingface_hub import snapshot_download
    snapshot_download(
        repo_id=MODEL_ID,
        local_dir=MODEL_CACHE,
        token=os.environ.get("HF_TOKEN"),
    )
    print("[startup] Download complete.")

print("[startup] Loading model into GPU...")

from diffusers import LTXImageToVideoPipeline
from diffusers.utils import export_to_video

pipe = LTXImageToVideoPipeline.from_pretrained(
    MODEL_CACHE,
    torch_dtype=torch.bfloat16,
    local_files_only=True,
)
pipe.to("cuda")
pipe.enable_vae_slicing()

print("[startup] Ready.")


def handler(job):
    inp = job["input"]

    image_b64: str = inp["image"]
    prompt: str = inp["prompt"]
    negative_prompt = inp.get(
        "negative_prompt",
        "worst quality, inconsistent motion, blurry, jittery, distorted",
    )
    num_frames = int(inp.get("num_frames", 25))
    num_inference_steps = int(inp.get("num_inference_steps", 8))
    guidance_scale = float(inp.get("guidance_scale", 1.0))
    seed = int(inp.get("seed", -1))
    width = int(inp.get("width", 704))
    height = int(inp.get("height", 480))
    fps = int(inp.get("fps", 24))

    if "," in image_b64:
        image_b64 = image_b64.split(",")[1]
    image = Image.open(io.BytesIO(base64.b64decode(image_b64))).convert("RGB")
    image = image.resize((width, height))

    generator = (
        torch.Generator(device="cuda").manual_seed(seed) if seed != -1 else None
    )

    output = pipe(
        image=image,
        prompt=prompt,
        negative_prompt=negative_prompt,
        num_frames=num_frames,
        num_inference_steps=num_inference_steps,
        guidance_scale=guidance_scale,
        width=width,
        height=height,
        generator=generator,
    )

    with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as tmp:
        tmp_path = tmp.name

    export_to_video(output.frames[0], tmp_path, fps=fps)

    with open(tmp_path, "rb") as f:
        video_b64 = base64.b64encode(f.read()).decode("utf-8")

    os.unlink(tmp_path)

    return {"video_b64": video_b64}


runpod.serverless.start({"handler": handler})
