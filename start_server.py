#!/usr/bin/env python3
"""
Simple server starter script for testing
"""

import uvicorn
import os
import sys

def start_server():
    """Start the FastAPI server"""
    print("🚀 Starting Enhanced UX Analyzer Server...")
    print("📍 Host: 127.0.0.1:8000")
    print("🔗 Health check: http://127.0.0.1:8000/health")
    print("🌐 Dashboard: http://127.0.0.1:8000/dashboard")
    print("📊 API Docs: http://127.0.0.1:8000/docs")
    print("-" * 50)
    
    try:
        # Import the app
        from enhanced_fastapi_server import app
        
        # Start server without reload to avoid import string issues
        uvicorn.run(
            app, 
            host="127.0.0.1", 
            port=8000, 
            reload=False,  # Disable reload for testing
            log_level="info"
        )
    except Exception as e:
        print(f"❌ Failed to start server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    start_server()
