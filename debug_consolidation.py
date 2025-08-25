#!/usr/bin/env python3
"""
Debug Consolidation Output
See what GPT-4o actually returned during consolidation
"""

import asyncio
from consolidation_analyzer import ConsolidationAnalyzer

async def debug_consolidation():
    """Debug the consolidation output"""
    
    print("🔍 DEBUGGING CONSOLIDATION OUTPUT")
    print("=" * 60)
    
    analyzer = ConsolidationAnalyzer()
    
    # Test with a smaller subset of bugs
    test_bugs = [
        {
            'title': 'Low color contrast in toolbar',
            'type': 'Accessibility',
            'severity': 'Red',
            'step_name': 'Navigate to Excel',
            'description': 'Text elements have insufficient contrast ratios',
            'impact': 'Makes content difficult to read for users with visual impairments',
            'immediate_fix': 'Increase contrast ratio to meet WCAG guidelines'
        },
        {
            'title': 'Insufficient contrast in dialog text',
            'type': 'Accessibility',
            'severity': 'Orange',
            'step_name': 'Dismiss Copilot Dialog',
            'description': 'Dialog text has poor contrast against background',
            'impact': 'Difficult to read for users with visual impairments',
            'immediate_fix': 'Increase text contrast ratio'
        },
        {
            'title': 'Dialog positioning blocks content',
            'type': 'Layout',
            'severity': 'Red',
            'step_name': 'Dismiss Copilot Dialog',
            'description': 'Dialog appears in position that obscures important content',
            'impact': 'Users can\'t see underlying spreadsheet data',
            'immediate_fix': 'Reposition dialog to avoid content obstruction'
        }
    ]
    
    test_steps = [
        {
            'step_name': 'Navigate to Excel',
            'description': 'User navigates to Excel web app',
            'screenshot_path': 'screenshots/excel_web/excel_initial_state_1756061972.png',
            'scenario_description': 'Excel Document Creation',
            'persona_type': 'User'
        },
        {
            'step_name': 'Dismiss Copilot Dialog',
            'description': 'User dismisses the Copilot dialog',
            'screenshot_path': 'screenshots/excel_web/excel_copilot_dialog_1756061967.png',
            'scenario_description': 'Excel Document Creation',
            'persona_type': 'User'
        }
    ]
    
    # Get the raw consolidation output
    context = analyzer._prepare_consolidation_context(test_bugs, test_steps)
    raw_output = await analyzer._run_consolidation_analysis(context)
    
    print(f"📄 RAW GPT-4o OUTPUT ({len(raw_output)} characters):")
    print("=" * 60)
    print(raw_output)
    print("=" * 60)
    
    # Try parsing
    consolidated_bugs = analyzer._parse_consolidated_bugs(raw_output, test_steps)
    
    print(f"\n🔍 PARSING RESULTS:")
    print(f"   Parsed bugs: {len(consolidated_bugs)}")
    
    if consolidated_bugs:
        for i, bug in enumerate(consolidated_bugs, 1):
            print(f"   Bug {i}: {bug.get('title')}")

if __name__ == "__main__":
    asyncio.run(debug_consolidation())

