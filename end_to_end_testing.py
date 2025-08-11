#!/usr/bin/env python3
"""
Comprehensive End-to-End Testing Script
Tests multiple scenarios across all Office apps with detailed analysis
"""

import requests
import json
import time
import sys
from typing import Dict, List, Any

# Test configurations for each Office app and scenario
TEST_SCENARIOS = [
    # Word scenarios
    {
        "app": "word",
        "scenario_id": "1.1",
        "name": "Basic Document Navigation",
        "url": "http://localhost:8080/mocks/word/basic-doc.html",
        "expected_issues": ["navigation", "accessibility", "craft_bugs"]
    },
    {
        "app": "word", 
        "scenario_id": "1.2",
        "name": "Comment Resolution Workflow",
        "url": "http://localhost:8080/mocks/word/basic-doc.html",
        "expected_issues": ["workflow", "comments", "craft_bugs"]
    },
    {
        "app": "word",
        "scenario_id": "1.3", 
        "name": "Document Editing and Formatting",
        "url": "http://localhost:8080/mocks/word/basic-doc.html",
        "expected_issues": ["editing", "formatting", "craft_bugs"]
    },
    
    # Excel scenarios
    {
        "app": "excel",
        "scenario_id": "excel_basic_nav",
        "name": "Excel: Open and format sheet", 
        "url": "http://localhost:8080/mocks/excel/open-format.html",
        "expected_issues": ["spreadsheet", "formatting", "craft_bugs"]
    },
    
    # PowerPoint scenarios
    {
        "app": "powerpoint",
        "scenario_id": "slide_creation",
        "name": "Slide Creation and Layout",
        "url": "http://localhost:8080/mocks/powerpoint/basic-deck.html", 
        "expected_issues": ["slides", "layout", "craft_bugs"]
    },
    {
        "app": "powerpoint",
        "scenario_id": "animation_controls",
        "name": "Animation and Transition Setup",
        "url": "http://localhost:8080/mocks/powerpoint/basic-deck.html",
        "expected_issues": ["animations", "transitions", "craft_bugs"]
    }
]

def wait_for_server(max_attempts=30):
    """Wait for the backend server to be ready"""
    for attempt in range(max_attempts):
        try:
            response = requests.get("http://localhost:8000/health", timeout=5)
            if response.status_code == 200:
                print("✅ Backend server is ready")
                return True
        except:
            print(f"⏳ Waiting for server... ({attempt + 1}/{max_attempts})")
            time.sleep(2)
    
    print("❌ Server failed to start")
    return False

def run_analysis(scenario: Dict[str, Any]) -> Dict[str, Any]:
    """Run analysis for a single scenario"""
    print(f"\n🧪 Testing {scenario['app'].upper()}: {scenario['name']}")
    print(f"   Scenario ID: {scenario['scenario_id']}")
    print(f"   URL: {scenario['url']}")
    
    # Start analysis
    payload = {
        "url": scenario["url"],
        "scenario_id": scenario["scenario_id"],
        "modules": {
            "performance": True,
            "accessibility": True,
            "ux_heuristics": True  # This enables craft bug detection
        }
    }
    
    try:
        # Start the analysis
        response = requests.post(
            "http://localhost:8000/api/analyze",
            json=payload,
            timeout=120  # 2 minutes timeout
        )
        
        if response.status_code != 200:
            return {
                "error": f"Analysis failed with status {response.status_code}: {response.text}",
                "scenario": scenario
            }
        
        result = response.json()
        analysis_id = result.get("analysis_id")
        
        if not analysis_id:
            return {
                "error": "No analysis ID returned",
                "scenario": scenario,
                "response": result
            }
        
        print(f"   ✅ Analysis started: {analysis_id}")
        
        # Wait for completion and get report
        time.sleep(5)  # Give it time to process
        
        report_response = requests.get(f"http://localhost:8000/api/reports/{analysis_id}")
        
        if report_response.status_code != 200:
            return {
                "error": f"Failed to get report: {report_response.status_code}",
                "analysis_id": analysis_id,
                "scenario": scenario
            }
        
        report = report_response.json()
        
        # Analyze the results
        analysis_result = analyze_report(report, scenario)
        analysis_result["analysis_id"] = analysis_id
        
        return analysis_result
        
    except Exception as e:
        return {
            "error": f"Exception during analysis: {str(e)}",
            "scenario": scenario
        }

def analyze_report(report: Dict[str, Any], scenario: Dict[str, Any]) -> Dict[str, Any]:
    """Analyze the report and extract key findings"""
    
    # Extract basic info
    ux_issues = report.get("ux_issues", [])
    performance_score = report.get("modules", {}).get("performance", {}).get("score", 0)
    accessibility_score = report.get("modules", {}).get("accessibility", {}).get("score", 0)
    
    # Count issues by type
    issue_types = {}
    craft_bugs = []
    accessibility_issues = []
    performance_issues = []
    
    for issue in ux_issues:
        issue_type = issue.get("type", "unknown")
        issue_types[issue_type] = issue_types.get(issue_type, 0) + 1
        
        # Categorize issues
        if "craft" in issue_type.lower() or "craft" in issue.get("message", "").lower():
            craft_bugs.append(issue)
        elif issue_type == "accessibility":
            accessibility_issues.append(issue)
        elif issue_type == "performance":
            performance_issues.append(issue)
    
    # Look for scenario-specific issues
    scenario_specific_issues = find_scenario_specific_issues(ux_issues, scenario)
    
    result = {
        "scenario": scenario,
        "status": report.get("status", "unknown"),
        "total_issues": len(ux_issues),
        "performance_score": performance_score,
        "accessibility_score": accessibility_score,
        "issue_breakdown": {
            "craft_bugs": len(craft_bugs),
            "accessibility": len(accessibility_issues), 
            "performance": len(performance_issues),
            "other": len(ux_issues) - len(craft_bugs) - len(accessibility_issues) - len(performance_issues)
        },
        "craft_bugs_found": craft_bugs,
        "accessibility_issues": accessibility_issues[:3],  # Show first 3
        "scenario_specific_issues": scenario_specific_issues,
        "issue_types_count": issue_types
    }
    
    return result

