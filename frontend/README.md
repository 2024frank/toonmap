# ToonMap Frontend

Interactive web interface for ToonMap - built with React, TypeScript, and Tailwind CSS.

## Features

- 🌍 Country selector with flag emojis
- 📍 Address input with auto-complete
- 📏 Interactive radius slider (100m - 2000m)
- 🏷️ Toggle landmark labels on/off
- 🖼️ Side-by-side satellite vs cartoon view
- ⚡ Real-time generation with loading states

## Tech Stack

- **React 19** - UI framework
- **TypeScript** - Type safety
- **Vite** - Build tool & dev server
- **Tailwind CSS v4** - Styling
- **FastAPI Backend** - REST API on port 8000

## Development

1. Install dependencies:
```bash
npm install
```

2. Start dev server:
```bash
npm run dev
```

3. Open [http://localhost:5175](http://localhost:5175)

## Build for Production

```bash
npm run build
npm run preview
```

## API Integration

The frontend connects to the FastAPI backend at `http://localhost:8000/toonmap` endpoint.

Make sure the backend is running:
```bash
cd ..
python3 main.py
```
