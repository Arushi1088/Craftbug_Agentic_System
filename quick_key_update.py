#!/usr/bin/env python3
"""
Quick script to update Gemini API key
"""

import os
import sys

def update_key():
    print("🔑 QUICK GEMINI API KEY UPDATE")
    print("=" * 35)
    print()
    
    # Get new key from user
    new_key = input("Paste your new Gemini API key: ").strip()
    
    if not new_key:
        print("❌ No key provided")
        return False
    
    if not new_key.startswith("AIza"):
        print("❌ Invalid key format")
        return False
    
    # Update .env file
    with open('.env', 'r') as f:
        content = f.read()
    
    # Replace the key
    import re
    new_content = re.sub(
        r'GEMINI_API_KEY=.*',
        f'GEMINI_API_KEY={new_key}',
        content
    )
    
    with open('.env', 'w') as f:
        f.write(new_content)
    
    print(f"✅ Updated .env with new key: {new_key[:10]}...")
    
    # Test the key
    print("\n🧪 Testing new key...")
    os.environ['GEMINI_API_KEY'] = new_key
    
    try:
        import requests
        
        url = "https://generativelanguage.googleapis.com/v1/models/gemini-1.5-pro:generateContent"
        headers = {"Content-Type": "application/json"}
        data = {
            "contents": [{"parts": [{"text": "Hello, respond with 'working' if you can see this."}]}]
        }
        
        response = requests.post(f"{url}?key={new_key}", headers=headers, json=data, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            if 'candidates' in result and len(result['candidates']) > 0:
                text = result['candidates'][0]['content']['parts'][0]['text']
                print(f"✅ API working! Response: {text}")
                print("\n🎉 New key is working! Restart the server to use it.")
                return True
            else:
                print("❌ Unexpected response format")
                return False
        else:
            print(f"❌ API error: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = update_key()
    if success:
        print("\n🚀 Ready to use real Gemini fixes!")
    else:
        print("\n💡 Please check your key and try again.")
