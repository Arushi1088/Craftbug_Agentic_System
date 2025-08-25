#!/usr/bin/env python3
"""
Test script to verify screenshot pipeline is working correctly.
This will test that each step gets its own screenshot and bugs are properly associated.
"""

import asyncio
import json
from pathlib import Path
from enhanced_ux_analyzer import EnhancedUXAnalyzer

async def test_screenshot_pipeline():
    """Test that screenshot pipeline assigns correct screenshots to each step"""
    
    print("🔍 TESTING SCREENSHOT PIPELINE...")
    
    # Initialize analyzer
    analyzer = EnhancedUXAnalyzer()
    
    # Create mock telemetry data with multiple steps and screenshots
    mock_telemetry = {
        "scenario_name": "Excel Document Creation",
        "steps": [
            {
                "step_name": "Navigate to Excel",
                "name": "Navigate to Excel",
                "description": "User navigates to Excel web app",
                "timing": 2.5,
                "success": True,
                "screenshot_path": "screenshots/excel_web/excel_initial_state_1756061972.png"
            },
            {
                "step_name": "Create New Workbook", 
                "name": "Create New Workbook",
                "description": "User creates a new blank workbook",
                "timing": 1.8,
                "success": True,
                "screenshot_path": "screenshots/excel_web/excel_workbook_created_1756061975.png"
            },
            {
                "step_name": "Dismiss Copilot Dialog",
                "name": "Dismiss Copilot Dialog", 
                "description": "User dismisses the Copilot dialog",
                "timing": 1.2,
                "success": True,
                "screenshot_path": "screenshots/excel_web/excel_copilot_dialog_1756061967.png"
            },
            {
                "step_name": "Enter Data",
                "name": "Enter Data",
                "description": "User enters data into cells",
                "timing": 3.1,
                "success": True,
                "screenshot_path": "screenshots/excel_web/excel_data_entered_1756061980.png"
            },
            {
                "step_name": "Save Workbook",
                "name": "Save Workbook",
                "description": "User saves the workbook",
                "timing": 2.0,
                "success": True,
                "screenshot_path": "screenshots/excel_web/excel_final_state_1755521895.png"
            }
        ]
    }
    
    print(f"📋 Testing with {len(mock_telemetry['steps'])} steps...")
    
    # Run analysis
    result = await analyzer.analyze_scenario_with_enhanced_data(mock_telemetry)
    
    # Extract bugs
    bugs = result.get('enhanced_craft_bugs', [])
    
    print(f"🎯 Found {len(bugs)} bugs total")
    
    # Analyze screenshot distribution
    screenshot_usage = {}
    step_bug_counts = {}
    
    for bug in bugs:
        screenshot_path = bug.get('screenshot_path', '')
        step_name = bug.get('step_name', 'Unknown')
        
        # Count screenshot usage
        if screenshot_path:
            screenshot_usage[screenshot_path] = screenshot_usage.get(screenshot_path, 0) + 1
        
        # Count bugs per step
        step_bug_counts[step_name] = step_bug_counts.get(step_name, 0) + 1
    
    print("\n📊 SCREENSHOT USAGE ANALYSIS:")
    print("=" * 50)
    
    for screenshot, count in screenshot_usage.items():
        print(f"📸 {screenshot}: {count} bugs")
    
    print("\n📊 BUGS PER STEP:")
    print("=" * 50)
    
    for step_name, count in step_bug_counts.items():
        print(f"🔍 {step_name}: {count} bugs")
    
    # Check for issues
    issues_found = []
    
    # Check if any screenshot is overused (>50% of bugs)
    total_bugs = len(bugs)
    for screenshot, count in screenshot_usage.items():
        percentage = (count / total_bugs) * 100 if total_bugs > 0 else 0
        if percentage > 50:
            issues_found.append(f"⚠️ Screenshot {screenshot} used for {percentage:.1f}% of bugs ({count}/{total_bugs})")
    
    # Check if all steps have bugs
    for step in mock_telemetry['steps']:
        step_name = step['step_name']
        if step_name not in step_bug_counts:
            issues_found.append(f"⚠️ Step '{step_name}' has no bugs")
    
    # Check if bugs have proper screenshot paths
    bugs_without_screenshots = [bug for bug in bugs if not bug.get('screenshot_path')]
    if bugs_without_screenshots:
        issues_found.append(f"⚠️ {len(bugs_without_screenshots)} bugs have no screenshot path")
    
    print("\n🔍 PIPELINE ANALYSIS:")
    print("=" * 50)
    
    if issues_found:
        print("❌ ISSUES FOUND:")
        for issue in issues_found:
            print(f"   {issue}")
    else:
        print("✅ PIPELINE LOOKS GOOD!")
        print("   - Screenshots are distributed across multiple files")
        print("   - Each step has bugs associated with it")
        print("   - All bugs have screenshot paths")
    
    # Show sample bugs with their screenshots
    print("\n📋 SAMPLE BUGS WITH SCREENSHOTS:")
    print("=" * 50)
    
    for i, bug in enumerate(bugs[:5]):  # Show first 5 bugs
        print(f"🐛 Bug {i+1}: {bug.get('title', 'Unknown')}")
        print(f"   Step: {bug.get('step_name', 'Unknown')}")
        print(f"   Screenshot: {bug.get('screenshot_path', 'None')}")
        print(f"   Type: {bug.get('type', 'Unknown')}")
        print(f"   Severity: {bug.get('severity', 'Unknown')}")
        print()

if __name__ == "__main__":
    asyncio.run(test_screenshot_pipeline())
