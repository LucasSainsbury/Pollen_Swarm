#!/usr/bin/env env python3
"""
Creative Advertising Campaign Image Generator Pipeline
=======================================================

A production-ready Python pipeline for generating creative advertising images
using text-to-image models optimized for CPU execution.

Installation:
-------------
# Minimal (API mode - recommended for CPU):
pip install pillow numpy requests

# Full local mode (requires more compute):
pip install pillow numpy requests torch torchvision diffusers transformers accelerate

Usage Examples:
---------------
# Quick generation using API (no GPU needed):
python creative_ad_generator.py --prompt "summer sale campaign" --out ./ads/summer.jpg

# Local CPU generation with custom settings:
python creative_ad_generator.py --prompt "luxury brand" --out ./ads/ --local --aspect 16:9 --filter warm_gold

# Batch generate all example prompts:
python creative_ad_generator.py --batch --out ./ads/

# Custom seed for reproducibility:
python creative_ad_generator.py --prompt "tech product launch" --out ./ads/ --seed 42

Author: Generated for creative advertising workflows
License: MIT
"""

import argparse
import json
import logging
import os
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union

import numpy as np
from PIL import Image, ImageEnhance, ImageFilter

# Optional imports for different modes
# Replace the requests import section with:
try:
    from huggingface_hub import InferenceClient
    HAS_HF_HUB = True
except ImportError:
    HAS_HF_HUB = False
    
try:
    import torch
    from diffusers import StableDiffusionPipeline
    HAS_DIFFUSERS = True
except ImportError:
    HAS_DIFFUSERS = False


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('creative_pipeline.log')
    ]
)
logger = logging.getLogger(__name__)


# Example creative advertising prompts
EXAMPLE_PROMPTS = [
    "bright summer supermarket sale with fresh produce, vibrant colors, photorealistic, high quality, professional advertising photography",
    "luxury winter campaign with gold typography, elegant snow background, premium brand aesthetic, cinematic lighting",
    "back-to-school energetic colorful theme, happy students, notebooks and pencils, bright and cheerful",
    "modern tech product launch, sleek smartphone, minimalist design, gradient blue background, studio lighting",
    "organic natural food brand, fresh vegetables on rustic wooden table, green and earthy tones, farm to table aesthetic",
    "fitness and wellness campaign, active lifestyle, sunrise yoga, motivational energy, healthy living",
    "holiday shopping season, festive decorations, gift boxes with ribbons, warm cozy atmosphere, celebration mood",
    "artisan coffee shop promotion, steaming latte with latte art, cozy cafe interior, morning light, premium quality"
]


# Brand color filter presets (RGB overlay values)
BRAND_FILTERS = {
    "warm_gold": (255, 215, 0, 30),      # Golden overlay, 30% opacity
    "cool_blue": (0, 119, 182, 25),       # Corporate blue
    "fresh_green": (46, 184, 92, 25),     # Natural/organic green
    "luxury_purple": (106, 27, 154, 30),  # Premium purple
    "energetic_red": (229, 28, 35, 25),   # Bold red
    "modern_teal": (0, 150, 136, 25),     # Contemporary teal
}


# Aspect ratio presets
ASPECT_RATIOS = {
    "1:1": (1024, 1024),      # Square - Instagram, Facebook
    "16:9": (1024, 576),      # Landscape - YouTube, presentations
    "9:16": (576, 1024),      # Portrait - Instagram Stories, TikTok
    "4:3": (1024, 768),       # Classic landscape
    "3:4": (768, 1024),       # Classic portrait
    "21:9": (1024, 439),      # Ultra-wide - banners
    "facebook_cover": (820, 312),  # Facebook cover photo
}


