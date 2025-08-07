#!/usr/bin/env python3
"""
Test runner for enhanced Word scenarios
Tests scenarios 1.4, 1.5, and 1.6 with AI-powered analysis
"""

import asyncio
import json
import yaml
import logging
from pathlib import Path
from enhanced_scenario_runner import CraftBugDetector
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_word_scenarios():
    """Test the new Word scenarios with AI analysis"""
    
    print("🚀 Testing Enhanced Word Scenarios (1.4-1.6)")
    print("=" * 60)
    
    # Load scenario file
    scenario_file = Path("scenarios/word_scenarios.yaml")
    if not scenario_file.exists():
        print(f"❌ Scenario file not found: {scenario_file}")
        return
    
    with open(scenario_file, 'r') as f:
        scenarios_data = yaml.safe_load(f)
    
    scenarios = scenarios_data.get('scenarios', [])
    
    # Initialize AI-powered detector
    detector = CraftBugDetector(enable_ai=True)
    
    # Test scenarios 1.4, 1.5, and 1.6
    target_scenarios = ['1.4', '1.5', '1.6']
    results = {}
    
    for scenario in scenarios:
        scenario_id = scenario.get('id')
        if scenario_id in target_scenarios:
            print(f"\n🎯 Testing Scenario {scenario_id}: {scenario.get('name')}")
            print(f"📝 Task Goal: {scenario.get('task_goal')}")
            
            try:
                # Run the scenario with AI analysis
                result = await detector.run_scenario(scenario)
                results[scenario_id] = result
                
                # Display results
                print(f"✅ Scenario {scenario_id} completed")
                print(f"   📊 Issues found: {result.get('total_issues_found', 0)}")
                print(f"   🤖 AI analysis: {'enabled' if result.get('ai_analysis_enabled') else 'disabled'}")
                print(f"   ⏱️  Execution time: {result.get('execution_results', {}).get('execution_time', 0)}ms")
                
                # Show top issues
                craft_issues = result.get('craft_issues', [])
                if craft_issues:
                    print(f"   🔍 Top issues:")
                    for i, issue in enumerate(craft_issues[:3], 1):
                        print(f"      {i}. {issue.get('title', 'Unknown')} ({issue.get('severity', 'unknown')})")
                
            except Exception as e:
                print(f"❌ Scenario {scenario_id} failed: {e}")
                results[scenario_id] = {"error": str(e)}
    
    # Save comprehensive results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results_file = f"reports/word_scenarios_test_{timestamp}.json"
    
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"\n💾 Results saved to: {results_file}")
    
    # Summary
    successful_scenarios = [k for k, v in results.items() if 'error' not in v]
    failed_scenarios = [k for k, v in results.items() if 'error' in v]
    
    print(f"\n📈 Test Summary:")
    print(f"   ✅ Successful: {len(successful_scenarios)} scenarios")
    print(f"   ❌ Failed: {len(failed_scenarios)} scenarios")
    
    if successful_scenarios:
        total_issues = sum(r.get('total_issues_found', 0) for r in results.values() if 'error' not in r)
        print(f"   🔍 Total UX issues detected: {total_issues}")
    
    return results

if __name__ == "__main__":
    asyncio.run(test_word_scenarios())
