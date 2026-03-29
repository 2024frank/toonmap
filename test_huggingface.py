"""
Test Hugging Face SDXL cartoon transformation
"""
import requests
import base64
from pathlib import Path
import time

API_URL = "http://localhost:8000"
OUTPUT_DIR = Path("test_outputs/hf_cartoons")
OUTPUT_DIR.mkdir(exist_ok=True, parents=True)

def test_hf_cartoon():
    """Test HuggingFace SDXL transformation"""
    
    print("\n" + "=" * 70)
    print("🤗 HUGGING FACE SDXL TEST: Oberlin, Ohio")
    print("=" * 70)
    print("\n⚙️  Settings:")
    print("   - Model: Stable Diffusion XL (stabilityai/sdxl-base-1.0)")
    print("   - Radius: 200m | Zoom: 18 | Pitch: 60° | Bearing: 45°")
    print("   - Style: 3D Cartoon Isometric")
    print("\n🚀 Starting transformation (30-60 seconds)...")
    
    start = time.time()
    
    try:
        response = requests.post(
            f"{API_URL}/cartoonify",
            json={
                "address": "135 West Lorain Street, Oberlin, Ohio",
                "radius_meters": 200,
                "pitch": 60,
                "bearing": 45,
                "style": "3d_cartoon"
            },
            timeout=180
        )
        
        if response.status_code != 200:
            print(f"\n❌ Error {response.status_code}:")
            print(response.text)
            return
        
        data = response.json()
        elapsed = time.time() - start
        
        print(f"\n✅ Transformation complete! ({elapsed:.1f}s)")
        
        # Save satellite
        sat_response = requests.get(data['satellite_image_url'])
        sat_path = OUTPUT_DIR / "satellite.png"
        with open(sat_path, "wb") as f:
            f.write(sat_response.content)
        print(f"\n📸 Satellite: {sat_path.name}")
        
        # Save cartoon
        cartoon_bytes = base64.b64decode(data['cartoon_image_base64'])
        cartoon_path = OUTPUT_DIR / "SDXL_CARTOON_3D.png"
        with open(cartoon_path, "wb") as f:
            f.write(cartoon_bytes)
        
        print(f"🎨 Cartoon: {cartoon_path.name} ({len(cartoon_bytes)/1024:.0f} KB)")
        print(f"\n🎉 OPEN THIS FILE: {cartoon_path}")
        
        print(f"\n💰 Cost: ~$0.002-0.004 (much cheaper than OpenAI!)")
        print(f"⏱️  Time: {elapsed:.1f}s")
        
    except requests.exceptions.Timeout:
        print("\n⏱️  Request timed out (>180s)")
        print("   The AI might still be processing. Check server logs.")
    except Exception as e:
        print(f"\n❌ Error: {e}")

if __name__ == "__main__":
    test_hf_cartoon()
    print("\n" + "=" * 70)
