import requests
import math
from typing import Dict, Optional
from urllib.parse import urlencode


class MapboxService:
    """Service for interacting with Mapbox APIs"""
    
    GEOCODING_API = "https://api.mapbox.com/geocoding/v5/mapbox.places"
    STATIC_API = "https://api.mapbox.com/styles/v1/mapbox/satellite-v9/static"
    STREETS_API = "https://api.mapbox.com/styles/v1/mapbox/streets-v12/static"
    
    def __init__(self, access_token: str):
        if not access_token:
            raise ValueError("Mapbox access token is required")
        self.access_token = access_token
    
    async def geocode(self, address: str) -> Optional[Dict[str, float]]:
        """
        Convert address to coordinates using Mapbox Geocoding API
        
        Returns:
            {"lat": float, "lng": float} or None if not found
        """
        url = f"{self.GEOCODING_API}/{address}.json"
        params = {
            "access_token": self.access_token,
            "limit": 1
        }
        
        response = requests.get(url, params=params)
        response.raise_for_status()
        
        data = response.json()
        
        if not data.get("features"):
            return None
        
        # Mapbox returns [lng, lat] format
        coordinates = data["features"][0]["geometry"]["coordinates"]
        
        return {
            "lng": coordinates[0],
            "lat": coordinates[1],
            "place_name": data["features"][0]["place_name"]
        }
    
    def calculate_bbox(
        self,
        lat: float,
        lng: float,
        radius_meters: int,
        padding_percent: float = 15
    ) -> Dict[str, float]:
        """
        Calculate bounding box around a center point
        
        Args:
            lat: Center latitude
            lng: Center longitude
            radius_meters: Radius in meters
            padding_percent: Extra padding percentage (e.g., 15 for 15%)
        
        Returns:
            {"min_lng", "min_lat", "max_lng", "max_lat"}
        """
        # Apply padding to radius
        effective_radius = radius_meters * (1 + padding_percent / 100)
        
        # Earth's radius in meters
        earth_radius = 6371000
        
        # Calculate degree offsets
        lat_offset = (effective_radius / earth_radius) * (180 / math.pi)
        lng_offset = (effective_radius / earth_radius) * (180 / math.pi) / math.cos(lat * math.pi / 180)
        
        return {
            "min_lng": lng - lng_offset,
            "min_lat": lat - lat_offset,
            "max_lng": lng + lng_offset,
            "max_lat": lat + lat_offset
        }
    
    def get_static_image_url(
        self,
        center_lng: float,
        center_lat: float,
        zoom: int = 16,
        pitch: int = 45,
        bearing: int = 0,
        width: int = 1280,
        height: int = 1280,
        style: str = "satellite"
    ) -> str:
        """
        Generate Mapbox Static Images API URL with 3D tilt
        
        Args:
            center_lng: Center longitude
            center_lat: Center latitude
            zoom: Zoom level (13-18 recommended for satellite detail)
            pitch: Camera tilt (0-60, where 60 is maximum tilt)
            bearing: Camera rotation (0-360 degrees)
            width: Image width in pixels
            height: Image height in pixels
            style: Map style - "satellite" or "streets"
        
        Returns:
            Full Mapbox Static API URL with 3D perspective
        """
        # Format: /[lng,lat,zoom,bearing,pitch]/[width]x[height]
        position = f"{center_lng},{center_lat},{zoom},{bearing},{pitch}"
        dimensions = f"{width}x{height}"
        
        # Select API endpoint based on style
        base_api = self.STREETS_API if style == "streets" else self.STATIC_API
        
        # Use @2x for retina quality
        url = f"{base_api}/{position}/{dimensions}@2x"
        
        params = {
            "access_token": self.access_token
        }
        
        return f"{url}?{urlencode(params)}"
    
    def adjust_zoom_for_radius(self, radius_meters: int) -> int:
        """
        Suggest optimal zoom level based on radius for high-detail cartoon capture
        
        Higher zoom = more detail for AI cartoon transformation
        - 200-400m: zoom 18 (maximum detail)
        - 400-800m: zoom 17 (high detail)
        - 800-1600m: zoom 16 (good detail)
        - 1600m+: zoom 15
        """
        if radius_meters <= 200:
            return 20
        elif radius_meters <= 400:
            return 19
        elif radius_meters <= 800:
            return 18
        elif radius_meters <= 1600:
            return 17
        else:
            return 16
