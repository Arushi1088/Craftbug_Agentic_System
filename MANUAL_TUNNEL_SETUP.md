# Quick Manual Setup for Cloudflare Tunnel

Since the terminal might be busy with the preview server, here are the manual steps:

## Terminal 1: Start Preview Server
```bash
cd /Users/arushitandon/Desktop/analyzer/web-ui
npm run build
npm run preview
```
This should show: `➜  Local:   http://localhost:4173/`

## Terminal 2: Install and Start Cloudflare Tunnel

### Install cloudflared (choose one method):

**Method A: Homebrew (recommended)**
```bash
brew install cloudflared
```

**Method B: Direct download**
```bash
# For Apple Silicon (M1/M2)
curl -L --output cloudflared.pkg https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-darwin-arm64.pkg
sudo installer -pkg cloudflared.pkg -target /
rm cloudflared.pkg

# For Intel Macs  
curl -L --output cloudflared.pkg https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-darwin-amd64.pkg
sudo installer -pkg cloudflared.pkg -target /
rm cloudflared.pkg
```

**Method C: Using npx (if available)**
```bash
npx cloudflared tunnel --url http://localhost:4173
```

### Start the tunnel:
```bash
cloudflared tunnel --url http://localhost:4173
```

## Step 3: Configure with Tunnel URL

After starting the tunnel, you'll get a URL like: `https://abc123.trycloudflare.com`

Copy this URL and update these files:

### Update vite.config.ts:
Add your specific tunnel URL to the allowedHosts array:
```typescript
preview: {
  allowedHosts: [
    '*.trycloudflare.com', 
    'leasing-gba-om-prior.trycloudflare.com',
    'abc123.trycloudflare.com'  // <-- Add your URL here
  ],
  port: 4173,
  host: true
}
```

### Update enhanced_fastapi_server.py:
Add your specific tunnel URL to the CORS allow_origins:
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
    "https://abc123.trycloudflare.com"  # <-- Add your URL here
],
```

## Step 4: Restart Servers

After updating the config files:

1. Stop the preview server (Ctrl+C in Terminal 1)
2. Stop the tunnel (Ctrl+C in Terminal 2)
3. Rebuild and restart:

```bash
# Terminal 1
cd web-ui
npm run build
npm run preview

# Terminal 2  
cloudflared tunnel --url http://localhost:4173
```

## Step 5: Test the Setup

1. Open the tunnel URL in your browser
2. Verify the app loads correctly
3. Test that scenarios load properly
4. Use this URL for ADO embedding

## Current Status

✅ **Vite config** already has wildcard support for `*.trycloudflare.com`
✅ **CORS config** already has wildcard support for `https://*.trycloudflare.com`
✅ **Preview port** is configured as 4173

You just need to add your specific tunnel URL to both configs for optimal reliability.
