#!/usr/bin/env python3
"""
Complete End-to-End Word Analysis Test
This tests the full loop: scenario execution → craft bug detection → comprehensive analysis
"""

import asyncio
import json
import requests
import time
from datetime import datetime

async def complete_word_analysis_test():
    """Run complete end-to-end Word analysis with craft bug detection"""
    
    print("🎯 COMPLETE WORD END-TO-END ANALYSIS")
    print("=" * 60)
    
    # Define our working scenario
    word_scenario = {
        "id": "word.craft.1",
        "name": "Word Document with Craft Bug Detection",
        "description": "Complete end-to-end Word analysis with craft bug detection",
        "app": "word",
        "trigger_craft_bugs": True,
        "interactive_analysis": True,
        "steps": [
            {
                "action": "navigate",
                "target": "http://localhost:8080/mocks/word/basic-doc.html",
                "description": "Open Word document mock"
            },
            {
                "action": "wait",
                "duration": 1000,
                "description": "Wait for page load"
            },
            {
                "action": "click",
                "target": "#comments-tab",
                "description": "Click comments tab to trigger interactions"
            },
            {
                "action": "wait",
                "duration": 500,
                "description": "Wait for comments panel"
            },
            {
                "action": "hover",
                "target": ".craft-bug-hover",
                "description": "Hover over craft bug element to trigger feedback issues",
                "craft_bug_trigger": "feedback_failure"
            },
            {
                "action": "wait",
                "duration": 300,
                "description": "Wait for hover metrics"
            },
            {
                "action": "click", 
                "target": ".share-button.craft-bug-hover",
                "description": "Click share button to trigger more craft bugs",
                "craft_bug_trigger": "feedback_failure"
            },
            {
                "action": "wait",
                "duration": 500,
                "description": "Wait for click response"
            },
            {
                "action": "type",
                "target": "textarea",
                "text": "Testing input lag detection",
                "description": "Type in textarea to trigger input lag craft bugs",
                "craft_bug_trigger": "input_lag"
            },
            {
                "action": "wait",
                "duration": 1000,
                "description": "Wait for input lag metrics to accumulate"
            },
            {
                "action": "click",
                "target": ".image-insert-btn.craft-bug-hover", 
                "description": "Final interaction to complete craft bug collection",
                "craft_bug_trigger": "feedback_failure"
            },
            {
                "action": "wait",
                "duration": 2000,
                "description": "Final wait for all craft bug metrics"
            }
        ]
    }
    
    print("📤 Running complete Word analysis with custom scenario...")
    
    # Test direct API call with comprehensive modules
    analysis_request = {
        "url": "http://localhost:8080/mocks/word/basic-doc.html",
        "options": {
            "browser": True,
            "performance": True,
            "accessibility": True,
            "ux_heuristics": True
        },
        "custom_scenario": word_scenario
    }
    
    try:
        print("🚀 Starting analysis...")
        response = requests.post(
            "http://localhost:8000/api/analyze",
            json=analysis_request,
            headers={"Content-Type": "application/json"},
            timeout=120
        )
        
        if response.status_code == 200:
            result = response.json()
            analysis_id = result.get("analysis_id")
            print(f"✅ Analysis started: {analysis_id}")
            
            # Wait for analysis to complete
            print("⏱️ Waiting for analysis to complete...")
            time.sleep(15)  # Give time for browser automation
            
            # Get detailed results
            report_response = requests.get(f"http://localhost:8000/api/reports/{analysis_id}")
            if report_response.status_code == 200:
                report = report_response.json()
                
                print("\n📊 COMPREHENSIVE ANALYSIS RESULTS")
                print("=" * 50)
                print(f"Overall Score: {report.get('overall_score', 'N/A')}")
                print(f"Total Issues: {report.get('total_issues', 0)}")
                print(f"Analysis Mode: {report.get('mode', 'unknown')}")
                print(f"Browser Automation: {report.get('browser_automation', False)}")
                
                # Performance Results
                perf = report.get('modules', {}).get('performance', {})
                print(f"\n🚀 PERFORMANCE:")
                print(f"   Score: {perf.get('score', 'N/A')}")
                print(f"   Issues: {len(perf.get('findings', []))}")
                
                # Accessibility Results
                acc = report.get('modules', {}).get('accessibility', {})
                print(f"\n♿ ACCESSIBILITY:")
                print(f"   Score: {acc.get('score', 'N/A')}")
                print(f"   Issues: {len(acc.get('findings', []))}")
                for finding in acc.get('findings', [])[:3]:
                    print(f"   - {finding.get('severity', 'unknown').upper()}: {finding.get('message', 'No message')}")
                
                # UX Heuristics Results (should contain craft bugs)
                ux = report.get('modules', {}).get('ux_heuristics', {})
                print(f"\n🎨 UX HEURISTICS (including craft bugs):")
                print(f"   Score: {ux.get('score', 'N/A')}")
                print(f"   Issues: {len(ux.get('findings', []))}")
                
                craft_bug_count = 0
                for finding in ux.get('findings', []):
                    if finding.get('craft_bug', False) or 'craft bug' in finding.get('message', '').lower():
                        craft_bug_count += 1
                        print(f"   🐛 CRAFT BUG: {finding.get('message', 'No message')}")
                        print(f"      Severity: {finding.get('severity', 'unknown')}")
                        print(f"      Element: {finding.get('element', 'unknown')}")
                
                print(f"\n🔍 CRAFT BUG SUMMARY: {craft_bug_count} detected")
                
                # Scenario Execution Results
                scenario_results = report.get('scenario_results', [])
                print(f"\n🎬 SCENARIO EXECUTION:")
                print(f"   Steps Executed: {len(scenario_results)}")
                successful_steps = sum(1 for step in scenario_results if step.get('status') == 'success')
                print(f"   Successful Steps: {successful_steps}")
                
                # Show key interactions
                for step in scenario_results:
                    action = step.get('action', 'unknown')
                    target = step.get('target', 'unknown')
                    status = step.get('status', 'unknown')
                    duration = step.get('duration_ms', 0)
                    if action in ['click', 'hover', 'type']:
                        print(f"   {action} {target} - {status} ({duration}ms)")
                
                print(f"\n📈 METRICS SUMMARY:")
                perf_metrics = report.get('performance_metrics', {})
                if perf_metrics:
                    print(f"   DOM Nodes: {perf_metrics.get('domNodes', 'N/A')}")
                    print(f"   First Paint: {perf_metrics.get('firstPaint', 'N/A')}ms")
                    print(f"   Load Complete: {perf_metrics.get('loadComplete', 'N/A')}ms")
                
                # Save comprehensive results
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"word_complete_analysis_{timestamp}.json"
                with open(filename, 'w') as f:
                    json.dump(report, f, indent=2)
                print(f"\n💾 Complete results saved to: {filename}")
                
                # Summary for user
                print(f"\n🎯 END-TO-END SUMMARY:")
                print(f"✅ Browser automation: {'Yes' if report.get('browser_automation') else 'No'}")
                print(f"✅ Scenario execution: {len(scenario_results)} steps")
                print(f"✅ Performance analysis: {len(perf.get('findings', []))} issues")
                print(f"✅ Accessibility analysis: {len(acc.get('findings', []))} issues")
                print(f"✅ UX/Craft bug analysis: {len(ux.get('findings', []))} issues ({craft_bug_count} craft bugs)")
                print(f"✅ Overall score: {report.get('overall_score', 'N/A')}")
                
                return report
            else:
                print(f"❌ Failed to get report: {report_response.status_code}")
                print(report_response.text)
        else:
            print(f"❌ Analysis failed: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"❌ Error: {e}")
    
    return None

if __name__ == "__main__":
    asyncio.run(complete_word_analysis_test())
