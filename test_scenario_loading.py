#!/usr/bin/env python3
"""
Test scenario loading and execution directly
"""

import asyncio
import logging
import sys
import os

# Add the current directory to Python path
sys.path.insert(0, '/Users/arushitandon/Desktop/analyzer')

from scenario_executor import ScenarioExecutor

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_scenario_loading():
    """Test loading and executing scenario 1.4 directly"""
    
    logger.info("🧪 Testing scenario loading and execution...")
    
    # Initialize scenario executor
    executor = ScenarioExecutor()
    
    try:
        # Test scenario 1.4 loading
        url = "http://127.0.0.1:9000/mocks/word/basic-doc.html"
        scenario_id = "1.4"
        modules = {"ux_heuristics": True, "performance": True}
        
        logger.info(f"🔗 URL: {url}")
        logger.info(f"📋 Scenario ID: {scenario_id}")
        logger.info(f"📊 Modules: {modules}")
        
        # Execute scenario by ID
        result = await executor.execute_scenario_by_id(url, scenario_id, modules)
        
        logger.info(f"✅ Execution completed!")
        logger.info(f"📈 Analysis ID: {result.get('analysis_id', 'N/A')}")
        logger.info(f"🎯 Mode: {result.get('mode', 'N/A')}")
        logger.info(f"🤖 Browser automation: {result.get('browser_automation', 'N/A')}")
        logger.info(f"📝 Total steps: {result.get('scenario_info', {}).get('steps_total', 0)}")
        logger.info(f"✅ Successful steps: {result.get('scenario_info', {}).get('steps_successful', 0)}")
        logger.info(f"❌ Failed steps: {result.get('scenario_info', {}).get('steps_failed', 0)}")
        logger.info(f"⚠️ Warning steps: {result.get('scenario_info', {}).get('steps_warnings', 0)}")
        logger.info(f"🐛 Total issues: {result.get('total_issues', 0)}")
        
        # Check if craft bugs were found
        ux_issues = result.get('ux_issues', [])
        craft_bugs = [issue for issue in ux_issues if issue.get('craft_bug', False)]
        logger.info(f"🐛 Craft bugs found: {len(craft_bugs)}")
        
        if craft_bugs:
            for i, bug in enumerate(craft_bugs[:3]):
                logger.info(f"🐛 Craft Bug {i+1}: {bug.get('message', 'Unknown')}")
        
        return result
        
    except Exception as e:
        logger.error(f"❌ Test failed: {e}")
        import traceback
        logger.error(f"Full traceback: {traceback.format_exc()}")
        return None

if __name__ == "__main__":
    result = asyncio.run(test_scenario_loading())
    if result:
        print("\n🎉 Test completed successfully!")
    else:
        print("\n❌ Test failed!")
