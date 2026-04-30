import os
import torch
import random
from diffusers import WanPipeline
from diffusers.quantizers import PipelineQuantizationConfig
from PIL import Image
import numpy as np
import imageio

class ImageToVideoModel:
    def __init__(self, model_id="Wan-AI/Wan2.1-I2V-14B-720P-Diffusers"):
        # The 14B model is the absolute King of Realism.
        # We use 4-bit quantization to fit this monster into the A10G's 24GB VRAM.
        self.model_id = model_id
        self.pipeline = None
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"DEBUG: Torch CUDA available: {torch.cuda.is_available()}")

    def load_model(self):
        """
        Loads Wan-2.1-14B with 4-bit quantization.
        """
        if self.pipeline:
            return

        print(f"Loading Wan-2.1 14B ({self.model_id}) on {self.device}...")
        
        try:
            # High-performance 4-bit quantization for 14B parameters
            quant_config = PipelineQuantizationConfig(
                quant_backend="bitsandbytes_4bit",
                quant_kwargs={
                    "load_in_4bit": True, 
                    "bnb_4bit_compute_dtype": torch.float16,
                    "bnb_4bit_use_double_quant": True,
                    "bnb_4bit_quant_type": "nf4"
                },
                components_to_quantize=["transformer"],
            )

            self.pipeline = WanPipeline.from_pretrained(
                self.model_id, 
                quantization_config=quant_config,
                torch_dtype=torch.float16,
                low_cpu_mem_usage=True, # Critical to prevent OOM kills on A10G Small RAM
            )
            
            # Offloading is still recommended for 14B to ensure 24GB safety
            if self.device == "cuda":
                self.pipeline.enable_model_cpu_offload()
            
            print(">>> REAL AI: Wan-2.1 14B Loaded successfully.")
        except Exception as e:
            print(f"CRITICAL ERROR LOADING MODEL: {e}")
            import traceback
            traceback.print_exc()
            self.pipeline = "mock"

    def generate(self, image_path: str, output_path: str, prompt="", num_frames=81):
        """
        Generates animation using Wan-2.1.
        Wan defaults to 81 frames (~5-6 seconds).
        """
        if not self.pipeline:
            raise Exception("Model not loaded. Call load_model() first.")

        if self.pipeline == "mock":
            return self._generate_mock(image_path, output_path)

        print(f">>> REAL AI: Generating Wan-2.1 animation for {image_path}...")
        
        # 1. Load and prepare image
        img = Image.open(image_path).convert("RGB")
        # Wan-2.1 prefers 832x480 or 1280x720
        img = img.resize((832, 480))
        
        # 2. Random Seed
        seed = random.randint(0, 1000000)
        generator = torch.manual_seed(seed)
        print(f">>> REAL AI: Using seed: {seed}")

        # 3. Run Pipeline
        full_prompt = prompt if prompt else "cinematic high quality motion, photorealistic"
        
        with torch.no_grad():
            output = self.pipeline(
                prompt=full_prompt,
                image=img,
                num_frames=num_frames,
                num_inference_steps=30,
                guidance_scale=5.0,
                generator=generator
            )
            frames = output.frames[0]

        # 4. Save to MP4
        frames_np = [np.array(f) for f in frames]
        imageio.mimsave(output_path, frames_np, fps=16) # Wan standard fps
        
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
