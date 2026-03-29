"""
Test BOTH OpenAI and HuggingFace cartoon transformations
"""
import requests
import base64
from pathlib import Path
import time

API_URL = "http://localhost:8000"
OUTPUT_DIR = Path("test_outputs/ai_comparison")
OUTPUT_DIR.mkdir(exist_ok=True, parents=True)

def test_ai_service(service_name: str):
    """Test a specific AI service"""
    
    print(f"\n{'='*70}")
    print(f"🎨 Testing: {service_name}")
    print(f"{'='*70}")
    
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
            print(f"❌ Error {response.status_code}: {response.json()['detail'][:100]}")
            return False
        
        data = response.json()
        elapsed = time.time() - start
        
        # Save cartoon
        cartoon_bytes = base64.b64decode(data['cartoon_image_base64'])
        cartoon_path = OUTPUT_DIR / f"{service_name}_cartoon.png"
        with open(cartoon_path, "wb") as f:
            f.write(cartoon_bytes)
        
        # Save satellite for reference
        if not (OUTPUT_DIR / "satellite.png").exists():
            sat_response = requests.get(data['satellite_image_url'])
            with open(OUTPUT_DIR / "satellite.png", "wb") as f:
                f.write(sat_response.content)
        
        print(f"✅ SUCCESS!")
        print(f"   Time: {elapsed:.1f}s")
        print(f"   File: {cartoon_path.name} ({len(cartoon_bytes)/1024:.0f} KB)")
        print(f"   🎉 OPEN THIS FILE TO SEE THE CARTOON!")
        
        return True
        
    except requests.exceptions.Timeout:
        print(f"⏱️  Timeout (>180s)")
        return False
    except Exception as e:
        print(f"❌ Error: {str(e)[:100]}")
        return False


if __name__ == "__main__":
    print("\n" + "="*70)
    print("🧪 AI CARTOON COMPARISON TEST")
    print("   Testing: OpenAI vs HuggingFace")
    print("="*70)
    
    results = {}
    
    # Test OpenAI gpt-image-1
    results['OpenAI'] = test_ai_service("OpenAI_GPT_Image_1")
    
    # Test HuggingFace instruct-pix2pix
    results['HuggingFace'] = test_ai_service("HuggingFace_InstructPix2Pix")
    
    print("\n" + "="*70)
    print("📊 RESULTS:")
    print("="*70)
    for service, success in results.items():
        status = "✅ Works" if success else "❌ Failed"
        print(f"   {service}: {status}")
    
    print(f"\n📂 Compare cartoons in: {OUTPUT_DIR}/")
    print("   Open both side-by-side to see which looks better!")
