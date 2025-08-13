#!/usr/bin/env python3
"""
Test real analysis functionality
"""

import asyncio
import os
from scenario_executor import ScenarioExecutor

async def test_real_analysis():
    """Test real analysis with browser automation"""
    
    print("🚀 TESTING REAL ANALYSIS SYSTEM")
    print("=" * 40)
    
    # Initialize scenario executor
    executor = ScenarioExecutor()
    
    # Test parameters - use the correct port for web-ui dev server
    url = "http://localhost:8080"  # Web-ui dev server
    scenario_id = "1.1"  # Word scenario
    modules = {
        "accessibility": True,
        "performance": True,
        "keyboard": True,
        "ux_heuristics": True,
        "best_practices": True
    }
    
    print(f"🔗 URL: {url}")
    print(f"📋 Scenario: {scenario_id}")
    print(f"🔧 Modules: {list(modules.keys())}")
    
    try:
        print("\n🔄 Starting real analysis...")
        result = await executor.execute_scenario_by_id(url, scenario_id, modules)
        
        if result:
            print("✅ Real analysis completed!")
            print(f"📊 Overall score: {result.get('overall_score', 'N/A')}")
            print(f"🐛 UX Issues found: {len(result.get('ux_issues', []))}")
            print(f"📸 Screenshots: {len(result.get('screenshots', []))}")
            print(f"🎥 Video: {'Yes' if result.get('video_data') else 'No'}")
            
            # Check if it's real data or mock
            if result.get('real_analysis', False):
                print("🎉 This is REAL analysis data!")
            else:
                print("⚠️ This appears to be mock data")
                
            return True
        else:
            print("❌ Analysis returned no result")
            return False
            
    except Exception as e:
        print(f"❌ Analysis failed: {e}")
        return False

if __name__ == "__main__":
    asyncio.run(test_real_analysis())
