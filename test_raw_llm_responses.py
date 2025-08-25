#!/usr/bin/env python3
"""
Test script to show raw LLM responses before filtering
"""

import asyncio
import os
import sys
from pathlib import Path

# Add the project root to the path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from llm_enhanced_analyzer import LLMEnhancedAnalyzer

async def test_raw_llm_responses():
    """Test and show raw LLM responses"""
    
    print("🔍 Testing Raw LLM Responses...")
    
    # Initialize the analyzer
    analyzer = LLMEnhancedAnalyzer()
    
    # Find a screenshot to test with
    screenshot_path = None
    screenshots_dir = Path("screenshots/excel_web")
    if screenshots_dir.exists():
        for screenshot in screenshots_dir.glob("*.png"):
            screenshot_path = str(screenshot)
            break
    
    if not screenshot_path:
        print("❌ No screenshots found to test with")
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
        # Get raw LLM responses
        print("\n🔍 Getting raw LLM responses...")
        analysis = await analyzer._perform_llm_analysis(step_data)
        
        print("\n" + "="*80)
        print("RAW LLM RESPONSES (BEFORE FILTERING)")
        print("="*80)
        
        for analysis_type, result in analysis.items():
            if isinstance(result, dict) and 'analysis' in result:
                print(f"\n📋 {analysis_type.upper()}:")
                print("-" * 40)
                print(result['analysis'])
                print("-" * 40)
        
        print("\n" + "="*80)
        print("EXTRACTED BUGS (AFTER FILTERING)")
        print("="*80)
        
        # Now test the bug extraction
        bugs = analyzer._extract_llm_bugs_from_analysis(analysis, step_data)
        
        if bugs:
            for i, bug in enumerate(bugs, 1):
                print(f"\n🐛 Bug #{i}:")
                print(f"   Title: {bug.get('title', 'N/A')}")
                print(f"   Type: {bug.get('bug_type', 'N/A')}")
                print(f"   Severity: {bug.get('severity', 'N/A')}")
                print(f"   Description: {bug.get('description', 'N/A')[:100]}...")
        else:
            print("❌ No bugs extracted (all filtered out)")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_raw_llm_responses())
