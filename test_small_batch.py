#!/usr/bin/env python3
"""
Test small batch analysis to see if bugs are being detected
"""

import asyncio
from final_craft_bug_analyzer import FinalCraftBugAnalyzer

async def test_small_batch():
    """Test bug detection with a small batch of screenshots"""
    print("🧪 Testing small batch bug detection...")
    
    # Sample test data with a few screenshots
    test_steps = [
        {
            'step_name': 'Test Step 1',
            'description': 'Testing bug detection',
            'screenshot_path': 'screenshots/excel_web/excel_initial_state_1756881064.png',
            'scenario_description': 'Excel Web Test Scenario',
            'persona_type': 'Power User'
        },
        {
            'step_name': 'Test Step 2', 
            'description': 'Testing bug detection',
            'screenshot_path': 'screenshots/excel_web/excel_copilot_dialog_1756881059.png',
            'scenario_description': 'Excel Web Test Scenario',
            'persona_type': 'Power User'
        }
    ]
    
    # Check if screenshots exist
    import os
    for step in test_steps:
        if os.path.exists(step['screenshot_path']):
            print(f"✅ Screenshot exists: {step['screenshot_path']}")
        else:
            print(f"❌ Screenshot missing: {step['screenshot_path']}")
    
    # Initialize analyzer
    try:
        analyzer = FinalCraftBugAnalyzer()
        print("✅ Final analyzer initialized")
        
        # Run analysis
        print("🔍 Running analysis...")
        bugs = await analyzer.analyze_screenshots(test_steps)
        
        print(f"🎯 Analysis complete! Found {len(bugs)} bugs")
        
        if bugs:
            for i, bug in enumerate(bugs, 1):
                print(f"\n--- Bug {i} ---")
                print(f"Title: {bug.get('title', 'Unknown')}")
                print(f"Type: {bug.get('type', 'Unknown')}")
                print(f"Severity: {bug.get('severity', 'Unknown')}")
                print(f"Confidence: {bug.get('confidence', 'Unknown')}")
        else:
            print("❌ No bugs detected - this suggests the prompts are still too restrictive")
            
    except Exception as e:
        print(f"❌ Analysis failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_small_batch())
