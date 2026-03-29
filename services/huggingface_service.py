import os
import requests
from huggingface_hub import InferenceClient
from typing import Optional
import logging
from io import BytesIO
from PIL import Image

logger = logging.getLogger(__name__)


class HuggingFaceService:
    """Service for AI cartoon transformation using Hugging Face"""
    
    def __init__(self, api_token: str):
        if not api_token:
            raise ValueError("Hugging Face token is required")
        # Use default HuggingFace inference (no provider needed for img2img)
        self.client = InferenceClient(token=api_token)
    
    def cartoonify_image(
        self,
        image_url: str,
        style: str = "3d_cartoon"
    ) -> bytes:
        """
        Transform satellite image into cartoon using Stable Diffusion XL img2img
        
        Args:
            image_url: URL of the satellite image from Mapbox
            style: Cartoon style preset
        
        Returns:
            PNG image bytes
        """
        
        # Style-specific prompts optimized for 3D aerial views
        style_prompts = {
            "3d_cartoon": """isometric 3D cartoon city map, vibrant colors, cute geometric buildings, 
dramatic perspective, low-poly game style, SimCity aesthetic, clean bold outlines, 
playful illustration, high angle view, exaggerated tall buildings, colorful rooftops, 
toy city, miniature world, bright and cheerful""",
            
            "pixar": """Pixar animated movie style cityscape, soft lighting, rounded buildings, 
vibrant happy colors, cute architectural details, smooth gradients, cinematic quality, 
whimsical and inviting atmosphere, toy story aesthetic""",
            
            "anime": """anime style city map illustration, Studio Ghibli aesthetic, 
watercolor painting style, soft dreamy colors, hand-drawn buildings, 
gentle shadows, artistic atmospheric, beautiful details""",
            
            "low_poly": """low-poly 3D city geometric shapes, flat triangular buildings, 
solid colors, mobile game art, minimalist clean, isometric game aesthetic, 
simple polygons""",
        }
        
        negative_prompt = """blurry, ugly, distorted, low quality, messy, realistic photo, 
grainy, text, watermark, labels, too dark, muddy colors, noisy"""
        
        prompt = style_prompts.get(style, style_prompts["3d_cartoon"])
        
        logger.info(f"Starting HuggingFace cartoon transformation with style: {style}")
        logger.info(f"Using: stabilityai/stable-diffusion-xl-base-1.0")
        
        try:
            # Download the satellite image first (Mapbox URLs require auth - HF server can't fetch them)
            logger.info(f"Downloading satellite image from: {image_url[:80]}...")
            img_response = requests.get(image_url, timeout=30)
            img_response.raise_for_status()
            image_data = Image.open(BytesIO(img_response.content)).convert("RGB")
            logger.info(f"Downloaded {len(img_response.content) / 1024:.0f} KB")

            # instruct-pix2pix uses instruction-style prompts
            instruction_prompt = f"transform this satellite map into: {prompt}"

            logger.info(f"Sending to HuggingFace instruct-pix2pix...")

            output_image = self.client.image_to_image(
                image=image_data,
                prompt=instruction_prompt,
                model="timbrooks/instruct-pix2pix",
                guidance_scale=7.5,
                num_inference_steps=30
            )
            
            logger.info("Transformation complete!")
            
            # Convert PIL Image to PNG bytes
            output_buffer = BytesIO()
            output_image.save(output_buffer, format='PNG')
            output_bytes = output_buffer.getvalue()
            
            logger.info(f"Output size: {len(output_bytes) / 1024:.0f} KB")
            
            return output_bytes
            
        except Exception as e:
            logger.error(f"HuggingFace API error: {str(e)}")
            raise
