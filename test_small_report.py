#!/usr/bin/env python3
"""
Test the full report generation with a small batch of screenshots
"""

import asyncio
import json
from pathlib import Path
from final_craft_bug_analyzer import FinalCraftBugAnalyzer
from comprehensive_report_generator import generate_comprehensive_html_report

async def test_small_report():
    """Test full report generation with small batch"""
    
    print("🧪 Testing Full Report Generation with Small Batch...")
    
    # Load existing telemetry data
    telemetry_file = Path("telemetry_output/telemetry_document_creation_20250825_125803.json")
    if not telemetry_file.exists():
        print("❌ Telemetry file not found")
        return
    
    with open(telemetry_file, 'r') as f:
        telemetry_data = json.load(f)
    
    # Get only 2-3 steps with screenshots for testing
    steps_with_screenshots = []
    for step in telemetry_data.get('steps', []):
        if step.get('screenshot_path') and Path(step['screenshot_path']).exists():
            steps_with_screenshots.append(step)
            if len(steps_with_screenshots) >= 3:  # Limit to 3 for testing
                break
    
    print(f"📸 Testing with {len(steps_with_screenshots)} screenshots")
    
    # Initialize analyzer
    analyzer = FinalCraftBugAnalyzer()
    
    # Run analysis
    bugs = await analyzer.analyze_screenshots(steps_with_screenshots)
    
    print(f"✅ Found {len(bugs)} bugs")
    
    if not bugs:
        print("❌ No bugs found, cannot test report generation")
        return False
    
    # Test report generation
    try:
        print("📄 Generating test report...")
        
        # Create test telemetry data
        test_telemetry = {
            'scenario_name': 'Test Small Batch',
            'persona_type': 'Power User',
            'steps': steps_with_screenshots
        }
        
        # Generate report
        html_content = generate_comprehensive_html_report(
            bugs=bugs,
            telemetry_data=test_telemetry,
            scenario_name="Test Small Batch Analysis"
        )
        
        # Save test report
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        test_report_path = f"reports/excel_ux/test_small_batch_report_{timestamp}.html"
        
        # Ensure directory exists
        Path("reports/excel_ux").mkdir(parents=True, exist_ok=True)
        
        with open(test_report_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"✅ Test report saved to: {test_report_path}")
        
        # Check if report contains embedded images
        if "data:image/png;base64," in html_content:
            print("✅ Report contains embedded screenshots")
        else:
            print("⚠️ Report does not contain embedded screenshots")
        
        # Open the test report
        import subprocess
        subprocess.run(['open', test_report_path])
        
        print("🎉 SUCCESS: Full report generation working!")
        return True
        
    except Exception as e:
        print(f"❌ Report generation failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_small_report())
    if success:
        print("\n🎉 Ready for full analysis on dashboard!")
    else:
        print("\n⚠️ Please fix issues before running full analysis")
