#!/bin/bash

# One-command startup - just run this!
echo "🚀 Starting UX Analyzer System..."

cd /Users/arushitandon/Desktop/analyzer

# Kill any existing processes
echo "🧹 Cleaning up..."
lsof -ti:5173,8000,3001 | xargs kill -9 2>/dev/null || true
sleep 2

# Start backend
echo "🔧 Starting Backend..."
python -m uvicorn enhanced_fastapi_server:app --host 0.0.0.0 --port 8000 &
sleep 3

# Start frontend  
echo "🎨 Starting Frontend..."
cd web-ui
npx vite --port 5173 &
sleep 3

# Start mocks
echo "� Starting Mock Apps..."
cd ../demos  
python -m http.server 3001 &
sleep 3

echo ""
echo "✅ All servers started!"
echo "🌐 Open: http://localhost:5173"
echo ""
echo "Wait 10 seconds then open the URL above!"

# Keep running
wait