class CreativeImagePipeline:
    """
    Complete pipeline for generating and processing creative advertising images.
    
    Supports both API-based generation (fast, CPU-friendly) and local model
    execution (slower but more control).
    """

    def __init__(
            self,
            use_local: bool = False,
            model_name: str = "black-forest-labs/FLUX.1-dev",  # Updated model
            api_url: str = None,  # No longer needed
            hf_token: Optional[str] = None,
            brightness: float = 1.1,
            contrast: float = 1.15,
            saturation: float = 1.2,
            sharpness: float = 1.1,
            aspect_ratio: str = "16:9",
            brand_filter: Optional[str] = None
    ):
        """
        Initialize the creative image pipeline.

        Args:
            use_local: Whether to use local model (requires GPU/CPU compute)
            model_name: HuggingFace model identifier for local mode
            api_url: API endpoint for remote inference
            hf_token: HuggingFace API token (gets from env if not provided)
            brightness: Brightness adjustment factor (1.0 = no change)
            contrast: Contrast adjustment factor (1.0 = no change)
            saturation: Color saturation factor (1.0 = no change)
            sharpness: Sharpness factor (1.0 = no change)
            aspect_ratio: Target aspect ratio (e.g., "16:9", "1:1")
            brand_filter: Optional brand color filter name
        """
        self.use_local = use_local
        self.model_name = model_name
        self.api_url = api_url

        # Prioritize provided token, then environment variable
        self.hf_token = hf_token or os.getenv("HF_TOKEN")
        if self.hf_token:
            logger.info("✓ HuggingFace token loaded")
        else:
            logger.warning("No HuggingFace token found - API rate limits will be lower")

        self.brightness = brightness
        self.contrast = contrast
        self.saturation = saturation
        self.sharpness = sharpness
        self.aspect_ratio = aspect_ratio
        self.brand_filter = brand_filter

        self.pipe = None

        if use_local:
            self._initialize_local_model()
        else:
            self._check_api_requirements()
            # Initialize InferenceClient for API mode
            self.client = InferenceClient(
                provider="nebius",
                api_key=self.hf_token
            )
            logger.info("Using API mode with InferenceClient (fast, recommended for CPU)")

    def _initialize_local_model(self) -> None:
        """Initialize local Stable Diffusion model for CPU execution."""
        if not HAS_DIFFUSERS:
            raise ImportError(
                "Local mode requires diffusers and torch. Install with: "
                "pip install torch torchvision diffusers transformers accelerate"
            )

        logger.info(f"Loading local model: {self.model_name}")
        logger.info("⚠️  Note: CPU execution will be slow. Consider using API mode instead.")

        # Check for HuggingFace token
        token = self.hf_token or os.getenv("HF_TOKEN")
        if not token:
            logger.warning("No HuggingFace token found. Some models may require authentication.")
            logger.info("Set HF_TOKEN environment variable or pass --hf-token")

        try:
            # Load model optimized for CPU with authentication
            self.pipe = StableDiffusionPipeline.from_pretrained(
                self.model_name,
                torch_dtype=torch.float32,
                safety_checker=None,
                use_auth_token=token
            )

            self.pipe = self.pipe.to("cpu")
            self.pipe.enable_attention_slicing()

            logger.info("✓ Local model loaded successfully (CPU mode)")

        except Exception as e:
            logger.error(f"Failed to load local model: {e}")
            logger.info("💡 Tip: Try setting HF_TOKEN environment variable")
            logger.info("💡 Or use API mode without --local flag")
            raise

    def _check_api_requirements(self) -> None:
        """Check if required packages for API mode are available."""
        if not HAS_HF_HUB:
            raise ImportError(
                "API mode requires 'huggingface_hub' library. Install with: pip install huggingface_hub"
            )
        logger.debug("API requirements satisfied")

    def generate(
        self,
        prompt: str,
        seed: Optional[int] = None,
        num_inference_steps: int = 20,
        guidance_scale: float = 7.5,
        width: int = 512,
        height: int = 512
    ) -> Image.Image:
        """Generate an image from a text prompt.
        
        Args:
            prompt: Text description of the desired image
            seed: Random seed for reproducibility (None = random)
            num_inference_steps: Number of denoising steps (more = better quality, slower)
            guidance_scale: How closely to follow the prompt (higher = more literal)
            width: Image width in pixels
            height: Image height in pixels
            
        Returns:
            Generated PIL Image
        """
        if seed is None:
            seed = int(time.time())
        
        logger.info(f"Generating image with prompt: '{prompt[:50]}...'")
        logger.info(f"Parameters: seed={seed}, steps={num_inference_steps}, guidance={guidance_scale}")
        
        if self.use_local:
            return self._generate_local(prompt, seed, num_inference_steps, guidance_scale, width, height)
        else:
            return self._generate_api(prompt, seed)
    
    def _generate_local(
        self,
        prompt: str,
        seed: int,
        num_inference_steps: int,
        guidance_scale: float,
        width: int,
        height: int
    ) -> Image.Image:
        """Generate image using local model."""
        generator = torch.Generator("cpu").manual_seed(seed)
        
        try:
            logger.info("🔄 Generating with local model (this may take several minutes on CPU)...")
            start_time = time.time()
            
            result = self.pipe(
                prompt=prompt,
                generator=generator,
                num_inference_steps=num_inference_steps,
                guidance_scale=guidance_scale,
                width=width,
                height=height
            )
            
            elapsed = time.time() - start_time
            logger.info(f"✓ Generation completed in {elapsed:.1f}s")
            
            return result.images[0]
            
        except Exception as e:
            logger.error(f"Local generation failed: {e}")
            raise

    def _generate_api(self, prompt: str, seed: int) -> Image.Image:
        """Generate image using HuggingFace InferenceClient."""
        if not self.hf_token:
            raise ValueError("HF_TOKEN is required for API mode. Set environment variable or pass --hf-token")

        try:
            logger.info("🔄 Calling HuggingFace Inference API...")

            # Generate image using the new client
            image = self.client.text_to_image(
                prompt,
                model=self.model_name
            )

            logger.info("✓ API generation successful")
            return image

        except Exception as e:
            logger.error(f"API request failed: {e}")
            logger.info("💡 Check your HF_TOKEN value")
            logger.info("💡 Or use --local flag for local CPU generation (slower)")
            raise
    
    def postprocess(self, image: Image.Image) -> Image.Image:
        """Apply post-processing enhancements to the generated image.
        
        Steps:
        1. Crop to target aspect ratio (intelligent center crop)
        2. Apply brightness adjustment
        3. Apply contrast adjustment
        4. Apply saturation boost
        5. Apply sharpening filter
        6. Apply optional brand color filter overlay
        
        Args:
            image: Input PIL Image
            
        Returns:
            Processed PIL Image
        """
        logger.info("🎨 Applying post-processing...")
        
        # Step 1: Intelligent crop to aspect ratio
        image = self._crop_to_aspect_ratio(image, self.aspect_ratio)
        
        # Step 2: Brightness adjustment
        if self.brightness != 1.0:
            enhancer = ImageEnhance.Brightness(image)
            image = enhancer.enhance(self.brightness)
            logger.debug(f"Applied brightness: {self.brightness}")
        
        # Step 3: Contrast adjustment
        if self.contrast != 1.0:
            enhancer = ImageEnhance.Contrast(image)
            image = enhancer.enhance(self.contrast)
            logger.debug(f"Applied contrast: {self.contrast}")
        
        # Step 4: Saturation boost
        if self.saturation != 1.0:
            enhancer = ImageEnhance.Color(image)
            image = enhancer.enhance(self.saturation)
            logger.debug(f"Applied saturation: {self.saturation}")
        
        # Step 5: Sharpening
        if self.sharpness != 1.0:
            enhancer = ImageEnhance.Sharpness(image)
            image = enhancer.enhance(self.sharpness)
            logger.debug(f"Applied sharpness: {self.sharpness}")
        
        # Step 6: Brand filter overlay (optional)
        if self.brand_filter:
            image = self._apply_brand_filter(image, self.brand_filter)
        
        logger.info("✓ Post-processing complete")
        return image
    
    def _crop_to_aspect_ratio(self, image: Image.Image, aspect_ratio: str) -> Image.Image:
        """Intelligently crop image to target aspect ratio using center crop.
        
        Args:
            image: Input PIL Image
            aspect_ratio: Target aspect ratio string (e.g., "16:9")
            
        Returns:
            Cropped PIL Image
        """
        if aspect_ratio not in ASPECT_RATIOS:
            logger.warning(f"Unknown aspect ratio '{aspect_ratio}', using original")
            return image
        
        target_width, target_height = ASPECT_RATIOS[aspect_ratio]
        target_aspect = target_width / target_height
        
        img_width, img_height = image.size
        img_aspect = img_width / img_height
        
        if abs(img_aspect - target_aspect) < 0.01:
            # Already correct aspect ratio, just resize
            return image.resize((target_width, target_height), Image.Resampling.LANCZOS)
        
        # Calculate crop dimensions (center crop)
        if img_aspect > target_aspect:
            # Image is wider, crop width
            new_width = int(img_height * target_aspect)
            new_height = img_height
            left = (img_width - new_width) // 2
            top = 0
        else:
            # Image is taller, crop height
            new_width = img_width
            new_height = int(img_width / target_aspect)
            left = 0
            top = (img_height - new_height) // 2
        
        # Perform center crop
        image = image.crop((left, top, left + new_width, top + new_height))
        
        # Resize to target dimensions
        image = image.resize((target_width, target_height), Image.Resampling.LANCZOS)
        
        logger.debug(f"Cropped to {aspect_ratio} ({target_width}x{target_height})")
        return image
    
    def _apply_brand_filter(self, image: Image.Image, filter_name: str) -> Image.Image:
        """Apply a brand color filter overlay to the image.
        
        Args:
            image: Input PIL Image
            filter_name: Name of the brand filter preset
            
        Returns:
            Image with color filter applied
        """
        if filter_name not in BRAND_FILTERS:
            logger.warning(f"Unknown brand filter '{filter_name}', skipping")
            return image
        
        r, g, b, alpha = BRAND_FILTERS[filter_name]
        
        # Create color overlay
        overlay = Image.new('RGB', image.size, (r, g, b))
        
        # Blend with original image
        image = Image.blend(image.convert('RGB'), overlay, alpha / 100.0)
        
        logger.debug(f"Applied brand filter: {filter_name}")
        return image
    
    def save(
        self,
        image: Image.Image,
        output_path: Union[str, Path],
        metadata: Optional[Dict] = None
    ) -> Tuple[Path, Path]:
        """Save image and metadata to disk.
        
        Args:
            image: PIL Image to save
            output_path: Output file path (with or without extension)
            metadata: Optional metadata dictionary to save as JSON
            
        Returns:
            Tuple of (image_path, metadata_path)
        """
        output_path = Path(output_path)
        
        # Ensure output directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Determine image path
        if output_path.suffix.lower() in ['.jpg', '.jpeg', '.png']:
            image_path = output_path
        else:
            # Default to .jpg
            image_path = output_path.with_suffix('.jpg')
        
        # Save image
        image.save(image_path, quality=95, optimize=True)
        logger.info(f"💾 Saved image: {image_path}")
        
        # Save metadata if provided
        metadata_path = None
        if metadata:
            metadata_path = image_path.with_suffix('.json')
            with open(metadata_path, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)
            logger.info(f"💾 Saved metadata: {metadata_path}")
        
        return image_path, metadata_path
    
    def run(
        self,
        prompt: str,
        output_path: Union[str, Path],
        seed: Optional[int] = None,
        **generate_kwargs
    ) -> Tuple[Path, Dict]:
        """Run the complete pipeline: generate → postprocess → save.
        
        Args:
            prompt: Text prompt for image generation
            output_path: Where to save the output
            seed: Random seed (None = random)
            **generate_kwargs: Additional arguments for generate()
            
        Returns:
            Tuple of (image_path, metadata_dict)
        """
        start_time = time.time()
        
        # Generate image
        image = self.generate(prompt, seed=seed, **generate_kwargs)
        
        # Post-process
        image = self.postprocess(image)
        
        # Prepare metadata
        metadata = {
            "prompt": prompt,
            "seed": seed,
            "timestamp": datetime.utcnow().isoformat(),
            "generation_time_seconds": time.time() - start_time,
            "model_mode": "local" if self.use_local else "api",
            "model_name": self.model_name if self.use_local else "api",
            "processing": {
                "aspect_ratio": self.aspect_ratio,
                "target_size": ASPECT_RATIOS.get(self.aspect_ratio),
                "brightness": self.brightness,
                "contrast": self.contrast,
                "saturation": self.saturation,
                "sharpness": self.sharpness,
                "brand_filter": self.brand_filter,
            },
            "final_size": image.size,
        }
        
        # Save everything
        image_path, metadata_path = self.save(image, output_path, metadata)
        
        total_time = time.time() - start_time
        logger.info(f"✅ Complete pipeline finished in {total_time:.1f}s")
        
        return image_path, metadata_path


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Creative Advertising Campaign Image Generator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Quick API generation (no GPU needed):
  python creative_ad_generator.py --prompt "summer sale campaign" --out ./ads/summer.jpg
  
  # Local CPU with custom settings:
  python creative_ad_generator.py --prompt "luxury brand" --out ./ads/ --local --aspect 16:9 --filter warm_gold
  
  # Batch generate all examples:
  python creative_ad_generator.py --batch --out ./ads/
  
  # With custom seed for reproducibility:
  python creative_ad_generator.py --prompt "tech launch" --seed 42 --out ./output/
        """
    )
    
    parser.add_argument(
        "--prompt", "-p",
        type=str,
        help="Text prompt describing the desired advertising image"
    )
    
    parser.add_argument(
        "--out", "-o",
        type=str,
        required=True,
        help="Output path (file or directory)"
    )
    
    parser.add_argument(
        "--seed", "-s",
        type=int,
        default=None,
        help="Random seed for reproducibility (default: random)"
    )
    
    parser.add_argument(
        "--local",
        action="store_true",
        help="Use local model instead of API (slower, requires more compute)"
    )
    
    parser.add_argument(
        "--aspect", "-a",
        type=str,
        default="16:9",
        choices=list(ASPECT_RATIOS.keys()),
        help="Target aspect ratio (default: 16:9)"
    )
    
    parser.add_argument(
        "--filter", "-f",
        type=str,
        default=None,
        choices=list(BRAND_FILTERS.keys()),
        help="Brand color filter to apply"
    )
    
    parser.add_argument(
        "--brightness",
        type=float,
        default=1.1,
        help="Brightness adjustment (1.0 = no change, default: 1.1)"
    )
    
    parser.add_argument(
        "--contrast",
        type=float,
        default=1.15,
        help="Contrast adjustment (1.0 = no change, default: 1.15)"
    )
    
    parser.add_argument(
        "--saturation",
        type=float,
        default=1.2,
        help="Saturation adjustment (1.0 = no change, default: 1.2)"
    )
    
    parser.add_argument(
        "--batch",
        action="store_true",
        help="Generate all example prompts (ignores --prompt)"
    )
    
    parser.add_argument(
        "--hf-token",
        type=str,
        default=os.getenv("HF_TOKEN"),
        help="HuggingFace API token (or set HF_TOKEN env var)"
    )
    
    args = parser.parse_args()
    
    # Validate arguments
    if not args.batch and not args.prompt:
        parser.error("Either --prompt or --batch must be specified")
    
    # Initialize pipeline
    pipeline = CreativeImagePipeline(
        use_local=args.local,
        hf_token=args.hf_token,
        brightness=args.brightness,
        contrast=args.contrast,
        saturation=args.saturation,
        aspect_ratio=args.aspect,
        brand_filter=args.filter
    )
    
    # Generate images
    if args.batch:
        logger.info(f"🚀 Batch mode: generating {len(EXAMPLE_PROMPTS)} example images")
        output_dir = Path(args.out)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        for i, prompt in enumerate(EXAMPLE_PROMPTS, 1):
            logger.info(f"\n{'='*80}")
            logger.info(f"Generating image {i}/{len(EXAMPLE_PROMPTS)}")
            logger.info(f"{'='*80}\n")
            
            output_path = output_dir / f"ad_example_{i:02d}.jpg"
            
            try:
                image_path, metadata = pipeline.run(prompt, output_path, seed=args.seed)
                logger.info(f"✓ Success: {image_path}\n")
            except Exception as e:
                logger.error(f"✗ Failed: {e}\n")
                continue
        
        logger.info(f"\n✅ Batch generation complete! Check {output_dir}/")
        
    else:
        # Single generation
        try:
            image_path, metadata = pipeline.run(args.prompt, args.out, seed=args.seed)
            logger.info(f"\n✅ Image generated successfully!")
            logger.info(f"📁 Output: {image_path}")
            logger.info(f"📝 Metadata: {image_path.with_suffix('.json')}")
            
        except Exception as e:
            logger.error(f"\n❌ Generation failed: {e}")
            return 1
    
    return 0


if __name__ == "__main__":
    exit(main())