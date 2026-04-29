import os
import torch
import random
from diffusers import StableVideoDiffusionPipeline
from PIL import Image
import numpy as np
import imageio

class ImageToVideoModel:
    def __init__(self, model_id="stabilityai/stable-video-diffusion-img2vid-xt-1-1"):
        # We use SVD 1.1 which is the most breathtaking for image-to-video
        self.model_id = model_id
        self.pipeline = None
        self.device = "cuda" if torch.cuda.is_available() else "cpu"

    def load_model(self):
        """
        Loads Stable Video Diffusion.
        Disables the safety checker for unrestricted usage.
        """
        if self.pipeline and self.pipeline != "mock":
            return

        print(f"Loading SVD ({self.model_id}) on {self.device}...")
        
        try:
            # 1. Try official repo with token
            print(f">>> REAL AI: Attempting to load official {self.model_id}...")
            self.pipeline = StableVideoDiffusionPipeline.from_pretrained(
                self.model_id, 
                torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
                variant="fp16" if self.device == "cuda" else None,
                token=True # Forces use of the token you just logged in with
            )
        except Exception as e:
            print(f">>> REAL AI: Official repo failed ({e}). Trying community mirror...")
            try:
                # 2. Try community mirror (not gated)
                mirror_id = "vdo/stable-video-diffusion-img2vid-xt-1-1"
                self.pipeline = StableVideoDiffusionPipeline.from_pretrained(
                    mirror_id,
                    torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
                    variant="fp16" if self.device == "cuda" else None,
                )
            except Exception as mirror_e:
                print(f"CRITICAL ERROR LOADING MODELS: {mirror_e}")
                import traceback
                traceback.print_exc()
                self.pipeline = "mock"
                return

        if self.device == "cuda":
            self.pipeline.to(self.device)
        
        print(">>> REAL AI: SVD loaded successfully.")

    def generate(self, image_path: str, output_path: str, prompt=None, num_frames=25):
        """
        Generates animation based on the input image.
        """
        if not self.pipeline:
            raise Exception("Model not loaded. Call load_model() first.")

        if self.pipeline == "mock":
            print("!!! WARNING: FAILED TO LOAD REAL AI. USING MOCK ZOOM INSTEAD !!!")
            return self._generate_mock(image_path, output_path, num_frames)

        print(f">>> REAL AI: Generating SVD animation for {image_path}...")
        
        # 1. Load image
        img = Image.open(image_path).convert("RGB")
        img = img.resize((1024, 576)) # SVD standard resolution
        
        # 2. Random Seed for unique results
        seed = random.randint(0, 1000000)
        generator = torch.manual_seed(seed)
        print(f">>> REAL AI: Using seed: {seed}")

        # 3. Run Pipeline
        with torch.no_grad():
            frames = self.pipeline(
                img, 
                decode_chunk_size=8, 
                num_frames=num_frames, 
                motion_bucket_id=180, # INCREASED from 127 for more motion
                noise_aug_strength=0.1, # Increased for more variety
                generator=generator
            ).frames[0]

        # 4. Save to MP4
        frames_np = [np.array(f) for f in frames]
        imageio.mimsave(output_path, frames_np, fps=7)
        
        print(f"AI Video saved to {output_path}")
        return output_path

    def _generate_mock(self, image_path: str, output_path: str, num_frames=16):
        """Fallback mock animation logic"""
        print("Using Mock Animation (No GPU/Real Model found)")
        img = Image.open(image_path).convert("RGB").resize((512, 512))
        frames = []
        img_np = np.array(img)
        for i in range(num_frames):
            zoom = 1 + (i * 0.01)
            h, w = img_np.shape[:2]
            curr_h, curr_w = int(h / zoom), int(w / zoom)
            y1, x1 = (h - curr_h) // 2, (w - curr_w) // 2
            cropped = img_np[y1:y1+curr_h, x1:x1+curr_w]
            frame = Image.fromarray(cropped).resize((512, 512))
            frames.append(np.array(frame))
        imageio.mimsave(output_path, frames, fps=8)
        return output_path

# Global instance for the worker to use
model_instance = ImageToVideoModel()
