#!/usr/bin/env python3
"""
Quick test script to test the system with 3-4 screenshots
instead of running the full Excel scenario
"""

import asyncio
import json
from pathlib import Path
from final_craft_bug_analyzer import FinalCraftBugAnalyzer

async def test_quick_analysis():
    """Test the system with just 3-4 screenshots"""
    
    print("🧪 Quick Test: Testing with 3-4 screenshots...")
    
    # Check if we have existing screenshots
    screenshots_dir = Path("screenshots/excel_web")
    if not screenshots_dir.exists():
        print("❌ No screenshots directory found. Please run a scenario first.")
        return
    
    # Find existing screenshots
    screenshot_files = list(screenshots_dir.glob("*.png"))
    if len(screenshot_files) < 3:
        print(f"❌ Not enough screenshots found. Found {len(screenshot_files)}, need at least 3.")
        return
    
    # Use the first 3 screenshots for testing
    test_screenshots = screenshot_files[:3]
    print(f"📸 Using {len(test_screenshots)} screenshots for quick test:")
    for i, screenshot in enumerate(test_screenshots, 1):
        print(f"   {i}. {screenshot.name}")
    
    # Create test data
    steps_data = []
    for i, screenshot in enumerate(test_screenshots):
        steps_data.append({
            "step_name": f"Test Step {i+1}",
            "step_description": f"Quick test step {i+1}",
            "screenshot_path": str(screenshot),
            "step_index": i
        })
    
    # Initialize the analyzer
    analyzer = FinalCraftBugAnalyzer()
    
    try:
        print("\n🚀 Running quick analysis...")
        bugs = await analyzer.analyze_screenshots(steps_data)
        
        print(f"\n✅ Quick test completed!")
        print(f"📊 Found {len(bugs)} bugs")
        
        # Show first few bugs
        for i, bug in enumerate(bugs[:3], 1):
            print(f"\n🐛 Bug {i}:")
            print(f"   Title: {bug.get('title', 'N/A')}")
            print(f"   Type: {bug.get('type', 'N/A')}")
            print(f"   Severity: {bug.get('severity', 'N/A')}")
            print(f"   Screenshot: {bug.get('screenshot_path', 'N/A')}")
        
        if len(bugs) > 3:
            print(f"\n... and {len(bugs) - 3} more bugs")
        
        return bugs
        
    except Exception as e:
        print(f"❌ Quick test failed: {e}")
        return None

if __name__ == "__main__":
    asyncio.run(test_quick_analysis())

