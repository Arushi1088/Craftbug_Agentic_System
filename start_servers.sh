#!/bin/bash

echo "🚀 Starting UX Analyzer Servers..."

# Kill existing processes
echo "Stopping existing servers..."
pkill -f "uvicorn.*8000" 2>/dev/null
pkill -f "vite.*8080" 2>/dev/null
sleep 2

# Start backend
echo "Starting backend API on port 8000..."
cd /Users/arushitandon/Desktop/analyzer
python3 -m uvicorn enhanced_fastapi_server:app --host 127.0.0.1 --port 8000 &
BACKEND_PID=$!

# Wait for backend to start
sleep 3

# Start frontend
echo "Starting frontend on port 8080..."
cd /Users/arushitandon/Desktop/analyzer/web-ui
npm run dev &
FRONTEND_PID=$!

# Wait for frontend to start
sleep 3

echo "✅ Servers started!"
echo "Backend API: http://127.0.0.1:8000"
echo "Frontend Dashboard: http://127.0.0.1:8080"
echo ""
echo "Backend PID: $BACKEND_PID"
echo "Frontend PID: $FRONTEND_PID"
echo ""
echo "To stop servers: pkill -f 'uvicorn.*8000' && pkill -f 'vite.*8080'"
