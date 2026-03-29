# ToonMap Deployment Guide

## Deployment Options

### Option 1: Vercel (Recommended for Frontend + Serverless Backend)

#### Deploy Frontend
```bash
cd frontend
npm install
npm run build

# Install Vercel CLI
npm i -g vercel

# Deploy
vercel --prod
```

#### Deploy Backend as Vercel Serverless
Create `vercel.json` in the root:

```json
{
  "builds": [
    {
      "src": "main.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "main.py"
    }
  ],
  "env": {
    "MAP_BOX_TOKEN": "@mapbox-token",
    "OPENAI_API_KEY": "@openai-key",
    "HF_TOKEN": "@hf-token"
  }
}
```

Add environment variables in Vercel dashboard:
```bash
vercel env add MAP_BOX_TOKEN
vercel env add OPENAI_API_KEY
vercel env add HF_TOKEN
```

---

### Option 2: Railway (Easiest Full-Stack)

1. Go to [railway.app](https://railway.app)
2. Click "New Project" → "Deploy from GitHub"
3. Select your `2024frank/toonmap` repo
4. Railway auto-detects both Python and Node.js
5. Add environment variables:
   - `MAP_BOX_TOKEN`
   - `OPENAI_API_KEY`
   - `HF_TOKEN`
   - `PORT=8000`

Railway will automatically:
- Build the frontend (`npm install && npm run build`)
- Start the backend (`python3 main.py`)
- Assign public URLs for both

---

### Option 3: Render

#### Backend (Web Service)
1. Go to [render.com](https://render.com)
2. New → Web Service
3. Connect GitHub repo
4. Settings:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python3 main.py`
   - **Environment**: Python 3
5. Add environment variables in dashboard

#### Frontend (Static Site)
1. New → Static Site
2. Settings:
   - **Build Command**: `cd frontend && npm install && npm run build`
   - **Publish Directory**: `frontend/dist`
3. Update `API_BASE` in `frontend/src/App.tsx` to your backend URL

---

### Option 4: Docker (Self-Hosting)

Create `Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend
COPY main.py .
COPY services/ services/

# Install Node.js for frontend
RUN apt-get update && apt-get install -y nodejs npm

# Build frontend
COPY frontend/ frontend/
WORKDIR /app/frontend
RUN npm install && npm run build

WORKDIR /app

EXPOSE 8000

CMD ["python3", "main.py"]
```

Build and run:
```bash
docker build -t toonmap .
docker run -p 8000:8000 --env-file .env toonmap
```

---

## Environment Variables Required

For any deployment, you need:

```env
MAP_BOX_TOKEN=pk.eyJ1Ij...your_token
OPENAI_API_KEY=sk-proj-...your_key
HF_TOKEN=hf_...your_token  # Optional
PORT=8000
DEBUG=False  # Set to False in production
```

---

## CORS Configuration

If deploying frontend and backend separately, update CORS in `main.py`:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://your-frontend-domain.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## Frontend API URL

Update `API_BASE` in `frontend/src/App.tsx` to your deployed backend URL:

```typescript
const API_BASE = 'https://your-backend-url.railway.app';
```

---

## Recommended: Railway

**Why?** Railway is the easiest for this project because:
- Automatically detects both Python and Node.js
- Handles frontend build + backend server in one deployment
- Free tier available
- Simple environment variable management
- One-click deploy from GitHub

**Steps:**
1. Push code to GitHub ✅ (Done!)
2. Connect Railway to your repo
3. Add environment variables
4. Deploy! (Takes ~5 minutes)
