# Render Deployment - Quick Fix Guide

## Your Backend Issue

The backend at `https://toonmap.onrender.com` is returning "Not Found" because:

**The Start Command is wrong!** You have it set to `$ yarn start` (Node.js) but this is a Python app.

## Fix Your Backend Now

1. Go to your Render dashboard: https://dashboard.render.com
2. Click on your **toonmap** service
3. Go to **Settings** tab
4. Find **Start Command** and change it to:
   ```
   python3 main.py
   ```
5. **Save Changes**
6. The service will auto-redeploy

Wait ~3-5 minutes, then test:
```bash
curl https://toonmap.onrender.com/
```

You should see:
```json
{
  "message": "Welcome to ToonMap API",
  "docs": "/docs",
  "endpoints": {...}
}
```

---

## Deploy Frontend (After Backend is Fixed)

### Method 1: Use render.yaml (Automatic)

I've added `render.yaml` to your repo. Just:

1. Go to Render Dashboard
2. **New +** → **Blueprint**
3. Connect your `2024frank/toonmap` repo
4. Render will auto-detect `render.yaml` and create both services
5. Add your environment variables when prompted

### Method 2: Manual Static Site

1. **New +** → **Static Site**
2. Connect repo: `2024frank/toonmap`
3. **Name**: `toonmap-frontend`
4. **Branch**: `main`
5. **Build Command**:
   ```bash
   cd frontend && npm install && npm run build
   ```
6. **Publish Directory**:
   ```
   frontend/dist
   ```
7. **Create Static Site**

---

## Important: Check These Settings

### Backend Service Settings:
- ✅ **Language**: Python
- ✅ **Build Command**: `pip install -r requirements.txt`
- ✅ **Start Command**: `python3 main.py` ⚠️ (FIX THIS!)
- ✅ **Branch**: main

### Environment Variables (Backend):
```
MAP_BOX_TOKEN=your_token
OPENAI_API_KEY=your_key
HF_TOKEN=your_token
PORT=8000
DEBUG=False
```

---

## After Both Deploy

Your app will be live at:
- 🔧 API: `https://toonmap.onrender.com`
- 🌐 Frontend: `https://toonmap-frontend.onrender.com`

The frontend is already configured to connect to the backend!

---

## Quick Test

Once backend is fixed and responding, test the complete flow:

```bash
# Test API
curl https://toonmap.onrender.com/

# Visit frontend
open https://toonmap-frontend.onrender.com
```
