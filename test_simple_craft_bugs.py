#!/usr/bin/env python3
"""
Simple test for Word scenario 1.4 craft bug analysis through dashboard
"""

import requests
import json
import time

def test_word_scenario_1_4():
    """Test Word scenario 1.4 which includes craft bug triggers"""
    
    print("🎯 TESTING WORD SCENARIO 1.4 WITH CRAFT BUG DETECTION")
    print("=" * 60)
    
    api_url = "http://localhost:8000/api/analyze"
    
    # Use scenario 1.4 which is designed for craft bug detection
    request_data = {
        "url": "http://localhost:8080/mocks/word/basic-doc.html",
        "scenario_id": "1.4",
        "modules": {
            "accessibility": True,
            "performance": True,
            "ux_heuristics": True
        }
    }
    
    print(f"📤 API Request: {api_url}")
    print(f"📋 Data: {json.dumps(request_data, indent=2)}")
    
    try:
        response = requests.post(api_url, json=request_data, timeout=90)
        
        if response.status_code == 200:
            result = response.json()
            analysis_id = result.get("analysis_id")
            
            print(f"✅ Analysis initiated successfully!")
            print(f"📊 Analysis ID: {analysis_id}")
            print(f"📝 Status: {result.get('status')}")
            print(f"💬 Message: {result.get('message')}")
            
            # Wait for analysis completion  
            print(f"\n⏳ Waiting for analysis to complete...")
            time.sleep(10)
            
            # Get the report
            report_url = f"http://localhost:8000/api/reports/{analysis_id}"
            print(f"📥 Getting report: {report_url}")
            
            report_response = requests.get(report_url)
            if report_response.status_code == 200:
                report = report_response.json()
                
                print(f"\n📊 ANALYSIS COMPLETE!")
                print(f"✅ Status: {report.get('status', 'unknown')}")
                print(f"🎯 Overall Score: {report.get('overall_score', 'N/A')}")
                print(f"🐛 Total Issues: {report.get('total_issues', 0)}")
                
                # Show key findings
                if 'ux_issues' in report and report['ux_issues']:
                    print(f"\n🔍 UX ISSUES FOUND ({len(report['ux_issues'])}):")
                    for i, issue in enumerate(report['ux_issues'][:5], 1):
                        print(f"  {i}. {issue.get('description', 'Unknown issue')}")
                        print(f"     Severity: {issue.get('severity', 'unknown')}")
                        print(f"     Category: {issue.get('category', 'unknown')}")
                
                # Check for craft bug detection
                module_results = report.get('module_results', {})
                if module_results:
                    print(f"\n📋 MODULE RESULTS:")
                    for module, data in module_results.items():
                        if isinstance(data, dict) and 'findings' in data:
                            findings_count = len(data['findings'])
                            print(f"  📊 {module}: {findings_count} findings")
                            
                            # Show some findings
                            if findings_count > 0:
                                for finding in data['findings'][:3]:
                                    description = finding.get('description', 'Unknown')
                                    if 'craft' in description.lower() or 'lag' in description.lower() or 'animation' in description.lower():
                                        print(f"     🐛 POTENTIAL CRAFT BUG: {description}")
                
                print(f"\n🎉 SUCCESS! Dashboard analysis completed with scenario 1.4")
                print(f"📝 You can view this report in the dashboard using analysis ID: {analysis_id}")
                print(f"🌐 Dashboard URL: http://localhost:3000 (if running)")
                
                return True
            else:
                print(f"❌ Failed to get report: {report_response.status_code}")
                print(report_response.text)
        else:
            print(f"❌ API request failed: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
    
    return False

if __name__ == "__main__":
    success = test_word_scenario_1_4()
    if success:
        print(f"\n🎯 NEXT STEPS:")
        print(f"1. 🌐 Open dashboard at http://localhost:3000")
        print(f"2. 📊 Find your analysis in the reports")
        print(f"3. 🐛 Look for craft bug detections in the detailed view")
        print(f"4. 🎭 Try scenario 1.5 or 1.7 for more craft bug tests")
    else:
        print(f"\n💥 Test failed - check server logs")
