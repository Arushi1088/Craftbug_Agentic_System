#!/bin/bash

# Simple server startup script with better error handling

echo "🚀 Starting UX Analyzer System (Simple Version)..."

# Function to check if a port is available
check_port() {
    local port=$1
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null ; then
        echo "❌ Port $port is already in use"
        return 1
    else
        echo "✅ Port $port is available"
        return 0
    fi
}

# Function to wait for server to start
wait_for_server() {
    local port=$1
    local name=$2
    local max_attempts=10
    local attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        if curl -s http://localhost:$port >/dev/null 2>&1; then
            echo "✅ $name is running on port $port"
            return 0
        fi
        echo "⏳ Waiting for $name (attempt $attempt/$max_attempts)..."
        sleep 2
        attempt=$((attempt + 1))
    done
    
    echo "❌ $name failed to start on port $port"
    return 1
}

# Check prerequisites
echo "🔍 Checking prerequisites..."

if ! command -v python &> /dev/null; then
    echo "❌ Python not found"
    exit 1
fi

if ! command -v node &> /dev/null; then
    echo "❌ Node.js not found"
    exit 1
fi

if ! command -v npm &> /dev/null; then
    echo "❌ npm not found"
    exit 1
fi

echo "✅ All prerequisites found"

# Check ports
echo "🔍 Checking ports..."
check_port 8000 || exit 1
check_port 5173 || exit 1
check_port 3001 || exit 1

# Start backend
echo "🔧 Starting Backend Server..."
cd /Users/arushitandon/Desktop/analyzer
python -m uvicorn enhanced_fastapi_server:app --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!
echo "Backend PID: $BACKEND_PID"

# Wait for backend
sleep 5

# Start frontend
echo "🎨 Starting Frontend Server..."
cd /Users/arushitandon/Desktop/analyzer/web-ui
npx vite --port 5173 --host 0.0.0.0 &
FRONTEND_PID=$!
echo "Frontend PID: $FRONTEND_PID"

# Wait for frontend
sleep 5

# Start mock apps
echo "📱 Starting Mock Apps Server..."
cd /Users/arushitandon/Desktop/analyzer/demos
python -m http.server 3001 &
MOCKS_PID=$!
echo "Mock Apps PID: $MOCKS_PID"

# Wait for all servers
sleep 5

echo ""
echo "🎯 Server Status Check:"
wait_for_server 8000 "Backend"
wait_for_server 5173 "Frontend" 
wait_for_server 3001 "Mock Apps"

echo ""
echo "🌐 Application URLs:"
echo "   Frontend:  http://localhost:5173"
echo "   Backend:   http://localhost:8000/docs"
echo "   Mock Apps: http://localhost:3001"
echo ""
echo "🛑 To stop all servers: kill $BACKEND_PID $FRONTEND_PID $MOCKS_PID"
echo ""

# Keep script running
read -p "Press Enter to stop all servers..."
kill $BACKEND_PID $FRONTEND_PID $MOCKS_PID 2>/dev/null
