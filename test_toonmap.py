#!/usr/bin/env python3
"""
Test the complete ToonMap endpoint with landmark overlay
"""
import requests
import json
import base64
from datetime import datetime

API_BASE = "http://localhost:8000"

def test_toonmap(address: str, radius: int = 500):
    """Test the complete ToonMap generation"""
    
    print(f"\n{'='*60}")
    print(f"TESTING COMPLETE TOONMAP")
    print(f"{'='*60}")
    print(f"Address: {address}")
    print(f"Radius: {radius}m")
    print(f"{'='*60}\n")
    
    # Call the /toonmap endpoint
    response = requests.post(
        f"{API_BASE}/toonmap",
        json={
            "address": address,
            "radius_meters": radius,
            "pitch": 60,
            "bearing": 0,
            "style": "3d_cartoon"
        }
    )
    
    if response.status_code != 200:
        print(f"❌ Error: {response.status_code}")
        print(response.text)
        return
    
    data = response.json()
    
    # Print results
    print(f"✅ ToonMap Generated!")
    print(f"\nParameters:")
    print(json.dumps(data["parameters"], indent=2))
    
    print(f"\nLandmarks ({len(data['landmarks'])}):")
    for i, landmark in enumerate(data["landmarks"], 1):
        print(f"  {i}. {landmark['name']} ({landmark['type']})")
    
    # Save all three images
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Satellite (download from URL)
    print(f"\nDownloading satellite image...")
    sat_response = requests.get(data["satellite_image_url"])
    sat_filename = f"output_satellite_{timestamp}.jpg"
    with open(sat_filename, "wb") as f:
        f.write(sat_response.content)
    print(f"✅ Saved: {sat_filename}")
    
    # Cartoon (decode base64)
    print(f"Saving cartoon image...")
    cartoon_data = base64.b64decode(data["cartoon_image_base64"])
    cartoon_filename = f"output_cartoon_{timestamp}.png"
    with open(cartoon_filename, "wb") as f:
        f.write(cartoon_data)
    print(f"✅ Saved: {cartoon_filename}")
    
    # ToonMap with icons (decode base64)
    print(f"Saving ToonMap with landmarks...")
    toonmap_data = base64.b64decode(data["toonmap_image_base64"])
    toonmap_filename = f"output_toonmap_{timestamp}.png"
    with open(toonmap_filename, "wb") as f:
        f.write(toonmap_data)
    print(f"✅ Saved: {toonmap_filename}")
    
    print(f"\n{'='*60}")
    print(f"🎉 COMPLETE TOONMAP READY!")
    print(f"{'='*60}")
    print(f"📸 Satellite: {sat_filename}")
    print(f"🎨 Cartoon: {cartoon_filename}")
    print(f"🗺️  ToonMap: {toonmap_filename}")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    # Test with Oberlin location
    test_toonmap("135 W Lorain Street, Oberlin, Ohio", radius=500)
