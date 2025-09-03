#!/usr/bin/env python3
"""
Test script to verify LLM bug detection with improved prompt
"""

import asyncio
import json
from final_craft_bug_analyzer import FinalCraftBugAnalyzer

async def test_bug_detection():
    """Test if the LLM is finding bugs with the improved prompt"""
    
    # Create test data with valid screenshot paths - using the expected field names
    test_steps = [
        {
            "index": 1,
            "step_name": "Navigate to Excel Web",
            "screenshot_path": "screenshots/excel_web/excel_initial_state_1756882907.png"
        },
        {
            "index": 2, 
            "step_name": "Click New Workbook",
            "screenshot_path": "screenshots/excel_web/excel_copilot_dialog_1756882901.png"
        },
        {
            "index": 3,
            "step_name": "Enter Sample Data", 
            "screenshot_path": "screenshots/excel_web/excel_data_entered_1756882911.png"
        }
    ]
    
    print("🔍 Testing LLM bug detection with improved prompt...")
    print(f"📸 Using {len(test_steps)} screenshots for testing")
    
    try:
        analyzer = FinalCraftBugAnalyzer()
        
        # Test the analysis
        bugs = await analyzer.analyze_screenshots(test_steps)
        
        print(f"✅ Analysis completed successfully!")
        print(f"📊 Found {len(bugs)} bugs")
        
        if bugs:
            print("\n🐛 Bugs found:")
            for i, bug in enumerate(bugs, 1):
                print(f"  {i}. {bug.get('title', 'No title')} - {bug.get('confidence', 'No confidence')}")
                print(f"     Type: {bug.get('type', 'Unknown')}, Severity: {bug.get('severity', 'Unknown')}")
        else:
            print("❌ No bugs found - LLM may still be over-filtering")
            
        return bugs
        
    except Exception as e:
        print(f"❌ Analysis failed: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    asyncio.run(test_bug_detection())
