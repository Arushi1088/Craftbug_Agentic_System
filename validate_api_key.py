#!/usr/bin/env python3
"""
OpenAI API Key Validator
Standalone script to validate API key configuration
"""

import os
import sys

def validate_openai_api_key():
    """Validate OpenAI API key configuration"""
    print("🔑 OpenAI API Key Validation")
    print("=" * 30)
    
    # Load environment variables
    try:
        from dotenv import load_dotenv
        load_dotenv()
        load_dotenv("production.env")
        print("✅ Environment files loaded")
    except ImportError:
        print("⚠️ python-dotenv not available, using OS environment only")
    
    # Check API key
    api_key = os.getenv("OPENAI_API_KEY")
    
    if not api_key:
        print("❌ OPENAI_API_KEY not found in environment")
        print("\n🔧 Fix this by:")
        print("   1. Edit .env file: nano .env")
        print("   2. Set: OPENAI_API_KEY=sk-your-actual-key")
        print("   3. Or export: export OPENAI_API_KEY=sk-your-key")
        return False
    
    if api_key == "your-openai-api-key-here":
        print("❌ OPENAI_API_KEY still using placeholder value")
        print("\n🔧 Fix this by:")
        print("   1. Get key from: https://platform.openai.com/api-keys")
        print("   2. Replace placeholder in .env file")
        return False
    
    if not api_key.startswith("sk-"):
        print("❌ Invalid API key format (should start with 'sk-')")
        print(f"   Current value: {api_key[:10]}...")
        return False
    
    print(f"✅ OpenAI API Key Valid: {api_key[:8]}... (truncated)")
    
    # Test OpenAI import
    try:
        from openai import OpenAI
        print("✅ OpenAI package available")
        
        # Test client initialization (without actual API call)
        try:
            client = OpenAI(api_key=api_key)
            print("✅ OpenAI client can be initialized")
            return True
        except Exception as e:
            print(f"❌ OpenAI client initialization failed: {e}")
            return False
            
    except ImportError:
        print("❌ OpenAI package not installed")
        print("   Fix: pip install openai")
        return False

if __name__ == "__main__":
    success = validate_openai_api_key()
    sys.exit(0 if success else 1)
