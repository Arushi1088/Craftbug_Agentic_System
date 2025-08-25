#!/usr/bin/env python3
"""
Simple Consolidated Bug Report Generator
"""

import asyncio
from consolidation_analyzer import ConsolidationAnalyzer

async def generate_simple_report():
    """Generate a simple consolidated report"""
    
    print("🔍 Generating Simple Consolidated Report...")
    
    analyzer = ConsolidationAnalyzer()
    
    # Sample bugs for testing
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
    
    # Run consolidation
    consolidated_bugs = await analyzer.consolidate_bugs(test_bugs, test_steps)
    
    # Generate simple HTML
    html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Consolidated Bug Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; }}
        .bug {{ background: #f5f5f5; padding: 20px; margin: 20px 0; border-radius: 8px; }}
        .title {{ font-size: 18px; font-weight: bold; margin-bottom: 10px; }}
        .meta {{ color: #666; margin-bottom: 10px; }}
        .description {{ margin-bottom: 10px; }}
        .fix {{ background: #e8f5e8; padding: 10px; border-radius: 5px; }}
    </style>
</head>
<body>
    <h1>Consolidated Bug Report</h1>
    <p><strong>Original bugs:</strong> {len(test_bugs)} | <strong>Consolidated:</strong> {len(consolidated_bugs)}</p>
"""
    
    for i, bug in enumerate(consolidated_bugs, 1):
        html_content += f"""
    <div class="bug">
        <div class="title">{bug.get('title', 'Unknown')}</div>
        <div class="meta">Type: {bug.get('type', 'Unknown')} | Severity: {bug.get('severity', 'Unknown')}</div>
        <div class="description"><strong>Issue:</strong> {bug.get('description', 'No description')}</div>
        <div class="description"><strong>Impact:</strong> {bug.get('impact', 'No impact')}</div>
        <div class="fix"><strong>Fix:</strong> {bug.get('immediate_fix', 'No fix')}</div>
    </div>
"""
    
    html_content += """
</body>
</html>
"""
    
    with open('simple_consolidated_report.html', 'w') as f:
        f.write(html_content)
    
    print("✅ Simple consolidated report generated: simple_consolidated_report.html")

if __name__ == "__main__":
    asyncio.run(generate_simple_report())

