#!/usr/bin/env python3
"""
Test script for the refactored CraftBugAnalyzer.
This script tests the new architecture without breaking existing functionality.
"""

import asyncio
import sys
import os

# Add the current directory to the path so we can import our modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.analyzers.craft_bug_analyzer import CraftBugAnalyzer
from config.settings import get_settings


async def test_refactored_analyzer():
    """Test the refactored analyzer with sample data."""
    print("🧪 Testing Refactored Craft Bug Analyzer...")
    
    try:
        # Initialize the refactored analyzer
        analyzer = CraftBugAnalyzer()
        print("✅ Refactored analyzer initialized successfully")
        
        # Test configuration
        settings = get_settings()
        print(f"✅ Configuration loaded: Model={settings.OPENAI_MODEL}, Max Tokens={settings.OPENAI_MAX_TOKENS}")
        
        # Sample test data (same as the original test)
        test_steps = [
            {
                'step_name': 'Navigate to Excel Web',
                'description': 'User navigates to Excel web app',
                'screenshot_path': 'screenshots/excel_web/excel_copilot_dialog_1756106826.png',
                'scenario_description': 'Excel Document Creation with Copilot',
                'persona_type': 'Power User'
            },
            {
                'step_name': 'Click New Workbook',
                'description': 'User clicks new workbook button',
                'screenshot_path': 'screenshots/excel_web/excel_initial_state_1756106832.png',
                'scenario_description': 'Excel Document Creation with Copilot',
                'persona_type': 'Power User'
            },
            {
                'step_name': 'Wait for Excel to Launch in New Window',
                'description': 'User waits for Excel to load',
                'screenshot_path': 'screenshots/excel_web/excel_data_entered_1756106836.png',
                'scenario_description': 'Excel Document Creation with Copilot',
                'persona_type': 'Power User'
            }
        ]
        
        # Filter out non-existent screenshots
        valid_steps = []
        for step in test_steps:
            if os.path.exists(step['screenshot_path']):
                valid_steps.append(step)
                print(f"  ✅ Found: {step['step_name']} → {os.path.basename(step['screenshot_path'])}")
            else:
                print(f"  ⚠️ Missing: {step['step_name']} → {os.path.basename(step['screenshot_path'])}")
        
        if not valid_steps:
            print("❌ No valid screenshots found for testing")
            return
        
        print(f"📸 Testing with {len(valid_steps)} screenshots")
        
        # Run analysis
        analysis_data = {'steps_data': valid_steps}
        result = await analyzer.analyze(analysis_data)
        
        # Display results
        print(f"\n🎯 Analysis Results:")
        print(f"✅ Success: {result.success}")
        print(f"📊 Total bugs: {len(result.bugs)}")
        print(f"🔍 Debug counters: {result.debug_counters}")
        
        if result.bugs:
            print(f"\n📋 Detected Bugs:")
            for i, bug in enumerate(result.bugs, 1):
                print(f"--- Bug {i} ---")
                print(f"Title: {bug.title}")
                print(f"Type: {bug.type}")
                print(f"Severity: {bug.severity}")
                print(f"Screenshot Paths: {len(bug.screenshot_paths)} assigned")
                for j, path in enumerate(bug.screenshot_paths, 1):
                    exists = "✅" if os.path.exists(path) else "❌"
                    print(f"  {exists} Screenshot {j}: {os.path.basename(path)}")
                print(f"Affected Steps: {len(bug.affected_steps)} referenced")
                print()
        
        # Summary
        print(f"📊 Summary:")
        print(f"  Total bugs: {len(result.bugs)}")
        print(f"  Total screenshots assigned: {sum(len(bug.screenshot_paths) for bug in result.bugs)}")
        print(f"  Valid screenshots: {sum(1 for bug in result.bugs for path in bug.screenshot_paths if os.path.exists(path))}")
        print(f"  Invalid screenshots: {sum(1 for bug in result.bugs for path in bug.screenshot_paths if not os.path.exists(path))}")
        
        if all(os.path.exists(path) for bug in result.bugs for path in bug.screenshot_paths):
            print("✅ SUCCESS: All screenshots are valid and properly assigned!")
            print("🎉 Refactored analyzer is working correctly!")
        else:
            print("❌ ISSUES FOUND: Some screenshots are invalid or missing")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_refactored_analyzer())
