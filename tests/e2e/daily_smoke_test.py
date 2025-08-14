#!/usr/bin/env python3
"""
Daily Smoke Test for Safe Refactoring
Runs every day to ensure the system still works correctly
"""

import asyncio
import json
import requests
import time
import sys
from typing import Dict, Any
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DailySmokeTest:
    """Daily smoke test to ensure system functionality"""
    
    def __init__(self):
        self.base_url = "http://localhost:8000"
        self.test_results = {
            "timestamp": datetime.now().isoformat(),
            "tests": {},
            "overall_status": "PENDING"
        }
    
    async def test_basic_analysis(self) -> bool:
        """Test 1: Basic analysis functionality"""
        logger.info("🧪 Test 1: Basic Analysis")
        
        try:
            payload = {
                "url": "http://127.0.0.1:8080/mocks/word/basic-doc.html",
                "scenario_id": "1.1",
                "modules": {
                    "performance": True,
                    "accessibility": True,
                    "ux_heuristics": True
                }
            }
            
            response = requests.post(
                f"{self.base_url}/api/analyze",
                json=payload,
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                analysis_id = result.get("analysis_id")
                
                if analysis_id:
                    logger.info(f"✅ Basic analysis passed: {analysis_id}")
                    self.test_results["tests"]["basic_analysis"] = {
                        "status": "PASSED",
                        "details": f"Analysis ID: {analysis_id}",
                        "analysis_id": analysis_id
                    }
                    return True
                else:
                    logger.error("❌ Basic analysis failed: No analysis ID")
                    self.test_results["tests"]["basic_analysis"] = {
                        "status": "FAILED",
                        "details": "No analysis ID returned"
                    }
                    return False
            else:
                logger.error(f"❌ Basic analysis failed: {response.status_code}")
                self.test_results["tests"]["basic_analysis"] = {
                    "status": "FAILED",
                    "details": f"Status code: {response.status_code}"
                }
                return False
                
        except Exception as e:
            logger.error(f"❌ Basic analysis failed: {e}")
            self.test_results["tests"]["basic_analysis"] = {
                "status": "FAILED",
                "details": str(e)
            }
            return False
    
    async def test_fix_with_agent(self) -> bool:
        """Test 2: Fix with Agent functionality"""
        logger.info("🧪 Test 2: Fix with Agent")
        
        try:
            payload = {
                "work_item_id": 999,
                "file_path": "web-ui/public/mocks/word/basic-doc.html",
                "instruction": "Add alt text to images for accessibility"
            }
            
            response = requests.post(
                f"{self.base_url}/api/ado/trigger-fix",
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get("status") == "success":
                    logger.info("✅ Fix with Agent passed")
                    self.test_results["tests"]["fix_with_agent"] = {
                        "status": "PASSED",
                        "details": "Fix triggered successfully"
                    }
                    return True
                else:
                    logger.error(f"❌ Fix with Agent failed: {result.get('message', 'Unknown error')}")
                    self.test_results["tests"]["fix_with_agent"] = {
                        "status": "FAILED",
                        "details": result.get('message', 'Unknown error')
                    }
                    return False
            else:
                logger.error(f"❌ Fix with Agent failed: {response.status_code}")
                self.test_results["tests"]["fix_with_agent"] = {
                    "status": "FAILED",
                    "details": f"Status code: {response.status_code}"
                }
                return False
                
        except Exception as e:
            logger.error(f"❌ Fix with Agent failed: {e}")
            self.test_results["tests"]["fix_with_agent"] = {
                "status": "FAILED",
                "details": str(e)
            }
            return False
    
    async def test_ado_integration(self) -> bool:
        """Test 3: ADO integration"""
        logger.info("🧪 Test 3: ADO Integration")
        
        try:
            payload = {
                "report_id": "test_report",
                "demo_mode": True
            }
            
            response = requests.post(
                f"{self.base_url}/api/dashboard/create-ado-tickets",
                data=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                work_items_created = result.get("work_items_created", 0)
                
                if work_items_created > 0:
                    logger.info(f"✅ ADO integration passed: {work_items_created} work items created")
                    self.test_results["tests"]["ado_integration"] = {
                        "status": "PASSED",
                        "details": f"{work_items_created} work items created"
                    }
                    return True
                else:
                    logger.error("❌ ADO integration failed: No work items created")
                    self.test_results["tests"]["ado_integration"] = {
                        "status": "FAILED",
                        "details": "No work items created"
                    }
                    return False
            else:
                logger.error(f"❌ ADO integration failed: {response.status_code}")
                self.test_results["tests"]["ado_integration"] = {
                    "status": "FAILED",
                    "details": f"Status code: {response.status_code}"
                }
                return False
                
        except Exception as e:
            logger.error(f"❌ ADO integration failed: {e}")
            self.test_results["tests"]["ado_integration"] = {
                "status": "FAILED",
                "details": str(e)
            }
            return False
    
    async def test_git_operations(self) -> bool:
        """Test 4: Git operations"""
        logger.info("🧪 Test 4: Git Operations")
        
        try:
            response = requests.get(f"{self.base_url}/api/git/status", timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                logger.info("✅ Git operations passed")
                self.test_results["tests"]["git_operations"] = {
                    "status": "PASSED",
                    "details": "Git status retrieved successfully"
                }
                return True
            else:
                logger.error(f"❌ Git operations failed: {response.status_code}")
                self.test_results["tests"]["git_operations"] = {
                    "status": "FAILED",
                    "details": f"Status code: {response.status_code}"
                }
                return False
                
        except Exception as e:
            logger.error(f"❌ Git operations failed: {e}")
            self.test_results["tests"]["git_operations"] = {
                "status": "FAILED",
                "details": str(e)
            }
            return False
    
    async def run_all_tests(self) -> Dict[str, Any]:
        """Run all smoke tests"""
        logger.info("🚀 Starting Daily Smoke Tests")
        logger.info("=" * 50)
        
        # Test 1: Basic analysis
        if not await self.test_basic_analysis():
            self.test_results["overall_status"] = "FAILED"
            return self.test_results
        
        # Test 2: Fix with Agent
        if not await self.test_fix_with_agent():
            self.test_results["overall_status"] = "FAILED"
            return self.test_results
        
        # Test 3: ADO integration
        if not await self.test_ado_integration():
            self.test_results["overall_status"] = "FAILED"
            return self.test_results
        
        # Test 4: Git operations
        if not await self.test_git_operations():
            self.test_results["overall_status"] = "FAILED"
            return self.test_results
        
        # All tests passed
        self.test_results["overall_status"] = "PASSED"
        logger.info("🎉 All smoke tests passed!")
        
        return self.test_results
    
    def save_results(self, filename: str = None):
        """Save test results to file"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"smoke_test_results_{timestamp}.json"
        
        with open(filename, 'w') as f:
            json.dump(self.test_results, f, indent=2)
        
        logger.info(f"💾 Smoke test results saved to: {filename}")
        return filename
    
    def print_summary(self):
        """Print test summary"""
        logger.info("\n📊 Smoke Test Summary")
        logger.info("=" * 40)
        
        total_tests = len(self.test_results["tests"])
        passed_tests = sum(1 for test in self.test_results["tests"].values() if test["status"] == "PASSED")
        failed_tests = total_tests - passed_tests
        
        logger.info(f"Overall Status: {self.test_results['overall_status']}")
        logger.info(f"Total Tests: {total_tests}")
        logger.info(f"Passed: {passed_tests}")
        logger.info(f"Failed: {failed_tests}")
        
        if failed_tests > 0:
            logger.info("\n❌ Failed Tests:")
            for test_name, test_result in self.test_results["tests"].items():
                if test_result["status"] == "FAILED":
                    logger.info(f"   - {test_name}: {test_result['details']}")

def main():
    """Main smoke test runner"""
    tester = DailySmokeTest()
    
    try:
        results = asyncio.run(tester.run_all_tests())
        tester.print_summary()
        tester.save_results()
        
        if results["overall_status"] == "PASSED":
            logger.info("🎉 All smoke tests passed! System is working correctly.")
            return True
        else:
            logger.error("❌ Some smoke tests failed! System needs attention.")
            return False
            
    except Exception as e:
        logger.error(f"❌ Smoke test suite failed with error: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
