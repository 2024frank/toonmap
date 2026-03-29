from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from typing import Optional, List
import os
from dotenv import load_dotenv
import logging

from services.mapbox_service import MapboxService
from services.overpass_service import OverpassService
from services.openai_service import OpenAIService
from services.icon_service import IconService
from services.overlay_service import OverlayService

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="ToonMap API",
    description="Transform satellite maps into stylized cartoon representations",
    version="0.1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

mapbox_service = MapboxService(
    access_token=os.getenv("MAP_BOX_TOKEN")
)
overpass_service = OverpassService()
openai_service = OpenAIService(
    api_key=os.getenv("OPENAI_API_KEY")
)
icon_service = IconService()
overlay_service = OverlayService()


class MapRequest(BaseModel):
    address: str = Field(..., description="Address or location name to fetch")
    radius_meters: Optional[int] = Field(
        default=500,
        ge=100,
        le=5000,
        description="Radius in meters around the center point"
    )
    pitch: Optional[int] = Field(
        default=60,
        ge=0,
        le=60,
        description="Camera tilt angle (0=flat, 60=max tilt) - 60° for maximum 3D effect"
    )
    bearing: Optional[int] = Field(
        default=0,
        ge=0,
        le=360,
        description="Camera rotation in degrees (0=north)"
    )


class Landmark(BaseModel):
    name: str
    type: str
    lat: float
    lon: float


class MapResponse(BaseModel):
    address: str
    center: dict
    bbox: dict
    image_url: str
    landmarks: List[Landmark]
    parameters: dict


class CartoonRequest(BaseModel):
    address: str = Field(..., description="Address or location name")
    radius_meters: Optional[int] = Field(default=500, ge=100, le=5000)
    pitch: Optional[int] = Field(default=60, ge=0, le=60)
    bearing: Optional[int] = Field(default=45, ge=0, le=360)
    style: Optional[str] = Field(
        default="3d_cartoon",
        description="Cartoon style: 3d_cartoon, pixar, anime, low_poly"
    )


class CartoonResponse(BaseModel):
    address: str
    satellite_image_url: str
    cartoon_image_base64: str  # Base64 encoded PNG
    landmarks: List[Landmark]
    parameters: dict


class ToonMapResponse(BaseModel):
    address: str
    satellite_image_url: str
    cartoon_image_base64: str
    toonmap_image_base64: str  # Cartoon with landmark icons
    landmarks: List[Landmark]
    parameters: dict


@app.get("/")
async def root():
    return {
        "message": "Welcome to ToonMap API",
        "docs": "/docs",
        "endpoints": {
            "fetch_map": "/fetch-map - Get satellite + landmarks",
            "cartoonify": "/cartoonify - Transform to cartoon",
            "toonmap": "/toonmap - Complete map with icons (Milestone 03)"
        },
        "milestone": "03 - Landmarks with Icons"
    }


