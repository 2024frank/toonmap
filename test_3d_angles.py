"""
Test multiple bearing angles to maximize 3D perspective effect
"""
import requests
from pathlib import Path

API_URL = "http://localhost:8000"
OUTPUT_DIR = Path("test_outputs/3d_angles")
OUTPUT_DIR.mkdir(exist_ok=True, parents=True)


def test_3d_angles(address: str, radius: int = 200):
    """Test different bearing angles with max pitch for best 3D view"""
    
    print(f"\n🎥 Testing 3D angles for: {address}")
    print(f"   Using: {radius}m radius, zoom 18, pitch 60° (MAX)")
    print("=" * 70)
    
    # Test different bearing angles
    angles = [
        {"bearing": 0, "label": "North (0°)"},
        {"bearing": 45, "label": "NE (45°)"},
        {"bearing": 90, "label": "East (90°)"},
        {"bearing": 135, "label": "SE (135°)"},
        {"bearing": 180, "label": "South (180°)"},
        {"bearing": 225, "label": "SW (225°)"},
        {"bearing": 270, "label": "West (270°)"},
        {"bearing": 315, "label": "NW (315°)"},
    ]
    
    for config in angles:
        bearing = config["bearing"]
        
        print(f"\n📐 {config['label']}")
        
        response = requests.post(
            f"{API_URL}/fetch-map",
            json={
                "address": address,
                "radius_meters": radius,
                "pitch": 60,  # Maximum tilt
                "bearing": bearing
            }
        )
        
        if response.status_code != 200:
            print(f"   ❌ Error")
            continue
        
        data = response.json()
        url = data['image_url']
        
        # Download image
        image_response = requests.get(url)
        if image_response.status_code == 200:
            filename = f"Oberlin_bearing{bearing:03d}.png"
            filepath = OUTPUT_DIR / filename
            
            with open(filepath, "wb") as f:
                f.write(image_response.content)
            
            size_kb = len(image_response.content) / 1024
            print(f"   ✅ {filename} ({size_kb:.0f} KB)")


if __name__ == "__main__":
    test_3d_angles("135 West Lorain Street, Oberlin, Ohio", radius=200)
    
    print("\n" + "=" * 70)
    print("✨ All 8 angles captured! Check test_outputs/3d_angles/")
    print("   Each shows the same location from a different rotation")
    print("   All have 60° tilt + zoom 18 for maximum 3D detail!")
