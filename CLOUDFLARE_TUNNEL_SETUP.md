# Cloudflare Tunnel Setup for ADO Embedding

This guide helps you set up a Cloudflare tunnel to embed the UI in Azure DevOps.

## Prerequisites

1. Preview server should be built and running on port 4173
2. Backend server should be running on port 8000
3. Cloudflared should be available

## Step-by-Step Instructions

### 1. Install cloudflared (if not already installed)

**Option A: Using Homebrew (recommended)**
```bash
brew install cloudflared
```

**Option B: Using NPX (alternative)**
```bash
npx cloudflared tunnel --url http://localhost:4173
```

**Option C: Direct download for macOS**
```bash
# For Apple Silicon (M1/M2)
curl -L --output cloudflared.pkg https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-darwin-arm64.pkg

# For Intel Macs
curl -L --output cloudflared.pkg https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-darwin-amd64.pkg

sudo installer -pkg cloudflared.pkg -target /
rm cloudflared.pkg
```

### 2. Build and start preview server

```bash
cd web-ui
npm run build
npm run preview  # Runs on http://localhost:4173
```

### 3. Start Cloudflare tunnel (in new terminal)

```bash
cloudflared tunnel --url http://localhost:4173
```

Or using npx:
```bash
npx cloudflared tunnel --url http://localhost:4173
```

### 4. Configure the tunnel URL

After starting the tunnel, you'll get a URL like: `https://abc123.trycloudflare.com`

**Add to vite.config.ts:**
```typescript
export default defineConfig({
  // ... existing config
  preview: {
    allowedHosts: [
      '*.trycloudflare.com', 
      'leasing-gba-om-prior.trycloudflare.com',
      'abc123.trycloudflare.com'  // Add your specific tunnel URL
    ],
    port: 4173,
    host: true
  }
})
```

**Add to enhanced_fastapi_server.py CORS:**
```python
allow_origins=[
    "http://localhost:3000", 
    "http://localhost:3001", 
    "http://localhost:3002", 
    "http://localhost:3003", 
    "http://localhost:3004",
    "http://localhost:5173",  # Vite dev server
    "https://dev.azure.com",
    "https://*.trycloudflare.com",
    "https://leasing-gba-om-prior.trycloudflare.com",
    "https://abc123.trycloudflare.com"  # Add your specific tunnel URL
],
```

### 5. Restart servers

```bash
# Stop preview server (Ctrl+C)
# Stop tunnel (Ctrl+C)

# Rebuild and restart
npm run build
npm run preview

# In new terminal, restart tunnel
cloudflared tunnel --url http://localhost:4173
```

### 6. Test the tunnel

1. Open the tunnel URL in your browser
2. Verify the app loads correctly
3. Test API connectivity
4. Use this URL for ADO embedding

## Current Configuration Status

✅ **Vite config** already has wildcard cloudflare support:
- `*.trycloudflare.com` in allowedHosts
- Preview port 4173 configured

✅ **CORS config** already has cloudflare support:
- `https://*.trycloudflare.com` in allow_origins
- Specific tunnel URL can be added

## Quick Commands

```bash
# Terminal 1: Start preview
cd web-ui && npm run build && npm run preview

# Terminal 2: Start tunnel  
cloudflared tunnel --url http://localhost:4173

# Terminal 3: Start backend (if not running)
python3 enhanced_fastapi_server.py
```