@app.post("/fetch-map", response_model=MapResponse)
async def fetch_map(request: MapRequest):
    """
    Milestone 01: Fetch satellite map and landmark data
    
    Takes an address and returns:
    - Tilted 3D satellite image URL from Mapbox
    - Top 5 landmarks from Overpass API
    """
    try:
        logger.info(f"Fetching map for address: {request.address}")
        
        # Step 1: Geocode address to coordinates
        center = await mapbox_service.geocode(request.address)
        if not center:
            raise HTTPException(
                status_code=404,
                detail=f"Could not geocode address: {request.address}"
            )
        
        logger.info(f"Geocoded to: {center}")
        
        # Step 2: Calculate bounding box with padding
        bbox = mapbox_service.calculate_bbox(
            lat=center["lat"],
            lng=center["lng"],
            radius_meters=request.radius_meters,
            padding_percent=15
        )
        
        logger.info(f"Bounding box: {bbox}")
        
        # Step 3: Determine optimal zoom for detail capture
        optimal_zoom = mapbox_service.adjust_zoom_for_radius(request.radius_meters)
        logger.info(f"Using zoom level {optimal_zoom} for {request.radius_meters}m radius")
        
        # Step 4: Fetch tilted satellite image from Mapbox
        image_url = mapbox_service.get_static_image_url(
            center_lng=center["lng"],
            center_lat=center["lat"],
            zoom=optimal_zoom,
            pitch=request.pitch,
            bearing=request.bearing,
            width=1280,
            height=1280
        )
        
        logger.info(f"Image URL generated: {image_url[:100]}...")
        
        # Step 5: Fetch landmarks from Overpass API
        landmarks = await overpass_service.get_landmarks(
            bbox=bbox,
            limit=5
        )
        
        logger.info(f"Found {len(landmarks)} landmarks")
        
        return MapResponse(
            address=request.address,
            center=center,
            bbox=bbox,
            image_url=image_url,
            landmarks=landmarks,
            parameters={
                "radius_meters": request.radius_meters,
                "pitch": request.pitch,
                "bearing": request.bearing
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing map request: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process map request: {str(e)}"
        )


@app.post("/cartoonify", response_model=CartoonResponse)
async def cartoonify_map(request: CartoonRequest):
    """
    Milestone 02: Transform satellite map into cartoon style
    
    This endpoint:
    1. Fetches tilted 3D satellite image
    2. Transforms it into cartoon style using AI
    3. Returns both original and cartoon versions
    """
    try:
        logger.info(f"Cartoonifying map for: {request.address}")
        
        # Step 1: Fetch satellite map data (reuse fetch-map logic)
        center = await mapbox_service.geocode(request.address)
        if not center:
            raise HTTPException(
                status_code=404,
                detail=f"Could not geocode address: {request.address}"
            )
        
        bbox = mapbox_service.calculate_bbox(
            lat=center["lat"],
            lng=center["lng"],
            radius_meters=request.radius_meters,
            padding_percent=15
        )
        
        optimal_zoom = mapbox_service.adjust_zoom_for_radius(request.radius_meters)
        
        satellite_url = mapbox_service.get_static_image_url(
            center_lng=center["lng"],
            center_lat=center["lat"],
            zoom=optimal_zoom,
            pitch=request.pitch,
            bearing=request.bearing,
            width=1280,
            height=1280,
            style="satellite"
        )
        
        streets_url = mapbox_service.get_static_image_url(
            center_lng=center["lng"],
            center_lat=center["lat"],
            zoom=optimal_zoom,
            pitch=request.pitch,
            bearing=request.bearing,
            width=1280,
            height=1280,
            style="streets"
        )
        
        logger.info(f"Satellite image: {satellite_url[:80]}...")
        logger.info(f"Streets layer: {streets_url[:80]}...")
        
        # Step 2: Transform with AI using OpenAI with dual-layer reference
        logger.info(f"Sending to OpenAI gpt-image-1 for {request.style} transformation with dual layers...")
        cartoon_base64 = openai_service.cartoonify_image(
            image_url=satellite_url,
            streets_url=streets_url,
            style=request.style,
            pitch=request.pitch,
            bearing=request.bearing,
        )
        
        if not cartoon_base64:
            raise HTTPException(status_code=500, detail="Failed to generate cartoon image")

        logger.info(f"Cartoon complete! ({len(cartoon_base64)/1024:.0f}KB)")
        
        # Step 3: Get landmarks
        landmarks = await overpass_service.get_landmarks(bbox=bbox, limit=5)
        
        return CartoonResponse(
            address=request.address,
            satellite_image_url=satellite_url,
            cartoon_image_base64=cartoon_base64,
            landmarks=landmarks,
            parameters={
                "radius_meters": request.radius_meters,
                "pitch": request.pitch,
                "bearing": request.bearing,
                "style": request.style,
                "zoom": optimal_zoom
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error cartoonifying map: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to cartoonify map: {str(e)}"
        )


@app.post("/toonmap", response_model=ToonMapResponse)
async def generate_toonmap(request: CartoonRequest):
    """
    Milestone 03: Complete ToonMap with landmark icons
    
    This endpoint:
    1. Fetches tilted 3D satellite image
    2. Transforms it into cartoon style using AI
    3. Overlays landmark icons and labels
    4. Returns: satellite, cartoon, and final ToonMap with icons
    """
    try:
        logger.info(f"Generating complete ToonMap for: {request.address}")
        
        # Step 1: Geocode and fetch satellite map
        center = await mapbox_service.geocode(request.address)
        if not center:
            raise HTTPException(
                status_code=404,
                detail=f"Could not geocode address: {request.address}"
            )
        
        bbox = mapbox_service.calculate_bbox(
            lat=center["lat"],
            lng=center["lng"],
            radius_meters=request.radius_meters,
            padding_percent=15
        )
        
        optimal_zoom = mapbox_service.adjust_zoom_for_radius(request.radius_meters)
        
        satellite_url = mapbox_service.get_static_image_url(
            center_lng=center["lng"],
            center_lat=center["lat"],
            zoom=optimal_zoom,
            pitch=request.pitch,
            bearing=request.bearing,
            width=1280,
            height=1280,
            style="satellite"
        )
        
        streets_url = mapbox_service.get_static_image_url(
            center_lng=center["lng"],
            center_lat=center["lat"],
            zoom=optimal_zoom,
            pitch=request.pitch,
            bearing=request.bearing,
            width=1280,
            height=1280,
            style="streets"
        )
        
        logger.info(f"Satellite image fetched: {satellite_url[:80]}...")
        logger.info(f"Streets layer fetched: {streets_url[:80]}...")
        
        # Step 2: Get landmarks
        landmarks = await overpass_service.get_landmarks(bbox=bbox, limit=5)
        logger.info(f"Found {len(landmarks)} landmarks")
        
        # Step 3: Cartoonify with AI (using both satellite + streets for better accuracy)
        logger.info(f"Applying {request.style} cartoon transformation with dual-layer reference...")
        cartoon_base64 = openai_service.cartoonify_image(
            image_url=satellite_url,
            streets_url=streets_url,
            style=request.style,
            pitch=request.pitch,
            bearing=request.bearing,
        )
        
        if not cartoon_base64:
            raise HTTPException(status_code=500, detail="Failed to generate cartoon image")
        
        logger.info(f"Cartoon generated ({len(cartoon_base64)/1024:.0f}KB)")
        
        # Step 4: Overlay landmarks on cartoon
        logger.info("Overlaying landmarks on cartoon...")
        import base64
        from PIL import Image
        from io import BytesIO
        
        # Decode cartoon base64 to PIL Image
        cartoon_bytes = base64.b64decode(cartoon_base64)
        cartoon_image = Image.open(BytesIO(cartoon_bytes))
        
        # Overlay landmarks
        toonmap_image = overlay_service.overlay_landmarks(
            cartoon_image=cartoon_image,
            landmarks=landmarks,
            bbox=bbox,
            icon_service=icon_service
        )
        
        # Encode final ToonMap to base64
        buffer = BytesIO()
        toonmap_image.save(buffer, format="PNG")
        toonmap_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
        
        logger.info(f"ToonMap complete with {len(landmarks)} landmarks!")
        
        return ToonMapResponse(
            address=request.address,
            satellite_image_url=satellite_url,
            cartoon_image_base64=cartoon_base64,
            toonmap_image_base64=toonmap_base64,
            landmarks=landmarks,
            parameters={
                "radius_meters": request.radius_meters,
                "pitch": request.pitch,
                "bearing": request.bearing,
                "style": request.style,
                "zoom": optimal_zoom
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating ToonMap: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate ToonMap: {str(e)}"
        )


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    debug = os.getenv("DEBUG", "True").lower() == "true"
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=debug
    )
