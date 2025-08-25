#!/usr/bin/env python3
"""
Test Final Analyzer with Known Issues
"""

import asyncio
from final_craft_bug_analyzer import FinalCraftBugAnalyzer

async def test_with_known_issues():
    """Test the final analyzer with screenshots that we know have craft bugs"""
    
    # Test with screenshots that we know have issues from our previous analysis
    test_steps = [
        {
            'step_name': 'Excel Initial State',
            'description': 'Excel web app initial interface with toolbar and ribbon',
            'screenshot_path': 'screenshots/excel_web/excel_initial_state_1756061972.png',
            'scenario_description': 'Excel Document Creation with Copilot - Known Issues Test',
            'persona_type': 'Power User'
        },
        {
            'step_name': 'Copilot Dialog',
            'description': 'Copilot dialog with suggestions and close button',
            'screenshot_path': 'screenshots/excel_web/excel_copilot_dialog_1756061967.png',
            'scenario_description': 'Excel Document Creation with Copilot - Known Issues Test',
            'persona_type': 'Power User'
        },
        {
            'step_name': 'Save Dialog',
            'description': 'Save dialog with buttons and form elements',
            'screenshot_path': 'screenshots/excel_web/excel_final_state_1755521895.png',
            'scenario_description': 'Excel Document Creation with Copilot - Known Issues Test',
            'persona_type': 'Power User'
        }
    ]
    
    print("🎯 Testing Final Analyzer with Known Issues")
    print("📊 Expected Issues from Previous Analysis:")
    print("   - Color contrast issues")
    print("   - Spacing inconsistencies")
    print("   - Typography mismatches")
    print("   - Alignment problems")
    print("   - Component token violations")
    print()
    
    # Initialize analyzer
    analyzer = FinalCraftBugAnalyzer()
    
    # Run analysis
    bugs = await analyzer.analyze_screenshots(test_steps)
    
    print(f"\n🎯 Final Analysis Results: {len(bugs)} craft bugs detected")
    
    if bugs:
        print("\n📋 DETECTED BUGS:")
        for i, bug in enumerate(bugs, 1):
            print(f"\n--- Bug {i} ---")
            print(f"Title: {bug.get('title', 'Unknown')}")
            print(f"Type: {bug.get('type', 'Unknown')}")
            print(f"Severity: {bug.get('severity', 'Unknown')}")
            print(f"Expected: {bug.get('expected', 'Unknown')}")
            print(f"Actual: {bug.get('actual', 'Unknown')}")
            print(f"What to Correct: {bug.get('what_to_correct', 'Unknown')}")
            print(f"Affected Steps: {bug.get('affected_steps', 'Unknown')}")
            print(f"Visual Impact: {bug.get('impact', 'Unknown')}")
    else:
        print("\n❌ No bugs detected - this might indicate:")
        print("   - Screenshots don't have obvious craft bugs")
        print("   - Prompt is too restrictive")
        print("   - Need to test with different screenshots")
        print("   - Model needs more specific guidance")

if __name__ == "__main__":
    asyncio.run(test_with_known_issues())

