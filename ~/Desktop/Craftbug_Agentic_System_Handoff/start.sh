#!/bin/bash

# Craftbug Agentic System - Startup Script
echo "🚀 Starting Craftbug Agentic System..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies if needed
if [ ! -f "venv/lib/python*/site-packages/fastapi" ]; then
    echo "📥 Installing Python dependencies..."
    pip install -r requirements.txt
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "⚠️  .env file not found!"
    echo "📝 Please copy .env.example to .env and add your OpenAI API key"
    echo "   cp .env.example .env"
    echo "   nano .env"
    exit 1
fi

# Check if web-ui node_modules exists
if [ ! -d "web-ui/node_modules" ]; then
    echo "📦 Installing frontend dependencies..."
    cd web-ui
    npm install
    cd ..
fi

# Create necessary directories
mkdir -p screenshots reports telemetry_output

echo "✅ System ready!"
echo ""
echo "🌐 Starting services..."
echo "   Backend: http://127.0.0.1:8000"
echo "   Frontend: http://127.0.0.1:8080"
echo ""
echo "📋 To start manually:"
echo "   Terminal 1: python3 enhanced_fastapi_server.py"
echo "   Terminal 2: cd web-ui && npm run dev"
echo ""
echo "🔍 To test: python3 test_screenshot_flow.py"
echo ""
echo "Press Ctrl+C to stop"
echo ""

# Start backend in background
echo "🔧 Starting backend server..."
python3 enhanced_fastapi_server.py &
BACKEND_PID=$!

# Wait a moment for backend to start
sleep 3

# Start frontend
echo "🎨 Starting frontend..."
cd web-ui
npm run dev &
FRONTEND_PID=$!
cd ..

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "🛑 Stopping services..."
    kill $BACKEND_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    echo "✅ Services stopped"
    exit 0
}

# Trap Ctrl+C and call cleanup
trap cleanup SIGINT

# Wait for background processes
wait
