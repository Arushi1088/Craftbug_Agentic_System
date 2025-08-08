#!/bin/bash

echo "🚀 Starting UX Analyzer Complete System..."
echo "📍 Working directory: $(pwd)"

# Kill any existing processes on our ports
echo "🧹 Cleaning up existing processes..."
lsof -ti:5173 | xargs kill -9 2>/dev/null || true
lsof -ti:8000 | xargs kill -9 2>/dev/null || true
lsof -ti:3001 | xargs kill -9 2>/dev/null || true

sleep 2

# Start backend server
echo "🔧 Starting Backend Server (port 8000)..."
cd /Users/arushitandon/Desktop/analyzer
python -m uvicorn enhanced_fastapi_server:app --host 0.0.0.0 --port 8000 --reload &
BACKEND_PID=$!

sleep 3

# Start frontend server
echo "🎨 Starting Frontend Server (port 5173)..."
cd /Users/arushitandon/Desktop/analyzer/web-ui
npx vite --port 5173 --host 0.0.0.0 &
FRONTEND_PID=$!

sleep 3

# Start mock apps server
echo "📱 Starting Mock Apps Server (port 3001)..."
cd /Users/arushitandon/Desktop/analyzer/demos
python -m http.server 3001 &
MOCKS_PID=$!

sleep 3

echo ""
echo "✅ All servers started successfully!"
echo ""
echo "🌐 Application URLs:"
echo "   Frontend:  http://localhost:5173"
echo "   Backend:   http://localhost:8000"
echo "   Mock Apps: http://localhost:3001"
echo ""
echo "🔧 Process IDs:"
echo "   Backend:  $BACKEND_PID"
echo "   Frontend: $FRONTEND_PID" 
echo "   Mocks:    $MOCKS_PID"
echo ""
echo "To stop all servers, run: kill $BACKEND_PID $FRONTEND_PID $MOCKS_PID"
echo ""
echo "🎯 Open http://localhost:5173 in your browser to use the application!"

# Keep script running
wait
