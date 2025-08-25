#!/usr/bin/env python3
"""
Debug Final Craft Bug Analyzer
"""

import asyncio
from final_craft_bug_analyzer import FinalCraftBugAnalyzer

async def debug_analyzer():
    """Debug the final analyzer to see the actual response"""
    
    # Sample test data
    test_steps = [
        {
            'step_name': 'Navigate to Excel',
            'description': 'User navigates to Excel web app',
            'screenshot_path': 'screenshots/excel_web/excel_initial_state_1756061972.png',
            'scenario_description': 'Excel Document Creation with Copilot',
            'persona_type': 'Power User'
        },
        {
            'step_name': 'Dismiss Copilot Dialog',
            'description': 'User dismisses the Copilot dialog',
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
    
    # Initialize analyzer
    analyzer = FinalCraftBugAnalyzer()
    
    # Prepare context and images
    context = analyzer._prepare_context(test_steps)
    image_files = await analyzer._prepare_images(test_steps)
    
    print(f"📊 Context: {context}")
    print(f"📸 Images: {len(image_files)} files")
    
    # Run analysis and capture raw response
    analysis_text = await analyzer._run_analysis(context, image_files)
    
    print(f"\n🔍 RAW RESPONSE ({len(analysis_text)} characters):")
    print("=" * 50)
    print(analysis_text)
    print("=" * 50)
    
    # Check if it contains "no visible craft bugs"
    if "no visible craft bugs" in analysis_text.lower():
        print("\n❌ Response indicates no bugs found")
    else:
        print("\n✅ Response may contain bugs - let's parse")
        bugs = analyzer._parse_bugs(analysis_text, test_steps)
        print(f"📊 Parsed {len(bugs)} bugs")

if __name__ == "__main__":
    asyncio.run(debug_analyzer())

