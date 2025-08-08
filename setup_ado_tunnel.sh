#!/bin/bash

# Cloudflare Tunnel Setup for ADO Embedding
# This script sets up a tunnel for embedding the UI in Azure DevOps

echo "🌐 Setting up Cloudflare Tunnel for ADO Embedding..."
echo "=============================================="

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Install cloudflared if not present
if ! command_exists cloudflared; then
    echo "📦 Installing cloudflared..."
    
    if command_exists brew; then
        echo "   Using Homebrew..."
        brew install cloudflared
    else
        echo "   Using direct download..."
        # For macOS ARM64 (Apple Silicon)
        if [[ $(uname -m) == "arm64" ]]; then
            curl -L --output cloudflared.pkg https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-darwin-arm64.pkg
        else
            curl -L --output cloudflared.pkg https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-darwin-amd64.pkg
        fi
        sudo installer -pkg cloudflared.pkg -target /
        rm cloudflared.pkg
    fi
else
    echo "✅ cloudflared is already installed"
fi

# Step 1: Build the preview
echo ""
echo "🔧 Step 1: Building preview..."
cd web-ui
npm run build

# Step 2: Start preview server in background
echo ""
echo "🚀 Step 2: Starting preview server on port 4173..."
npm run preview &
PREVIEW_PID=$!
sleep 3

# Step 3: Start tunnel
echo ""
echo "🌐 Step 3: Starting Cloudflare tunnel..."
echo "📋 Copy the tunnel URL from below and follow these steps:"
echo ""
echo "   1. Copy the https://<something>.trycloudflare.com URL"
echo "   2. Add it to vite.config.ts preview.allowedHosts"
echo "   3. Add it to CORS in enhanced_fastapi_server.py"
echo "   4. Restart both servers"
echo ""
echo "Press Ctrl+C to stop both servers when done"
echo "=============================================="

# Start tunnel
cloudflared tunnel --url http://localhost:4173

# Cleanup when script exits
trap "kill $PREVIEW_PID 2>/dev/null" EXIT
