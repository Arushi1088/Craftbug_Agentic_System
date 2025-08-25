#!/usr/bin/env python3
"""
Test Explicit Issues Detection
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

async def test_explicit_issues():
    """Test with explicit instructions to look for specific issues"""
    
    # Explicit test prompt
    explicit_prompt = """You are a UX designer analyzing Excel Web screenshots for visual craft bugs.

IMPORTANT: Look carefully for these specific issues that are common in Excel Web:

1. **Color Issues:**
   - Button colors that don't match the design system
   - Text that might have poor contrast
   - Hover states that look wrong

2. **Spacing Issues:**
   - Uneven spacing between elements
   - Padding that looks too tight or too loose
   - Inconsistent gaps between buttons or icons

3. **Typography Issues:**
   - Text that looks too small or too large
   - Font weights that seem inconsistent
   - Line spacing that looks cramped

4. **Alignment Issues:**
   - Elements that don't line up properly
   - Buttons that seem misaligned
   - Icons that don't align with text

5. **Component Issues:**
   - Border radius that looks wrong
   - Shadows that seem too strong or too weak
   - Dialog positioning that looks off

6. **Layout Issues:**
   - Dialog boxes that might be too close to edges
   - Panels that don't seem properly centered
   - Elements that look cramped or too spread out

Analyze the provided screenshots and report ANY visual issues you can spot, even if they seem minor.

Format your response as:
CRAFT BUG #1
Type: [Color|Spacing|Typography|Alignment|Component|Layout]
Severity: [Red|Orange|Yellow]
Title: [Brief description]
Description: [What looks wrong]
Expected: [What should look like]
Actual: [What currently looks like]

If you find ANY issues, report them. Only say "No visible craft bugs detected" if you are absolutely certain there are no visual issues at all.

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
                {"type": "text", "text": explicit_prompt}
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
    
    print("🚀 Testing explicit issues detection with 3 screenshots...")
    
    try:
        response = await client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            max_tokens=4000,
            temperature=0.1
        )
        
        analysis_text = response.choices[0].message.content
        print(f"✅ Explicit analysis complete: {len(analysis_text)} characters")
        
        print(f"\n🔍 EXPLICIT ANALYSIS RESPONSE:")
        print("=" * 50)
        print(analysis_text)
        print("=" * 50)
        
        # Check for bugs
        if "craft bug" in analysis_text.lower():
            print("\n✅ Explicit prompt detected craft bugs!")
        else:
            print("\n❌ Even explicit prompt found no bugs")
            print("This suggests the screenshots might actually be well-designed!")
            
    except Exception as e:
        print(f"❌ Explicit analysis failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_explicit_issues())

