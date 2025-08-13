#!/usr/bin/env python3
"""
Quick script to update the Gemini API key
"""

import os
import re

def update_gemini_key():
    """Update the Gemini API key in .env file"""
    
    print("🔑 GEMINI API KEY UPDATER")
    print("=" * 30)
    
    # Get the new key from user
    new_key = input("Enter your new Gemini API key: ").strip()
    
    if not new_key:
        print("❌ No key provided")
        return False
    
    if not new_key.startswith('AIza'):
        print("❌ Invalid key format. Gemini API keys start with 'AIza'")
        return False
    
    # Read the current .env file
    try:
        with open('.env', 'r') as f:
            content = f.read()
    except FileNotFoundError:
        print("❌ .env file not found")
        return False
    
    # Replace the existing GEMINI_API_KEY
    pattern = r'GEMINI_API_KEY=.*'
    replacement = f'GEMINI_API_KEY={new_key}'
    
    if re.search(pattern, content):
        new_content = re.sub(pattern, replacement, content)
    else:
        # Add the key if it doesn't exist
        new_content = content + f'\nGEMINI_API_KEY={new_key}'
    
    # Write back to .env
    with open('.env', 'w') as f:
        f.write(new_content)
    
    print("✅ Gemini API key updated in .env file")
    
    # Set environment variable for current session
    os.environ['GEMINI_API_KEY'] = new_key
    print("✅ Environment variable set for current session")
    
    # Test the key
    print("\n🧪 Testing the new key...")
    test_result = test_api_key(new_key)
    
    if test_result:
        print("🎉 New key is working!")
        return True
    else:
        print("❌ Key test failed. Please check your key and try again.")
        return False

def test_api_key(api_key):
    """Test if the API key works"""
    import requests
    
    url = "https://generativelanguage.googleapis.com/v1/models/gemini-1.5-pro:generateContent"
    headers = {"Content-Type": "application/json"}
    
    data = {
        "contents": [{"parts": [{"text": "Say 'Hello' if you can see this."}]}]
    }
    
    try:
        response = requests.post(f"{url}?key={api_key}", headers=headers, json=data, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            if 'candidates' in result and len(result['candidates']) > 0:
                text = result['candidates'][0]['content']['parts'][0]['text']
                print(f"✅ API test successful: {text}")
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
    update_gemini_key()
