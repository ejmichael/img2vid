import os
import torch
import random
from diffusers import CogVideoXImageToVideoPipeline
from PIL import Image
import numpy as np
import imageio

class ImageToVideoModel:
    def __init__(self, model_id="THUDM/CogVideoX-5b-I2V"):
        # CogVideoX-5B is the industry standard for realistic open video gen
        self.model_id = model_id
        self.pipeline = None
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"DEBUG: Torch CUDA available: {torch.cuda.is_available()}")

    def load_model(self):
        """
        Loads CogVideoX-5B-I2V.
        """
        if self.pipeline:
            return

        print(f"Loading CogVideoX ({self.model_id}) on {self.device}...")
        
        try:
            self.pipeline = CogVideoXImageToVideoPipeline.from_pretrained(
                self.model_id, 
                torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
            )
            
            if self.device == "cuda":
                self.pipeline.to(self.device)
                # Essential for T4 (15GB) memory safety
                self.pipeline.enable_model_cpu_offload()
                # Optional: self.pipeline.enable_sequential_cpu_offload() for even less VRAM
            
            print(">>> REAL AI: CogVideoX Loaded successfully.")
        except Exception as e:
            print(f"CRITICAL ERROR LOADING MODEL: {e}")
            import traceback
            traceback.print_exc()
            self.pipeline = "mock"

    def generate(self, image_path: str, output_path: str, prompt="", num_frames=49):
        """
        Generates animation using CogVideoX.
        CogVideoX defaults to 49 frames (~6 seconds at 8fps).
        """
        if not self.pipeline:
            raise Exception("Model not loaded. Call load_model() first.")

        if self.pipeline == "mock":
            return self._generate_mock(image_path, output_path)

        print(f">>> REAL AI: Generating CogVideoX animation for {image_path}...")
        
        # 1. Load and prepare image
        img = Image.open(image_path).convert("RGB")
        # CogVideoX 5B I2V standard resolution is 720x480 or similar
        img = img.resize((720, 480))
        
        # 2. Random Seed
        seed = random.randint(0, 1000000)
        generator = torch.manual_seed(seed)
        print(f">>> REAL AI: Using seed: {seed}")

        # 3. Run Pipeline
        full_prompt = prompt if prompt else "cinematic high quality motion"
        
        with torch.no_grad():
            frames = self.pipeline(
                prompt=full_prompt,
                image=img,
                num_frames=num_frames,
                num_inference_steps=30,
                guidance_scale=6.0,
                generator=generator
            ).frames[0]

        # 4. Save to MP4
        frames_np = [np.array(f) for f in frames]
        imageio.mimsave(output_path, frames_np, fps=8)
        
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
