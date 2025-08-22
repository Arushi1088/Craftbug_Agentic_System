#!/usr/bin/env python3
"""
Test script to verify screenshot flow in LLM analysis
"""

import asyncio
import os
import sys
from pathlib import Path

# Add the project root to the path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from llm_enhanced_analyzer import LLMEnhancedAnalyzer

async def test_screenshot_flow():
    """Test that screenshots are properly passed to LLM analysis"""
    
    print("🧪 Testing Screenshot Flow in LLM Analysis")
    print("=" * 50)
    
    # Initialize the LLM analyzer
    analyzer = LLMEnhancedAnalyzer()
    
    # Create test step data with a screenshot path
    test_step_data = {
        "step_name": "Test Step - Screenshot Verification",
        "description": "Testing screenshot flow",
        "timing": 1000,
        "success": True,
        "dialog_detected": False,
        "dialog_type": None,
        "screenshot_path": "screenshots/excel_web/test_screenshot.png"  # This should exist
    }
    
    print(f"📋 Test Step Data:")
    print(f"   Step Name: {test_step_data['step_name']}")
    print(f"   Screenshot Path: {test_step_data['screenshot_path']}")
    print(f"   Screenshot Exists: {os.path.exists(test_step_data['screenshot_path'])}")
    
    # Check if screenshot exists
    if not os.path.exists(test_step_data['screenshot_path']):
        print("⚠️  Test screenshot not found, looking for any available screenshot...")
        
        # Look for any available screenshot
        screenshots_dir = Path("screenshots/excel_web")
        if screenshots_dir.exists():
            available_screenshots = list(screenshots_dir.glob("*.png"))
            if available_screenshots:
                test_step_data['screenshot_path'] = str(available_screenshots[0])
                print(f"✅ Using available screenshot: {test_step_data['screenshot_path']}")
            else:
                print("❌ No screenshots found in screenshots/excel_web/")
                return
        else:
            print("❌ Screenshots directory not found")
            return
    
    print(f"\n🔍 Testing LLM Analysis with Screenshot...")
    
    try:
        # Run LLM analysis
        bugs = await analyzer.analyze_step_with_llm(test_step_data)
        
        print(f"\n📊 Results:")
        print(f"   Total Bugs Found: {len(bugs)}")
        
        if bugs:
            print(f"\n🐛 Bug Details:")
            for i, bug in enumerate(bugs, 1):
                print(f"   Bug #{i}:")
                print(f"     Title: {bug.get('title', 'N/A')}")
                print(f"     Type: {bug.get('type', 'N/A')}")
                print(f"     Severity: {bug.get('severity', 'N/A')}")
                print(f"     Analysis Type: {bug.get('analysis_type', 'N/A')}")
                print(f"     Step: {bug.get('step_name', 'N/A')}")
                print()
        else:
            print("   No bugs detected (this might be normal for a test screenshot)")
        
        print("✅ Screenshot flow test completed successfully!")
        
    except Exception as e:
        print(f"❌ Error during LLM analysis: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_screenshot_flow())
