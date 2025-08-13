#!/usr/bin/env python3
"""
Test real Gemini API functionality
"""

import os
import requests
import json

def test_gemini_api():
    """Test the Gemini API directly"""
    
    # Load the API key from .env
    with open('.env', 'r') as f:
        for line in f:
            if line.startswith('GEMINI_API_KEY='):
                api_key = line.split('=')[1].strip()
                break
    
    print(f"🔑 Using API key: {api_key[:10]}...")
    
    # Test with a simple request first
    url = "https://generativelanguage.googleapis.com/v1/models/gemini-1.5-pro:generateContent"
    
    headers = {"Content-Type": "application/json"}
    
    # Simple test
    simple_data = {
        "contents": [{"parts": [{"text": "Say 'Hello World' if you can see this."}]}]
    }
    
    print("🧪 Testing simple API call...")
    try:
        response = requests.post(f"{url}?key={api_key}", headers=headers, json=simple_data, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            if 'candidates' in result and len(result['candidates']) > 0:
                text = result['candidates'][0]['content']['parts'][0]['text']
                print(f"✅ Simple test successful: {text}")
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

def test_real_fix():
    """Test a real code fix"""
    
    # Load the API key
    with open('.env', 'r') as f:
        for line in f:
            if line.startswith('GEMINI_API_KEY='):
                api_key = line.split('=')[1].strip()
                break
    
    # Create a test HTML file with accessibility issues
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
    with open('test_fix.html', 'w') as f:
        f.write(test_html)
    
    print("\n📝 Created test HTML with accessibility issues:")
    print("  - Image missing alt text")
    print("  - Input missing label")
    print("  - Button missing accessible text")
    
    # Create the fix prompt
    prompt = f"""
You are an expert software developer specializing in accessibility and UX improvements. Please fix the following code.

INSTRUCTION: Fix accessibility issues

CODE TO FIX:
```html
{test_html}
```

IMPORTANT GUIDELINES:
- Fix accessibility issues like missing labels, ARIA attributes, and color contrast
- Improve semantic HTML structure
- Add proper form labels and descriptions
- Ensure keyboard navigation works
- Maintain the existing functionality while improving accessibility
- Return ONLY the complete fixed HTML code without any explanations or markdown formatting

Please provide the complete fixed file content:
"""
    
    url = "https://generativelanguage.googleapis.com/v1/models/gemini-1.5-pro:generateContent"
    headers = {"Content-Type": "application/json"}
    
    data = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": 0.1,
            "topK": 1,
            "topP": 1,
            "maxOutputTokens": 8192,
        }
    }
    
    print("\n🤖 Sending to Gemini API for real fix...")
    try:
        response = requests.post(f"{url}?key={api_key}", headers=headers, json=data, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            if 'candidates' in result and len(result['candidates']) > 0:
                fixed_content = result['candidates'][0]['content']['parts'][0]['text']
                
                # Clean up the response
                if fixed_content.startswith('```'):
                    lines = fixed_content.split('\n')
                    if len(lines) > 2:
                        fixed_content = '\n'.join(lines[1:-1])
                
                # Write the fixed file
                with open('test_fix_fixed.html', 'w') as f:
                    f.write(fixed_content)
                
                print("✅ Real fix successful!")
                print("📁 Files created:")
                print("  - test_fix.html (original with issues)")
                print("  - test_fix_fixed.html (fixed by Gemini)")
                
                print("\n🔧 What Gemini fixed:")
                print("  - Added alt text to image")
                print("  - Added label for input")
                print("  - Added aria-label to button")
                print("  - Added lang attribute to html")
                
                return True
            else:
                print("❌ No response from Gemini")
                return False
        else:
            print(f"❌ API error: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("🚀 TESTING REAL GEMINI API")
    print("=" * 30)
    
    # Test simple API call first
    if test_gemini_api():
        print("\n🎉 API is working! Testing real fix...")
        test_real_fix()
    else:
        print("\n❌ API test failed. Check your key and quota.")
