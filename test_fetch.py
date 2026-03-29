"""
Test script for ToonMap API - Downloads the tilted satellite image
"""
import requests
import json
from pathlib import Path

API_URL = "http://localhost:8000"
OUTPUT_DIR = Path("test_outputs")
OUTPUT_DIR.mkdir(exist_ok=True)


def test_fetch_map(address: str, radius: int = 500, pitch: int = 45, bearing: int = 0):
    """Test the /fetch-map endpoint and download the satellite image"""
    
    print(f"\n🗺️  Testing: {address}")
    print(f"   Radius: {radius}m | Pitch: {pitch}° | Bearing: {bearing}°")
    print("-" * 60)
    
    # Step 1: Call the API
    response = requests.post(
        f"{API_URL}/fetch-map",
        json={
            "address": address,
            "radius_meters": radius,
            "pitch": pitch,
            "bearing": bearing
        }
    )
    
    if response.status_code != 200:
        print(f"❌ Error: {response.status_code}")
        print(response.text)
        return
    
    data = response.json()
    
    # Step 2: Display results
    print(f"✅ Geocoded: {data['center']['place_name']}")
    print(f"   Coordinates: ({data['center']['lat']}, {data['center']['lng']})")
    print(f"\n📍 Found {len(data['landmarks'])} landmarks:")
    
    for i, landmark in enumerate(data['landmarks'], 1):
        print(f"   {i}. {landmark['name']} ({landmark['type']})")
    
    # Step 3: Download the satellite image
    image_url = data['image_url']
    print(f"\n🛰️  Downloading satellite image...")
    
    image_response = requests.get(image_url)
    
    if image_response.status_code == 200:
        # Save image
        safe_name = address.replace(" ", "_").replace(",", "")
        image_path = OUTPUT_DIR / f"{safe_name}_p{pitch}_r{radius}.png"
        
        with open(image_path, "wb") as f:
            f.write(image_response.content)
        
        print(f"✅ Saved to: {image_path}")
        print(f"   Size: {len(image_response.content) / 1024:.1f} KB")
        
        # Save JSON metadata
        json_path = OUTPUT_DIR / f"{safe_name}_p{pitch}_r{radius}.json"
        with open(json_path, "w") as f:
            json.dump(data, f, indent=2)
        print(f"✅ Metadata: {json_path}")
    else:
        print(f"❌ Failed to download image: {image_response.status_code}")
    
    print("\n" + "=" * 60)


if __name__ == "__main__":
    # Test 1: Times Square with default 45° pitch
    test_fetch_map("Times Square, New York", radius=500, pitch=45)
    
    # Test 2: Eiffel Tower with maximum 60° pitch for dramatic angle
    test_fetch_map("Eiffel Tower, Paris", radius=500, pitch=60)
    
    # Test 3: Golden Gate Bridge with side angle (bearing=90)
    test_fetch_map("Golden Gate Bridge, San Francisco", radius=800, pitch=45, bearing=90)
    
    print("\n✨ All tests complete! Check the test_outputs/ folder for images.")
