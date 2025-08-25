#!/usr/bin/env python3
"""
Test Comprehensive Report Generator
"""

import asyncio
from comprehensive_report_generator import generate_comprehensive_html_report, save_comprehensive_report

async def test_comprehensive_report():
    """Test the comprehensive report generator"""
    
    # Sample bugs data
    sample_bugs = [
        {
            'title': 'Low contrast in toolbar icons',
            'type': 'Color',
            'severity': 'Orange',
            'description': 'Toolbar icons have insufficient contrast against the background',
            'impact': 'Makes icons difficult to see for users with visual impairments',
            'what_to_correct': 'Increase contrast ratio of toolbar icons',
            'affected_steps': 'Step 1 (excel_initial_state_1756061972.png)',
            'screenshot_path': 'screenshots/excel_web/excel_initial_state_1756061972.png',
            'expected': 'Icons should have sufficient contrast to be easily visible',
            'actual': 'Icons blend into the background, making them hard to see',
            'confidence': 'High'
        },
        {
            'title': 'Inconsistent spacing between toolbar items',
            'type': 'Spacing',
            'severity': 'Yellow',
            'description': 'The spacing between some toolbar items is inconsistent',
            'impact': 'Reduces visual hierarchy and professional appearance',
            'what_to_correct': 'Standardize spacing between toolbar items',
            'affected_steps': 'Step 1 (excel_initial_state_1756061972.png), Step 2 (excel_copilot_dialog_1756061967.png)',
            'screenshot_path': 'screenshots/excel_web/excel_copilot_dialog_1756061967.png',
            'expected': 'Equal spacing between all toolbar items',
            'actual': 'Uneven spacing observed',
            'confidence': 'Medium'
        },
        {
            'title': 'Overlapping elements in Copilot dialog',
            'type': 'Layout',
            'severity': 'Red',
            'description': 'Elements in the Copilot window overlap, causing readability issues',
            'impact': 'Users cannot read overlapping text and buttons',
            'what_to_correct': 'Fix element positioning to prevent overlap',
            'affected_steps': 'Step 2 (excel_copilot_dialog_1756061967.png)',
            'screenshot_path': 'screenshots/excel_web/excel_final_state_1755521895.png',
            'expected': 'Clear separation between elements',
            'actual': 'Overlapping text and buttons',
            'confidence': 'High'
        }
    ]
    
    # Sample telemetry data
    sample_telemetry = {
        'scenario_name': 'Excel Document Creation with Copilot',
        'steps': [
            {'step_name': 'Navigate to Excel', 'screenshot_path': 'screenshots/excel_web/excel_initial_state_1756061972.png'},
            {'step_name': 'Dismiss Copilot Dialog', 'screenshot_path': 'screenshots/excel_web/excel_copilot_dialog_1756061967.png'},
            {'step_name': 'Save Workbook', 'screenshot_path': 'screenshots/excel_web/excel_final_state_1755521895.png'}
        ]
    }
    
    print("🧪 Testing Comprehensive Report Generator...")
    
    # Generate comprehensive HTML report
    html_content = generate_comprehensive_html_report(
        bugs=sample_bugs,
        telemetry_data=sample_telemetry,
        scenario_name="Excel Web Analysis Test"
    )
    
    print(f"✅ Generated HTML report: {len(html_content)} characters")
    
    # Save the report
    filename = save_comprehensive_report(html_content, "test_comprehensive_report.html")
    
    print(f"✅ Test report saved: {filename}")
    print("🎉 Comprehensive report generator is working!")

if __name__ == "__main__":
    asyncio.run(test_comprehensive_report())

