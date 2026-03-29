"""
Test AI cartoon transformation (Milestone 02)
"""
import requests
from pathlib import Path
import time

API_URL = "http://localhost:8000"
OUTPUT_DIR = Path("test_outputs/cartoons")
OUTPUT_DIR.mkdir(exist_ok=True, parents=True)


def test_cartoon(address: str, radius: int = 200, style: str = "3d_cartoon"):
    """Test cartoon transformation"""
    
    print(f"\n🎨 Cartoonifying: {address}")
    print(f"   Style: {style} | Radius: {radius}m | Pitch: 60° | Zoom: 18")
    print("=" * 70)
    
    start = time.time()
    
    print("\n🚀 Sending request to API...")
    response = requests.post(
        f"{API_URL}/cartoonify",
        json={
            "address": address,
            "radius_meters": radius,
            "pitch": 60,
            "bearing": 45,  # Angled view for better 3D
            "style": style
        }
    )
    
    if response.status_code != 200:
        print(f"❌ Error {response.status_code}: {response.text}")
        return
    
    data = response.json()
    elapsed = time.time() - start
    
    print(f"✅ API Response received ({elapsed:.1f}s)")
    print(f"\n📍 Location: {data['center']['place_name']}")
    print(f"🏛️  Landmarks: {len(data['landmarks'])} found")
    
    # Download satellite image
    print(f"\n📥 Downloading satellite image...")
    sat_response = requests.get(data['satellite_image_url'])
    if sat_response.status_code == 200:
        sat_path = OUTPUT_DIR / f"{address.replace(' ', '_').replace(',', '')}_satellite.png"
        with open(sat_path, "wb") as f:
            f.write(sat_response.content)
        print(f"   ✅ {sat_path.name} ({len(sat_response.content)/1024:.0f} KB)")
    
    # Download cartoon image
    print(f"\n🎨 Downloading CARTOON image...")
    cartoon_response = requests.get(data['cartoon_image_url'])
    if cartoon_response.status_code == 200:
        cartoon_path = OUTPUT_DIR / f"{address.replace(' ', '_').replace(',', '')}_cartoon_{style}.png"
        with open(cartoon_path, "wb") as f:
            f.write(cartoon_response.content)
        print(f"   ✅ {cartoon_path.name} ({len(cartoon_response.content)/1024:.0f} KB)")
        print(f"\n   🖼️  OPEN THIS FILE TO SEE THE 3D CARTOON RESULT!")
    
    print("\n" + "=" * 70)
    total_time = time.time() - start
    print(f"⏱️  Total time: {total_time:.1f}s")


if __name__ == "__main__":
    # Test with Oberlin
    print("\n🧪 MILESTONE 02 TEST: AI Cartoon Transformation")
    print("   This may take 30-60 seconds (AI processing time)...")
    
    test_cartoon("135 West Lorain Street, Oberlin, Ohio", radius=200, style="3d_cartoon")
    
    print("\n✨ TEST COMPLETE!")
    print("   Compare satellite vs cartoon in test_outputs/cartoons/")
