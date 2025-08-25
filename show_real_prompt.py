#!/usr/bin/env python3
"""
Show the actual prompt with real context filled in
"""

import asyncio
import sys
from pathlib import Path

# Add the project root to the path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from llm_enhanced_analyzer import LLMEnhancedAnalyzer

async def show_real_prompt():
    """Show the actual prompt with real context"""
    
    print("🔍 ACTUAL PROMPT WITH REAL CONTEXT")
    print("="*80)
    
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
    
    # Prepare real step data
    step_data = {
        'step_name': 'Take Screenshot - Initial State',
        'scenario_description': 'Excel Document Creation with UX Analysis',
        'persona_type': 'Power User',
        'screenshot_path': screenshot_path
    }
    
    # Prepare context (this is what gets filled into the prompt)
    context = analyzer._prepare_step_context(step_data)
    
    print(f"\n📋 CONTEXT BEING FILLED INTO PROMPT:")
    print("-" * 40)
    for key, value in context.items():
        print(f"{key}: {value}")
    
    print(f"\n" + "="*80)
    print("ACTUAL PROMPT SENT TO LLM (COMPREHENSIVE_VISUAL_ANALYSIS)")
    print("="*80)
    
    # Get the actual prompt with context filled in
    prompt_template = analyzer.analysis_prompts['comprehensive_visual_analysis']
    actual_prompt = prompt_template.format(**context)
    
    print(actual_prompt)
    
    print(f"\n" + "="*80)
    print("PROMPT STATISTICS")
    print("="*80)
    print(f"📏 Total characters: {len(actual_prompt)}")
    print(f"📄 Total lines: {actual_prompt.count(chr(10)) + 1}")
    print(f"🔤 Words: {len(actual_prompt.split())}")
    
    # Show what gets sent to OpenAI
    print(f"\n" + "="*80)
    print("WHAT GETS SENT TO OPENAI API")
    print("="*80)
    
    # Read screenshot as base64
    import base64
    with open(screenshot_path, 'rb') as f:
        image_data = base64.b64encode(f.read()).decode('utf-8')
    
    print("Message structure:")
    print(f"- Model: {analyzer.llm_model}")
    print(f"- Max tokens: {analyzer.llm_max_tokens}")
    print(f"- Role: user")
    print(f"- Content: [")
    print(f"  {{'type': 'text', 'text': '{actual_prompt[:100]}...'}},")
    print(f"  {{'type': 'image_url', 'image_url': {{'url': 'data:image/png;base64,{image_data[:50]}...'}}}}")
    print(f"]")
    print(f"- Screenshot size: {len(image_data)} base64 characters")

if __name__ == "__main__":
    asyncio.run(show_real_prompt())
