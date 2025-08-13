#!/usr/bin/env python3
"""
Comprehensive Gemini API setup and testing script
"""

import os
import requests
import json
import subprocess
import sys

def print_setup_instructions():
    """Print detailed setup instructions"""
    print("🚀 GEMINI API SETUP INSTRUCTIONS")
    print("=" * 50)
    print()
    print("📋 Step 1: Get a new API key")
    print("1. Go to: https://makersuite.google.com/app/apikey")
    print("2. Sign in with your Google account")
    print("3. Click 'Create API Key'")
    print("4. Copy the new API key")
    print()
    print("📋 Step 2: Enable Gemini API")
    print("1. Go to: https://console.cloud.google.com/")
    print("2. Select or create a project")
    print("3. Go to 'APIs & Services' > 'Library'")
    print("4. Search for 'Gemini API'")
    print("5. Click 'Enable'")
    print()
    print("📋 Step 3: Set the API key")
    print("Run this command with your new API key:")
    print("export GEMINI_API_KEY='your-new-api-key-here'")
    print()
    print("📋 Step 4: Test the API")
    print("Run: python test_gemini_api.py")
    print()

def test_with_mock_response():
    """Test the fix functionality with a mock response"""
    print("🧪 TESTING WITH MOCK RESPONSE")
    print("=" * 40)
    
    # Create a mock HTML file to test with
    test_html = """<!DOCTYPE html>
<html>
<head>
    <title>Test Document</title>
</head>
<body>
    <h1>Test Document</h1>
    <img src="test.jpg" alt="">
    <input type="text" id="name">
    <button onclick="submit()">Submit</button>
</body>
</html>"""
    
    # Write test file
    with open('test_document.html', 'w') as f:
        f.write(test_html)
    
    print("✅ Created test HTML file with accessibility issues")
    print("📝 Issues in the file:")
    print("  - Image missing alt text")
    print("  - Input missing label")
    print("  - Button missing accessible text")
    print()
    
    # Mock the Gemini API response
    mock_fixed_html = """<!DOCTYPE html>
<html lang="en">
<head>
    <title>Test Document</title>
</head>
<body>
    <h1>Test Document</h1>
    <img src="test.jpg" alt="Test image description" aria-label="Test image">
    <label for="name">Name:</label>
    <input type="text" id="name" aria-describedby="name-help">
    <div id="name-help">Please enter your full name</div>
    <button onclick="submit()" aria-label="Submit form">Submit</button>
</body>
</html>"""
    
    print("🔧 Mock Gemini API would fix these issues:")
    print("  - Added alt text to image")
    print("  - Added label for input")
    print("  - Added aria-describedby for better accessibility")
    print("  - Added aria-label to button")
    print("  - Added lang attribute to html")
    print()
    
    # Write the "fixed" file
    with open('test_document_fixed.html', 'w') as f:
        f.write(mock_fixed_html)
    
    print("✅ Created mock fixed HTML file")
    print("📁 Files created:")
    print("  - test_document.html (original with issues)")
    print("  - test_document_fixed.html (fixed version)")
    print()
    print("🎯 This demonstrates what the real Gemini API would do!")
    print("   Once you get a valid API key, the system will:")
    print("   1. Read the original file")
    print("   2. Send it to Gemini API")
    print("   3. Get back the fixed version")
    print("   4. Apply the changes")
    print("   5. Update the ADO work item status")
    print()

def main():
    """Main function"""
    print("🔍 GEMINI API STATUS CHECK")
    print("=" * 30)
    
    api_key = os.getenv('GEMINI_API_KEY')
    
    if not api_key:
        print("❌ No API key found")
        print_setup_instructions()
        return
    
    print(f"🔑 Found API key: {api_key[:10]}...")
    
    # Test the API
    url = "https://generativelanguage.googleapis.com/v1/models/gemini-1.5-pro:generateContent"
    
    headers = {"Content-Type": "application/json"}
    data = {
        "contents": [{"parts": [{"text": "Hello, respond with 'working' if you can see this."}]}]
    }
    
    try:
        print("🧪 Testing API...")
        response = requests.post(f"{url}?key={api_key}", headers=headers, json=data, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            if 'candidates' in result and len(result['candidates']) > 0:
                text = result['candidates'][0]['content']['parts'][0]['text']
                print(f"✅ API working! Response: {text}")
                print("\n🎉 Your Gemini API is ready to use!")
                print("   The 'Fix with Agent' functionality should work now.")
                return
            else:
                print("❌ Unexpected response format")
        else:
            print(f"❌ API error: {response.status_code}")
            print(f"Response: {response.text}")
            
            if "API key not valid" in response.text:
                print("\n🔧 API key is invalid!")
                print_setup_instructions()
                
    except Exception as e:
        print(f"❌ Error: {e}")
        print_setup_instructions()
    
    # If we get here, the API isn't working
    print("\n🧪 DEMO MODE")
    print("Since the API isn't working, let's show you what it would do:")
    test_with_mock_response()

if __name__ == "__main__":
    main()
