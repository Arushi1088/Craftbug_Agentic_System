#!/usr/bin/env python3
"""
Test script to verify Scenario 1.2 triggers craft bugs and UX issues
This tests the Comment Resolution Workflow with Craft Bug Detection
"""

import requests
import json
import time
from typing import Dict, Any

def test_scenario_1_2_craft_bugs():
    """Test that scenario 1.2 properly triggers craft bugs and UX issues"""
    
    print("🎯 Testing Scenario 1.2: Comment Resolution Workflow with Craft Bug Detection")
    print("=" * 80)
    
    # Test configuration
    payload = {
        "url": "http://127.0.0.1:8080/mocks/word/basic-doc.html",
        "scenario_id": "1.2",
        "modules": {
            "performance": True,
            "accessibility": True,
            "ux_heuristics": True  # This enables craft bug detection
        }
    }
    
    try:
        print("🚀 Starting analysis...")
        response = requests.post(
            "http://localhost:8000/api/analyze",
            json=payload,
            timeout=120
        )
        
        if response.status_code != 200:
            print(f"❌ Analysis failed with status {response.status_code}: {response.text}")
            return False
        
        result = response.json()
        analysis_id = result.get("analysis_id")
        
        if not analysis_id:
            print("❌ No analysis ID returned")
            return False
        
        print(f"✅ Analysis started with ID: {analysis_id}")
        
        # Wait for analysis to complete
        print("⏳ Waiting for analysis to complete...")
        time.sleep(10)
        
        # Get the results
        results_response = requests.get(f"http://localhost:8000/api/reports/{analysis_id}")
        
        if results_response.status_code != 200:
            print(f"❌ Failed to get results: {results_response.status_code}")
            return False
        
        report = results_response.json()
        
        # Analyze the results
        print("\n📊 Analysis Results:")
        print("-" * 40)
        
        # Check for craft bugs
        ux_issues = report.get("ux_issues", [])
        craft_bugs_found = []
        accessibility_issues = []
        ux_issues_found = []
        
        for issue in ux_issues:
            issue_type = issue.get("type", "").lower()
            message = issue.get("message", "").lower()
            
            if "craft" in issue_type or "craft" in message:
                craft_bugs_found.append(issue)
            elif "accessibility" in issue_type or "accessibility" in message:
                accessibility_issues.append(issue)
            else:
                ux_issues_found.append(issue)
        
        print(f"🐛 Craft Bugs Found: {len(craft_bugs_found)}")
        for bug in craft_bugs_found[:3]:  # Show first 3
            print(f"   - {bug.get('message', 'Craft bug detected')}")
        
        print(f"♿ Accessibility Issues: {len(accessibility_issues)}")
        for issue in accessibility_issues[:3]:  # Show first 3
            print(f"   - {issue.get('message', 'Accessibility issue')}")
        
        print(f"🎯 UX Issues Found: {len(ux_issues_found)}")
        for issue in ux_issues_found[:3]:  # Show first 3
            print(f"   - {issue.get('message', 'UX issue')}")
        
        # Check if we have the expected craft bug types
        expected_craft_bugs = ["animation_conflicts", "feedback_failure", "input_lag"]
        found_craft_bug_types = []
        
        for bug in craft_bugs_found:
            message = bug.get("message", "").lower()
            if any(bug_type in message for bug_type in expected_craft_bugs):
                found_craft_bug_types.append(bug)
        
        print(f"\n🎯 Expected Craft Bug Types Found: {len(found_craft_bug_types)}")
        for bug in found_craft_bug_types:
            print(f"   - {bug.get('message', 'Expected craft bug type')}")
        
        # Success criteria
        success = len(craft_bugs_found) > 0 and len(found_craft_bug_types) > 0
        
        if success:
            print(f"\n✅ SUCCESS: Scenario 1.2 properly triggered {len(craft_bugs_found)} craft bugs!")
            print(f"   - Found {len(found_craft_bug_types)} expected craft bug types")
            print(f"   - Accessibility issues: {len(accessibility_issues)} (expected, but not the main focus)")
        else:
            print(f"\n❌ FAILURE: Scenario 1.2 did not trigger expected craft bugs")
            print(f"   - Craft bugs found: {len(craft_bugs_found)}")
            print(f"   - Expected types found: {len(found_craft_bug_types)}")
        
        return success
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        return False

if __name__ == "__main__":
    success = test_scenario_1_2_craft_bugs()
    exit(0 if success else 1)
