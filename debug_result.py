#!/usr/bin/env python3
"""Debug script to examine the result structure"""

import asyncio
import json
from scenario_executor import ScenarioExecutor

async def test_result_structure():
    print("🔍 Testing result structure...")
    
    executor = ScenarioExecutor()
    
    try:
        result = await executor.execute_specific_scenario(
            url='http://localhost:8080/mocks/word/basic-doc.html',
            scenario_path='scenarios/word_scenarios.yaml', 
            scenario_id='1.1',
            modules={'ux_heuristics': True, 'performance': True}
        )
        
        print("📊 Full result keys:", list(result.keys()))
        
        # Check if there are step results
        if 'modules' in result and 'ux_heuristics' in result['modules']:
            ux_module = result['modules']['ux_heuristics']
            if 'step_results' in ux_module:
                print(f"🔧 Step results found: {len(ux_module['step_results'])} steps")
                for i, step in enumerate(ux_module['step_results'][:3]):  # Show first 3
                    print(f"  Step {i+1}: {step.get('action')} -> {step.get('status')}")
            
            if 'craft_bugs' in ux_module:
                craft_bugs = ux_module['craft_bugs']
                print(f"🐛 Craft bugs found: {craft_bugs.get('total_bugs_found', 0)}")
                if craft_bugs.get('bugs_detected'):
                    for bug in craft_bugs['bugs_detected']:
                        print(f"  - {bug.get('type')}: {bug.get('message')}")
        
        # Check execution info
        if 'analysis_info' in result:
            analysis_info = result['analysis_info']
            print(f"⚙️ Analysis info: {analysis_info}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_result_structure())
