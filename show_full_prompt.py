#!/usr/bin/env python3
"""
Show the complete full prompt without truncation
"""

import asyncio
import sys
from pathlib import Path

# Add the project root to the path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from llm_enhanced_analyzer import LLMEnhancedAnalyzer

async def show_full_prompt():
    """Show the complete full prompt"""
    
    print("🔍 COMPLETE FULL PROMPT SENT TO LLM")
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
    
    # Prepare context
    context = analyzer._prepare_step_context(step_data)
    
    print(f"\n📋 CONTEXT:")
    print("-" * 40)
    for key, value in context.items():
        print(f"{key}: {value}")
    
    print(f"\n" + "="*80)
    print("COMPLETE PROMPT (COMPREHENSIVE_VISUAL_ANALYSIS)")
    print("="*80)
    
    # Get the complete prompt with context filled in
    prompt_template = analyzer.analysis_prompts['comprehensive_visual_analysis']
    complete_prompt = prompt_template.format(**context)
    
    # Show the complete prompt without any truncation
    print(complete_prompt)
    
    print(f"\n" + "="*80)
    print("PROMPT STATISTICS")
    print("="*80)
    print(f"📏 Total characters: {len(complete_prompt)}")
    print(f"📄 Total lines: {complete_prompt.count(chr(10)) + 1}")
    print(f"🔤 Words: {len(complete_prompt.split())}")
    print(f"📊 Model: {analyzer.llm_model}")
    print(f"📊 Max tokens: {analyzer.llm_max_tokens}")

if __name__ == "__main__":
    asyncio.run(show_full_prompt())
