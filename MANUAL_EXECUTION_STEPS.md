# 🚀 Manual Steps to Start Cloudflare Tunnel

Since the terminal is busy with running servers, here are the manual steps:

## Step 1: Open a New Terminal Window

Open a fresh terminal window/tab (not in VS Code) and navigate to your project:

```bash
cd /Users/arushitandon/Desktop/analyzer
```

## Step 2: Make Scripts Executable

Run this command to make the scripts executable:

```bash
chmod +x start_cloudflare_tunnel.sh complete_ado_setup.sh setup_ado_tunnel.sh
```

## Step 3: Start Preview Server (if not running)

If you don't have the preview server running yet:

```bash
cd web-ui
npm run build
npm run preview
```

You should see: `➜  Local:   http://localhost:4173/`

## Step 4: Start Tunnel (in new terminal)

Open another terminal window and run:

```bash
cd /Users/arushitandon/Desktop/analyzer
./start_cloudflare_tunnel.sh
```

Or manually:

```bash
# Install cloudflared (choose one)
brew install cloudflared
# OR
npx cloudflared tunnel --url http://localhost:4173

# Start tunnel
cloudflared tunnel --url http://localhost:4173
```

## Step 5: Copy Tunnel URL

You'll see output like:
```
2025-08-09T... INF Thank you for trying Cloudflare Tunnel. Connections to your hostname are available at the following URLs:
2025-08-09T... INF ┌────────────────────────────────────────┐
2025-08-09T... INF │ https://abc123.trycloudflare.com │
2025-08-09T... INF └────────────────────────────────────────┘
```

**Copy the URL:** `https://abc123.trycloudflare.com`

## Step 6: Update Config Files (Optional but Recommended)

### Update vite.config.ts:
Add your specific tunnel URL:
```typescript
preview: {
  allowedHosts: [
    '*.trycloudflare.com', 
    'leasing-gba-om-prior.trycloudflare.com',
    'abc123.trycloudflare.com'  // Add your URL here
  ],
  port: 4173,
  host: true
}
```

### Update enhanced_fastapi_server.py:
Add your specific tunnel URL to CORS:
```python
allow_origins=[
    "http://localhost:3000", 
    "http://localhost:3001", 
    "http://localhost:3002", 
    "http://localhost:3003", 
    "http://localhost:3004",
    "http://localhost:5173",
    "https://dev.azure.com",
    "https://*.trycloudflare.com",
    "https://leasing-gba-om-prior.trycloudflare.com",
    "https://abc123.trycloudflare.com"  // Add your URL here
],
```

## Step 7: Test the Tunnel

1. Open the tunnel URL in your browser
2. Verify the UI loads correctly
3. Test scenario loading functionality
4. Ready for ADO embedding!

## Quick Commands Summary

```bash
# Terminal 1: Preview Server
cd /Users/arushitandon/Desktop/analyzer/web-ui
npm run build && npm run preview

# Terminal 2: Tunnel
cd /Users/arushitandon/Desktop/analyzer
chmod +x start_cloudflare_tunnel.sh
./start_cloudflare_tunnel.sh

# Or manual tunnel:
cloudflared tunnel --url http://localhost:4173
```

## Troubleshooting

- **"Command not found: cloudflared"** → Run `brew install cloudflared`
- **"Connection refused"** → Make sure preview server is running on port 4173
- **"Access denied"** → The wildcard `*.trycloudflare.com` in configs should handle this

---
**Status**: Ready to execute manually in new terminal windows! 🎉
