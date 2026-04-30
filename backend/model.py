import os
import torch
import random
from diffusers import I2VGenXLPipeline
from PIL import Image
import numpy as np
import imageio

class ImageToVideoModel:
    def __init__(self, model_id="ali-vilab/i2vgen-xl"):
        # I2VGen-XL is a high-fidelity, realistic image-to-video model from Alibaba
        self.model_id = model_id
        self.pipeline = None
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"DEBUG: Torch CUDA available: {torch.cuda.is_available()}")

    def load_model(self):
        """
        Loads I2VGen-XL.
        """
        if self.pipeline:
            return

        print(f"Loading I2VGen-XL ({self.model_id}) on {self.device}...")
        
        try:
            self.pipeline = I2VGenXLPipeline.from_pretrained(
                self.model_id, 
                torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
                variant="fp16" if self.device == "cuda" else None,
            )
            
            if self.device == "cuda":
                self.pipeline.to(self.device)
            
            print(">>> REAL AI: I2VGen-XL Loaded successfully.")
        except Exception as e:
            print(f"CRITICAL ERROR LOADING MODEL: {e}")
            import traceback
            traceback.print_exc()
            self.pipeline = "mock"

    def generate(self, image_path: str, output_path: str, prompt="", num_frames=16):
        """
        Generates animation using I2VGen-XL.
        Default is 16 frames.
        """
        if not self.pipeline:
            raise Exception("Model not loaded. Call load_model() first.")

        if self.pipeline == "mock":
            return self._generate_mock(image_path, output_path)

        print(f">>> REAL AI: Generating I2VGen-XL animation for {image_path}...")
        
        # 1. Load and prepare image
        img = Image.open(image_path).convert("RGB")
        # I2VGen-XL prefers 704x448
        img = img.resize((704, 448))
        
        # 2. Random Seed
        seed = random.randint(0, 1000000)
        generator = torch.manual_seed(seed)
        print(f">>> REAL AI: Using seed: {seed}")

        # 3. Run Pipeline
        full_prompt = prompt if prompt else "cinematic high quality motion"
        
        with torch.no_grad():
            # I2VGen-XL uses 'image' as input
            frames = self.pipeline(
                prompt=full_prompt,
                image=img,
                num_inference_steps=50, # High quality
                guidance_scale=9.0,
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
