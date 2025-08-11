#!/usr/bin/env python3
"""
Word Complete Analysis Test - Using Direct Scenario Execution
This directly calls the scenario executor to ensure we get craft bug detection
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from scenario_executor import ScenarioExecutor
import json
from datetime import datetime

async def direct_word_analysis():
    """Run Word analysis directly through scenario executor"""
    
    print("🎯 DIRECT WORD ANALYSIS TEST")
    print("=" * 50)
    
    # Create scenario executor
    executor = ScenarioExecutor()
    
    # Define our working scenario
    word_scenario = {
        "id": "word.craft.direct",
        "name": "Direct Word Craft Bug Analysis",
        "description": "Direct scenario execution with craft bug detection",
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
                "description": "Click comments tab"
            },
            {
                "action": "wait",
                "duration": 500,
                "description": "Wait for comments panel"
            },
            {
                "action": "hover",
                "target": ".craft-bug-hover",
                "description": "Hover over craft bug element",
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
                "description": "Click share button",
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
                "text": "Testing input lag",
                "description": "Type to trigger input lag",
                "craft_bug_trigger": "input_lag"
            },
            {
                "action": "wait",
                "duration": 2000,
                "description": "Final wait for metrics"
            }
        ]
    }
    
    url = "http://localhost:8080/mocks/word/basic-doc.html"
    analysis_id = f"word_direct_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    # Configure modules for comprehensive analysis
    modules = {
        "performance": True,
        "accessibility": True,
        "ux_heuristics": True,  # This should trigger craft bug detection
        "keyboard": True,
        "best_practices": True
    }
    
    print(f"🚀 Starting direct analysis: {analysis_id}")
    print(f"📄 URL: {url}")
    print(f"🎬 Scenario: {word_scenario['name']}")
    print(f"📋 Modules: {list(modules.keys())}")
    
    try:
        # Execute the scenario directly
        result = await executor.execute_scenario(
            analysis_id=analysis_id,
            url=url,
            scenario_config=word_scenario,
            modules=modules
        )
        
        print("\n📊 DIRECT ANALYSIS RESULTS")
        print("=" * 40)
        print(f"Analysis ID: {result.get('analysis_id', 'N/A')}")
        print(f"Overall Score: {result.get('overall_score', 'N/A')}")
        print(f"Total Issues: {result.get('total_issues', 0)}")
        print(f"Execution Mode: {result.get('mode', 'unknown')}")
        print(f"Browser Used: {result.get('browser_automation', False)}")
        
        # Module Results
        modules_data = result.get('modules', {})
        
        print(f"\n🚀 Performance: Score {modules_data.get('performance', {}).get('score', 'N/A')}, Issues {len(modules_data.get('performance', {}).get('findings', []))}")
        print(f"♿ Accessibility: Score {modules_data.get('accessibility', {}).get('score', 'N/A')}, Issues {len(modules_data.get('accessibility', {}).get('findings', []))}")
        print(f"🎨 UX Heuristics: Score {modules_data.get('ux_heuristics', {}).get('score', 'N/A')}, Issues {len(modules_data.get('ux_heuristics', {}).get('findings', []))}")
        
        # Check for craft bugs specifically
        ux_issues = result.get('ux_issues', [])
        craft_bugs = [issue for issue in ux_issues if issue.get('craft_bug', False) or 'craft bug' in issue.get('message', '').lower()]
        
        print(f"\n🐛 CRAFT BUG DETECTION:")
        print(f"   Total UX Issues: {len(ux_issues)}")
        print(f"   Craft Bugs Found: {len(craft_bugs)}")
        
        if craft_bugs:
            print(f"\n🔍 CRAFT BUG DETAILS:")
            for i, bug in enumerate(craft_bugs, 1):
                print(f"   {i}. {bug.get('message', 'No message')}")
                print(f"      Severity: {bug.get('severity', 'unknown')}")
                print(f"      Category: {bug.get('category', 'unknown')}")
                print(f"      Element: {bug.get('element', 'unknown')}")
        else:
            print("   ⚠️ No craft bugs detected in UX issues")
        
        # Scenario execution details
        scenario_results = result.get('scenario_results', [])
        print(f"\n🎬 SCENARIO EXECUTION:")
        print(f"   Steps Executed: {len(scenario_results)}")
        successful = sum(1 for step in scenario_results if step.get('status') == 'success')
        print(f"   Successful: {successful}")
        
        print(f"\n📋 EXECUTION DETAILS:")
        for step in scenario_results:
            action = step.get('action', 'unknown')
            target = step.get('target', '')
            status = step.get('status', 'unknown')
            duration = step.get('duration_ms', 0)
            desc = step.get('description', '')
            print(f"   {action.upper()} {target} - {status} ({duration}ms) - {desc}")
        
        # Save results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"word_direct_analysis_{timestamp}.json"
        with open(filename, 'w') as f:
            json.dump(result, f, indent=2)
        print(f"\n💾 Results saved to: {filename}")
        
        print(f"\n🎯 SUMMARY:")
        print(f"✅ End-to-end execution: Complete")
        print(f"✅ Browser automation: {'Yes' if result.get('browser_automation') else 'No'}")
        print(f"✅ Craft bug detection: {len(craft_bugs)} found")
        print(f"✅ Total analysis issues: {result.get('total_issues', 0)}")
        
        return result
        
    except Exception as e:
        print(f"❌ Direct analysis failed: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    result = asyncio.run(direct_word_analysis())
