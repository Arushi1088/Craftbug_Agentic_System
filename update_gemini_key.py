#!/usr/bin/env python3
"""
Simple script to update the Gemini API key
"""

import os
import sys

def update_gemini_key():
    """Update the Gemini API key"""
    
    print("🔑 GEMINI API KEY UPDATE")
    print("=" * 30)
    print()
    
    # Get the new API key from user
    new_key = input("Please paste your new Gemini API key: ").strip()
    
    if not new_key:
        print("❌ No API key provided")
        return False
    
    if not new_key.startswith("AIza"):
        print("❌ Invalid API key format. Gemini API keys should start with 'AIza'")
        return False
    
    # Update .env file
    env_file = ".env"
    
    # Read current .env file
    if os.path.exists(env_file):
        with open(env_file, 'r') as f:
            lines = f.readlines()
    else:
        lines = []
    
    # Find and replace or add GEMINI_API_KEY
    key_found = False
    for i, line in enumerate(lines):
        if line.startswith("GEMINI_API_KEY="):
            lines[i] = f"GEMINI_API_KEY={new_key}\n"
            key_found = True
            break
    
    if not key_found:
        lines.append(f"GEMINI_API_KEY={new_key}\n")
    
    # Write back to .env file
    with open(env_file, 'w') as f:
        f.writelines(lines)
    
    print(f"✅ Updated .env file with new API key: {new_key[:10]}...")
    
    # Set environment variable for current session
    os.environ['GEMINI_API_KEY'] = new_key
    print("✅ Set environment variable for current session")
    
    # Test the new key
    print("\n🧪 Testing new API key...")
    
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
                print("\n🎉 Your Gemini API is now ready!")
                print("   The 'Fix with Agent' functionality should work now.")
                return True
            else:
                print("❌ Unexpected response format")
                return False
        else:
            print(f"❌ API error: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing API: {e}")
        return False

if __name__ == "__main__":
    success = update_gemini_key()
    if success:
        print("\n🚀 Ready to use Gemini AI fixes!")
    else:
        print("\n💡 Please check your API key and try again.")
