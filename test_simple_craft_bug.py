#!/usr/bin/env python3
"""
Create and test a simple craft bug scenario via API
"""

import json
import requests
import time

def test_simple_craft_bug_scenario():
    """Test a simple craft bug detection scenario"""
    
    print("🎯 SIMPLE CRAFT BUG SCENARIO TEST")
    print("=" * 50)
    
    # Just analyze the URL directly with UX heuristics enabled
    # The craft bug detection should run automatically
    scenario_data = {
        "url": "http://localhost:8080/mocks/word/basic-doc.html",
        "options": {
            "browser": True,
            "performance": True,
            "accessibility": True,
            "ux_heuristics": True
        }
    }
    
    print("📤 Sending simple analysis request with UX heuristics...")
    
    response = requests.post(
        "http://localhost:8000/api/analyze",
        json=scenario_data,
        headers={"Content-Type": "application/json"}
    )
    
    if response.status_code == 200:
        result = response.json()
        analysis_id = result.get("analysis_id")
        print(f"✅ Analysis started: {analysis_id}")
        
        # Wait for completion
        time.sleep(5)
        
        # Get report
        report_response = requests.get(f"http://localhost:8000/api/reports/{analysis_id}")
        if report_response.status_code == 200:
            report = report_response.json()
            
            print(f"\n📊 ANALYSIS RESULTS:")
            print(f"Overall Score: {report.get('overall_score', 'N/A')}")
            print(f"Total Issues: {report.get('total_issues', 0)}")
            
            # Check UX Heuristics
            ux_results = report.get('modules', {}).get('ux_heuristics', {})
            ux_findings = ux_results.get('findings', [])
            
            print(f"\n🔍 UX Heuristics:")
            print(f"Score: {ux_results.get('score', 'N/A')}")
            print(f"Findings: {len(ux_findings)}")
            
            craft_bug_found = False
            for finding in ux_findings:
                print(f"   - {finding.get('severity', 'unknown').upper()}: {finding.get('message', 'No message')}")
                if 'craft' in finding.get('message', '').lower() or finding.get('type') == 'craft_bug':
                    craft_bug_found = True
                    print("     ^^^^ CRAFT BUG DETECTED! ^^^^")
            
            if not craft_bug_found:
                print("⚠️ No craft bugs found in UX heuristics results")
                
            # Save results for inspection
            filename = f"simple_craft_test_{analysis_id}.json"
            with open(filename, 'w') as f:
                json.dump(report, f, indent=2)
            print(f"\n💾 Full report saved to: {filename}")
            
            return report
        else:
            print(f"❌ Failed to get report: {report_response.status_code}")
    else:
        print(f"❌ Analysis failed: {response.status_code}")
        print(response.text)
    
    return None

if __name__ == "__main__":
    test_simple_craft_bug_scenario()
