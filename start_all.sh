#!/bin/bash

# UX Analyzer System Startup Script
# This script starts all required servers for the UX Analyzer dashboard

echo "🚀 Starting UX Analyzer System..."
echo "=================================="

# Function to check if a port is in use
check_port() {
    local port=$1
    if lsof -ti:$port > /dev/null 2>&1; then
        return 0  # Port is in use
    else
        return 1  # Port is free
    fi
}

# Function to kill process on port
kill_port() {
    local port=$1
    echo "🔄 Killing existing process on port $port..."
    lsof -ti:$port | xargs kill -9 2>/dev/null || true
    sleep 2
}

# Change to the analyzer directory
cd /Users/arushitandon/Desktop/analyzer

echo "📡 Starting Backend API (port 8000)..."
if check_port 8000; then
    echo "✅ Backend already running on port 8000"
else
    echo "🔧 Starting FastAPI backend..."
    python3 -m uvicorn enhanced_fastapi_server:app --host 127.0.0.1 --port 8000 &
    sleep 5
fi

echo "🎨 Starting Frontend Dashboard (port 8080)..."
if check_port 8080; then
    echo "🔄 Restarting frontend on port 8080..."
    kill_port 8080
fi
echo "🔧 Starting Vite dev server..."
cd web-ui
npm run dev -- --host 127.0.0.1 --port 8080 --force &
cd ..
sleep 3

echo "📱 Starting Mock Apps Server (port 4174)..."
if check_port 4174; then
    echo "🔄 Restarting mock apps on port 4174..."
    kill_port 4174
fi
echo "🔧 Starting HTTP server for mock apps..."
python3 -m http.server 4174 --directory web-ui/dist &
sleep 2

echo ""
echo "✅ System Startup Complete!"
echo "========================="
echo ""
echo "🔗 Access URLs:"
echo "   Dashboard: http://127.0.0.1:8080/"
echo "   Backend API: http://127.0.0.1:8000/"
echo "   Mock Apps: http://localhost:4174/"
echo ""
echo "🧪 Test Features:"
echo "   • Select 'Mock App Scenario' analysis mode"
echo "   • Choose 'Word' as target app"
echo "   • All 6 Word scenarios available (1.1-1.6)"
echo "   • Real UX analysis with actual findings"
echo ""
echo "📊 Check system status: ./check_servers.sh"
echo ""
