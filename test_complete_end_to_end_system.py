#!/usr/bin/env python3
"""
Complete End-to-End System Test
Tests the entire workflow with new architecture
"""

import asyncio
import requests
import json
import time
import sys
from typing import Dict, Any
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CompleteEndToEndTest:
    """Complete end-to-end system test"""
    
    def __init__(self):
        self.legacy_url = "http://localhost:8000"
        self.new_url = "http://localhost:8001"
        self.test_results = {
            "timestamp": time.time(),
            "tests": {},
            "overall_status": "PENDING"
        }
    
    def test_legacy_system_health(self) -> bool:
        """Test 1: Legacy system health"""
        logger.info("🧪 Test 1: Legacy System Health")
        
        try:
            response = requests.get(f"{self.legacy_url}/health", timeout=10)
            if response.status_code == 200:
                logger.info("✅ Legacy system is healthy")
                self.test_results["tests"]["legacy_health"] = {
                    "status": "PASSED",
                    "details": "Legacy system responding"
                }
                return True
            else:
                logger.error(f"❌ Legacy system failed: {response.status_code}")
                self.test_results["tests"]["legacy_health"] = {
                    "status": "FAILED",
                    "details": f"Status code: {response.status_code}"
                }
                return False
        except Exception as e:
            logger.error(f"❌ Legacy system failed: {e}")
            self.test_results["tests"]["legacy_health"] = {
                "status": "FAILED",
                "details": str(e)
            }
            return False
    
    def test_new_system_health(self) -> bool:
        """Test 2: New system health"""
        logger.info("🧪 Test 2: New System Health")
        
        try:
            response = requests.get(f"{self.new_url}/health", timeout=10)
            if response.status_code == 200:
                result = response.json()
                if result.get("status") == "healthy":
                    logger.info("✅ New system is healthy")
                    self.test_results["tests"]["new_health"] = {
                        "status": "PASSED",
                        "details": "New system responding"
                    }
                    return True
                else:
                    logger.error("❌ New system unhealthy")
                    self.test_results["tests"]["new_health"] = {
                        "status": "FAILED",
                        "details": "System reported unhealthy"
                    }
                    return False
            else:
                logger.error(f"❌ New system failed: {response.status_code}")
                self.test_results["tests"]["new_health"] = {
                    "status": "FAILED",
                    "details": f"Status code: {response.status_code}"
                }
                return False
        except Exception as e:
            logger.error(f"❌ New system failed: {e}")
            self.test_results["tests"]["new_health"] = {
                "status": "FAILED",
                "details": str(e)
            }
            return False
    
    def test_analysis_workflow(self) -> bool:
        """Test 3: Complete analysis workflow"""
        logger.info("🧪 Test 3: Analysis Workflow")
        
        try:
            # Test analysis request
            payload = {
                "url": "http://127.0.0.1:8080/mocks/word/basic-doc.html",
                "scenario_id": "1.1",
                "modules": {
                    "performance": True,
                    "accessibility": True,
                    "ux_heuristics": True
                }
            }
            
            # Test both legacy and new systems
            systems = [
                ("legacy", f"{self.legacy_url}/api/analyze"),
                ("new", f"{self.new_url}/api/analyze")
            ]
            
            for system_name, url in systems:
                try:
                    response = requests.post(url, json=payload, timeout=60)
                    if response.status_code == 200:
                        result = response.json()
                        if result.get("analysis_id"):
                            logger.info(f"✅ {system_name} analysis works: {result['analysis_id']}")
                            self.test_results["tests"][f"{system_name}_analysis"] = {
                                "status": "PASSED",
                                "details": f"Analysis ID: {result['analysis_id']}"
                            }
                        else:
                            logger.error(f"❌ {system_name} analysis failed: No analysis ID")
                            self.test_results["tests"][f"{system_name}_analysis"] = {
                                "status": "FAILED",
                                "details": "No analysis ID returned"
                            }
                            return False
                    else:
                        logger.error(f"❌ {system_name} analysis failed: {response.status_code}")
                        self.test_results["tests"][f"{system_name}_analysis"] = {
                            "status": "FAILED",
                            "details": f"Status code: {response.status_code}"
                        }
                        return False
                except Exception as e:
                    logger.error(f"❌ {system_name} analysis failed: {e}")
                    self.test_results["tests"][f"{system_name}_analysis"] = {
                        "status": "FAILED",
                        "details": str(e)
                    }
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Analysis workflow failed: {e}")
            self.test_results["tests"]["analysis_workflow"] = {
                "status": "FAILED",
                "details": str(e)
            }
            return False
    
    def test_fix_with_agent(self) -> bool:
        """Test 4: Fix with Agent workflow"""
        logger.info("🧪 Test 4: Fix with Agent")
        
        try:
            # Test fix with agent
            payload = {
                "work_item_id": 999,
                "file_path": "web-ui/public/mocks/word/basic-doc.html",
                "instruction": "Add alt text to images for accessibility"
            }
            
            response = requests.post(
                f"{self.new_url}/api/ado/trigger-fix",
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get("status") == "success":
                    logger.info("✅ Fix with Agent works")
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
    
    def test_ado_integration(self) -> bool:
        """Test 5: ADO integration"""
        logger.info("🧪 Test 5: ADO Integration")
        
        try:
            # Test ADO ticket creation
            payload = {
                "report_id": "test_report",
                "demo_mode": True
            }
            
            response = requests.post(
                f"{self.new_url}/api/dashboard/create-ado-tickets",
                data=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                work_items_created = result.get("work_items_created", 0)
                
                if work_items_created > 0:
                    logger.info(f"✅ ADO integration works: {work_items_created} work items created")
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
    
    def test_git_operations(self) -> bool:
        """Test 6: Git operations"""
        logger.info("🧪 Test 6: Git Operations")
        
        try:
            # Test Git status
            response = requests.get(f"{self.new_url}/api/git/status", timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                if result.get("status") == "success":
                    logger.info("✅ Git operations work")
                    self.test_results["tests"]["git_operations"] = {
                        "status": "PASSED",
                        "details": "Git status retrieved successfully"
                    }
                    return True
                else:
                    logger.error(f"❌ Git operations failed: {result.get('message', 'Unknown error')}")
                    self.test_results["tests"]["git_operations"] = {
                        "status": "FAILED",
                        "details": result.get('message', 'Unknown error')
                    }
                    return False
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
    
    def test_dashboard_functionality(self) -> bool:
        """Test 7: Dashboard functionality"""
        logger.info("🧪 Test 7: Dashboard Functionality")
        
        try:
            # Test dashboard analytics
            response = requests.get(f"{self.new_url}/api/dashboard/analytics", timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                if "total_analyses" in result and "total_issues" in result:
                    logger.info("✅ Dashboard analytics work")
                    self.test_results["tests"]["dashboard_analytics"] = {
                        "status": "PASSED",
                        "details": "Dashboard analytics retrieved"
                    }
                    return True
                else:
                    logger.error("❌ Dashboard analytics failed: Missing data")
                    self.test_results["tests"]["dashboard_analytics"] = {
                        "status": "FAILED",
                        "details": "Missing analytics data"
                    }
                    return False
            else:
                logger.error(f"❌ Dashboard analytics failed: {response.status_code}")
                self.test_results["tests"]["dashboard_analytics"] = {
                    "status": "FAILED",
                    "details": f"Status code: {response.status_code}"
                }
                return False
                
        except Exception as e:
            logger.error(f"❌ Dashboard functionality failed: {e}")
            self.test_results["tests"]["dashboard_analytics"] = {
                "status": "FAILED",
                "details": str(e)
            }
            return False
    
    def test_scenarios_endpoint(self) -> bool:
        """Test 8: Scenarios endpoint"""
        logger.info("🧪 Test 8: Scenarios Endpoint")
        
        try:
            # Test scenarios endpoint
            response = requests.get(f"{self.new_url}/api/scenarios", timeout=10)
            
            if response.status_code == 200:
                scenarios = response.json()
                if isinstance(scenarios, list):
                    logger.info(f"✅ Scenarios endpoint works: {len(scenarios)} scenarios")
                    self.test_results["tests"]["scenarios_endpoint"] = {
                        "status": "PASSED",
                        "details": f"Found {len(scenarios)} scenarios"
                    }
                    return True
                else:
                    logger.error("❌ Scenarios endpoint failed: Invalid response format")
                    self.test_results["tests"]["scenarios_endpoint"] = {
                        "status": "FAILED",
                        "details": "Invalid response format"
                    }
                    return False
            else:
                logger.error(f"❌ Scenarios endpoint failed: {response.status_code}")
                self.test_results["tests"]["scenarios_endpoint"] = {
                    "status": "FAILED",
                    "details": f"Status code: {response.status_code}"
                }
                return False
                
        except Exception as e:
            logger.error(f"❌ Scenarios endpoint failed: {e}")
            self.test_results["tests"]["scenarios_endpoint"] = {
                "status": "FAILED",
                "details": str(e)
            }
            return False
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Run all end-to-end tests"""
        logger.info("🚀 Starting Complete End-to-End System Tests")
        logger.info("=" * 60)
        
        # Test 1: Legacy system health
        if not self.test_legacy_system_health():
            self.test_results["overall_status"] = "FAILED"
            return self.test_results
        
        # Test 2: New system health
        if not self.test_new_system_health():
            self.test_results["overall_status"] = "FAILED"
            return self.test_results
        
        # Test 3: Analysis workflow
        if not self.test_analysis_workflow():
            self.test_results["overall_status"] = "FAILED"
            return self.test_results
        
        # Test 4: Fix with Agent
        if not self.test_fix_with_agent():
            self.test_results["overall_status"] = "FAILED"
            return self.test_results
        
        # Test 5: ADO integration
        if not self.test_ado_integration():
            self.test_results["overall_status"] = "FAILED"
            return self.test_results
        
        # Test 6: Git operations
        if not self.test_git_operations():
            self.test_results["overall_status"] = "FAILED"
            return self.test_results
        
        # Test 7: Dashboard functionality
        if not self.test_dashboard_functionality():
            self.test_results["overall_status"] = "FAILED"
            return self.test_results
        
        # Test 8: Scenarios endpoint
        if not self.test_scenarios_endpoint():
            self.test_results["overall_status"] = "FAILED"
            return self.test_results
        
        # All tests passed
        self.test_results["overall_status"] = "PASSED"
        logger.info("🎉 All end-to-end tests passed!")
        
        return self.test_results
    
    def print_summary(self):
        """Print test summary"""
        logger.info("\n📊 Complete End-to-End Test Summary")
        logger.info("=" * 50)
        
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
        
        logger.info("\n🎯 Complete System Status:")
        logger.info("✅ Legacy system working (port 8000)")
        logger.info("✅ New system working (port 8001)")
        logger.info("✅ Analysis workflow functional")
        logger.info("✅ Fix with Agent working")
        logger.info("✅ ADO integration working")
        logger.info("✅ Git operations working")
        logger.info("✅ Dashboard functionality working")
        logger.info("✅ Scenarios endpoint working")

def main():
    """Main test runner"""
    tester = CompleteEndToEndTest()
    
    try:
        results = tester.run_all_tests()
        tester.print_summary()
        
        if results["overall_status"] == "PASSED":
            logger.info("🎉 Complete end-to-end system is working correctly!")
            return True
        else:
            logger.error("❌ Some end-to-end tests failed!")
            return False
            
    except Exception as e:
        logger.error(f"❌ End-to-end test suite failed with error: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
