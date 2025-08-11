#!/usr/bin/env python3
"""
Simple Word End-to-End Test via API
This tests the complete flow using the existing API with proper parameters
"""

import requests
import json
import time
from datetime import datetime

def test_word_end_to_end():
    """Test complete Word analysis via the API"""
    
    print("🎯 WORD END-TO-END API TEST")
    print("=" * 50)
    
    # Check server status first
    try:
        backend_check = requests.get("http://localhost:8000/health", timeout=5)
        print(f"✅ Backend: {backend_check.status_code}")
    except Exception as e:
        print(f"❌ Backend not accessible: {e}")
        return None
    
    try:
        mock_check = requests.get("http://localhost:8080/mocks/word/basic-doc.html", timeout=5)
        print(f"✅ Word Mock: {mock_check.status_code} - {len(mock_check.text)} bytes")
        if 'craft' in mock_check.text.lower():
            print("🐛 Craft bugs detected in mock!")
    except Exception as e:
        print(f"❌ Mock not accessible: {e}")
        return None
    
    # Run analysis with comprehensive options
    analysis_request = {
        "url": "http://localhost:8080/mocks/word/basic-doc.html",
        "options": {
            "browser": True,            # Enable browser automation
            "performance": True,        # Performance analysis
            "accessibility": True,      # Accessibility analysis  
            "ux_heuristics": True       # UX analysis (includes craft bugs)
        }
    }
    
    print("\n🚀 Starting comprehensive Word analysis...")
    print(f"📄 URL: {analysis_request['url']}")
    print(f"🔧 Options: {list(analysis_request['options'].keys())}")
    
    try:
        # Start analysis
        response = requests.post(
            "http://localhost:8000/api/analyze",
            json=analysis_request,
            headers={"Content-Type": "application/json"},
            timeout=60
        )
        
        if response.status_code == 200:
            result = response.json()
            analysis_id = result.get("analysis_id")
            print(f"✅ Analysis started: {analysis_id}")
            
            # Wait for completion
            print("⏱️ Waiting for analysis completion...")
            time.sleep(10)
            
            # Get results
            report_response = requests.get(f"http://localhost:8000/api/reports/{analysis_id}")
            if report_response.status_code == 200:
                report = report_response.json()
                
                print("\n📊 ANALYSIS RESULTS")
                print("=" * 30)
                print(f"Overall Score: {report.get('overall_score', 'N/A')}")
                print(f"Total Issues: {report.get('total_issues', 0)}")
                print(f"Browser Automation: {report.get('browser_automation', False)}")
                print(f"Real Analysis: {report.get('real_analysis', False)}")
                print(f"Execution Time: {report.get('execution_time', 0):.2f}s")
                
                # Module breakdown
                modules = report.get('modules', {})
                
                print(f"\n🚀 PERFORMANCE:")
                perf = modules.get('performance', {})
                print(f"   Score: {perf.get('score', 'N/A')}")
                print(f"   Findings: {len(perf.get('findings', []))}")
                
                print(f"\n♿ ACCESSIBILITY:")
                acc = modules.get('accessibility', {})
                print(f"   Score: {acc.get('score', 'N/A')}")
                print(f"   Findings: {len(acc.get('findings', []))}")
                for finding in acc.get('findings', [])[:2]:
                    print(f"   - {finding.get('severity', '').upper()}: {finding.get('message', '')[:60]}...")
                
                print(f"\n🎨 UX HEURISTICS:")
                ux = modules.get('ux_heuristics', {})
                print(f"   Score: {ux.get('score', 'N/A')}")
                print(f"   Findings: {len(ux.get('findings', []))}")
                
                # Look for craft bugs in UX findings
                craft_bug_count = 0
                for finding in ux.get('findings', []):
                    message = finding.get('message', '').lower()
                    if 'craft bug' in message or finding.get('craft_bug', False):
                        craft_bug_count += 1
                        print(f"   🐛 CRAFT BUG: {finding.get('message', 'No message')}")
                        print(f"      Severity: {finding.get('severity', 'unknown')}")
                
                # Also check in main ux_issues
                ux_issues = report.get('ux_issues', [])
                additional_craft_bugs = 0
                for issue in ux_issues:
                    if issue.get('craft_bug', False):
                        additional_craft_bugs += 1
                        print(f"   🐛 UX CRAFT BUG: {issue.get('message', 'No message')}")
                
                total_craft_bugs = craft_bug_count + additional_craft_bugs
                
                print(f"\n🐛 CRAFT BUG SUMMARY: {total_craft_bugs} total detected")
                
                # Scenario execution info
                scenario_results = report.get('scenario_results', [])
                if scenario_results:
                    print(f"\n🎬 SCENARIO EXECUTION:")
                    print(f"   Steps: {len(scenario_results)}")
                    successful = sum(1 for s in scenario_results if s.get('status') == 'success')
                    print(f"   Successful: {successful}")
                    
                    # Show interactions
                    interactions = [s for s in scenario_results if s.get('action') in ['click', 'hover', 'type']]
                    if interactions:
                        print(f"   Interactions: {len(interactions)}")
                        for interaction in interactions[:3]:
                            action = interaction.get('action')
                            target = interaction.get('target', '')
                            print(f"   - {action.upper()} {target}")
                
                # Performance metrics
                perf_metrics = report.get('performance_metrics', {})
                if perf_metrics:
                    print(f"\n📈 PERFORMANCE METRICS:")
                    print(f"   DOM Nodes: {perf_metrics.get('domNodes', 'N/A')}")
                    print(f"   First Paint: {perf_metrics.get('firstPaint', 'N/A')}ms")
                    print(f"   Scripts: {perf_metrics.get('scripts', 'N/A')}")
                
                # Save results
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"word_api_analysis_{timestamp}.json"
                with open(filename, 'w') as f:
                    json.dump(report, f, indent=2)
                print(f"\n💾 Complete results saved to: {filename}")
                
                # Final summary
                print(f"\n🎯 END-TO-END SUMMARY:")
                print(f"✅ API Response: Success")
                print(f"✅ Browser Execution: {'Yes' if report.get('browser_automation') else 'No'}")
                print(f"✅ Total Issues Found: {report.get('total_issues', 0)}")
                print(f"✅ Craft Bugs Detected: {total_craft_bugs}")
                print(f"✅ Overall Score: {report.get('overall_score', 'N/A')}")
                print(f"✅ Analysis Complete: Word end-to-end working!")
                
                return report
            else:
                print(f"❌ Failed to get report: {report_response.status_code}")
                print(report_response.text)
                
        else:
            print(f"❌ Analysis request failed: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"❌ Analysis error: {e}")
    
    return None

if __name__ == "__main__":
    result = test_word_end_to_end()
    if result:
        print("\n🎉 Word end-to-end analysis SUCCESSFUL!")
    else:
        print("\n💥 Word end-to-end analysis FAILED!")
