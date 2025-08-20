#!/usr/bin/env python3
"""
Environment Variable Loader
==========================

Loads environment variables from .env file for authentication tokens.
"""

import os
from pathlib import Path

def load_env_file():
    """Load environment variables from .env file"""
    env_file = Path('.env')
    
    if env_file.exists():
        print("🔍 Loading environment variables from .env file...")
        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key] = value
                    print(f"   Loaded: {key}")
        print("✅ Environment variables loaded!")
    else:
        print("⚠️ No .env file found")

def check_tokens():
    """Check if authentication tokens are available"""
    figma_token = os.getenv('FIGMA_ACCESS_TOKEN')
    ado_token = os.getenv('AZURE_DEVOPS_PAT')
    
    print("\n🔐 Token Status:")
    print(f"   Figma token: {'✅ Set' if figma_token else '❌ Not set'}")
    if figma_token:
        print(f"      Value: {figma_token[:10]}...")
    
    print(f"   ADO token: {'✅ Set' if ado_token else '❌ Not set'}")
    if ado_token:
        print(f"      Value: {ado_token[:10]}...")
    
    return figma_token is not None, ado_token is not None

if __name__ == "__main__":
    load_env_file()
    check_tokens()
