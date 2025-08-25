#!/usr/bin/env python3
"""
Generate a real comprehensive report to show format, structure, and bug quality
"""

import asyncio
import json
from pathlib import Path
from datetime import datetime
from final_craft_bug_analyzer import FinalCraftBugAnalyzer
from comprehensive_report_generator import generate_comprehensive_html_report

async def generate_real_report():
    """Generate a real comprehensive report"""
    
    print("📊 Generating Real Comprehensive Report...")
    
    # Load existing telemetry data
    telemetry_file = Path("telemetry_output/telemetry_document_creation_20250825_125803.json")
    if not telemetry_file.exists():
        print("❌ Telemetry file not found. Please run a scenario first.")
        return
    
    with open(telemetry_file, 'r') as f:
        telemetry_data = json.load(f)
    
    print(f"📋 Loaded telemetry data with {len(telemetry_data.get('steps', []))} steps")
    
    # Get screenshots from telemetry
    screenshots_dir = Path("screenshots/excel_web")
    screenshot_files = list(screenshots_dir.glob("*.png"))
    
    if len(screenshot_files) < 3:
        print("❌ Not enough screenshots found.")
        return
    
    # Create steps data for analysis
    steps_data = []
    for i, step in enumerate(telemetry_data.get('steps', [])[:3]):  # Use first 3 steps
        screenshot_path = str(screenshot_files[i]) if i < len(screenshot_files) else None
        steps_data.append({
            "step_name": step.get('name', f'Step {i+1}'),
            "step_description": step.get('description', f'Test step {i+1}'),
            "screenshot_path": screenshot_path,
            "step_index": i
        })
    
    print(f"📸 Using {len(steps_data)} steps with screenshots for analysis")
    
    # Run analysis
    analyzer = FinalCraftBugAnalyzer()
    bugs = await analyzer.analyze_screenshots(steps_data)
    
    print(f"✅ Analysis complete: {len(bugs)} bugs found")
    
    # Assign screenshot paths to bugs based on step data
    enhanced_bugs = []
    for bug in bugs:
        # Find the most relevant screenshot for this bug
        # For now, assign the first screenshot to all bugs
        if steps_data and steps_data[0].get('screenshot_path'):
            enhanced_bug = bug.copy()
            enhanced_bug['screenshot_path'] = steps_data[0]['screenshot_path']
            enhanced_bug['step_name'] = steps_data[0]['step_name']
            enhanced_bugs.append(enhanced_bug)
        else:
            enhanced_bugs.append(bug)
    
    print(f"📸 Enhanced {len(enhanced_bugs)} bugs with screenshot paths")
    
    # Generate comprehensive HTML report
    scenario_name = telemetry_data.get('scenario_name', 'Excel Web Analysis')
    
    html_content = generate_comprehensive_html_report(
        bugs=enhanced_bugs,
        telemetry_data=telemetry_data,
        scenario_name=scenario_name
    )
    
    # Save report
    reports_dir = Path("reports/excel_ux")
    reports_dir.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_filename = f"real_comprehensive_report_{timestamp}.html"
    report_path = reports_dir / report_filename
    
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"✅ Real comprehensive report saved to: {report_path}")
    print(f"📊 Report URL: http://127.0.0.1:8000/reports/excel_ux/{report_filename}")
    
    # Show bug summary
    print(f"\n📋 Bug Summary:")
    print(f"   Total bugs: {len(enhanced_bugs)}")
    
    bug_types = {}
    severities = {}
    for bug in enhanced_bugs:
        bug_type = bug.get('type', 'Unknown')
        severity = bug.get('severity', 'Unknown')
        bug_types[bug_type] = bug_types.get(bug_type, 0) + 1
        severities[severity] = severities.get(severity, 0) + 1
    
    print(f"   Bug types: {bug_types}")
    print(f"   Severities: {severities}")
    
    # Show first few bugs
    print(f"\n🐛 Sample Bugs:")
    for i, bug in enumerate(enhanced_bugs[:5], 1):
        print(f"   {i}. {bug.get('title', 'N/A')} ({bug.get('type', 'N/A')} - {bug.get('severity', 'N/A')})")
        print(f"      Screenshot: {bug.get('screenshot_path', 'N/A')}")
    
    if len(enhanced_bugs) > 5:
        print(f"   ... and {len(enhanced_bugs) - 5} more bugs")
    
    return report_path

if __name__ == "__main__":
    asyncio.run(generate_real_report())
