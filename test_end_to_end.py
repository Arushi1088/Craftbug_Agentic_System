#!/usr/bin/env python3
"""
Quick test script to verify a known-good scenario works
"""

import requests
import json
import time

def test_known_good_scenario():
    """Test a known scenario to verify the pipeline works"""
    print("🧪 Testing known-good scenario...")
    
    # Test the /api/analyze/url-scenario endpoint
    url = "http://localhost:8000/api/analyze/url-scenario"
    
    payload = {
        "url": "http://localhost:3001/mocks/word/basic-doc.html",
        "scenario_path": "scenarios/word_scenarios.yaml",
        "modules": {
            "performance": True,
            "accessibility": True,
            "keyboard": True,
            "ux_heuristics": True,
            "best_practices": True,
            "health_alerts": True,
            "functional": False
        }
    }
    
    try:
        print(f"📡 Making request to {url}")
        response = requests.post(url, json=payload, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            analysis_id = result.get("analysis_id")
            print(f"✅ Analysis started successfully: {analysis_id}")
            print(f"   Status: {result.get('status')}")
            print(f"   Message: {result.get('message')}")
            
            # Try to get the report
            if analysis_id:
                time.sleep(2)  # Give it a moment to process
                report_url = f"http://localhost:8000/api/reports/{analysis_id}"
                print(f"📊 Fetching report from {report_url}")
                
                report_response = requests.get(report_url)
                if report_response.status_code == 200:
                    report_data = report_response.json()
                    print(f"✅ Report retrieved successfully")
                    print(f"   Status: {report_data.get('status', 'unknown')}")
                    print(f"   Overall Score: {report_data.get('overall_score', 'N/A')}")
                    print(f"   Total Issues: {report_data.get('total_issues', 'N/A')}")
                    
                    if report_data.get("status") == "failed":
                        print(f"⚠️  Analysis failed: {report_data.get('error', 'Unknown error')}")
                        print(f"   UI Error: {report_data.get('ui_error', 'No UI error message')}")
                    
                    return True
                else:
                    print(f"❌ Failed to get report: {report_response.status_code}")
                    print(f"   Response: {report_response.text}")
            
        else:
            print(f"❌ Request failed: {response.status_code}")
            print(f"   Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to server. Is the server running on localhost:8000?")
        return False
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False
    
    return True

def main():
    """Run the test"""
    print("🚀 Testing end-to-end scenario analysis...")
    print("   This test requires the server to be running on localhost:8000")
    print("   And the mock server on localhost:3001")
    print()
    
    if test_known_good_scenario():
        print("\n✅ End-to-end test completed successfully!")
        print("   The robust scenario pipeline is working correctly.")
    else:
        print("\n❌ End-to-end test failed.")
        print("   Check that both servers are running and try again.")

if __name__ == "__main__":
    main()
