#!/usr/bin/env python3
"""
Fast craft bug test with reduced timeouts
"""

import asyncio
import logging
from datetime import datetime
import requests

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_fast_api_call():
    """Test API call with timeout to avoid hanging"""
    
    logger.info("🚀 Testing fast API call for craft bug scenario...")
    
    url = "http://127.0.0.1:9000/mocks/word/basic-doc.html"
    scenario_id = "1.4"
    
    # Test basic connectivity first
    try:
        logger.info("🔗 Testing basic connectivity...")
        response = requests.get("http://localhost:8000/health", timeout=5)
        logger.info(f"✅ API health: {response.status_code}")
    except Exception as e:
        logger.error(f"❌ API not accessible: {e}")
        return False
    
    # Test Word mock accessibility
    try:
        logger.info("📝 Testing Word mock accessibility...")
        response = requests.get(url, timeout=5)
        logger.info(f"✅ Word mock: {response.status_code}")
    except Exception as e:
        logger.error(f"❌ Word mock not accessible: {e}")
        return False
    
    # Make API call with timeout
    try:
        logger.info(f"🧪 Testing scenario {scenario_id} via API...")
        
        start_time = datetime.now()
        
        response = requests.post(
            "http://localhost:8000/api/analyze",
            json={
                "url": url,
                "scenario_id": scenario_id,
                "modules": {
                    "ux_heuristics": True,
                    "performance": True
                }
            },
            timeout=30  # 30 second timeout for API call
        )
        
        duration = (datetime.now() - start_time).total_seconds()
        logger.info(f"⏱️ API call completed in {duration:.1f} seconds")
        
        if response.status_code == 200:
            result = response.json()
            analysis_id = result.get('analysis_id', 'N/A')
            total_issues = result.get('total_issues', 0)
            mode = result.get('mode', 'N/A')
            browser_automation = result.get('browser_automation', False)
            
            logger.info(f"✅ Analysis completed!")
            logger.info(f"📈 Analysis ID: {analysis_id}")
            logger.info(f"🎯 Mode: {mode}")
            logger.info(f"🤖 Browser automation: {browser_automation}")
            logger.info(f"🐛 Total issues: {total_issues}")
            
            # Check for craft bugs specifically
            ux_issues = result.get('ux_issues', [])
            craft_bugs = [issue for issue in ux_issues if issue.get('craft_bug', False) or 'craft bug' in issue.get('message', '').lower()]
            logger.info(f"🐛 Craft bugs found: {len(craft_bugs)}")
            
            if craft_bugs:
                for i, bug in enumerate(craft_bugs[:3]):
                    logger.info(f"🐛 Craft Bug {i+1}: {bug.get('message', 'Unknown')}")
            
            return True
        else:
            logger.error(f"❌ API call failed: {response.status_code}")
            logger.error(f"Response: {response.text[:200]}")
            return False
            
    except requests.exceptions.Timeout:
        logger.error(f"❌ API call timed out after 30 seconds")
        return False
    except Exception as e:
        logger.error(f"❌ API call failed: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_fast_api_call())
    if success:
        print("\n🎉 Fast test completed successfully!")
    else:
        print("\n❌ Fast test failed!")
