#!/bin/bash

echo "🗺️  Starting ToonMap..."
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "❌ Error: .env file not found!"
    echo "Please create .env with your API keys."
    exit 1
fi

# Start backend in background
echo "🚀 Starting API server on http://localhost:8000..."
python3 main.py &
BACKEND_PID=$!

sleep 3

# Start frontend
echo "🎨 Starting frontend on http://localhost:5173..."
cd frontend
npm run dev &
FRONTEND_PID=$!

echo ""
echo "✅ ToonMap is running!"
echo ""
echo "📡 API Server: http://localhost:8000"
echo "🌐 Web UI: http://localhost:5173"
echo "📚 API Docs: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop all servers"
echo ""

# Wait for user interrupt
trap "echo ''; echo '🛑 Stopping servers...'; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit 0" INT

wait
