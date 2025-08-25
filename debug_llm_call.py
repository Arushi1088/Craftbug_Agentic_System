#!/usr/bin/env python3
"""
Debug LLM call to see exactly what's happening
"""

import asyncio
import sys
import base64
import os
from pathlib import Path

# Add the project root to the path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from llm_enhanced_analyzer import LLMEnhancedAnalyzer

async def debug_llm_call():
    """Debug the actual LLM call"""
    
    print("🔍 DEBUGGING LLM CALL...")
    
    # Initialize analyzer
    analyzer = LLMEnhancedAnalyzer()
    
    # Find a screenshot
    screenshot_path = None
    screenshots_dir = Path("screenshots/excel_web")
    if screenshots_dir.exists():
        for screenshot in screenshots_dir.glob("*.png"):
            screenshot_path = str(screenshot)
            break
    
    if not screenshot_path:
        print("❌ No screenshots found")
        return
    
    print(f"📸 Using screenshot: {screenshot_path}")
    
    # Prepare test step data
    step_data = {
        'step_name': 'Test Step',
        'scenario_description': 'Test Scenario',
        'persona_type': 'User',
        'screenshot_path': screenshot_path
    }
    
    try:
        # Prepare context
        context = analyzer._prepare_step_context(step_data)
        
        # Get the prompt
        prompt_template = analyzer.analysis_prompts['comprehensive_visual_analysis']
        actual_prompt = prompt_template.format(**context)
        
        print(f"\n📋 PROMPT BEING SENT:")
        print("="*50)
        print(actual_prompt)
        print("="*50)
        
        # Read screenshot
        with open(screenshot_path, 'rb') as f:
            screenshot_bytes = f.read()
            screenshot_base64 = base64.b64encode(screenshot_bytes).decode('utf-8')
        
        # Create the exact message that gets sent
        messages = [
            {
                "role": "user", 
                "content": [
                    {"type": "text", "text": actual_prompt},
                    {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{screenshot_base64}"}}
                ]
            }
        ]
        
        print(f"\n🚀 SENDING TO OPENAI:")
        print(f"Model: {analyzer.llm_model}")
        print(f"Max tokens: {analyzer.llm_max_tokens}")
        print(f"Prompt length: {len(actual_prompt)} chars")
        print(f"Screenshot size: {len(screenshot_base64)} base64 chars")
        
        # Make the actual call
        response = await analyzer.llm_client.chat.completions.create(
            model=analyzer.llm_model,
            messages=messages,
            max_completion_tokens=analyzer.llm_max_tokens
        )
        
        content = response.choices[0].message.content.strip()
        
        print(f"\n📥 RESPONSE FROM OPENAI:")
        print("="*50)
        print(f"Finish reason: {response.choices[0].finish_reason}")
        print(f"Content length: {len(content)} chars")
        print(f"Content: {repr(content)}")
        print("="*50)
        
        if content:
            print(f"\n📄 ACTUAL CONTENT:")
            print(content)
        else:
            print("❌ EMPTY RESPONSE!")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(debug_llm_call())
