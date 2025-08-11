#!/usr/bin/env python3
"""
Interactive Craft Bug Detection Test
This script will directly test craft bug detection with proper element targeting
"""

import json
import requests
import time
from datetime import datetime

def test_craft_bug_detection():
    """Test craft bug detection with corrected selectors"""
    
    print("🎯 CRAFT BUG INTERACTIVE TEST")
    print("=" * 60)
    
    # Custom scenario with correct selectors
    scenario_data = {
        "url": "http://localhost:8080/mocks/word/basic-doc.html",
        "scenario": {
            "id": "craft-test",
            "name": "Craft Bug Detection Test",
            "description": "Test craft bug detection with correct selectors",
            "steps": [
                {
                    "action": "navigate",
                    "target": "http://localhost:8080/mocks/word/basic-doc.html",
                    "description": "Open Word mock with craft bugs"
                },
                {
                    "action": "wait",
                    "duration": 1000,
                    "description": "Wait for page load"
                },
                {
                    "action": "hover",
                    "target": ".craft-bug-hover",
                    "description": "Hover over craft bug element",
                    "craft_bug_trigger": "feedback_failure"
                },
                {
                    "action": "click",
                    "target": ".craft-bug-hover",
                    "description": "Click craft bug element",
                    "craft_bug_trigger": "loading_delay"
                },
                {
                    "action": "wait",
                    "duration": 2000,
                    "description": "Wait for craft bug metrics"
                },
                {
                    "action": "hover",
                    "target": ".share-button.craft-bug-hover",
                    "description": "Test share button hover",
                    "craft_bug_trigger": "feedback_failure"
                },
                {
                    "action": "click",
                    "target": ".start-button",
                    "description": "Test start button for loading delay",
                    "craft_bug_trigger": "loading_delay"
                }
            ]
        },
        "options": {
            "browser": True,
            "performance": True,
            "accessibility": True,
            "ux_heuristics": True
        }
    }
    
    print("📤 Sending custom craft bug test scenario...")
    
    try:
        response = requests.post(
            "http://localhost:8000/api/analyze",
            json=scenario_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            analysis_id = result.get("analysis_id")
            print(f"✅ Analysis started: {analysis_id}")
            
            # Get detailed results
            time.sleep(3)  # Wait for analysis to complete
            
            report_response = requests.get(f"http://localhost:8000/api/reports/{analysis_id}")
            if report_response.status_code == 200:
                report = report_response.json()
                
                print("\n📊 CRAFT BUG DETECTION RESULTS")
                print("-" * 40)
                print(f"Overall Score: {report.get('overall_score', 'N/A')}")
                print(f"Total Issues: {report.get('total_issues', 0)}")
                
                # Check UX Heuristics specifically for craft bugs
                ux_results = report.get('modules', {}).get('ux_heuristics', {})
                print(f"\n🔍 UX Heuristics Score: {ux_results.get('score', 'N/A')}")
                print(f"UX Findings: {len(ux_results.get('findings', []))}")
                
                for finding in ux_results.get('findings', []):
                    print(f"   - {finding.get('severity', 'unknown').upper()}: {finding.get('message', 'No message')}")
                
                # Check scenario results for craft bug interactions
                scenario_results = report.get('scenario_results', [])
                print(f"\n🎬 Scenario Steps: {len(scenario_results)}")
                for i, step in enumerate(scenario_results, 1):
                    status = step.get('status', 'unknown')
                    action = step.get('action', 'unknown')
                    target = step.get('target', 'unknown')
                    duration = step.get('duration_ms', 0)
                    print(f"   {i}. {action} {target} - {status} ({duration}ms)")
                
                # Check for any craft bug specific metrics
                if 'craft_bugs' in report:
                    print(f"\n🐛 CRAFT BUGS DETECTED: {len(report['craft_bugs'])}")
                    for bug in report['craft_bugs']:
                        print(f"   - {bug}")
                
                # Save detailed results
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"craft_bug_interactive_test_{timestamp}.json"
                with open(filename, 'w') as f:
                    json.dump(report, f, indent=2)
                print(f"\n💾 Detailed results saved to: {filename}")
                
                return report
            else:
                print(f"❌ Failed to get report: {report_response.status_code}")
        else:
            print(f"❌ Analysis failed: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"❌ Error: {e}")
    
    return None

if __name__ == "__main__":
    test_craft_bug_detection()
