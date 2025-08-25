#!/usr/bin/env python3
"""
Test Loose Prompt - See actual LLM response
"""

import asyncio
from final_craft_bug_analyzer import FinalCraftBugAnalyzer

async def test_loose_prompt():
    """Test the loose prompt and see the actual LLM response"""
    
    # Sample test data
    test_steps = [
        {
            'step_name': 'Navigate to Excel',
            'description': 'User navigates to Excel web app',
            'screenshot_path': 'screenshots/excel_web/excel_initial_state_1756061972.png',
            'scenario_description': 'Excel Document Creation with Copilot',
            'persona_type': 'Power User'
        },
        {
            'step_name': 'Dismiss Copilot Dialog',
            'description': 'User dismisses the Copilot dialog',
            'screenshot_path': 'screenshots/excel_web/excel_copilot_dialog_1756061967.png',
            'scenario_description': 'Excel Document Creation with Copilot',
            'persona_type': 'Power User'
        },
        {
            'step_name': 'Save Workbook',
            'description': 'User saves the workbook',
            'screenshot_path': 'screenshots/excel_web/excel_final_state_1755521895.png',
            'scenario_description': 'Excel Document Creation with Copilot',
            'persona_type': 'Power User'
        }
    ]
    
    # Initialize analyzer
    analyzer = FinalCraftBugAnalyzer()
    
    print("🚀 Testing Loose Prompt with 3 screenshots...")
    
    # Run analysis
    bugs = await analyzer.analyze_screenshots(test_steps)
    
    print(f"\n📊 Analysis Results: {len(bugs)} bugs detected")
    
    if bugs:
        print("\n🔍 DETECTED BUGS:")
        for i, bug in enumerate(bugs, 1):
            print(f"\n--- Bug {i} ---")
            print(f"Title: {bug.get('title', 'Unknown')}")
            print(f"Type: {bug.get('type', 'Unknown')}")
            print(f"Severity: {bug.get('severity', 'Unknown')}")
            print(f"Confidence: {bug.get('confidence', 'Unknown')}")
            print(f"Expected: {bug.get('expected', 'Unknown')}")
            print(f"Actual: {bug.get('actual', 'Unknown')}")
            print(f"What to Correct: {bug.get('what_to_correct', 'Unknown')}")
            print(f"Affected Steps: {bug.get('affected_steps', 'Unknown')}")
            print(f"Visual Impact: {bug.get('impact', 'Unknown')}")
    else:
        print("\n❌ No bugs detected")
    
    # Now let's test with a much simpler prompt to see if we can get more bugs
    print("\n" + "="*50)
    print("🧪 TESTING WITH SIMPLER PROMPT")
    print("="*50)
    
    # Create a simpler prompt that should generate more bugs
    simple_prompt = """You are a UX designer analyzing Excel Web screenshots for visual craft bugs.

Look at the provided screenshots and find ALL visual issues you can see, including:
- Color contrast problems
- Spacing inconsistencies
- Typography mismatches
- Alignment issues
- Component styling problems
- Layout problems
- Visual hierarchy issues
- Any other visual defects

Be thorough and find as many issues as possible. Don't be conservative.

Format each bug as:
CRAFT BUG #X
Type: [Color|Spacing|Typography|Alignment|Component|Layout|Hierarchy]
Severity: [Red|Orange|Yellow]
Confidence: [High|Medium|Low]
Title: [Brief description]
Description: [What's wrong]
Expected: [What should be correct]
Actual: [What's currently wrong]

Find at least 5-8 bugs per screenshot. Be detailed and specific."""

    # Test with simple prompt
    try:
        from openai import AsyncOpenAI
        import os
        import base64
        from PIL import Image
        import io
        
        # Prepare images
        image_files = []
        for step in test_steps:
            screenshot_path = step.get('screenshot_path')
            if screenshot_path and os.path.exists(screenshot_path):
                with Image.open(screenshot_path) as img:
                    max_width = 1280
                    if img.width > max_width:
                        ratio = max_width / img.width
                        new_height = int(img.height * ratio)
                        img = img.resize((max_width, new_height), Image.Resampling.LANCZOS)
                    
                    buffer = io.BytesIO()
                    img.save(buffer, format='JPEG', quality=85)
                    buffer.seek(0)
                    image_files.append((screenshot_path, buffer.getvalue()))
        
        # Build messages
        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": simple_prompt}
                ]
            }
        ]
        
        # Add images
        for image_path, image_data in image_files:
            base64_image = base64.b64encode(image_data).decode('utf-8')
            messages[0]["content"].append({
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/jpeg;base64,{base64_image}"
                }
            })
        
        # Make API call
        client = AsyncOpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        response = await client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            max_tokens=8000,
            temperature=0.1
        )
        
        analysis_text = response.choices[0].message.content
        print(f"\n🔍 SIMPLE PROMPT RESPONSE ({len(analysis_text)} characters):")
        print("="*50)
        print(analysis_text)
        print("="*50)
        
        # Count bugs in response
        bug_count = analysis_text.lower().count('craft bug #')
        print(f"\n📊 Simple prompt found {bug_count} bugs")
        
    except Exception as e:
        print(f"❌ Simple prompt test failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_loose_prompt())

