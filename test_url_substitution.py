#!/usr/bin/env python3
"""
Test URL substitution to see what's happening with the mock URLs
"""

import asyncio
import logging
import sys
import os
import yaml

# Add the current directory to Python path
sys.path.insert(0, '/Users/arushitandon/Desktop/analyzer')

from scenario_executor import ScenarioExecutor, substitute_mock_urls

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_url_substitution():
    """Test URL substitution logic"""
    
    logger.info("🧪 Testing URL substitution...")
    
    # Load the scenario file
    with open('/Users/arushitandon/Desktop/analyzer/scenarios/word_scenarios.yaml', 'r') as f:
        scenario_data = yaml.safe_load(f)
    
    # Find scenario 1.4
    scenarios = scenario_data.get('scenarios', [])
    target_scenario = None
    for scenario in scenarios:
        if scenario.get('id') == '1.4':
            target_scenario = scenario
            break
    
    if not target_scenario:
        logger.error("❌ Scenario 1.4 not found!")
        return
    
    logger.info(f"📋 Original scenario target: {target_scenario.get('steps', [{}])[0].get('target', 'N/A')}")
    
    # Test URL substitution
    substituted_scenario = substitute_mock_urls(target_scenario)
    
    logger.info(f"🔄 After substitution target: {substituted_scenario.get('steps', [{}])[0].get('target', 'N/A')}")
    
    # Check if the URL is accessible
    import requests
    try:
        first_step = substituted_scenario.get('steps', [{}])[0]
        url = first_step.get('target', '')
        if url and url.startswith('http'):
            response = requests.get(url, timeout=5)
            logger.info(f"✅ URL accessible: {url} - Status: {response.status_code}")
        else:
            logger.warning(f"⚠️ URL not properly substituted: {url}")
    except Exception as e:
        logger.error(f"❌ URL not accessible: {e}")

if __name__ == "__main__":
    test_url_substitution()
