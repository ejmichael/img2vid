import os
import torch
<<<<<<< HEAD
import random
import diffusers
print(f"DEBUG: Diffusers version: {diffusers.__version__}")
# The official class name in latest diffusers is LTXPipeline
try:
    from diffusers import LTXPipeline
except ImportError:
    # Older community implementation support
    from diffusers import LTXVideoPipeline as LTXPipeline

=======
from diffusers import AnimateDiffPipeline, MotionAdapter, EulerDiscreteScheduler
from diffusers.utils import export_to_gif
>>>>>>> acf77ad9603785ec6b875a72ef483968aa79d4f2
from PIL import Image
import numpy as np
import imageio

class ImageToVideoModel:
<<<<<<< HEAD
    def __init__(self, model_id="Lightricks/LTX-Video"):
        # LTX-Video is the new standard for realistic, efficient video generation.
        # It handles motion and realism significantly better than older UNet models.
        self.model_id = model_id
        self.pipeline = None
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"DEBUG: Torch CUDA available: {torch.cuda.is_available()}")

    def load_model(self):
        """
        Loads LTX-Video.
        """
        if self.pipeline:
            return

        print(f"Loading LTX-Video ({self.model_id}) on {self.device}...")
        
        try:
            self.pipeline = LTXPipeline.from_pretrained(
                self.model_id, 
                torch_dtype=torch.bfloat16 if self.device == "cuda" else torch.float32,
                low_cpu_mem_usage=True, # Critical safety feature for Hugging Face RAM
            )
            
            if self.device == "cuda":
                # Keep in VRAM to avoid HF System RAM limit OOM
                self.pipeline.to("cuda")
            
            print(">>> REAL AI: LTX-Video Loaded successfully.")
        except Exception as e:
            print(f"CRITICAL ERROR LOADING MODEL: {e}")
            import traceback
            traceback.print_exc()
            self.pipeline = "mock"

    def generate(self, image_path: str, output_path: str, prompt="", num_frames=81):
        """
        Generates animation using LTX-Video.
        LTX-Video handles 0.5s to 5s generations. 81 frames is ~3-4 seconds.
=======
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
>>>>>>> acf77ad9603785ec6b875a72ef483968aa79d4f2
        """
        if not self.pipeline:
            raise Exception("Model not loaded. Call load_model() first.")

        if self.pipeline == "mock":
<<<<<<< HEAD
            return self._generate_mock(image_path, output_path)

        print(f">>> REAL AI: Generating LTX-Video animation for {image_path}...")
        
        # 1. Load and prepare image
        img = Image.open(image_path).convert("RGB")
        # LTX-Video prefers multiples of 32. 704x480 is a good medium.
        # It also handles 512x512 or 768x512.
        img = img.resize((768, 512))
        
        # 2. Random Seed
        seed = random.randint(0, 1000000)
        generator = torch.manual_seed(seed)
        print(f">>> REAL AI: Using seed: {seed}")

        # 3. Run Pipeline
        full_prompt = prompt if prompt else "cinematic high quality motion, realistic"
        
        with torch.no_grad():
            # LTX-Video I2V uses image as the 'image' argument
            output = self.pipeline(
                prompt=full_prompt,
                image=img,
                num_frames=num_frames, # 81 frames
                width=768,
                height=512,
                num_inference_steps=30,
                guidance_scale=4.0,
                generator=generator
            )
            frames = output.frames[0]
            
            if self.device == "cuda":
                torch.cuda.empty_cache()

        # 4. Save to MP4
        frames_np = [np.array(f) for f in frames]
        imageio.mimsave(output_path, frames_np, fps=24) # Smooth 24fps
=======
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
>>>>>>> acf77ad9603785ec6b875a72ef483968aa79d4f2
        
        print(f"AI Video saved to {output_path}")
        return output_path

<<<<<<< HEAD
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
=======
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
>>>>>>> acf77ad9603785ec6b875a72ef483968aa79d4f2
            frames.append(np.array(frame))
        imageio.mimsave(output_path, frames, fps=8)
        return output_path

# Global instance for the worker to use
model_instance = ImageToVideoModel()
