"""
Test AI cartoon transformation using OpenAI (Milestone 02)
"""
import requests
from pathlib import Path
import base64
import time

API_URL = "http://localhost:8000"
OUTPUT_DIR = Path("test_outputs/cartoons_openai")
OUTPUT_DIR.mkdir(exist_ok=True, parents=True)


def test_cartoon(address: str, radius: int = 200, style: str = "3d_cartoon"):
    """Test OpenAI cartoon transformation"""
    
    print(f"\n🎨 OPENAI CARTOON TEST: {address}")
    print(f"   Style: {style} | Radius: {radius}m | Pitch: 60° | Zoom: 18")
    print("=" * 70)
    
    start = time.time()
    
    print("\n🚀 Sending to ToonMap API (this will take 30-120 seconds)...")
    print("   1️⃣  Fetching satellite image from Mapbox...")
    print("   2️⃣  Downloading image...")
    print("   3️⃣  Sending to OpenAI GPT-Image-1.5...")
    print("   4️⃣  AI is cartoonifying (30-120s)...")
    
    response = requests.post(
        f"{API_URL}/cartoonify",
        json={
            "address": address,
            "radius_meters": radius,
            "pitch": 60,
            "bearing": 45,  # Angled view for better 3D
            "style": style
        },
        timeout=180  # 3 minute timeout for AI processing
    )
    
    if response.status_code != 200:
        print(f"\n❌ Error {response.status_code}:")
        print(response.text)
        return
    
    data = response.json()
    elapsed = time.time() - start
    
    print(f"\n✅ API Response received! ({elapsed:.1f}s total)")
    print(f"\n📍 Location: {data['address']}")
    print(f"🏛️  Landmarks: {len(data['landmarks'])} found")
    
    # Download satellite image
    print(f"\n📥 Saving satellite image...")
    sat_response = requests.get(data['satellite_image_url'])
    if sat_response.status_code == 200:
        safe_name = address.replace(' ', '_').replace(',', '')
        sat_path = OUTPUT_DIR / f"{safe_name}_satellite.png"
        with open(sat_path, "wb") as f:
            f.write(sat_response.content)
        print(f"   ✅ {sat_path.name}")
    
    # Save cartoon image from base64
    print(f"\n🎨 Saving CARTOON image...")
    cartoon_base64 = data['cartoon_image_base64']
    cartoon_bytes = base64.b64decode(cartoon_base64)
    
    safe_name = address.replace(' ', '_').replace(',', '')
    cartoon_path = OUTPUT_DIR / f"{safe_name}_CARTOON_{style}.png"
    with open(cartoon_path, "wb") as f:
        f.write(cartoon_bytes)
    
    print(f"   ✅ {cartoon_path.name} ({len(cartoon_bytes)/1024:.0f} KB)")
    print(f"\n   🎉 OPEN THIS FILE TO SEE YOUR 3D CARTOON MAP!")
    
    # Show landmarks found
    if data['landmarks']:
        print(f"\n📍 Landmarks found:")
        for i, lm in enumerate(data['landmarks'][:5], 1):
            print(f"   {i}. {lm['name']} ({lm['type']})")
    
    print("\n" + "=" * 70)
    print(f"⏱️  Total processing time: {elapsed:.1f}s")
    print(f"💰 Estimated cost: ~$0.13-0.20 (OpenAI GPT-Image-1.5 high quality)")


if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("🎨 MILESTONE 02: AI CARTOON TRANSFORMATION with OpenAI")
    print("=" * 70)
    
    # Test with Oberlin, Ohio
    test_cartoon(
        address="135 West Lorain Street, Oberlin, Ohio",
        radius=200,
        style="3d_cartoon"
    )
    
    print("\n\n✨ TEST COMPLETE!")
    print(f"   Check: test_outputs/cartoons_openai/")
    print(f"   Compare satellite vs cartoon side-by-side!")
