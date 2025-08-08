#!/bin/bash

# Git commit script for Cloudflare tunnel setup
echo "🔄 Committing Cloudflare tunnel setup to git..."

cd /Users/arushitandon/Desktop/analyzer

echo "📋 Adding files to git..."
git add .

echo "💾 Committing with detailed message..."
git commit -m "Add Cloudflare tunnel setup for ADO embedding

✅ Cloudflare Tunnel Infrastructure:
- start_cloudflare_tunnel.sh: Enhanced tunnel startup script with error checking
- complete_ado_setup.sh: Automated full setup script  
- setup_ado_tunnel.sh: Alternative tunnel setup script
- test_tunnel.sh: Simple tunnel testing script

✅ Documentation:
- CLOUDFLARE_TUNNEL_SETUP.md: Comprehensive setup guide
- MANUAL_TUNNEL_SETUP.md: Quick manual instructions
- TUNNEL_SETUP_COMPLETE.md: Status summary and overview
- MANUAL_EXECUTION_STEPS.md: Step-by-step execution guide

✅ Configuration Status:
- vite.config.ts: Already configured with *.trycloudflare.com support
- enhanced_fastapi_server.py: Already configured with CORS for cloudflare domains
- Preview server setup for port 4173
- Automatic cloudflared installation via Homebrew

✅ Tunnel Verified Working:
- Successfully created tunnel: https://operates-circle-heroes-roommates.trycloudflare.com
- Public HTTPS endpoint ready for ADO embedding
- All infrastructure tested and operational

This completes Step 5 of the ADO embedding setup with full tunnel infrastructure."

echo "🚀 Pushing to remote repository..."
git push origin feature/ado-mock-scenarios

echo "✅ Git commit and push complete!"
git log --oneline -1
