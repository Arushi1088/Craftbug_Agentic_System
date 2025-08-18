#!/usr/bin/env python3
"""
Simple server startup script without any file watching or auto-reload
"""

import uvicorn
from enhanced_fastapi_server import app

if __name__ == "__main__":
    print("🚀 Starting Enhanced UX Analyzer FastAPI Server (NO RELOAD)...")
    print("📝 This server will NOT auto-reload on file changes")
    print("🔧 To restart, manually stop and start the server")
    
    uvicorn.run(
        app,
        host="127.0.0.1",
        port=8000,
        reload=False,
        log_level="info"
    )

