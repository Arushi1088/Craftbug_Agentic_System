#!/usr/bin/env python3
"""
Comprehensive test for multi-screenshot analyzer
Tests with multiple screenshots and analyzes the full output
"""

import asyncio
import json
from multi_screenshot_analyzer import MultiScreenshotAnalyzer

async def test_comprehensive_multi_screenshot():
    """Test multi-screenshot analyzer with comprehensive data"""
    
    print("🚀 COMPREHENSIVE MULTI-SCREENSHOT TEST")
    print("=" * 50)
    
    analyzer = MultiScreenshotAnalyzer()
    
    # Test with more comprehensive data
    test_steps = [
        {
            'step_name': 'Navigate to Excel',
            'description': 'User navigates to Excel web app and sees initial interface',
            'screenshot_path': 'screenshots/excel_web/excel_initial_state_1756061972.png',
            'scenario_description': 'Excel Document Creation with Copilot',
            'persona_type': 'Power User'
        },
        {
            'step_name': 'Create New Workbook',
            'description': 'User creates a new blank workbook',
            'screenshot_path': 'screenshots/excel_web/excel_initial_state_1756061972.png',  # Using same for test
            'scenario_description': 'Excel Document Creation with Copilot',
            'persona_type': 'Power User'
        },
        {
            'step_name': 'Copilot Dialog Appears',
            'description': 'Copilot dialog appears with suggestions',
            'screenshot_path': 'screenshots/excel_web/excel_copilot_dialog_1756061967.png',
            'scenario_description': 'Excel Document Creation with Copilot',
            'persona_type': 'Power User'
        },
        {
            'step_name': 'Save Workbook',
            'description': 'User saves the workbook',
            'screenshot_path': 'screenshots/excel_web/excel_final_state_1755521895.png',
            'scenario_description': 'Excel Document Creation with Copilot',
            'persona_type': 'Power User'
        }
    ]
    
    print(f"📋 Testing with {len(test_steps)} steps...")
    print(f"📸 Screenshots: {len([s for s in test_steps if s.get('screenshot_path')])} files")
    print()
    
    # Run analysis
    bugs = await analyzer.analyze_multiple_screenshots(test_steps)
    
    print("\n📊 ANALYSIS RESULTS:")
    print("=" * 50)
    print(f"🎯 Total bugs found: {len(bugs)}")
    
    if bugs:
        print("\n🐛 BUG DETAILS:")
        for i, bug in enumerate(bugs, 1):
            print(f"\n--- Bug {i} ---")
            print(f"Title: {bug.get('title')}")
            print(f"Type: {bug.get('type')}")
            print(f"Severity: {bug.get('severity')}")
            print(f"Affected Steps: {bug.get('affected_steps')}")
            print(f"Screenshots: {len(bug.get('screenshot_paths', []))} files")
            print(f"Impact: {bug.get('impact', 'N/A')}")
            print(f"Fix: {bug.get('immediate_fix', 'N/A')}")
            
            # Show persona impact
            persona_impact = bug.get('persona_impact', {})
            if persona_impact:
                print(f"Persona Impact:")
                print(f"  Novice: {persona_impact.get('novice', 'N/A')}")
                print(f"  Power: {persona_impact.get('power', 'N/A')}")
                print(f"  Super Fans: {persona_impact.get('super_fans', 'N/A')}")
    else:
        print("ℹ️ No bugs detected - this could mean:")
        print("  - Screenshots are clean")
        print("  - GPT-4o didn't find issues")
        print("  - Prompt needs adjustment")
    
    # Test token usage estimation
    print(f"\n💰 TOKEN USAGE ESTIMATION:")
    print(f"Model: {analyzer.llm_model}")
    print(f"Max tokens: {analyzer.llm_max_tokens}")
    print(f"Temperature: {analyzer.llm_temperature}")
    
    # Test image compression
    print(f"\n🖼️ IMAGE COMPRESSION TEST:")
    for i, step in enumerate(test_steps, 1):
        screenshot_path = step.get('screenshot_path')
        if screenshot_path:
            try:
                compressed = await analyzer._compress_image(screenshot_path)
                if compressed:
                    size_kb = len(compressed) / 1024
                    print(f"Screenshot {i}: {size_kb:.1f} KB")
                else:
                    print(f"Screenshot {i}: Compression failed")
            except Exception as e:
                print(f"Screenshot {i}: Error - {e}")
    
    print(f"\n✅ COMPREHENSIVE TEST COMPLETE!")

if __name__ == "__main__":
    asyncio.run(test_comprehensive_multi_screenshot())

