#!/usr/bin/env python3
import os
import sys
from pathlib import Path

# Add the application directory to the Python path
app_dir = Path(__file__).parent
sys.path.insert(0, str(app_dir))

# Import the Flask application
try:
    from github_agent_server import app as application
    print("Successfully imported github_agent_server")
except ImportError as e:
    print(f"Import error: {e}")
    print(f"Current directory: {os.getcwd()}")
    print(f"Files in directory: {os.listdir('.')}")
    sys.exit(1)

if __name__ == "__main__":
    application.run(host='0.0.0.0', port=8000)
