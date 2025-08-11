#!/usr/bin/env python3
"""
Test script to verify the complete end-to-end mock app analysis flow
"""

import requests
import json
import time
import sys

BASE_URL = "http://127.0.0.1:8000"
MOCK_APP_URL = "http://localhost:4174/mocks/word/basic-doc.html"

def test_scenarios_api():
    """Test that scenarios are available"""
    print("🔍 Testing scenarios API...")
    response = requests.get(f"{BASE_URL}/api/scenarios")
    if response.status_code != 200:
        print(f"❌ Scenarios API failed: {response.status_code}")
        return False
    
    data = response.json()
    scenarios = data.get('scenarios', [])
    word_scenarios = [s for s in scenarios if s.get('app_type') == 'word']
    
    print(f"✅ Found {len(scenarios)} total scenarios, {len(word_scenarios)} Word scenarios")
    for scenario in word_scenarios[:3]:
        print(f"   - {scenario['name']}")
    
    return len(word_scenarios) > 0

def test_mock_app_url():
    """Test that mock app URL is accessible"""
    print(f"🔍 Testing mock app URL: {MOCK_APP_URL}")
    try:
        response = requests.get(MOCK_APP_URL, timeout=5)
        if response.status_code == 200:
            print("✅ Mock app URL is accessible")
            return True
        else:
            print(f"❌ Mock app URL returned: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Mock app URL failed: {e}")
        return False

def test_mock_scenario_analysis():
    """Test complete mock scenario analysis"""
    print("🔍 Testing mock scenario analysis...")
    
    scenario_content = """# Mock app scenario for word
tests:
  Mock App Analysis:
    description: Automated testing of word application
    scenarios:
    - name: App Interface Analysis
      steps:
      - action: navigate_to_url
        url: "{url}"
      - action: wait_for_element
        selector: "body"
        timeout: 5000
      - action: accessibility_scan
        scope: full_page
      - action: performance_check
        metrics: ['load_time', 'responsiveness']
    - name: User Experience Evaluation
      steps:
      - action: ui_consistency_check
        scope: all_elements
      - action: navigation_flow_test
        verify_usability: true"""

    files = {
        'scenario_file': ('mock-scenario.yaml', scenario_content, 'text/yaml')
    }
    data = {
        'url': MOCK_APP_URL
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/analyze/scenario", files=files, data=data)
        if response.status_code != 200:
            print(f"❌ Analysis request failed: {response.status_code}")
            print(f"Response: {response.text}")
            return None
        
        result = response.json()
        analysis_id = result.get('analysis_id')
        print(f"✅ Analysis started with ID: {analysis_id}")
        return analysis_id
        
    except Exception as e:
        print(f"❌ Analysis request failed: {e}")
        return None

def test_report_retrieval(analysis_id):
    """Test report retrieval"""
    print(f"🔍 Testing report retrieval for {analysis_id}...")
    
    try:
        response = requests.get(f"{BASE_URL}/api/reports/{analysis_id}")
        if response.status_code != 200:
            print(f"❌ Report retrieval failed: {response.status_code}")
            return False
        
        report = response.json()
        print(f"✅ Report retrieved successfully")
        print(f"   - Status: {report.get('status')}")
        print(f"   - Overall Score: {report.get('overall_score')}")
        print(f"   - Scenario Results: {len(report.get('scenario_results', []))}")
        print(f"   - Module Results: {len(report.get('module_results', {}))}")
        
        return True
        
    except Exception as e:
        print(f"❌ Report retrieval failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Starting End-to-End Mock App Analysis Test")
    print("=" * 50)
    
    # Test 1: Scenarios API
    if not test_scenarios_api():
        print("❌ Scenarios test failed")
        return False
    
    print()
    
    # Test 2: Mock App URL
    if not test_mock_app_url():
        print("❌ Mock app URL test failed")
        return False
    
    print()
    
    # Test 3: Mock Scenario Analysis
    analysis_id = test_mock_scenario_analysis()
    if not analysis_id:
        print("❌ Mock scenario analysis failed")
        return False
    
    print()
    
    # Test 4: Report Retrieval
    if not test_report_retrieval(analysis_id):
        print("❌ Report retrieval failed")
        return False
    
    print()
    print("🎉 All tests passed! End-to-end mock app analysis is working.")
    print(f"📊 Report URL: http://127.0.0.1:8080/reports/{analysis_id}")
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
