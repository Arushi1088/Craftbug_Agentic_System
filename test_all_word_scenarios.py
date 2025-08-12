#!/usr/bin/env python3
"""
Comprehensive test script to test all Word scenarios and identify issues
"""

import requests
import json
import time
from typing import Dict, Any

# All Word scenarios to test
WORD_SCENARIOS = [
    {"id": "1.1", "name": "Basic Document Navigation"},
    {"id": "1.2", "name": "Comment Resolution Workflow with Craft Bug Detection"},
    {"id": "1.3", "name": "Interactive Document Editing with Craft Bug Triggers"},
    {"id": "1.4", "name": "Comment Workflow with Animation Conflicts"},
    {"id": "1.5", "name": "Insert Image and Add Alt Text"},
    {"id": "1.6", "name": "Performance-Heavy Interactive Text Editing"},
    {"id": "craft-1", "name": "Word Craft Bug Detection Test"},
    {"id": "craft-2", "name": "Word Performance Stress Test with Craft Bugs"}
]

def test_scenario(scenario: Dict[str, str]) -> Dict[str, Any]:
    """Test a single scenario and return results"""
    
    print(f"\n🧪 Testing Scenario {scenario['id']}: {scenario['name']}")
    print("=" * 60)
    
    payload = {
        "url": "http://127.0.0.1:8080/mocks/word/basic-doc.html",
        "scenario_id": scenario["id"],
        "modules": {
            "performance": True,
            "accessibility": True,
            "ux_heuristics": True
        }
    }
    
    try:
        # Start analysis
        response = requests.post(
            "http://127.0.0.1:8000/api/analyze",
            json=payload,
            timeout=120
        )
        
        if response.status_code != 200:
            return {
                "scenario": scenario,
                "status": "failed",
                "error": f"Analysis failed with status {response.status_code}",
                "issues": []
            }
        
        result = response.json()
        analysis_id = result.get("analysis_id")
        
        if not analysis_id:
            return {
                "scenario": scenario,
                "status": "failed",
                "error": "No analysis ID returned",
                "issues": []
            }
        
        print(f"✅ Analysis started: {analysis_id}")
        
        # Wait for analysis to complete
        time.sleep(15)
        
        # Get results
        results_response = requests.get(f"http://127.0.0.1:8000/api/reports/{analysis_id}")
        
        if results_response.status_code != 200:
            return {
                "scenario": scenario,
                "status": "failed",
                "error": f"Failed to get results: {results_response.status_code}",
                "issues": []
            }
        
        report = results_response.json()
        
        # Analyze results
        ux_issues = report.get("ux_issues", [])
        craft_bugs = [issue for issue in ux_issues if issue.get("type") == "craft_bug"]
        accessibility_issues = [issue for issue in ux_issues if issue.get("type") == "accessibility"]
        other_issues = [issue for issue in ux_issues if issue.get("type") not in ["craft_bug", "accessibility"]]
        
        # Check for specific issues
        element_not_found_issues = [issue for issue in ux_issues if "not found" in issue.get("message", "").lower()]
        timeout_issues = [issue for issue in ux_issues if "timeout" in issue.get("message", "").lower()]
        error_issues = [issue for issue in ux_issues if issue.get("status") == "error"]
        
        result = {
            "scenario": scenario,
            "status": "completed",
            "analysis_id": analysis_id,
            "total_issues": len(ux_issues),
            "craft_bugs": len(craft_bugs),
            "accessibility_issues": len(accessibility_issues),
            "other_issues": len(other_issues),
            "element_not_found": len(element_not_found_issues),
            "timeout_issues": len(timeout_issues),
            "error_issues": len(error_issues),
            "issues": ux_issues[:5]  # Show first 5 issues
        }
        
        print(f"📊 Results:")
        print(f"   - Total Issues: {result['total_issues']}")
        print(f"   - Craft Bugs: {result['craft_bugs']}")
        print(f"   - Accessibility Issues: {result['accessibility_issues']}")
        print(f"   - Element Not Found: {result['element_not_found']}")
        print(f"   - Timeout Issues: {result['timeout_issues']}")
        print(f"   - Error Issues: {result['error_issues']}")
        
        if element_not_found_issues:
            print(f"   ⚠️  Element Issues:")
            for issue in element_not_found_issues[:3]:
                print(f"      - {issue.get('message', 'Unknown issue')}")
        
        return result
        
    except Exception as e:
        return {
            "scenario": scenario,
            "status": "failed",
            "error": str(e),
            "issues": []
        }

def main():
    """Test all Word scenarios"""
    
    print("🎯 COMPREHENSIVE WORD SCENARIO TESTING")
    print("=" * 80)
    
    results = []
    
    for scenario in WORD_SCENARIOS:
        result = test_scenario(scenario)
        results.append(result)
        time.sleep(5)  # Wait between tests
    
    # Summary report
    print("\n📋 SUMMARY REPORT")
    print("=" * 80)
    
    successful_scenarios = [r for r in results if r["status"] == "completed"]
    failed_scenarios = [r for r in results if r["status"] == "failed"]
    
    print(f"✅ Successful Scenarios: {len(successful_scenarios)}/{len(WORD_SCENARIOS)}")
    print(f"❌ Failed Scenarios: {len(failed_scenarios)}/{len(WORD_SCENARIOS)}")
    
    if failed_scenarios:
        print(f"\n❌ Failed Scenarios:")
        for scenario in failed_scenarios:
            print(f"   - {scenario['scenario']['id']}: {scenario['scenario']['name']}")
            print(f"     Error: {scenario['error']}")
    
    # Element analysis
    total_element_issues = sum(r.get("element_not_found", 0) for r in successful_scenarios)
    total_timeout_issues = sum(r.get("timeout_issues", 0) for r in successful_scenarios)
    total_craft_bugs = sum(r.get("craft_bugs", 0) for r in successful_scenarios)
    
    print(f"\n🔍 Element Analysis:")
    print(f"   - Total Element Not Found Issues: {total_element_issues}")
    print(f"   - Total Timeout Issues: {total_timeout_issues}")
    print(f"   - Total Craft Bugs Detected: {total_craft_bugs}")
    
    # Recommendations
    print(f"\n💡 Recommendations:")
    
    if total_element_issues > 0:
        print(f"   ⚠️  Fix element selectors in scenarios")
    
    if total_timeout_issues > 0:
        print(f"   ⚠️  Increase timeout durations or fix slow elements")
    
    if total_craft_bugs == 0:
        print(f"   ⚠️  No craft bugs detected - check craft bug implementation")
    else:
        print(f"   ✅ Craft bugs are being detected properly")
    
    # Save detailed results
    with open("word_scenario_test_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"\n📄 Detailed results saved to: word_scenario_test_results.json")

if __name__ == "__main__":
    main()
