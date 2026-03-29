import requests
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import logging
from typing import Dict, Optional

logger = logging.getLogger(__name__)


class IconService:
    """Service for getting landmark icons"""
    
    # Icon mapping for different landmark types
    ICON_URLS = {
        "attraction": "🎡",  # Tourist attraction
        "museum": "🏛️",
        "viewpoint": "👁️",
        "historic": "🏛️",
        "place_of_worship": "⛪",
        "park": "🌳",
        "ruins": "🏛️",
        "default": "📍"
    }
    
    ICON_COLORS = {
        "attraction": "#FF6B6B",  # Red
        "museum": "#4ECDC4",      # Teal
        "viewpoint": "#95E1D3",   # Light teal
        "historic": "#F38181",    # Pink
        "place_of_worship": "#AA96DA",  # Purple
        "park": "#5FD068",        # Green
        "ruins": "#C7CEEA",       # Light blue
        "default": "#FFC75F"      # Orange
    }
    
    def create_icon_pin(
        self, 
        landmark_type: str, 
        size: int = 80
    ) -> Image.Image:
        """
        Create a map pin icon for a landmark type
        
        Args:
            landmark_type: Type of landmark (park, museum, etc.)
            size: Icon size in pixels
        
        Returns:
            PIL Image of the icon with transparency
        """
        # Create a circular pin with emoji
        icon = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(icon)
        
        # Get color for this landmark type
        color = self.ICON_COLORS.get(landmark_type, self.ICON_COLORS["default"])
        
        # Draw pin background (circle)
        padding = 10
        draw.ellipse(
            [padding, padding, size-padding, size-padding],
            fill=color,
            outline="white",
            width=3
        )
        
        # Add shadow
        shadow_offset = 5
        draw.ellipse(
            [padding+shadow_offset, padding+shadow_offset, 
             size-padding+shadow_offset, size-padding+shadow_offset],
            fill=(0, 0, 0, 60)
        )
        
        # Add emoji
        emoji = self.ICON_URLS.get(landmark_type, self.ICON_URLS["default"])
        
        try:
            # Use a font that supports emojis (system default)
            font_size = int(size * 0.4)
            font = ImageFont.truetype("/System/Library/Fonts/Apple Color Emoji.ttc", font_size)
            
            # Center the emoji
            bbox = draw.textbbox((0, 0), emoji, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            position = ((size - text_width) // 2, (size - text_height) // 2 - padding//2)
            
            draw.text(position, emoji, font=font, embedded_color=True)
        except:
            # Fallback: just draw a colored circle
            logger.warning(f"Could not load emoji font, using simple marker")
        
        return icon
    
    def create_simple_marker(
        self,
        landmark_type: str,
        size: int = 60
    ) -> Image.Image:
        """
        Create a simple colored marker pin
        
        Returns:
            PIL Image of a pin marker
        """
        icon = Image.new('RGBA', (size, int(size * 1.5)), (0, 0, 0, 0))
        draw = ImageDraw.Draw(icon)
        
        color = self.ICON_COLORS.get(landmark_type, self.ICON_COLORS["default"])
        
        # Draw teardrop pin shape
        center_x = size // 2
        circle_y = size // 2
        
        # Circle part
        draw.ellipse(
            [5, 5, size-5, size-5],
            fill=color,
            outline="white",
            width=3
        )
        
        # Pointed bottom
        draw.polygon(
            [(center_x, int(size * 1.4)), 
             (center_x - size//4, size-5), 
             (center_x + size//4, size-5)],
            fill=color,
            outline="white"
        )
        
        return icon
