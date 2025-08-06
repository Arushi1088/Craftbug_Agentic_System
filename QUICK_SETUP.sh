#!/bin/bash
# 🚀 UX Analyzer - Quick Setup Script for Developers

echo "🎯 UX Analyzer - Quick Setup Script"
echo "===================================="
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed."
    exit 1
fi

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is required but not installed."
    exit 1
fi

echo "✅ Python 3 and Node.js are installed"
echo ""

# Backend setup
echo "🔧 Setting up Backend (Python/FastAPI)..."
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
echo "✅ Backend dependencies installed"
echo ""

# Frontend setup
echo "🔧 Setting up Frontend (React/Vite)..."
cd web-ui
npm install
echo "✅ Frontend dependencies installed"
cd ..
echo ""

echo "🎉 Setup Complete!"
echo ""
echo "🚀 To start the application:"
echo "1. Backend:  python3 production_server.py"
echo "2. Frontend: cd web-ui && npm run dev"
echo "3. Open:     http://localhost:3000"
echo ""
echo "📚 See DEVELOPER_HANDOFF.md for detailed documentation"
