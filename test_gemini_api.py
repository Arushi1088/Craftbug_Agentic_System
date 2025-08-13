#!/usr/bin/env python3
"""
Test script to verify Gemini API key and provide setup instructions
"""

import os
import requests
import json

def test_gemini_api():
    """Test the Gemini API key"""
    
    api_key = os.getenv('GEMINI_API_KEY')
    
    if not api_key:
        print("❌ GEMINI_API_KEY not found in environment")
        print("\n📋 To set up your Gemini API key:")
        print("1. Go to https://makersuite.google.com/app/apikey")
        print("2. Create a new API key")
        print("3. Run: export GEMINI_API_KEY='your-api-key-here'")
        print("4. Or add it to your .env file")
        return False
    
    print(f"🔑 Found API key: {api_key[:10]}...")
    
    # Test with a simple request
    url = "https://generativelanguage.googleapis.com/v1/models/gemini-1.5-pro:generateContent"
    
    headers = {
        "Content-Type": "application/json"
    }
    
    data = {
        "contents": [
            {
                "parts": [
                    {
                        "text": "Hello, please respond with 'API working' if you can see this message."
                    }
                ]
            }
        ]
    }
    
    try:
        print("🧪 Testing Gemini API...")
        response = requests.post(
            f"{url}?key={api_key}",
            headers=headers,
            json=data,
            timeout=10
        )
        
        print(f"📊 Response status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            if 'candidates' in result and len(result['candidates']) > 0:
                text = result['candidates'][0]['content']['parts'][0]['text']
                print(f"✅ API working! Response: {text}")
                return True
            else:
                print("❌ Unexpected response format")
                print(f"Response: {json.dumps(result, indent=2)}")
                return False
        else:
            print(f"❌ API error: {response.status_code}")
            print(f"Response: {response.text}")
            
            if "API key not valid" in response.text:
                print("\n🔧 Your API key appears to be invalid. Please:")
                print("1. Go to https://makersuite.google.com/app/apikey")
                print("2. Create a new API key")
                print("3. Make sure the Gemini API is enabled for your project")
                print("4. Update your .env file with the new key")
            
            return False
            
    except Exception as e:
        print(f"❌ Error testing API: {e}")
        return False

if __name__ == "__main__":
    success = test_gemini_api()
    if success:
        print("\n🎉 Gemini API is working correctly!")
    else:
        print("\n💡 Please fix the API key issue and try again.")
