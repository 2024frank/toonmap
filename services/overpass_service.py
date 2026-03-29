import requests
from typing import List, Dict
import logging

logger = logging.getLogger(__name__)


class OverpassService:
    """Service for querying OpenStreetMap data via Overpass API"""
    
    OVERPASS_API = "https://overpass-api.de/api/interpreter"
    
    async def get_landmarks(
        self,
        bbox: Dict[str, float],
        limit: int = 5
    ) -> List[Dict]:
        """
        Query Overpass API for tourist landmarks and POIs
        
        Args:
            bbox: Bounding box dict with min_lat, min_lng, max_lat, max_lng
            limit: Maximum number of landmarks to return
        
        Returns:
            List of landmark dicts with name, type, lat, lon
        """
        # Overpass API uses bbox format: south,west,north,east
        bbox_str = f"{bbox['min_lat']},{bbox['min_lng']},{bbox['max_lat']},{bbox['max_lng']}"
        
        # Overpass QL query for tourist attractions and notable POIs
        query = f"""
        [out:json][timeout:25];
        (
          node["tourism"="attraction"]({bbox_str});
          node["tourism"="museum"]({bbox_str});
          node["tourism"="viewpoint"]({bbox_str});
          node["historic"]({bbox_str});
          node["amenity"="place_of_worship"]({bbox_str});
          node["leisure"="park"]({bbox_str});
          way["tourism"="attraction"]({bbox_str});
          way["tourism"="museum"]({bbox_str});
          way["leisure"="park"]({bbox_str});
        );
        out center {limit + 10};
        """
        
        try:
            response = requests.post(
                self.OVERPASS_API,
                data={"data": query},
                timeout=30
            )
            response.raise_for_status()
            
            data = response.json()
            elements = data.get("elements", [])
            
            landmarks = []
            for element in elements[:limit]:
                # Get coordinates (nodes have lat/lon, ways have center)
                if element["type"] == "node":
                    lat = element["lat"]
                    lon = element["lon"]
                else:
                    # For ways, use center point
                    lat = element.get("center", {}).get("lat")
                    lon = element.get("center", {}).get("lon")
                
                if lat is None or lon is None:
                    continue
                
                # Extract name and type
                tags = element.get("tags", {})
                name = tags.get("name", "Unknown")
                
                # Determine landmark type
                landmark_type = self._determine_type(tags)
                
                landmarks.append({
                    "name": name,
                    "type": landmark_type,
                    "lat": lat,
                    "lon": lon
                })
            
            logger.info(f"Found {len(landmarks)} landmarks from Overpass")
            return landmarks
            
        except Exception as e:
            logger.error(f"Overpass API error: {str(e)}")
            return []
    
    def _determine_type(self, tags: Dict) -> str:
        """Determine landmark type from OSM tags"""
        if "tourism" in tags:
            return tags["tourism"]
        elif "historic" in tags:
            return "historic"
        elif "leisure" in tags:
            return tags["leisure"]
        elif "amenity" in tags:
            return tags["amenity"]
        else:
            return "poi"
