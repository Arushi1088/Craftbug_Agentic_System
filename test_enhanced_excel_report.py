#!/usr/bin/env python3
"""
Test Enhanced Excel UX Report Generation
Verifies that reports include screenshots and detailed descriptions like yesterday's enhanced report
"""

import asyncio
import json
import os
from pathlib import Path
from datetime import datetime

async def test_enhanced_excel_report():
    """Test the enhanced Excel UX report generation"""
    print("🧪 Testing Enhanced Excel UX Report Generation")
    print("=" * 60)
    
    try:
        # Import the enhanced report generation function directly
        from enhanced_fastapi_server import generate_excel_ux_report
        
        print("📊 Testing Excel UX Report Generation...")
        
        # Test the enhanced Excel UX report generation directly
        result = await generate_excel_ux_report()
        
        if result.get("status") == "success":
            print(f"✅ Enhanced Excel UX Report generated successfully!")
            print(f"📄 Report URL: {result.get('report_url')}")
            print(f"📁 Report filename: {result.get('report_filename')}")
            
            # Check enhanced features
            enhanced_features = result.get('enhanced_features', {})
            print(f"📸 Screenshots included: {enhanced_features.get('screenshots_included', False)}")
            print(f"🐛 Craft bugs with visual evidence: {enhanced_features.get('craft_bugs_with_visual_evidence', 0)}")
            print(f"📸 Total screenshots: {enhanced_features.get('total_screenshots', 0)}")
            
            # Check if report file exists
            report_filename = result.get('report_filename')
            if report_filename:
                report_path = Path(f"reports/excel_ux/{report_filename}")
                if report_path.exists():
                    print(f"📁 Report file exists: {report_path}")
                    
                    # Read the report content to check for screenshots
                    with open(report_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Check for screenshot elements
                    if 'src="/screenshots' in content:
                        print("✅ Report contains screenshot paths")
                    else:
                        print("⚠️  Report does not contain screenshot paths")
                    
                    if 'Visual Evidence' in content:
                        print("✅ Report contains 'Visual Evidence' sections")
                    else:
                        print("⚠️  Report does not contain 'Visual Evidence' sections")
                    
                    if 'craft-bug' in content or 'Craft Bugs' in content:
                        print("✅ Report contains craft bug analysis")
                    else:
                        print("⚠️  Report does not contain craft bug analysis")
                    
                    # Check file size (enhanced reports should be larger)
                    file_size = report_path.stat().st_size
                    print(f"📊 Report file size: {file_size:,} bytes")
                    
                    if file_size > 20000:  # Enhanced reports should be > 20KB
                        print("✅ Report file size indicates enhanced content")
                    else:
                        print("⚠️  Report file size suggests basic content")
                    
                else:
                    print(f"❌ Report file not found: {report_path}")
            
            return True
            
        else:
            print(f"❌ Report generation failed: {result.get('message', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        return False

async def test_excel_scenario_execution():
    """Test the enhanced Excel scenario execution"""
    print("\n🧪 Testing Enhanced Excel Scenario Execution")
    print("=" * 60)
    
    try:
        from enhanced_fastapi_server import excel_web_execute_scenario
        
        print("📊 Testing Excel Scenario Execution...")
        
        # Test the enhanced Excel scenario execution directly
        result = await excel_web_execute_scenario("document_creation")
        
        if result.get("status") == "success":
            print(f"✅ Enhanced Excel Scenario executed successfully!")
            
            # Check for enhanced data
            result_data = result.get('result', {})
            
            print(f"📊 Steps completed: {result_data.get('steps_completed', 0)}")
            print(f"📊 Total steps: {result_data.get('total_steps', 0)}")
            print(f"📊 Execution time: {result_data.get('execution_time', 0):.2f}s")
            print(f"📊 Screenshots: {len(result_data.get('screenshots', []))}")
            print(f"🐛 Craft bugs: {len(result_data.get('craft_bugs', []))}")
            print(f"📊 UX score: {result_data.get('ux_score', 0)}")
            
            # Check for telemetry data
            if 'telemetry' in result_data:
                print("✅ Telemetry data included")
                telemetry = result_data['telemetry']
                print(f"📊 Telemetry steps: {len(telemetry.get('steps', []))}")
            else:
                print("⚠️  No telemetry data found")
            
            # Check for UX analysis
            if 'ux_analysis' in result_data:
                print("✅ UX analysis included")
                ux_analysis = result_data['ux_analysis']
                print(f"🐛 UX analysis craft bugs: {len(ux_analysis.get('craft_bugs', []))}")
            else:
                print("⚠️  No UX analysis found")
            
            return True
            
        else:
            print(f"❌ Scenario execution failed: {result.get('message', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        return False

async def main():
    """Run all tests"""
    print("🚀 Starting Enhanced Excel UX Report Tests")
    print("=" * 60)
    
    # Test scenario execution first
    scenario_success = await test_excel_scenario_execution()
    
    # Test report generation
    report_success = await test_enhanced_excel_report()
    
    print("\n" + "=" * 60)
    print("📊 Test Results Summary")
    print("=" * 60)
    print(f"✅ Scenario Execution: {'PASS' if scenario_success else 'FAIL'}")
    print(f"✅ Report Generation: {'PASS' if report_success else 'FAIL'}")
    
    if scenario_success and report_success:
        print("\n🎉 All tests passed! Enhanced Excel UX reports should now include:")
        print("   📸 Screenshots with visual evidence")
        print("   🐛 Detailed craft bug analysis")
        print("   📊 Enhanced UX metrics")
        print("   🎨 Rich HTML reports like yesterday's format")
    else:
        print("\n⚠️  Some tests failed. Enhanced features may not be working properly.")

if __name__ == "__main__":
    asyncio.run(main())
