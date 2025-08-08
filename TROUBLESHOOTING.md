# 🔧 Server Startup Troubleshooting Guide

## Current Issue: Unable to start servers

### Step 1: Check Prerequisites

Open a new Terminal and run these commands one by one:

```bash
# Check if you're in the right directory
cd /Users/arushitandon/Desktop/analyzer
pwd

# Check Python
python --version
python -c "import fastapi; print('FastAPI available')"

# Check Node/npm
node --version
npm --version

# Check if web-ui directory exists and has dependencies
ls -la web-ui/
ls -la web-ui/node_modules/ | head -10
```

### Step 2: Manual Server Startup (One by One)

#### Start Backend Server:
```bash
cd /Users/arushitandon/Desktop/analyzer
python -c "import enhanced_fastapi_server; print('Server module can be imported')"
python -m uvicorn enhanced_fastapi_server:app --host 0.0.0.0 --port 8000
```

#### Start Frontend Server (in a new terminal):
```bash
cd /Users/arushitandon/Desktop/analyzer/web-ui
npm list vite
npx vite --version
npx vite --port 5173
```

#### Start Mock Apps Server (in a third terminal):
```bash
cd /Users/arushitandon/Desktop/analyzer/demos
ls -la
python -m http.server 3001
```

### Step 3: Check for Common Issues

#### A. Port conflicts:
```bash
lsof -ti:5173 | xargs kill -9
lsof -ti:8000 | xargs kill -9  
lsof -ti:3001 | xargs kill -9
```

#### B. Permission issues:
```bash
chmod +x /Users/arushitandon/Desktop/analyzer/start_all_servers.sh
```

#### C. Node modules corruption:
```bash
cd /Users/arushitandon/Desktop/analyzer/web-ui
rm -rf node_modules package-lock.json
npm install
```

#### D. Python environment issues:
```bash
cd /Users/arushitandon/Desktop/analyzer
pip install -r requirements.txt
```

### Step 4: Test Each Server Individually

1. **Backend Test**: http://localhost:8000/docs
2. **Frontend Test**: http://localhost:5173
3. **Mock Apps Test**: http://localhost:3001

### Step 5: If All Else Fails

Use the simple startup commands in separate terminals:

**Terminal 1:**
```bash
cd /Users/arushitandon/Desktop/analyzer && python -m uvicorn enhanced_fastapi_server:app --port 8000
```

**Terminal 2:** 
```bash
cd /Users/arushitandon/Desktop/analyzer/web-ui && npx vite --port 5173
```

**Terminal 3:**
```bash
cd /Users/arushitandon/Desktop/analyzer/demos && python -m http.server 3001
```

## Expected Output

When working correctly, you should see:
- Backend: "Uvicorn running on http://0.0.0.0:8000"
- Frontend: "Local: http://localhost:5173/"
- Mock Apps: "Serving HTTP on :: port 3001"

## Report Back

Please run the Step 1 commands and let me know what output you get!
