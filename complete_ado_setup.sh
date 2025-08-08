#!/bin/bash

# Complete Cloudflare Tunnel Setup for ADO Embedding
# This script handles the entire process automatically

set -e  # Exit on any error

echo "🌐 Cloudflare Tunnel Setup for ADO Embedding"
echo "============================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Check if we're in the right directory
if [ ! -f "enhanced_fastapi_server.py" ] || [ ! -d "web-ui" ]; then
    print_error "Please run this script from the analyzer root directory"
    exit 1
fi

print_status "Found project files"

# Step 1: Check for cloudflared
print_info "Step 1: Checking for cloudflared..."

if command -v cloudflared >/dev/null 2>&1; then
    print_status "cloudflared is already installed"
elif command -v brew >/dev/null 2>&1; then
    print_info "Installing cloudflared via Homebrew..."
    brew install cloudflared
    print_status "cloudflared installed successfully"
else
    print_warning "Homebrew not found. You'll need to install cloudflared manually:"
    echo ""
    echo "For Apple Silicon Macs:"
    echo "curl -L --output cloudflared.pkg https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-darwin-arm64.pkg"
    echo ""
    echo "For Intel Macs:"
    echo "curl -L --output cloudflared.pkg https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-darwin-amd64.pkg"
    echo ""
    echo "Then run: sudo installer -pkg cloudflared.pkg -target /"
    echo ""
    echo "After installation, run this script again."
    exit 1
fi

# Step 2: Build the frontend
print_info "Step 2: Building frontend..."
cd web-ui
npm run build
print_status "Frontend built successfully"

# Step 3: Start preview server in background
print_info "Step 3: Starting preview server..."
npm run preview &
PREVIEW_PID=$!
echo "Preview server PID: $PREVIEW_PID"

# Wait for server to start
sleep 3

# Check if server is running
if curl -s http://localhost:4173 >/dev/null; then
    print_status "Preview server is running on http://localhost:4173"
else
    print_error "Preview server failed to start"
    kill $PREVIEW_PID 2>/dev/null || true
    exit 1
fi

# Step 4: Start tunnel
print_info "Step 4: Starting Cloudflare tunnel..."
echo ""
print_warning "IMPORTANT: Copy the tunnel URL and follow these steps:"
echo ""
echo "1. 📋 Copy the https://<something>.trycloudflare.com URL from below"
echo "2. 🔧 Add it to web-ui/vite.config.ts in preview.allowedHosts array"
echo "3. 🔧 Add it to enhanced_fastapi_server.py in CORS allow_origins"
echo "4. 🔄 Restart this script after updating the config files"
echo ""
echo "Example:"
echo "  allowedHosts: ['*.trycloudflare.com', 'your-tunnel-here.trycloudflare.com']"
echo "  \"https://your-tunnel-here.trycloudflare.com\""
echo ""
print_info "Press Ctrl+C to stop both servers when done configuring"
echo "============================================="

# Cleanup function
cleanup() {
    print_info "Stopping servers..."
    kill $PREVIEW_PID 2>/dev/null || true
    print_status "Cleanup complete"
}

# Set trap for cleanup
trap cleanup EXIT

# Start the tunnel
cd ..
cloudflared tunnel --url http://localhost:4173
