#!/usr/bin/env python3
"""
Test the multi-layer (satellite + streets) AI transformation
"""
import requests
import json
import base64
from datetime import datetime

API_BASE = "http://localhost:8000"

def test_multilayer(address: str, radius: int = 500):
    """Test ToonMap with dual-layer reference"""
    
    print(f"\n{'='*70}")
    print(f"TESTING MULTI-LAYER AI TRANSFORMATION")
    print(f"{'='*70}")
    print(f"Address: {address}")
    print(f"Radius: {radius}m")
    print(f"Layers: Satellite (3D) + Streets (structure reference)")
    print(f"{'='*70}\n")
    
    print("🚀 Sending request to /toonmap endpoint...")
    print("   This will composite satellite + streets before AI transformation")
    print("   Expected: More accurate building placement and road structure\n")
    
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
    print(f"✅ Multi-Layer ToonMap Generated!")
    print(f"\nParameters:")
    print(json.dumps(data["parameters"], indent=2))
    
    print(f"\nLandmarks ({len(data['landmarks'])}):")
    for i, landmark in enumerate(data["landmarks"], 1):
        icon = "⛪" if landmark['type'] == 'place_of_worship' else \
               "🌳" if landmark['type'] == 'park' else \
               "🏛️" if landmark['type'] == 'historic' else "📍"
        print(f"  {i}. {icon} {landmark['name']} ({landmark['type']})")
    
    # Save images
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Satellite
    print(f"\n💾 Saving outputs...")
    sat_response = requests.get(data["satellite_image_url"])
    sat_filename = f"multilayer_satellite_{timestamp}.jpg"
    with open(sat_filename, "wb") as f:
        f.write(sat_response.content)
    print(f"   📸 Satellite: {sat_filename}")
    
    # Cartoon (with dual-layer reference)
    cartoon_data = base64.b64decode(data["cartoon_image_base64"])
    cartoon_filename = f"multilayer_cartoon_{timestamp}.png"
    with open(cartoon_filename, "wb") as f:
        f.write(cartoon_data)
    print(f"   🎨 Cartoon (dual-layer AI): {cartoon_filename}")
    
    # ToonMap with icons
    toonmap_data = base64.b64decode(data["toonmap_image_base64"])
    toonmap_filename = f"multilayer_toonmap_{timestamp}.png"
    with open(toonmap_filename, "wb") as f:
        f.write(toonmap_data)
    print(f"   🗺️  ToonMap (with labels): {toonmap_filename}")
    
    print(f"\n{'='*70}")
    print(f"🎉 MULTI-LAYER TRANSFORMATION COMPLETE!")
    print(f"{'='*70}")
    print(f"\nThe cartoon should have:")
    print(f"  ✓ More accurate building shapes and positions")
    print(f"  ✓ Clearer road layouts and structure")
    print(f"  ✓ Better preservation of spatial relationships")
    print(f"  ✓ Enhanced detail from streets layer reference")
    print(f"{'='*70}\n")


if __name__ == "__main__":
    # Test with a well-known location
    test_multilayer("Times Square, New York City", radius=500)
