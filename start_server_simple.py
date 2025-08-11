#!/usr/bin/env python3
import subprocess
import sys
import time

print("🚀 Starting FastAPI server...")

# Start uvicorn
process = subprocess.Popen([
    sys.executable, "-m", "uvicorn", 
    "enhanced_fastapi_server:app", 
    "--host", "127.0.0.1", 
    "--port", "8000"
], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)

# Wait a moment for startup
time.sleep(3)

# Check if it's running
if process.poll() is None:
    print("✅ Server started successfully!")
    print("📊 Server running on http://127.0.0.1:8000")
    print("🔍 Health check: http://127.0.0.1:8000/api/health")
else:
    print("❌ Server failed to start")
    stdout, stderr = process.communicate()
    print("Output:", stdout)
    print("Errors:", stderr)
