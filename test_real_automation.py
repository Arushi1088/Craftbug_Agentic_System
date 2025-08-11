#!/usr/bin/env python3
"""
Test real browser automation implementation
"""
import requests
import json
import time
import sys
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_browser_automation():
    """Test the real browser automation"""
    
    # First check if servers are running
    try:
        # Check backend
        response = requests.get("http://localhost:8000/health", timeout=2)
        logger.info("✅ Backend server is running")
    except requests.exceptions.RequestException:
        logger.error("❌ Backend server not running on port 8000")
        return False
    
    try:
        # Check frontend
        response = requests.get("http://localhost:4173", timeout=2)
        logger.info("✅ Frontend server is running on port 4173")
    except requests.exceptions.RequestException:
        logger.error("❌ Frontend server not running on port 4173")
        return False
    
    # Test the real browser automation
    logger.info("🚀 Testing real browser automation...")
    
    payload = {
        "url": "http://localhost:4173",
        "scenario_id": "1.1",
        "modules": {
            "performance": True,
            "accessibility": True,
            "usability": True
        }
    }
    
    try:
        response = requests.post(
            "http://localhost:8000/api/analyze",
            json=payload,
            timeout=30  # Give it time for browser automation
        )
        
        if response.status_code == 200:
            result = response.json()
            logger.info(f"✅ Analysis completed! ID: {result.get('analysis_id')}")
            logger.info(f"   Status: {result.get('status')}")
            logger.info(f"   Message: {result.get('message')}")
            
            # Get the full report
            analysis_id = result.get('analysis_id')
            if analysis_id:
                report_response = requests.get(f"http://localhost:8000/api/reports/{analysis_id}")
                if report_response.status_code == 200:
                    report = report_response.json()
                    logger.info(f"📊 Report Details:")
                    logger.info(f"   Overall Score: {report.get('overall_score', 'N/A')}")
                    logger.info(f"   Mode: {report.get('mode', 'N/A')}")
                    logger.info(f"   Real Analysis: {report.get('real_analysis', 'N/A')}")
                    logger.info(f"   Browser Automation: {report.get('browser_automation', 'N/A')}")
                    logger.info(f"   Total Issues: {report.get('total_issues', 'N/A')}")
                    
                    # Show some modules
                    modules = report.get('modules', {})
                    for module_name, module_data in modules.items():
                        score = module_data.get('score', 'N/A')
                        findings = len(module_data.get('findings', []))
                        logger.info(f"   {module_name}: Score {score}, {findings} findings")
                    
                    if report.get('real_analysis') and report.get('browser_automation'):
                        logger.info("🎉 SUCCESS: Real browser automation is working!")
                        return True
                    else:
                        logger.warning("⚠️ WARNING: Report indicates mock data, not real automation")
                        return False
        else:
            logger.error(f"❌ API request failed: {response.status_code}")
            logger.error(f"   Response: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        logger.error("❌ Request timed out - browser automation may be taking too long")
        return False
    except Exception as e:
        logger.error(f"❌ Request failed: {e}")
        return False

if __name__ == "__main__":
    success = test_browser_automation()
    sys.exit(0 if success else 1)
