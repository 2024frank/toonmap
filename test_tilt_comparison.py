"""
Compare different tilt angles to see 3D effect
"""
import requests
from pathlib import Path

API_URL = "http://localhost:8000"
OUTPUT_DIR = Path("test_outputs/tilt_comparison")
OUTPUT_DIR.mkdir(exist_ok=True, parents=True)


def test_tilt(address: str, radius: int = 500):
    """Test different tilt angles"""
    
    print(f"\n🎬 Testing tilt angles for: {address}")
    print("=" * 70)
    
    # Test different pitch values
    tilts = [
        {"pitch": 0, "label": "Flat (0°) - No 3D"},
        {"pitch": 30, "label": "Light Tilt (30°)"},
        {"pitch": 45, "label": "Strong Tilt (45°)"},
        {"pitch": 60, "label": "Maximum Tilt (60°) - Most 3D"},
    ]
    
    for config in tilts:
        pitch = config["pitch"]
        
        print(f"\n🎥 {config['label']}")
        print("-" * 70)
        
        response = requests.post(
            f"{API_URL}/fetch-map",
            json={
                "address": address,
                "radius_meters": radius,
                "pitch": pitch
            }
        )
        
        if response.status_code != 200:
            print(f"❌ Error: {response.status_code}")
            continue
        
        data = response.json()
        url = data['image_url']
        
        # Download image
        image_response = requests.get(url)
        if image_response.status_code == 200:
            filename = f"{address.replace(' ', '_').replace(',', '')}_pitch{pitch}.png"
            filepath = OUTPUT_DIR / filename
            
            with open(filepath, "wb") as f:
                f.write(image_response.content)
            
            size_kb = len(image_response.content) / 1024
            print(f"   ✅ {filepath.name} ({size_kb:.1f} KB)")


if __name__ == "__main__":
    # Test with an iconic location
    test_tilt("Times Square, New York", radius=500)
    
    print("\n" + "=" * 70)
    print("✨ Compare the images in test_outputs/tilt_comparison/")
    print("   pitch=60 gives the strongest 3D cartoon effect!")
