from PIL import Image, ImageDraw, ImageFont
from typing import List, Dict, Tuple
import logging
from io import BytesIO
import math

logger = logging.getLogger(__name__)


class OverlayService:
    """Service for overlaying icons and labels on cartoon maps"""
    
    def overlay_landmarks(
        self,
        cartoon_image: Image.Image,
        landmarks: List[Dict],
        bbox: Dict[str, float],
        icon_service
    ) -> Image.Image:
        """
        Overlay landmark icons and labels on the cartoon map
        
        Args:
            cartoon_image: The cartoonified map
            landmarks: List of landmarks with lat/lon
            bbox: Bounding box of the map
            icon_service: IconService instance for generating icons
        
        Returns:
            Image with icons and labels overlaid
        """
        # Work on a copy
        result = cartoon_image.copy()
        width, height = result.size
        
        logger.info(f"Overlaying {len(landmarks)} landmarks on {width}x{height} image")
        
        for landmark in landmarks:
            try:
                # Convert lat/lng to pixel coordinates
                x, y = self._latlon_to_pixels(
                    lat=landmark["lat"],
                    lon=landmark["lon"],
                    bbox=bbox,
                    image_width=width,
                    image_height=height
                )
                
                # Check if coordinates are within image bounds
                if 0 <= x < width and 0 <= y < height:
                    # Create icon for this landmark type
                    icon = icon_service.create_simple_marker(
                        landmark_type=landmark["type"],
                        size=50
                    )
                    
                    # Paste icon centered at the landmark position
                    icon_x = int(x - icon.width // 2)
                    icon_y = int(y - icon.height)  # Pin points to location
                    
                    result.paste(icon, (icon_x, icon_y), icon)
                    
                    # Add label below the icon
                    self._add_label(
                        result,
                        landmark["name"],
                        x,
                        y + 10
                    )
                    
                    logger.info(f"Added icon for '{landmark['name']}' at ({x}, {y})")
                else:
                    logger.warning(f"Landmark '{landmark['name']}' outside image bounds")
                    
            except Exception as e:
                logger.error(f"Error adding landmark '{landmark['name']}': {e}")
        
        return result
    
    def _latlon_to_pixels(
        self,
        lat: float,
        lon: float,
        bbox: Dict[str, float],
        image_width: int,
        image_height: int
    ) -> Tuple[int, int]:
        """
        Convert latitude/longitude to pixel coordinates
        
        Args:
            lat: Latitude of the point
            lon: Longitude of the point
            bbox: Bounding box with min/max lat/lon
            image_width: Width of the image
            image_height: Height of the image
        
        Returns:
            (x, y) pixel coordinates
        """
        # Normalize coordinates to 0-1 range
        lon_range = bbox["max_lng"] - bbox["min_lng"]
        lat_range = bbox["max_lat"] - bbox["min_lat"]
        
        # Calculate position as percentage
        x_percent = (lon - bbox["min_lng"]) / lon_range
        y_percent = 1 - ((lat - bbox["min_lat"]) / lat_range)  # Flip Y axis
        
        # Convert to pixels
        x = int(x_percent * image_width)
        y = int(y_percent * image_height)
        
        return x, y
    
    def _add_label(
        self,
        image: Image.Image,
        text: str,
        x: int,
        y: int
    ):
        """Add a text label at the specified position"""
        draw = ImageDraw.Draw(image)
        
        try:
            # Try to load a nice font
            font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 18)
        except:
            # Fallback to default
            font = ImageFont.load_default()
        
        # Truncate long names
        if len(text) > 20:
            text = text[:17] + "..."
        
        # Get text size for background
        bbox = draw.textbbox((x, y), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        # Center text horizontally
        text_x = x - text_width // 2
        text_y = y
        
        # Draw background rectangle
        padding = 4
        draw.rectangle(
            [text_x - padding, text_y - padding, 
             text_x + text_width + padding, text_y + text_height + padding],
            fill=(255, 255, 255, 220),
            outline=(0, 0, 0, 255),
            width=2
        )
        
        # Draw text
        draw.text((text_x, text_y), text, fill=(0, 0, 0, 255), font=font)
