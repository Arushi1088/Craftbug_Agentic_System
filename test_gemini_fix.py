#!/usr/bin/env python3
"""
Test the Gemini CLI fix function
"""

from gemini_cli import fix_issue_with_thinking_steps
import json

def test_gemini_fix():
    """Test the Gemini CLI fix function"""
    
    print("🔧 TESTING GEMINI CLI FIX FUNCTION")
    print("=" * 40)
    
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
    
    print("📝 Created test HTML with accessibility issues:")
    print("  - Image missing alt text")
    print("  - Input missing label")
    print("  - Button missing accessible text")
    
    try:
        print("\n🔄 Testing Gemini CLI fix...")
        result = fix_issue_with_thinking_steps(
            work_item_id=999,
            file_path='test_fix.html',
            instruction='Fix accessibility issues'
        )
        
        if result.get('success'):
            print("✅ Fix completed successfully!")
            print(f"📊 Work Item ID: {result.get('work_item_id')}")
            print(f"📁 File: {result.get('file_path')}")
            print(f"🔧 Changes Applied: {result.get('changes_applied')}")
            
            # Show thinking steps
            print("\n🧠 Thinking Steps:")
            for step in result.get('thinking_steps', []):
                print(f"  {step.get('step', 'Unknown step')}")
            
            # Show the fixed content
            print("\n📄 Fixed Content:")
            print(result.get('fixed_content', 'No content'))
            
            return True
        else:
            print("❌ Fix failed:")
            print(f"   Error: {result.get('error', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

if __name__ == "__main__":
    test_gemini_fix()
