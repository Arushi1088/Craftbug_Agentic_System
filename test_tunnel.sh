#!/bin/bash

echo "🌐 Testing Cloudflare Tunnel with npx..."

# Check if we can use npx cloudflared
if npx cloudflared --help > /dev/null 2>&1; then
    echo "✅ npx cloudflared is available"
    echo "🚀 Starting tunnel for localhost:4173..."
    echo ""
    echo "📋 Instructions:"
    echo "1. Copy the tunnel URL that appears below"
    echo "2. Add it to vite.config.ts allowedHosts"  
    echo "3. Add it to CORS in enhanced_fastapi_server.py"
    echo "4. Restart the preview server"
    echo ""
    echo "Press Ctrl+C to stop the tunnel"
    echo "=============================================="
    
    npx cloudflared tunnel --url http://localhost:4173
else
    echo "❌ npx cloudflared not available"
    echo "📦 Please install cloudflared using one of these methods:"
    echo ""
    echo "Method 1 - Homebrew (recommended):"
    echo "  brew install cloudflared"
    echo ""
    echo "Method 2 - Direct download:"
    echo "  See CLOUDFLARE_TUNNEL_SETUP.md for detailed instructions"
    echo ""
    echo "Then run: cloudflared tunnel --url http://localhost:4173"
fi
