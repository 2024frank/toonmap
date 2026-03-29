import base64
import requests
from openai import OpenAI
from typing import Optional, Callable
import logging
from io import BytesIO
from PIL import Image, ImageChops

logger = logging.getLogger(__name__)


class OpenAIService:
    """Service for AI cartoon transformation using OpenAI Image API"""
    
    def __init__(self, api_key: Optional[str] = None):
        if not api_key or api_key == "None" or api_key.strip() == "":
            raise ValueError("OpenAI API key is required - check your .env file")
        self.client = OpenAI(api_key=api_key)
    
    def cartoonify_image(
        self,
        image_url: str,
        streets_url: Optional[str] = None,
        style: str = "3d_cartoon",
        pitch: int = 60,
        bearing: int = 0,
        progress_callback: Optional[Callable[[str, int], None]] = None,
    ) -> Optional[str]:
        """
        Transform satellite image into cartoon style using OpenAI's gpt-image-1.

        Args:
            image_url: URL of the satellite image from Mapbox
            streets_url: Optional URL of streets layer for reference
            style: Cartoon style preset
            pitch: Camera tilt of the source satellite image (0-60°)
            bearing: Camera bearing of the source satellite image (0-360°)
            progress_callback: Optional callback(message, percent) for progress updates

        Returns:
            Base64 encoded cartoon image
        """

        # Style-specific prompts optimized for 3D aerial views
        style_prompts = {
            "3d_cartoon": (
                "Transform this composite map reference (satellite imagery + street overlay) into a highly "
                "detailed 3D cartoon style map. The input shows both textures from satellite view and "
                "structural outlines from street maps. Use both layers to understand building positions, "
                "road layouts, and spatial relationships accurately. "
                "Preserve the EXACT layout, road positions, building shapes, and spatial relationships. "
                "Render everything in a stylized isometric 3D illustration style. Buildings should look "
                "like miniature architectural models with soft lighting, rounded edges, and subtle shadows. "
                "Roads should remain in the same position with smooth dark surfaces and clean edges. "
                "Trees should appear lush, vibrant, and slightly exaggerated in a playful cartoon style. "
                "Grass areas should look bright green with gentle texture. Parking lots should contain "
                "simplified small cars. Use warm sunlight, soft ambient occlusion, and vivid colors. "
                "Keep proportions consistent with the original map so every structure stays in the correct place. "
                "Do not invent new locations or move buildings. "
                "IMPORTANT: Preserve the exact camera perspective — viewing angle is {pitch} degrees pitch "
                "and {bearing} degrees bearing. Do not flatten to top-down, do not rotate the scene. "
                "The horizon line, vanishing point, and depth of all elements must match the original exactly. "
                "Style inspired by Pixar, SimCity, Cities Skylines cartoon mode, and architectural scale models. "
                "Avoid: distorted layout, incorrect map geometry, misplaced roads, missing buildings, "
                "text artifacts, unrealistic proportions, blurry, photorealistic satellite imagery, "
                "changed camera angle, warped streets, removed labels or roads."
            ),

            "pixar": """Stylize this aerial satellite map into a Pixar-inspired illustrated city map.
Keep every street, building, park, and landmark exactly in place — preserve all real layout details.
Apply warm soft lighting from the top-left, gentle rounded edges on building rooftops,
vibrant but realistic colors. The map should remain fully readable with all details intact.""",

            "anime": """Stylize this aerial satellite map into a Studio Ghibli illustrated city map.
Preserve all streets, buildings, parks, and layout exactly as shown.
Apply soft watercolor textures over the buildings and green areas,
keep streets clearly visible with light warm tones.
All roads, blocks and structures must remain accurate and detailed.""",

            "low_poly": """Stylize this aerial satellite map into a clean low-poly illustrated map.
Preserve all street layouts, building positions, and park areas exactly.
Apply flat geometric color fills: grey streets, pastel buildings, bright green parks.
Keep the map fully readable and detailed — do not simplify or remove any structure.""",
        }
        
        prompt = style_prompts.get(style, style_prompts["3d_cartoon"]).format(
            pitch=pitch, bearing=bearing
        )
        
        logger.info(f"Starting OpenAI gpt-image-1 transformation with style: {style}")
        
        if progress_callback:
            progress_callback("Downloading satellite image...", 10)
        
        try:
            # Step 1: Download the satellite image from Mapbox
            logger.info(f"Downloading satellite image from: {image_url[:80]}...")
            image_response = requests.get(image_url, timeout=30)
            image_response.raise_for_status()
            image_bytes = image_response.content
            
            logger.info(f"Downloaded {len(image_bytes) / 1024:.0f} KB satellite image")
            
            if progress_callback:
                progress_callback("Processing satellite layer...", 25)
            
            # Step 2: Load satellite image
            satellite_img = Image.open(BytesIO(image_bytes)).convert("RGB")
            if satellite_img.size != (1024, 1024):
                logger.info(f"Resizing satellite from {satellite_img.size} to 1024x1024")
                satellite_img = satellite_img.resize((1024, 1024), Image.Resampling.LANCZOS)
            
            # Step 3: If streets URL provided, composite layers for better AI reference
            if streets_url:
                if progress_callback:
                    progress_callback("Downloading streets layer...", 35)
                
                logger.info(f"Downloading streets layer from: {streets_url[:80]}...")
                streets_response = requests.get(streets_url, timeout=30)
                streets_response.raise_for_status()
                streets_bytes = streets_response.content
                
                logger.info(f"Downloaded {len(streets_bytes) / 1024:.0f} KB streets layer")
                
                if progress_callback:
                    progress_callback("Compositing layers...", 45)
                
                streets_img = Image.open(BytesIO(streets_bytes)).convert("RGB")
                if streets_img.size != (1024, 1024):
                    streets_img = streets_img.resize((1024, 1024), Image.Resampling.LANCZOS)
                
                # Blend: 70% satellite for textures, 30% streets for structure/labels
                img = Image.blend(satellite_img, streets_img, alpha=0.3)
                logger.info("Composited satellite + streets layers for enhanced AI reference")
            else:
                img = satellite_img
            
            if progress_callback:
                progress_callback("Preparing image for AI...", 55)

            png_buffer = BytesIO()
            img.save(png_buffer, format='PNG')
            png_buffer.seek(0)

            logger.info(f"Prepared RGB PNG ({len(png_buffer.getvalue()) / 1024:.0f} KB)")

            if progress_callback:
                progress_callback("Sending to OpenAI AI for transformation...", 65)

            # Step 4: Transform using gpt-image-1 via raw HTTP
            logger.info("Sending to OpenAI gpt-image-1 for transformation...")

            api_response = requests.post(
                "https://api.openai.com/v1/images/edits",
                headers={"Authorization": f"Bearer {self.client.api_key}"},
                files={"image": ("satellite.png", png_buffer, "image/png")},
                data={"model": "gpt-image-1", "prompt": prompt, "size": "1024x1024"},
                timeout=120,
            )
            api_response.raise_for_status()

            if progress_callback:
                progress_callback("AI transformation complete!", 90)

            image_base64 = api_response.json()["data"][0]["b64_json"]
            
            logger.info("Cartoon transformation complete!")
            logger.info(f"Result size: {len(image_base64) / 1024:.0f} KB (base64)")
            
            if progress_callback:
                progress_callback("Finalizing...", 95)
            
            return image_base64
            
        except Exception as e:
            logger.error(f"OpenAI API error: {str(e)}")
            raise
