# ToonMap

Transform satellite maps into stylized cartoon representations with 3D tilted views and landmark icons.

## Features

- 🌍 **Interactive Web UI** - React + TypeScript frontend with country selector
- ✅ **Address Verification** - Confirm location before generation
- 📊 **Progress Tracking** - Real-time percentage bar with stage updates
- 🗺️ **3D Satellite Imagery** - Tilted views up to 60° pitch from Mapbox
- 🏙️ **Multi-Layer AI Reference** - Composites satellite + streets for better accuracy
- 📍 **Smart Landmarks** - Automatic detection via OpenStreetMap
- 🎨 **AI Cartoon Filter** - OpenAI DALL-E 2 transformation with dual-layer input
- 📌 **Icon Overlay** - Color-coded landmark pins and labels (toggle on/off)
- ⚙️ **Full Control** - Configurable radius (100-2000m), side-by-side comparison

## Quick Start

### Backend Setup

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

2. Configure `.env`:
```env
MAP_BOX_TOKEN=your_mapbox_token
OPENAI_API_KEY=your_openai_api_key
HF_TOKEN=your_huggingface_token  # Optional
PORT=8000
DEBUG=True
```

3. Start the API server:
```bash
python3 main.py
```

The API will be available at `http://localhost:8000`

### Frontend Setup

1. Navigate to frontend:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Start dev server:
```bash
npm run dev
```

The web UI will open at `http://localhost:5175`

## Usage

1. Open the web interface (default: `http://localhost:5177`)
2. **Select Country** - Choose from 12 countries with flag emojis
3. **Enter Address** - Type location name or street address
4. **Adjust Radius** - Slide between 100m - 2000m
5. **Verify Address** - Click to confirm the exact location (shows coordinates)
6. **Generate ToonMap** - Watch the progress bar track AI transformation
7. **Toggle Labels** - Switch between cartoon-only or with landmark icons
8. **Compare Side-by-Side** - Satellite (left) vs Cartoon/ToonMap (right)

### Multi-Layer AI Enhancement

The AI now receives a **composite reference** made from:
- 70% Satellite imagery (textures, natural features)
- 30% Streets layer (building outlines, road structure)

This dual-layer approach gives the AI better spatial understanding, resulting in:
- More accurate building placement and shapes
- Clearer road layouts and intersections
- Better preservation of architectural details
- Enhanced structural fidelity

## API Endpoints

### 1. `POST /fetch-map` - Milestone 01: Data Fetch

Fetches tilted satellite imagery and landmark data.

**Request:**
```json
{
  "address": "Central Park, New York",
  "radius_meters": 500,
  "pitch": 60,
  "bearing": 0
}
```

**Response:**
Returns satellite image URL, center coordinates, bounding box, and top 5 landmarks.

---

### 2. `POST /cartoonify` - Milestone 02: AI Transformation

Transforms satellite map into cartoon style using AI.

**Request:**
```json
{
  "address": "135 W Lorain Street, Oberlin, Ohio",
  "radius_meters": 500,
  "pitch": 60,
  "bearing": 0,
  "style": "3d_cartoon"
}
```

**Response:**
Returns both satellite URL and cartoon image (base64 encoded PNG) plus landmarks.

---

### 3. `POST /toonmap` - Milestone 03: Complete ToonMap

Generates the complete ToonMap with landmark icons and labels overlaid.

**Request:**
```json
{
  "address": "135 W Lorain Street, Oberlin, Ohio",
  "radius_meters": 500,
  "pitch": 60,
  "bearing": 0,
  "style": "3d_cartoon"
}
```

**Response:**
Returns:
- `satellite_image_url`: Original tilted satellite image
- `cartoon_image_base64`: AI-transformed cartoon (base64 PNG)
- `toonmap_image_base64`: Final map with landmark icons (base64 PNG)
- `landmarks`: List of landmarks with coordinates
- `parameters`: Applied settings

## Parameters

- `address` (required): Location name or address
- `radius_meters` (optional): Radius around center point (default: 500m, range: 100-5000m)
- `pitch` (optional): Camera tilt angle (default: 45°, range: 0-60°)
- `bearing` (optional): Camera rotation (default: 0°/north, range: 0-360°)

## Roadmap

- ✅ **Milestone 01**: Data Fetch - Fetch satellite image & landmark data
- ✅ **Milestone 02**: Basic Style - Apply AI cartoon filter via OpenAI DALL-E 2
- ✅ **Milestone 03**: Landmarks - Overlay icons and labels on cartoonified map

## Quick Test

Run the test script to generate a complete ToonMap:

```bash
python3 test_toonmap.py
```

Or test with cURL:

```bash
curl -X POST "http://localhost:8000/toonmap" \
  -H "Content-Type: application/json" \
  -d '{
    "address": "Eiffel Tower, Paris",
    "radius_meters": 500,
    "pitch": 60,
    "style": "3d_cartoon"
  }'
```

## Interactive Docs

Visit `http://localhost:8000/docs` for interactive Swagger UI.
