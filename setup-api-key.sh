#!/bin/bash
# API Key Setup Script for UX Analyzer
# This script helps you configure your OpenAI API key

echo "🔧 UX Analyzer - API Key Setup"
echo "==============================="
echo ""

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "❌ .env file not found. Creating one..."
    cp .env.example .env 2>/dev/null || {
        echo "Creating .env file from template..."
        cat > .env << 'EOF'
# UX Analyzer Environment Configuration
# Add your OpenAI API key below

# OpenAI Configuration
OPENAI_API_KEY=your-openai-api-key-here

# Backend Configuration
BACKEND_HOST=localhost
BACKEND_PORT=8000

# Frontend Configuration  
FRONTEND_PORT=3000
VITE_API_BASE_URL=http://localhost:8000

# Development Mode
DEBUG=true
EOF
    }
fi

echo "📄 Current .env file status:"
if grep -q "your-openai-api-key-here" .env; then
    echo "   ❌ OpenAI API key not configured (placeholder found)"
else
    echo "   ✅ OpenAI API key appears to be configured"
fi

echo ""
echo "🔑 To set your OpenAI API key:"
echo "   1. Edit the .env file:"
echo "      nano .env"
echo ""
echo "   2. Replace 'your-openai-api-key-here' with your actual API key"
echo ""
echo "   3. Or export it directly in this terminal:"
echo "      export OPENAI_API_KEY=sk-your-actual-key-here"
echo ""

# Check current environment
current_key=$(echo $OPENAI_API_KEY)
if [ -z "$current_key" ]; then
    echo "   ❌ OPENAI_API_KEY not set in current environment"
else
    echo "   ✅ OPENAI_API_KEY is set in current environment"
fi

echo ""
echo "🧪 To test the setup:"
echo "   python3 validate_api_key.py"
echo ""
echo "🔍 Quick runtime test:"
echo "   python3 -c \"import os; print('API Key found:', bool(os.getenv('OPENAI_API_KEY')))\""
echo ""
echo "🚀 After setting the key, restart your servers:"
echo "   python3 enhanced_fastapi_server.py"
echo "   cd web-ui && npm run dev"
