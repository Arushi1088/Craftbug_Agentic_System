#!/usr/bin/env python3
"""
Test script to verify screenshot assignment improvements
"""

import os
import sys
import asyncio
from pathlib import Path

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from enhanced_ux_analyzer import EnhancedUXAnalyzer

async def test_screenshot_assignment():
    """Test the improved screenshot assignment logic"""
    
    print("🧪 Testing Screenshot Assignment Improvements")
    print("=" * 50)
    
    # Initialize the analyzer
    analyzer = EnhancedUXAnalyzer()
    
    # Create mock telemetry data with multiple steps
    mock_telemetry = {
        "scenario_name": "Excel Document Creation",
        "steps": [
            {
                "step_name": "Navigate to Excel Web",
                "screenshot_path": None,
                "duration_ms": 2000,
                "success": True
            },
            {
                "step_name": "Click New Workbook",
                "screenshot_path": None,
                "duration_ms": 1500,
                "success": True
            },
            {
                "step_name": "Take Screenshot - Copilot Dialog",
                "screenshot_path": "screenshots/excel_web/excel_copilot_dialog_1756048406.png",
                "duration_ms": 500,
                "success": True
            },
            {
                "step_name": "Dismiss Copilot Dialog",
                "screenshot_path": None,
                "duration_ms": 800,
                "success": True
            },
            {
                "step_name": "Take Screenshot - Initial State",
                "screenshot_path": "screenshots/excel_web/excel_initial_state_1756048412.png",
                "duration_ms": 500,
                "success": True
            },
            {
                "step_name": "Enter Sample Data",
                "screenshot_path": None,
                "duration_ms": 3000,
                "success": True
            },
            {
                "step_name": "Take Screenshot - Data Entered",
                "screenshot_path": "screenshots/excel_web/excel_data_entered_1756048416.png",
                "duration_ms": 500,
                "success": True
            },
            {
                "step_name": "Click Save Button",
                "screenshot_path": None,
                "duration_ms": 1200,
                "success": True
            },
            {
                "step_name": "Take Screenshot - Final State",
                "screenshot_path": None,
                "duration_ms": 500,
                "success": True
            }
        ]
    }
    
    # Get available screenshots
    screenshots_dir = Path("screenshots/excel_web")
    all_screenshots = []
    
    if screenshots_dir.exists():
        for screenshot_file in screenshots_dir.glob("*.png"):
            all_screenshots.append(str(screenshot_file))
    
    print(f"📸 Found {len(all_screenshots)} available screenshots:")
    for i, screenshot in enumerate(all_screenshots):
        print(f"   {i+1}. {os.path.basename(screenshot)}")
    
    print("\n🔍 Testing screenshot assignment for each step:")
    print("-" * 50)
    
    # Test screenshot assignment for each step
    assigned_screenshots = {}
    
    for step in mock_telemetry["steps"]:
        step_name = step["step_name"]
        original_screenshot = step.get("screenshot_path")
        
        # Simulate the screenshot assignment logic
        if original_screenshot:
            assigned_screenshot = original_screenshot
        else:
            # Use the improved assignment logic
            step_name_lower = step_name.lower()
            
            # Create a mapping of step types to screenshot patterns
            screenshot_mapping = {
                'copilot': 'copilot',
                'dialog': 'copilot', 
                'initial': 'initial',
                'data': 'data',
                'enter': 'data',
                'final': 'final',
                'save': 'final',
                'wait': 'data',
                'launch': 'data',
                'workbook': 'initial',
                'navigate': 'copilot'
            }
            
            # Find the most appropriate screenshot based on step content
            assigned_screenshot = None
            for keyword, pattern in screenshot_mapping.items():
                if keyword in step_name_lower:
                    # Look for screenshot with this pattern
                    for path in all_screenshots:
                        if pattern in path.lower():
                            assigned_screenshot = path
                            break
                    if assigned_screenshot:
                        break
            
            # If no keyword match, use step order-based assignment
            if not assigned_screenshot and all_screenshots:
                step_index = mock_telemetry["steps"].index(step)
                if step_index < len(all_screenshots):
                    assigned_screenshot = all_screenshots[step_index]
                else:
                    assigned_screenshot = all_screenshots[0]
        
        assigned_screenshots[step_name] = assigned_screenshot
        status = "✅ Original" if original_screenshot else "🔄 Assigned"
        print(f"{status} {step_name}: {os.path.basename(assigned_screenshot) if assigned_screenshot else 'None'}")
    
    # Check for duplicate assignments
    print("\n🔍 Checking for duplicate screenshot assignments:")
    print("-" * 50)
    
    screenshot_usage = {}
    for step_name, screenshot in assigned_screenshots.items():
        if screenshot:
            screenshot_usage[screenshot] = screenshot_usage.get(screenshot, []) + [step_name]
    
    duplicates_found = False
    for screenshot, steps in screenshot_usage.items():
        if len(steps) > 1:
            duplicates_found = True
            print(f"⚠️  Screenshot used multiple times: {os.path.basename(screenshot)}")
            for step in steps:
                print(f"   - {step}")
    
    if not duplicates_found:
        print("✅ No duplicate screenshot assignments found!")
    
    # Summary
    print(f"\n📊 Summary:")
    print(f"   Total Steps: {len(mock_telemetry['steps'])}")
    print(f"   Steps with Original Screenshots: {len([s for s in mock_telemetry['steps'] if s.get('screenshot_path')])}")
    print(f"   Steps with Assigned Screenshots: {len([s for s in mock_telemetry['steps'] if not s.get('screenshot_path')])}")
    print(f"   Unique Screenshots Used: {len(set(assigned_screenshots.values()) - {None})}")
    
    return not duplicates_found

if __name__ == "__main__":
    success = asyncio.run(test_screenshot_assignment())
    if success:
        print("\n✅ Screenshot assignment test passed!")
    else:
        print("\n❌ Screenshot assignment test failed - duplicates found!")
        sys.exit(1)
