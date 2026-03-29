import replicate
import requests
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class ReplicateService:
    """Service for AI cartoon transformation using Replicate"""
    
    def __init__(self, api_token: str):
        if not api_token:
            raise ValueError("Replicate API token is required")
        self.client = replicate.Client(api_token=api_token)
    
    def cartoonify_image(
        self,
        image_url: str,
        style: str = "3d_cartoon",
        prompt_strength: float = 0.8
    ) -> Optional[str]:
        """
        Transform satellite image into cartoon style using Stable Diffusion
        
        Args:
            image_url: URL of the satellite image
            style: Cartoon style preset
            prompt_strength: How much to transform (0.0-1.0)
        
        Returns:
            URL of the cartoonified image
        """
        
        # Style presets with optimized prompts
        style_prompts = {
            "3d_cartoon": "isometric 3D cartoon city map, vibrant colors, cute buildings, dramatic perspective, low-poly style, SimCity aesthetic, clean lines, playful illustration, high angle view",
            "pixar": "Pixar style 3D city illustration, colorful buildings, soft lighting, cute and whimsical, animated movie quality, vibrant and cheerful",
            "anime": "anime style city map, studio ghibli aesthetic, watercolor painting, soft colors, detailed buildings, hand-drawn quality",
            "low_poly": "low-poly 3D city, geometric buildings, flat colors, simple shapes, isometric game art, mobile game style",
        }
        
        prompt = style_prompts.get(style, style_prompts["3d_cartoon"])
        
        logger.info(f"Starting cartoon transformation with style: {style}")
        logger.info(f"Prompt: {prompt}")
        
        try:
            # Using ControlNet Canny - preserves map structure while transforming style
            output = self.client.run(
                "jagilley/controlnet-canny:aff48af9c68d162388d230a2ab003f68d2638d88307bdaf1c2f1ac95079c9613",
                input={
                    "image": image_url,
                    "prompt": prompt,
                    "negative_prompt": "blurry, ugly, distorted, low quality, messy, realistic photo, grainy, text, watermark, labels",
                    "structure": "scribble",  # Preserves edges
                    "num_samples": 1,
                    "image_resolution": 1280,
                    "ddim_steps": 20,
                    "scale": 7.5,
                }
            )
            
            # Output is a list of URLs
            if output and len(output) > 0:
                result_url = output[0]
                logger.info(f"Cartoon transformation complete: {result_url}")
                return result_url
            else:
                logger.error("No output from Replicate")
                return None
                
        except Exception as e:
            logger.error(f"Replicate API error: {str(e)}")
            raise
