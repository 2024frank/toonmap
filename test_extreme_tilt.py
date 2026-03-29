"""
Test extreme tilt angles beyond 60° to see if Static API supports it
"""
import requests
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

OUTPUT_DIR = Path("test_outputs/extreme_tilt")
OUTPUT_DIR.mkdir(exist_ok=True, parents=True)

MAPBOX_TOKEN = os.getenv("MAP_BOX_TOKEN")

def test_pitch_values():
    """Test if Static API accepts pitch > 60°"""
    
    # Oberlin coordinates
    lng = -82.222015
    lat = 41.29386
    zoom = 18
    bearing = 45  # Angled view
    
    print("🧪 Testing extreme pitch values on Mapbox Static Images API")
    print("=" * 70)
    
    test_pitches = [60, 65, 70, 75, 80, 85]
    
    for pitch in test_pitches:
        print(f"\n📐 Testing pitch={pitch}°...")
        
        url = f"https://api.mapbox.com/styles/v1/mapbox/satellite-v9/static/{lng},{lat},{zoom},{bearing},{pitch}/1280x1280@2x?access_token={MAPBOX_TOKEN}"
        
        response = requests.get(url)
        
        if response.status_code == 200:
            filepath = OUTPUT_DIR / f"oberlin_pitch{pitch}.png"
            with open(filepath, "wb") as f:
                f.write(response.content)
            
            size_kb = len(response.content) / 1024
            print(f"   ✅ SUCCESS! pitch={pitch}° works ({size_kb:.0f} KB)")
        else:
            print(f"   ❌ FAILED: pitch={pitch}° - Status {response.status_code}")
            if pitch > 60:
                print(f"      (Static API may be capped at 60°)")


if __name__ == "__main__":
    test_pitch_values()
    
    print("\n" + "=" * 70)
    print("📊 Results: Check which pitch values worked!")
    print("   If pitch > 60° works, we can get even MORE 3D tilt! 🎉")
