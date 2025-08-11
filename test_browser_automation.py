#!/usr/bin/env python3
"""
Test script for real browser automation functionality
"""
import json
import requests
import time

def test_real_browser_automation():
    print("🚀 Testing Real Browser Automation")
    
    # Test data
    test_payload = {
        "url": "http://localhost:8080",
        "scenario_id": "1.1",
        "modules": {
            "performance": True,
            "accessibility": True,
            "usability": True
        }
    }
    
    print(f"📡 Sending request to http://localhost:8000/api/analyze")
    print(f"📋 Payload: {json.dumps(test_payload, indent=2)}")
    
    try:
        # Make the request
        start_time = time.time()
        response = requests.post(
            "http://localhost:8000/api/analyze",
            json=test_payload,
            timeout=60  # 60 second timeout for browser automation
        )
        end_time = time.time()
        
        print(f"⏱️  Request took {end_time - start_time:.2f} seconds")
        print(f"📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ SUCCESS! Real browser automation worked!")
            print(f"🎯 Analysis ID: {result.get('analysis_id', 'N/A')}")
            print(f"🏆 Overall Score: {result.get('overall_score', 'N/A')}")
            print(f"🔍 Total Issues Found: {result.get('total_issues', 'N/A')}")
            print(f"🤖 Browser Automation: {result.get('browser_automation', 'N/A')}")
            print(f"📈 Real Analysis: {result.get('real_analysis', 'N/A')}")
            print(f"⚡ Execution Mode: {result.get('mode', 'N/A')}")
            
            # Show module results
            modules = result.get('modules', {})
            print(f"\n📊 Module Results:")
            for module_name, module_data in modules.items():
                score = module_data.get('score', 'N/A')
                findings_count = len(module_data.get('findings', []))
                print(f"   {module_name}: Score {score}, {findings_count} findings")
            
            # Show some issues if found
            ux_issues = result.get('ux_issues', [])
            if ux_issues:
                print(f"\n🔍 Sample UX Issues Found:")
                for i, issue in enumerate(ux_issues[:3]):  # Show first 3
                    print(f"   {i+1}. {issue.get('type', 'unknown')}: {issue.get('message', 'No message')}")
            
            # Show scenario execution details
            scenario_info = result.get('scenario_info', {})
            if scenario_info:
                print(f"\n🎬 Scenario Execution:")
                print(f"   Name: {scenario_info.get('name', 'N/A')}")
                print(f"   Steps Total: {scenario_info.get('steps_total', 'N/A')}")
                print(f"   Steps Successful: {scenario_info.get('steps_successful', 'N/A')}")
                print(f"   Steps Failed: {scenario_info.get('steps_failed', 'N/A')}")
            
            return True
        else:
            print(f"❌ FAILED! Status: {response.status_code}")
            print(f"📄 Response: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ FAILED! Could not connect to server. Is it running on port 8000?")
        return False
    except requests.exceptions.Timeout:
        print("❌ FAILED! Request timed out. Browser automation may have taken too long.")
        return False
    except Exception as e:
        print(f"❌ FAILED! Unexpected error: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_real_browser_automation()
    if success:
        print("\n🎉 Real browser automation test PASSED!")
    else:
        print("\n💥 Real browser automation test FAILED!")
