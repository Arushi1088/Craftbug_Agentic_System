#!/usr/bin/env python3
"""Debug script to test Chromium launching"""

import asyncio
import sys
from scenario_executor import ScenarioExecutor

async def test_chromium_launch():
    print("🔍 Testing Chromium launch with scenario executor...")
    
    executor = ScenarioExecutor()
    
    # Check if Playwright is available
    from scenario_executor import PLAYWRIGHT_AVAILABLE
    print(f"📦 Playwright available: {PLAYWRIGHT_AVAILABLE}")
    
    if not PLAYWRIGHT_AVAILABLE:
        print("❌ Playwright not available - this is the issue!")
        return
    
    try:
        print("🚀 Attempting to execute scenario...")
        result = await executor.execute_specific_scenario(
            url='http://localhost:8080/mocks/word/basic-doc.html',
            scenario_path='scenarios/word_scenarios.yaml', 
            scenario_id='1.1',
            modules={'ux_heuristics': True, 'performance': True}
        )
        
        print(f"✅ Scenario executed")
        print(f"📊 Status: {result.get('status')}")
        print(f"🔧 Execution mode: {result.get('execution_mode')}")
        print(f"📈 Modules: {list(result.get('modules', {}).keys())}")
        
        # Check if browser automation was used
        if 'browser_execution' in result:
            print("🌐 Browser automation was used!")
        else:
            print("⚠️ Browser automation was NOT used - might be falling back to mock")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_chromium_launch())
