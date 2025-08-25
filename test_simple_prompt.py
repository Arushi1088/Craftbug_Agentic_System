#!/usr/bin/env python3
"""
Test Simple Prompt for Craft Bug Detection
"""

import os
import base64
import asyncio
from PIL import Image
import io
from dotenv import load_dotenv
import openai
from openai import AsyncOpenAI

load_dotenv()

async def test_simple_prompt():
    """Test with a simpler prompt to see if we can detect any issues"""
    
    # Simple test prompt
    simple_prompt = """You are a UX designer analyzing Excel Web screenshots for visual craft bugs.

Look for these types of issues:
- Color contrast problems
- Spacing inconsistencies  
- Typography mismatches
- Alignment issues
- Component styling problems

Analyze the provided screenshots and report any visual issues you find.

Format your response as:
CRAFT BUG #1
Type: [Color|Spacing|Typography|Alignment|Component]
Severity: [Red|Orange|Yellow]
Title: [Brief description]
Description: [What's wrong]
Expected: [What should be correct]
Actual: [What's currently wrong]

If no issues found, say "No visible craft bugs detected."

Screenshots to analyze:
- Step 1: Excel initial state
- Step 2: Copilot dialog
- Step 3: Save dialog"""

    # Test data
    test_steps = [
        {
            'screenshot_path': 'screenshots/excel_web/excel_initial_state_1756061972.png',
        },
        {
            'screenshot_path': 'screenshots/excel_web/excel_copilot_dialog_1756061967.png',
        },
        {
            'screenshot_path': 'screenshots/excel_web/excel_final_state_1755521895.png',
        }
    ]
    
    # Prepare images
    image_files = []
    for step in test_steps:
        screenshot_path = step.get('screenshot_path')
        if screenshot_path and os.path.exists(screenshot_path):
            try:
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
            except Exception as e:
                print(f"Error processing {screenshot_path}: {e}")
    
    if not image_files:
        print("❌ No valid images found")
        return
    
    # Prepare messages
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
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("❌ No OpenAI API key found")
        return
    
    client = AsyncOpenAI(api_key=api_key)
    
    print("🚀 Testing simple prompt with 3 screenshots...")
    
    try:
        response = await client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            max_tokens=4000,
            temperature=0.1
        )
        
        analysis_text = response.choices[0].message.content
        print(f"✅ Simple analysis complete: {len(analysis_text)} characters")
        
        print(f"\n🔍 SIMPLE ANALYSIS RESPONSE:")
        print("=" * 50)
        print(analysis_text)
        print("=" * 50)
        
        # Check for bugs
        if "craft bug" in analysis_text.lower():
            print("\n✅ Simple prompt detected craft bugs!")
        else:
            print("\n❌ Simple prompt also found no bugs")
            
    except Exception as e:
        print(f"❌ Simple analysis failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_simple_prompt())

