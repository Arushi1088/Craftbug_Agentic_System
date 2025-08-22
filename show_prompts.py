#!/usr/bin/env python3
"""
Show Prompts
===========

Display the complete prompts being sent to the LLM.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def show_prompts():
    """Show the complete prompts being sent to the LLM"""
    
    print("📋 COMPLETE LLM PROMPTS")
    print("=" * 50)
    
    try:
        from llm_enhanced_analyzer import LLMEnhancedAnalyzer
        
        # Create analyzer to access prompts
        analyzer = LLMEnhancedAnalyzer()
        
        if hasattr(analyzer, 'analysis_prompts'):
            print(f"📊 Found {len(analyzer.analysis_prompts)} analysis prompts\n")
            
            for prompt_name, prompt_content in analyzer.analysis_prompts.items():
                print(f"🔍 PROMPT: {prompt_name.upper()}")
                print("-" * 40)
                print(prompt_content)
                print("\n" + "="*80 + "\n")
        else:
            print("❌ No analysis prompts found")
            
    except Exception as e:
        print(f"❌ Error accessing prompts: {e}")
        import traceback
        traceback.print_exc()

def show_actual_prompt_with_screenshot():
    """Show the actual prompt being sent with a real screenshot"""
    
    print("\n🎯 ACTUAL PROMPT WITH SCREENSHOT")
    print("=" * 50)
    
    try:
        from llm_enhanced_analyzer import LLMEnhancedAnalyzer
        
        # Find a screenshot
        screenshots_dir = Path("screenshots/excel_web")
        if not screenshots_dir.exists():
            print("❌ No screenshots directory found")
            return
        
        screenshot_files = list(screenshots_dir.glob("*.png"))
        if not screenshot_files:
            print("❌ No screenshot files found")
            return
        
        test_screenshot = max(screenshot_files, key=lambda x: x.stat().st_mtime)
        print(f"📸 Using screenshot: {test_screenshot.name}")
        
        # Create test step
        test_step = {
            "step_name": "Test Step (1 of 1)",
            "action_type": "test",
            "duration_ms": 1000,
            "screenshot_path": str(test_screenshot),
            "scenario_description": "Quick Test Scenario",
            "persona_type": "Test User"
        }
        
        # Create analyzer
        analyzer = LLMEnhancedAnalyzer()
        
        # Get the craft bug detection prompt
        craft_prompt = analyzer.analysis_prompts.get('craft_bug_detection', '')
        
        print("\n📝 CRAFT BUG DETECTION PROMPT:")
        print("-" * 40)
        print(craft_prompt)
        
        # Show what would be sent to OpenAI
        print("\n🚀 WHAT GETS SENT TO OPENAI:")
        print("-" * 40)
        
        # Read the screenshot as base64
        import base64
        with open(test_screenshot, 'rb') as f:
            image_data = base64.b64encode(f.read()).decode('utf-8')
        
        # Show the actual message structure
        print("Message structure:")
        print(f"- Role: user")
        print(f"- Content: [")
        print(f"  {{'type': 'text', 'text': '{craft_prompt[:100]}...'}},")
        print(f"  {{'type': 'image_url', 'image_url': {{'url': 'data:image/png;base64,{image_data[:50]}...'}}}}")
        print(f"]")
        
        print(f"\n📊 Screenshot size: {len(image_data)} base64 characters")
        print(f"📊 Prompt length: {len(craft_prompt)} characters")
        
    except Exception as e:
        print(f"❌ Error showing actual prompt: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    show_prompts()
    show_actual_prompt_with_screenshot()