def find_scenario_specific_issues(ux_issues: List[Dict], scenario: Dict[str, Any]) -> List[Dict]:
    """Find issues that are specific to this scenario"""
    scenario_specific = []
    scenario_keywords = scenario["name"].lower().split() + [scenario["app"]]
    
    for issue in ux_issues:
        message = issue.get("message", "").lower()
        for keyword in scenario_keywords:
            if keyword in message and len(keyword) > 3:  # Skip short words
                scenario_specific.append(issue)
                break
    
    return scenario_specific

def print_test_summary(results: List[Dict[str, Any]]):
    """Print a comprehensive summary of all tests"""
    
    print("\n" + "="*80)
    print("🎯 COMPREHENSIVE END-TO-END TEST RESULTS")
    print("="*80)
    
    total_tests = len(results)
    successful_tests = len([r for r in results if "error" not in r])
    failed_tests = total_tests - successful_tests
    
    print(f"\n📊 OVERALL STATISTICS:")
    print(f"   Total tests run: {total_tests}")
    print(f"   ✅ Successful: {successful_tests}")
    print(f"   ❌ Failed: {failed_tests}")
    
    # App-wise breakdown
    app_stats = {}
    for result in results:
        if "error" not in result:
            app = result["scenario"]["app"]
            if app not in app_stats:
                app_stats[app] = {"total": 0, "craft_bugs": 0, "total_issues": 0}
            
            app_stats[app]["total"] += 1
            app_stats[app]["craft_bugs"] += result["issue_breakdown"]["craft_bugs"]
            app_stats[app]["total_issues"] += result["total_issues"]
    
    print(f"\n📱 APP-WISE BREAKDOWN:")
    for app, stats in app_stats.items():
        print(f"   {app.upper()}:")
        print(f"      Scenarios tested: {stats['total']}")
        print(f"      Total issues found: {stats['total_issues']}")
        print(f"      Craft bugs detected: {stats['craft_bugs']}")
        print(f"      Avg issues per scenario: {stats['total_issues']/stats['total']:.1f}")
    
    print(f"\n🔍 DETAILED SCENARIO RESULTS:")
    for i, result in enumerate(results, 1):
        if "error" in result:
            print(f"\n   {i}. ❌ {result['scenario']['app'].upper()}: {result['scenario']['name']}")
            print(f"      Error: {result['error']}")
        else:
            scenario = result["scenario"]
            print(f"\n   {i}. ✅ {scenario['app'].upper()}: {scenario['name']}")
            print(f"      Analysis ID: {result.get('analysis_id', 'N/A')}")
            print(f"      Total issues: {result['total_issues']}")
            print(f"      Performance score: {result['performance_score']}")
            print(f"      Accessibility score: {result['accessibility_score']}")
            print(f"      Issue breakdown: {result['issue_breakdown']}")
            
            # Show craft bugs if any
            if result["craft_bugs_found"]:
                print(f"      🐛 Craft bugs detected:")
                for bug in result["craft_bugs_found"][:2]:  # Show first 2
                    print(f"         - {bug.get('description', bug.get('message', 'Unknown'))}")
            
            # Show scenario-specific issues
            if result["scenario_specific_issues"]:
                print(f"      🎯 Scenario-specific issues:")
                for issue in result["scenario_specific_issues"][:2]:
                    print(f"         - {issue.get('message', 'Unknown issue')}")

def main():
    """Main testing function"""
    print("🚀 Starting Comprehensive End-to-End Testing")
    print(f"Testing {len(TEST_SCENARIOS)} scenarios across 3 Office applications")
    
    # Wait for server
    if not wait_for_server():
        sys.exit(1)
    
    # Run all tests
    results = []
    for i, scenario in enumerate(TEST_SCENARIOS, 1):
        print(f"\n[{i}/{len(TEST_SCENARIOS)}] Running test...")
        result = run_analysis(scenario)
        results.append(result)
        
        # Brief status
        if "error" in result:
            print(f"   ❌ FAILED: {result['error']}")
        else:
            print(f"   ✅ SUCCESS: {result['total_issues']} issues found ({result['issue_breakdown']['craft_bugs']} craft bugs)")
        
        # Small delay between tests
        time.sleep(2)
    
    # Print comprehensive summary
    print_test_summary(results)
    
    # Save detailed results
    with open("end_to_end_test_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"\n💾 Detailed results saved to: end_to_end_test_results.json")
    print("🎉 Testing completed!")

if __name__ == "__main__":
    main()
