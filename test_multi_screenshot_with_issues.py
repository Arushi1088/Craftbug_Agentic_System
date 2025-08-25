#!/usr/bin/env python3
"""
Test multi-screenshot analyzer with screenshots that have known issues
"""

import asyncio
from multi_screenshot_analyzer import MultiScreenshotAnalyzer

async def test_with_known_issues():
    """Test with screenshots that should have detectable issues"""
    
    print("🔍 TESTING WITH KNOWN ISSUES")
    print("=" * 50)
    
    analyzer = MultiScreenshotAnalyzer()
    
    # Use screenshots that are known to have issues from previous analysis
    test_steps = [
        {
            'step_name': 'Excel Initial State',
            'description': 'Initial Excel interface with potential visual issues',
            'screenshot_path': 'screenshots/excel_web/excel_initial_state_1756061972.png',
            'scenario_description': 'Excel Document Creation - Visual Issues Test',
            'persona_type': 'UX Designer'
        },
        {
            'step_name': 'Copilot Dialog',
            'description': 'Copilot dialog with potential interaction issues',
            'screenshot_path': 'screenshots/excel_web/excel_copilot_dialog_1756061967.png',
            'scenario_description': 'Excel Document Creation - Visual Issues Test',
            'persona_type': 'UX Designer'
        }
    ]
    
    print(f"📋 Testing with {len(test_steps)} steps...")
    print("🎯 These screenshots should have detectable UX issues")
    print()
    
    # Run analysis
    bugs = await analyzer.analyze_multiple_screenshots(test_steps)
    
    print("\n📊 RESULTS:")
    print("=" * 50)
    print(f"🎯 Bugs found: {len(bugs)}")
    
    if bugs:
        print("\n🐛 DETECTED ISSUES:")
        for i, bug in enumerate(bugs, 1):
            print(f"\n--- Issue {i} ---")
            print(f"Title: {bug.get('title')}")
            print(f"Type: {bug.get('type')}")
            print(f"Severity: {bug.get('severity')}")
            print(f"Affected Steps: {bug.get('affected_steps')}")
            print(f"Impact: {bug.get('impact', 'N/A')}")
            print(f"Fix: {bug.get('immediate_fix', 'N/A')}")
    else:
        print("ℹ️ No issues detected")
        print("This could mean:")
        print("  - Screenshots are actually clean")
        print("  - Issues are too subtle for detection")
        print("  - Prompt needs refinement")
    
    # Test the raw response to see what GPT-4o actually returned
    print(f"\n🔍 DEBUGGING:")
    print("=" * 50)
    
    # Let's see what the actual response was
    context = analyzer._prepare_multi_screenshot_context(test_steps)
    image_files = await analyzer._prepare_images_for_analysis(test_steps)
    
    if image_files:
        try:
            raw_response = await analyzer._run_gpt4o_analysis(context, image_files)
            print(f"📄 Raw GPT-4o Response ({len(raw_response)} chars):")
            print(f"'{raw_response}'")
        except Exception as e:
            print(f"❌ Failed to get raw response: {e}")
    
    print(f"\n✅ TEST COMPLETE!")

if __name__ == "__main__":
    asyncio.run(test_with_known_issues())

