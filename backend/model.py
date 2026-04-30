import os
import torch
import random
from diffusers import WanPipeline
from PIL import Image
import numpy as np
import imageio

class ImageToVideoModel:
    def __init__(self, model_id="Wan-AI/Wan2.1-I2V-1.3B-720P-Diffusers"):
        # Wan-2.1 is the new GOAT for open video generation
        self.model_id = model_id
        self.pipeline = None
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"DEBUG: Torch CUDA available: {torch.cuda.is_available()}")

    def load_model(self):
        """
        Loads Wan-2.1-I2V.
        """
        if self.pipeline:
            return

        print(f"Loading Wan-2.1 ({self.model_id}) on {self.device}...")
        
        try:
            self.pipeline = WanPipeline.from_pretrained(
                self.model_id, 
                torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
                variant="fp16" if self.device == "cuda" else None,
            )
            
            if self.device == "cuda":
                self.pipeline.to(self.device)
                # Wan is heavy, so we use cpu offload for T4 compatibility
                self.pipeline.enable_model_cpu_offload()
            
            print(">>> REAL AI: Wan-2.1 loaded successfully.")
        except Exception as e:
            print(f"CRITICAL ERROR LOADING MODEL: {e}")
            import traceback
            traceback.print_exc()
            self.pipeline = "mock"

    def generate(self, image_path: str, output_path: str, prompt="", num_frames=81):
        """
        Generates animation based on the input image using Wan-2.1.
        Wan-2.1 defaults to 81 frames (~5 seconds).
        """
        if not self.pipeline:
            raise Exception("Model not loaded. Call load_model() first.")

        if self.pipeline == "mock":
            return self._generate_mock(image_path, output_path)

        print(f">>> REAL AI: Generating Wan-2.1 animation for {image_path}...")
        
        # 1. Load and prepare image
        img = Image.open(image_path).convert("RGB")
        # Wan-2.1-I2V-1.3B usually handles 720p (1280x720) or 480p well
        # We'll stick to a standard size for T4 VRAM safety
        img = img.resize((832, 480))
        
        # 2. Random Seed
        seed = random.randint(0, 1000000)
        generator = torch.manual_seed(seed)
        print(f">>> REAL AI: Using seed: {seed}")

        # 3. Run Pipeline
        # Wan-2.1 uses a combined prompt + image interface
        full_prompt = prompt if prompt else "cinematic high quality motion"
        
        with torch.no_grad():
            output = self.pipeline(
                prompt=full_prompt,
                image=img,
                num_frames=num_frames, # 81 is standard
                height=480,
                width=832,
                num_inference_steps=30,
                guidance_scale=5.0,
                generator=generator
            )
            frames = output.frames[0]

        # 4. Save to MP4
        # Wan generates at 16 FPS usually, but we can set 24 for smoothness
        frames_np = [np.array(f) for f in frames]
        imageio.mimsave(output_path, frames_np, fps=16)
        
        print(f"AI Video saved to {output_path}")
        return output_path

    def _generate_mock(self, image_path, output_path):
        """Fallback mock animation logic"""
        print("Using Mock Animation (No GPU/Real Model found)")
        img = Image.open(image_path).convert("RGB").resize((480, 480))
        frames = []
        img_np = np.array(img)
        for i in range(25):
            zoom = 1 + (i * 0.01)
            h, w = img_np.shape[:2]
            curr_h, curr_w = int(h / zoom), int(w / zoom)
            y1, x1 = (h - curr_h) // 2, (w - curr_w) // 2
            cropped = img_np[y1:y1+curr_h, x1:x1+curr_w]
            frame = Image.fromarray(cropped).resize((480, 480))
            frames.append(np.array(frame))
        imageio.mimsave(output_path, frames, fps=8)
        return output_path

# Global instance for the worker to use
model_instance = ImageToVideoModel()
