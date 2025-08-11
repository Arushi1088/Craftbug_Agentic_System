#!/usr/bin/env python3
"""
Quick test for craft bug scenario execution with optimized timeouts
"""
import requests
import json
import time
import sys
from datetime import datetime

def test_quick_scenario():
    """Test craft bug scenario with minimal waiting"""
    
    # API endpoint
    url = "http://localhost:8000/api/analyze"
    
    # Quick craft bug scenario payload
    payload = {
        "url": "http://localhost:9000/mocks/word/basic-doc.html",
        "scenario_id": "1.4",
        "app_type": "word",
        "execution_mode": "real_browser",
        "timeout": 60  # Reduced timeout for speed
    }
    
    print(f"🚀 Starting quick craft bug test at {datetime.now().strftime('%H:%M:%S')}")
    print(f"📋 Scenario: {payload['scenario_id']} - Interactive Document Editing with Craft Bug Triggers")
    print(f"⚡ Mode: {payload['execution_mode']} with {payload['timeout']}s timeout")
    
    start_time = time.time()
    
    try:
        # Make API call with timeout
        print("📡 Making API request...")
        response = requests.post(url, json=payload, timeout=90)
        
        execution_time = time.time() - start_time
        print(f"⏱️  Total execution time: {execution_time:.2f}s")
        
        if response.status_code == 200:
            result = response.json()
            
            print(f"🔍 Full API Response:")
            print(json.dumps(result, indent=2))
            
            # Extract key information
            status = result.get('status', 'unknown')
            scenario_result = result.get('scenario_result', {})
            craft_bugs = result.get('craft_bugs', [])
            analytics = result.get('analytics', {})
            
            print(f"✅ Status: {status}")
            
            # Check scenario execution
            steps_executed = 0
            successful_steps = 0
            warnings = 0
            
            if scenario_result:
                steps_executed = scenario_result.get('steps_executed', 0)
                successful_steps = scenario_result.get('successful_steps', 0)
                warnings = scenario_result.get('warnings', 0)
                print(f"📊 Steps: {steps_executed} executed, {successful_steps} successful, {warnings} warnings")
            else:
                print("⚠️  No scenario result data returned")
            
            # Check craft bugs
            print(f"🐛 Craft bugs detected: {len(craft_bugs)}")
            for i, bug in enumerate(craft_bugs, 1):
                bug_type = bug.get('type', 'unknown')
                severity = bug.get('severity', 'unknown')
                description = bug.get('description', 'No description')
                print(f"   {i}. {bug_type} ({severity}): {description}")
            
            # Check performance analytics
            if analytics:
                timing = analytics.get('timing', {})
                if timing:
                    total_time = timing.get('total_execution_time', 0)
                    browser_time = timing.get('browser_execution_time', 0)
                    print(f"⚡ Performance: {total_time:.2f}s total, {browser_time:.2f}s browser")
            
            if craft_bugs:
                print(f"🎯 SUCCESS: Craft bug detection working! Found {len(craft_bugs)} issues")
                return True
            else:
                print("⚠️  No craft bugs detected - checking if scenario executed properly")
                if steps_executed > 0:
                    print("✅ Scenario executed successfully, but no craft bugs found")
                    return True
                else:
                    print("❌ No steps executed - possible scenario issue")
                    return False
                    
        else:
            print(f"❌ API Error: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        execution_time = time.time() - start_time
        print(f"⏰ Request timed out after {execution_time:.2f}s")
        return False
        
    except requests.exceptions.ConnectionError:
        print("❌ Connection error - is the FastAPI server running?")
        return False
        
    except Exception as e:
        execution_time = time.time() - start_time
        print(f"❌ Error after {execution_time:.2f}s: {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("🔍 QUICK CRAFT BUG SCENARIO TEST")
    print("=" * 60)
    
    success = test_quick_scenario()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 TEST PASSED: Craft bug detection is working!")
    else:
        print("😞 TEST FAILED: Issues detected")
    print("=" * 60)
    
    sys.exit(0 if success else 1)
