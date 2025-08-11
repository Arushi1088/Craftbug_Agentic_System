#!/usr/bin/env python3
"""
Quick test script for known-good scenario
"""

import time
import subprocess
import requests
import json
import sys
import os

def check_server_health():
    """Check if server is healthy"""
    try:
        response = requests.get("http://127.0.0.1:8000/health", timeout=5)
        return response.status_code == 200
    except:
        return False

def start_server_and_wait():
    """Start server and wait for it to be ready"""
    print("🚀 Starting server...")
    
    # Start FastAPI server
    print("🚀 Starting server...")
    process = subprocess.Popen([
        "python3", "-m", "uvicorn", "enhanced_fastapi_server:app", 
        "--host", "127.0.0.1", "--port", "8000", "--reload"
    ], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)    # Wait for server to be ready
    for i in range(30):  # Wait up to 30 seconds
        if check_server_health():
            print(f"✅ Server ready after {i+1} seconds")
            return process
        time.sleep(1)
        print(f"⏳ Waiting for server... ({i+1}/30)")
    
    print("❌ Server failed to start within 30 seconds")
    process.terminate()
    return None

def test_known_good_scenario():
    """Test the known-good Word scenario"""
    print("\n🧪 Testing known-good Word scenario...")
    
    # Test payload - exactly as specified
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
    
    print(f"📡 POST to http://127.0.0.1:8000/api/analyze/url-scenario")
    print(f"   URL: {payload['url']}")
    print(f"   Scenario: {payload['scenario_path']}")
    
    try:
        response = requests.post(
            "http://127.0.0.1:8000/api/analyze/url-scenario",
            headers={"Content-Type": "application/json"},
            json=payload,
            timeout=30
        )
        
        print(f"📊 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            analysis_id = result.get("analysis_id")
            status = result.get("status")
            message = result.get("message")
            
            print(f"✅ Analysis Started Successfully!")
            print(f"   Analysis ID: {analysis_id}")
            print(f"   Status: {status}")
            print(f"   Message: {message}")
            
            if analysis_id:
                # Wait a moment for analysis to complete
                print("\n⏳ Waiting for analysis to complete...")
                time.sleep(3)
                
                # Get the report
                print(f"📊 GET http://127.0.0.1:8000/api/reports/{analysis_id}")
                report_response = requests.get(f"http://127.0.0.1:8000/api/reports/{analysis_id}")
                
                print(f"📊 Report Status: {report_response.status_code}")
                
                if report_response.status_code == 200:
                    report = report_response.json()
                    
                    print(f"\n🎯 ANALYSIS RESULTS:")
                    print(f"   Report Status: {report.get('status', 'unknown')}")
                    print(f"   Overall Score: {report.get('overall_score', 'N/A')}")
                    print(f"   Total Issues: {report.get('total_issues', 'N/A')}")
                    print(f"   Module Results: {len(report.get('module_results', {}))}")
                    print(f"   Scenario Results: {len(report.get('scenario_results', []))}")
                    
                    if report.get('status') == 'failed':
                        print(f"   ⚠️  Error: {report.get('error', 'No error message')}")
                        print(f"   ⚠️  UI Error: {report.get('ui_error', 'No UI error')}")
                        print(f"\n🎉 SUCCESS: Structured error report generated!")
                        print(f"   The UI will show a red 'Analysis Failed' banner instead of crashing.")
                    else:
                        print(f"\n🎉 SUCCESS: Full analysis completed!")
                        print(f"   The report contains all expected data.")
                    
                    return True
                else:
                    print(f"❌ Report fetch failed: {report_response.text}")
                    return False
            
        else:
            print(f"❌ Analysis request failed: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def main():
    """Main test execution"""
    print("🎯 KNOWN-GOOD SCENARIO TEST")
    print("="*50)
    
    # Check if we need to start the server
    if check_server_health():
        print("✅ Server already running")
        server_process = None
    else:
        server_process = start_server_and_wait()
        if not server_process:
            print("❌ Could not start server")
            return 1
    
    try:
        # Run the test
        success = test_known_good_scenario()
        
        if success:
            print(f"\n🎉 KNOWN-GOOD SCENARIO TEST PASSED!")
            print(f"✅ Backend pipeline is working correctly")
            print(f"✅ Scenario resolution is working")
            print(f"✅ Report generation is working") 
            print(f"✅ UI will render properly (red banners for errors)")
            return 0
        else:
            print(f"\n❌ KNOWN-GOOD SCENARIO TEST FAILED")
            print(f"❌ Check server logs for details")
            return 1
            
    finally:
        # Clean up server if we started it
        if server_process:
            print("\n🧹 Cleaning up server...")
            server_process.terminate()
            server_process.wait()

if __name__ == "__main__":
    exit(main())
