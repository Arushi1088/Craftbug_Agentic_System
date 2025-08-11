#!/usr/bin/env python3
"""
Test Word Craft Bug Analysis through Dashboard API
This script tests the new /api/analyze/word-craft-bugs endpoint
"""

import requests
import json
import time

def test_word_craft_bug_dashboard():
    """Test Word craft bug detection through the dashboard API"""
    
    print("🎯 TESTING WORD CRAFT BUG ANALYSIS THROUGH DASHBOARD")
    print("=" * 60)
    
    # Test the new API endpoint
    api_url = "http://localhost:8000/api/analyze/word-craft-bugs"
    
    request_data = {
        "url": "http://localhost:8080/mocks/word/basic-doc.html",
        "scenario_id": "craft-1",
        "modules": {
            "accessibility": True,
            "performance": True,
            "craft_bugs": True
        }
    }
    
    print(f"📤 Making request to: {api_url}")
    print(f"📋 Request data: {json.dumps(request_data, indent=2)}")
    
    try:
        response = requests.post(api_url, json=request_data, timeout=120)
        
        if response.status_code == 200:
            result = response.json()
            analysis_id = result.get("analysis_id")
            
            print(f"✅ Analysis started successfully!")
            print(f"📊 Analysis ID: {analysis_id}")
            print(f"📝 Message: {result.get('message')}")
            
            # Wait for completion and get report
            print(f"\n⏳ Waiting 5 seconds for analysis to complete...")
            time.sleep(5)
            
            # Get the report
            report_url = f"http://localhost:8000/api/reports/{analysis_id}"
            print(f"📥 Fetching report from: {report_url}")
            
            report_response = requests.get(report_url)
            if report_response.status_code == 200:
                report = report_response.json()
                
                print(f"\n📊 ANALYSIS RESULTS:")
                print(f"✅ Status: {report.get('status')}")
                print(f"🎯 Overall Score: {report.get('overall_score', 'N/A')}")
                print(f"🐛 Total Issues: {report.get('total_issues', 0)}")
                print(f"🔍 Craft Bugs Detected: {report.get('craft_bugs_detected', 0)}")
                
                # Show craft bug details
                craft_bug_analysis = report.get('craft_bug_analysis', {})
                if craft_bug_analysis:
                    print(f"\n🐛 CRAFT BUG DETAILS:")
                    print(f"Total Bugs Found: {craft_bug_analysis.get('total_bugs_found', 0)}")
                    
                    findings = craft_bug_analysis.get('findings', [])
                    if findings:
                        print(f"\n🔍 CRAFT BUG FINDINGS:")
                        for i, finding in enumerate(findings, 1):
                            print(f"  {i}. {finding.get('description', 'Unknown')}")
                            print(f"     Category: {finding.get('category', 'Unknown')}")
                            print(f"     Severity: {finding.get('severity', 'Unknown')}")
                            print(f"     Location: {finding.get('location', 'Unknown')}")
                
                # Show module results
                module_results = report.get('module_results', {})
                if module_results:
                    print(f"\n📋 MODULE RESULTS:")
                    for module, data in module_results.items():
                        if module == 'craft_bugs':
                            print(f"  🐛 {module}: {data.get('total_detected', 0)} bugs detected")
                        else:
                            print(f"  📊 {module}: {len(data.get('findings', []))} issues")
                
                print(f"\n🎉 Dashboard API test completed successfully!")
                print(f"📝 You can view this report in the dashboard with ID: {analysis_id}")
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

def test_dashboard_workflow():
    """Test the complete dashboard workflow"""
    print("\n" + "="*60)
    print("🎯 TESTING COMPLETE DASHBOARD WORKFLOW")
    print("="*60)
    
    print("\n📋 Step 1: Check server status")
    try:
        health_response = requests.get("http://localhost:8000/health", timeout=5)
        if health_response.status_code == 200:
            print("✅ Backend server is running")
        else:
            print("❌ Backend server issues")
            return False
    except:
        print("❌ Backend server is not accessible")
        return False
    
    try:
        frontend_response = requests.get("http://localhost:8080/mocks/word/basic-doc.html", timeout=5)
        if frontend_response.status_code == 200 and 'craft' in frontend_response.text.lower():
            print("✅ Frontend server is running with craft bugs")
        else:
            print("❌ Frontend server or craft bugs not accessible")
            return False
    except:
        print("❌ Frontend server is not accessible")
        return False
    
    print("\n📋 Step 2: Test Word craft bug analysis")
    success = test_word_craft_bug_dashboard()
    
    if success:
        print("\n🎉 COMPLETE DASHBOARD WORKFLOW TEST SUCCESSFUL!")
        print("🎯 You can now:")
        print("1. Open the dashboard at http://localhost:3000")
        print("2. Use the Word craft bug analysis endpoint")
        print("3. View craft bug results in the reports")
    else:
        print("\n💥 Dashboard workflow test failed!")
    
    return success

if __name__ == "__main__":
    test_dashboard_workflow()
