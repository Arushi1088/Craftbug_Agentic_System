#!/bin/bash

# Script to start Cloudflare tunnel for ADO embedding
echo "🌐 Starting Cloudflare Tunnel Setup for ADO Embedding..."

# Check current directory
if [ ! -f "enhanced_fastapi_server.py" ]; then
    echo "❌ Please run this script from the analyzer root directory"
    echo "   Current directory: $(pwd)"
    echo "   Expected files: enhanced_fastapi_server.py, web-ui/"
    exit 1
fi

# Check if preview server is running
if ! curl -s http://localhost:4173 >/dev/null 2>&1; then
    echo "⚠️  Preview server not detected on port 4173"
    echo "📋 Please start it first:"
    echo "   cd web-ui"
    echo "   npm run build"
    echo "   npm run preview"
    echo ""
    read -p "Press Enter when preview server is running on port 4173..."
fi

# Check if cloudflared is installed
if ! command -v cloudflared &> /dev/null; then
    echo "❌ cloudflared is not installed. Installing..."
    
    # Install cloudflared on macOS
    if command -v brew &> /dev/null; then
        echo "📦 Installing cloudflared via Homebrew..."
        brew install cloudflared
    else
        echo "📦 Installing cloudflared via direct download..."
        # Detect architecture
        if [[ $(uname -m) == "arm64" ]]; then
            curl -L --output cloudflared.pkg https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-darwin-arm64.pkg
        else
            curl -L --output cloudflared.pkg https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-darwin-amd64.pkg
        fi
        sudo installer -pkg cloudflared.pkg -target /
        rm cloudflared.pkg
    fi
fi

echo "✅ cloudflared is available"
echo "🚀 Starting tunnel for http://localhost:4173..."
echo ""
echo "📋 IMPORTANT: After tunnel starts, copy the tunnel URL and:"
echo "   1. Add it to web-ui/vite.config.ts allowedHosts array"
echo "   2. Add it to enhanced_fastapi_server.py CORS allow_origins" 
echo "   3. Restart both preview server and this tunnel"
echo ""
echo "Press Ctrl+C to stop the tunnel"
echo "============================================="

# Start the tunnel
cloudflared tunnel --url http://localhost:4173
