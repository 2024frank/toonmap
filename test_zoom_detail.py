"""
Test different zoom levels to find optimal detail for cartoon transformation
"""
import requests
from pathlib import Path

API_URL = "http://localhost:8000"
OUTPUT_DIR = Path("test_outputs/zoom_comparison")
OUTPUT_DIR.mkdir(exist_ok=True, parents=True)


def test_zoom_levels(address: str):
    """Test the same location at different zoom levels"""
    
    print(f"\n🔍 Testing zoom detail for: {address}")
    print("=" * 70)
    
    # Test with different radius values to trigger different zoom levels
    test_configs = [
        {"radius": 300, "expected_zoom": 18, "label": "Maximum Detail"},
        {"radius": 500, "expected_zoom": 17, "label": "High Detail"},
        {"radius": 900, "expected_zoom": 16, "label": "Medium Detail"},
    ]
    
    for config in test_configs:
        radius = config["radius"]
        
        print(f"\n📐 Testing: {radius}m radius ({config['label']})")
        print("-" * 70)
        
        response = requests.post(
            f"{API_URL}/fetch-map",
            json={
                "address": address,
                "radius_meters": radius,
                "pitch": 45
            }
        )
        
        if response.status_code != 200:
            print(f"❌ Error: {response.status_code}")
            continue
        
        data = response.json()
        
        # Extract zoom from URL
        url = data['image_url']
        zoom_part = url.split('/static/')[1].split('/')[0]
        actual_zoom = int(zoom_part.split(',')[2])
        
        print(f"   Actual zoom used: {actual_zoom}")
        
        # Download image
        image_response = requests.get(url)
        if image_response.status_code == 200:
            filename = f"{address.replace(' ', '_').replace(',', '')}_zoom{actual_zoom}_r{radius}.png"
            filepath = OUTPUT_DIR / filename
            
            with open(filepath, "wb") as f:
                f.write(image_response.content)
            
            size_kb = len(image_response.content) / 1024
            print(f"   ✅ Saved: {filepath.name} ({size_kb:.1f} KB)")
        
    print("\n" + "=" * 70)
    print(f"✨ Check {OUTPUT_DIR}/ to compare detail levels!")


if __name__ == "__main__":
    # Test with an urban area that has lots of detail
    test_zoom_levels("Times Square, New York")
    
    print("\n💡 Recommendation:")
    print("   - Zoom 18 (300m radius): Best for capturing fine details (buildings, cars)")
    print("   - Zoom 17 (500m radius): Good balance - your current default ✅")
    print("   - Zoom 16 (900m radius): Too far for cartoon detail")
