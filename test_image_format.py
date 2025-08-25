#!/usr/bin/env python3
"""
Test Image Format - Check if image format is causing LLM issues
"""

import asyncio
from openai import AsyncOpenAI
import os
import base64
from PIL import Image
import io
from dotenv import load_dotenv

load_dotenv()

async def test_image_format():
    """Test different image formats to see which works with GPT-4o"""
    
    # Test with PNG format (original)
    print("🧪 Testing PNG format...")
    
    test_steps = [
        {
            'screenshot_path': 'screenshots/excel_web/excel_initial_state_1756061972.png',
        }
    ]
    
    # Test PNG
    try:
        screenshot_path = test_steps[0]['screenshot_path']
        with Image.open(screenshot_path) as img:
            # Keep original PNG format
            buffer = io.BytesIO()
            img.save(buffer, format='PNG')
            buffer.seek(0)
            png_data = buffer.getvalue()
        
        # Build messages with PNG
        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "Look at this Excel screenshot and tell me what you see. Describe the interface elements, colors, and any visual issues you notice."},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/png;base64,{base64.b64encode(png_data).decode('utf-8')}"
                        }
                    }
                ]
            }
        ]
        
        client = AsyncOpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        response = await client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            max_tokens=1000,
            temperature=0.1
        )
        
        png_response = response.choices[0].message.content
        print(f"📊 PNG Response ({len(png_response)} chars): {png_response[:200]}...")
        
        if "cannot see" in png_response.lower() or "unable to view" in png_response.lower():
            print("❌ PNG format not working")
        else:
            print("✅ PNG format working")
            
    except Exception as e:
        print(f"❌ PNG test failed: {e}")
    
    # Test JPEG format
    print("\n🧪 Testing JPEG format...")
    try:
        screenshot_path = test_steps[0]['screenshot_path']
        with Image.open(screenshot_path) as img:
            # Convert to JPEG
            buffer = io.BytesIO()
            img.save(buffer, format='JPEG', quality=95)
            buffer.seek(0)
            jpeg_data = buffer.getvalue()
        
        # Build messages with JPEG
        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "Look at this Excel screenshot and tell me what you see. Describe the interface elements, colors, and any visual issues you notice."},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64.b64encode(jpeg_data).decode('utf-8')}"
                        }
                    }
                ]
            }
        ]
        
        client = AsyncOpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        response = await client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            max_tokens=1000,
            temperature=0.1
        )
        
        jpeg_response = response.choices[0].message.content
        print(f"📊 JPEG Response ({len(jpeg_response)} chars): {jpeg_response[:200]}...")
        
        if "cannot see" in jpeg_response.lower() or "unable to view" in jpeg_response.lower():
            print("❌ JPEG format not working")
        else:
            print("✅ JPEG format working")
            
    except Exception as e:
        print(f"❌ JPEG test failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_image_format())
