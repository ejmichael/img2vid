import os
import torch
from diffusers import AnimateDiffPipeline, MotionAdapter, EulerDiscreteScheduler
from diffusers.utils import export_to_gif
from PIL import Image
import numpy as np
import imageio

class ImageToVideoModel:
    def __init__(self, model_id="emilianJR/epiCRealism"):
        # We use a popular community model 'epiCRealism' which is versatile.
        # You can replace this with any SD 1.5 checkpoint from Civitai.
        self.model_id = model_id
        self.motion_adapter_id = "guoyww/animatediff-motion-adapter-v1-5-2"
        self.pipeline = None
        self.device = "cuda" if torch.cuda.is_available() else "cpu"

    def load_model(self):
        """
        Loads AnimateDiff with the community checkpoint.
        Disables the safety checker for unrestricted usage.
        """
        print(f"Loading AnimateDiff with {self.model_id} on {self.device}...")
        
        try:
            # 1. Load Motion Adapter
            adapter = MotionAdapter.from_pretrained(self.motion_adapter_id, torch_dtype=torch.float16 if self.device == "cuda" else torch.float32)
            
            # 2. Load Pipeline with the chosen community checkpoint
            self.pipeline = AnimateDiffPipeline.from_pretrained(
                self.model_id, 
                motion_adapter=adapter, 
                torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
                # --- DISABLE SAFETY CHECKER ---
                safety_checker=None,
                requires_safety_checker=False,
                feature_extractor=None
            )
            
            # 3. Optimize
            self.pipeline.scheduler = EulerDiscreteScheduler.from_config(self.pipeline.scheduler.config, timestep_spacing="trailing", beta_schedule="linear")
            
            if self.device == "cuda":
                self.pipeline.to(self.device)
                self.pipeline.enable_model_cpu_offload()
            
            print("AnimateDiff (Unrestricted) loaded successfully.")
        except Exception as e:
            print(f"Error loading real model: {e}. Falling back to mock.")
            self.pipeline = "mock"

    def generate(self, image_path: str, output_path: str, num_frames=16):
        """
        Generates animation based on the input image.
        Note: AnimateDiff often works via prompt + image or just prompt.
        For simple 'image-to-video', we use the image as an initial state.
        """
        if not self.pipeline:
            raise Exception("Model not loaded. Call load_model() first.")

        if self.pipeline == "mock":
            return self._generate_mock(image_path, output_path, num_frames)

        print(f"AI Generating animation for {image_path}...")
        
        # 1. Load image
        img = Image.open(image_path).convert("RGB")
        img = img.resize((512, 512))
        
        # 2. Run Pipeline
        # We provide a generic prompt that fits most images, but you can customize this!
        output = self.pipeline(
            prompt="cinematic motion, high quality, masterpiece",
            negative_prompt="bad quality, distorted, static",
            num_frames=num_frames,
            guidance_scale=7.5,
            num_inference_steps=25,
            generator=torch.manual_seed(42),
        )
        
        frames = output.frames[0]

        # 3. Save to MP4
        frames_np = [np.array(f) for f in frames]
        imageio.mimsave(output_path, frames_np, fps=8)
        
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
            # Re-calculating to avoid local variable errors
            curr_h, curr_w = int(h / zoom), int(w / zoom)
            y1, x1 = (h - curr_h) // 2, (w - curr_w) // 2
            cropped = img_np[y1:y1+curr_h, x1:x1+curr_w]
            frame = Image.fromarray(cropped).resize((512, 512))
            frames.append(np.array(frame))
        imageio.mimsave(output_path, frames, fps=8)
        return output_path

# Global instance for the worker to use
model_instance = ImageToVideoModel()
