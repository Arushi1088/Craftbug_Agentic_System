#!/usr/bin/env python3
"""
Complete End-to-End Workflow Test Suite
Tests the entire system workflow to ensure functionality is preserved during refactoring
"""

import asyncio
import json
import requests
import time
import sys
from typing import Dict, List, Any
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CompleteWorkflowTest:
    """Test the entire end-to-end workflow"""
    
    def __init__(self):
        self.base_url = "http://localhost:8000"
        self.test_results = {
            "timestamp": datetime.now().isoformat(),
            "tests": {},
            "overall_status": "PENDING"
        }
    
    def test_server_health(self) -> bool:
        """Test 1: Server health check"""
        logger.info("🧪 Test 1: Server Health Check")
        
        try:
            response = requests.get(f"{self.base_url}/health", timeout=10)
            if response.status_code == 200:
                logger.info("✅ Server health check passed")
                self.test_results["tests"]["server_health"] = {
                    "status": "PASSED",
                    "details": "Server is responding"
                }
                return True
            else:
                logger.error(f"❌ Server health check failed: {response.status_code}")
                self.test_results["tests"]["server_health"] = {
                    "status": "FAILED",
                    "details": f"Server returned {response.status_code}"
                }
                return False
        except Exception as e:
            logger.error(f"❌ Server health check failed: {e}")
            self.test_results["tests"]["server_health"] = {
                "status": "FAILED",
                "details": str(e)
            }
            return False
    
    def test_scenarios_endpoint(self) -> bool:
        """Test 2: Scenarios endpoint"""
        logger.info("🧪 Test 2: Scenarios Endpoint")
        
        try:
            response = requests.get(f"{self.base_url}/api/scenarios", timeout=10)
            if response.status_code == 200:
                scenarios = response.json()
                if isinstance(scenarios, list) and len(scenarios) > 0:
                    logger.info(f"✅ Scenarios endpoint passed: {len(scenarios)} scenarios found")
                    self.test_results["tests"]["scenarios_endpoint"] = {
                        "status": "PASSED",
                        "details": f"Found {len(scenarios)} scenarios"
                    }
                    return True
                else:
                    logger.error("❌ Scenarios endpoint failed: No scenarios returned")
                    self.test_results["tests"]["scenarios_endpoint"] = {
                        "status": "FAILED",
                        "details": "No scenarios returned"
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
    
    def test_basic_analysis(self) -> bool:
        """Test 3: Basic URL analysis"""
        logger.info("🧪 Test 3: Basic URL Analysis")
        
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
                timeout=120
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
                    return True, analysis_id
                else:
                    logger.error("❌ Basic analysis failed: No analysis ID returned")
                    self.test_results["tests"]["basic_analysis"] = {
                        "status": "FAILED",
                        "details": "No analysis ID returned"
                    }
                    return False, None
            else:
                logger.error(f"❌ Basic analysis failed: {response.status_code}")
                self.test_results["tests"]["basic_analysis"] = {
                    "status": "FAILED",
                    "details": f"Status code: {response.status_code}"
                }
                return False, None
        except Exception as e:
            logger.error(f"❌ Basic analysis failed: {e}")
            self.test_results["tests"]["basic_analysis"] = {
                "status": "FAILED",
                "details": str(e)
            }
            return False, None
    
    def test_report_retrieval(self, analysis_id: str) -> bool:
        """Test 4: Report retrieval"""
        logger.info(f"🧪 Test 4: Report Retrieval for {analysis_id}")
        
        try:
            # Wait a bit for analysis to complete
            time.sleep(5)
            
            response = requests.get(f"{self.base_url}/api/reports/{analysis_id}", timeout=30)
            
            if response.status_code == 200:
                report = response.json()
                
                # Validate report structure
                required_fields = ["analysis_id", "status", "url", "overall_score"]
                missing_fields = [field for field in required_fields if field not in report]
                
                if not missing_fields:
                    logger.info(f"✅ Report retrieval passed: Score {report.get('overall_score', 'N/A')}")
                    self.test_results["tests"]["report_retrieval"] = {
                        "status": "PASSED",
                        "details": f"Score: {report.get('overall_score', 'N/A')}",
                        "report_id": analysis_id
                    }
                    return True
                else:
                    logger.error(f"❌ Report retrieval failed: Missing fields {missing_fields}")
                    self.test_results["tests"]["report_retrieval"] = {
                        "status": "FAILED",
                        "details": f"Missing fields: {missing_fields}"
                    }
                    return False
            else:
                logger.error(f"❌ Report retrieval failed: {response.status_code}")
                self.test_results["tests"]["report_retrieval"] = {
                    "status": "FAILED",
                    "details": f"Status code: {response.status_code}"
                }
                return False
        except Exception as e:
            logger.error(f"❌ Report retrieval failed: {e}")
            self.test_results["tests"]["report_retrieval"] = {
                "status": "FAILED",
                "details": str(e)
            }
            return False
    
    def test_fix_with_agent(self) -> bool:
        """Test 5: Fix with Agent functionality"""
        logger.info("🧪 Test 5: Fix with Agent")
        
        try:
            # Test the fix with agent endpoint
            payload = {
                "work_item_id": 999,  # Test work item
                "file_path": "web-ui/public/mocks/word/basic-doc.html",
                "instruction": "Add alt text to images for accessibility"
            }
            
            response = requests.post(
                f"{self.base_url}/api/ado/trigger-fix",
                json=payload,
                timeout=60
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
    
    def test_ado_integration(self) -> bool:
        """Test 6: Azure DevOps integration"""
        logger.info("🧪 Test 6: Azure DevOps Integration")
        
        try:
            # Test ADO work item creation (demo mode)
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
    
    def test_git_operations(self) -> bool:
        """Test 7: Git operations"""
        logger.info("🧪 Test 7: Git Operations")
        
        try:
            # Test git status endpoint
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
    
    def test_mock_app_scenarios(self) -> bool:
        """Test 8: Mock app scenarios"""
        logger.info("🧪 Test 8: Mock App Scenarios")
        
        scenarios = [
            {"app": "word", "scenario_id": "1.1", "name": "Word Basic Navigation"},
            {"app": "excel", "scenario_id": "excel_basic_nav", "name": "Excel Basic Navigation"},
            {"app": "powerpoint", "scenario_id": "slide_creation", "name": "PowerPoint Slide Creation"}
        ]
        
        passed_scenarios = 0
        
        for scenario in scenarios:
            try:
                payload = {
                    "url": f"http://127.0.0.1:8080/mocks/{scenario['app']}/basic-doc.html",
                    "scenario_id": scenario["scenario_id"],
                    "modules": {"performance": True, "accessibility": True, "ux_heuristics": True}
                }
                
                response = requests.post(f"{self.base_url}/api/analyze", json=payload, timeout=60)
                
                if response.status_code == 200:
                    result = response.json()
                    if result.get("analysis_id"):
                        passed_scenarios += 1
                        logger.info(f"✅ {scenario['name']} passed")
                    else:
                        logger.error(f"❌ {scenario['name']} failed: No analysis ID")
                else:
                    logger.error(f"❌ {scenario['name']} failed: {response.status_code}")
            except Exception as e:
                logger.error(f"❌ {scenario['name']} failed: {e}")
        
        success_rate = passed_scenarios / len(scenarios)
        
        if success_rate >= 0.67:  # At least 2 out of 3 scenarios pass
            logger.info(f"✅ Mock app scenarios passed: {passed_scenarios}/{len(scenarios)}")
            self.test_results["tests"]["mock_app_scenarios"] = {
                "status": "PASSED",
                "details": f"{passed_scenarios}/{len(scenarios)} scenarios passed"
            }
            return True
        else:
            logger.error(f"❌ Mock app scenarios failed: {passed_scenarios}/{len(scenarios)}")
            self.test_results["tests"]["mock_app_scenarios"] = {
                "status": "FAILED",
                "details": f"{passed_scenarios}/{len(scenarios)} scenarios passed"
            }
            return False
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Run all end-to-end tests"""
        logger.info("🚀 Starting Complete End-to-End Workflow Tests")
        logger.info("=" * 60)
        
        # Test 1: Server health
        if not self.test_server_health():
            self.test_results["overall_status"] = "FAILED"
            return self.test_results
        
        # Test 2: Scenarios endpoint
        if not self.test_scenarios_endpoint():
            self.test_results["overall_status"] = "FAILED"
            return self.test_results
        
        # Test 3: Basic analysis
        analysis_success, analysis_id = self.test_basic_analysis()
        if not analysis_success:
            self.test_results["overall_status"] = "FAILED"
            return self.test_results
        
        # Test 4: Report retrieval
        if not self.test_report_retrieval(analysis_id):
            self.test_results["overall_status"] = "FAILED"
            return self.test_results
        
        # Test 5: Fix with Agent
        if not self.test_fix_with_agent():
            self.test_results["overall_status"] = "FAILED"
            return self.test_results
        
        # Test 6: ADO integration
        if not self.test_ado_integration():
            self.test_results["overall_status"] = "FAILED"
            return self.test_results
        
        # Test 7: Git operations
        if not self.test_git_operations():
            self.test_results["overall_status"] = "FAILED"
            return self.test_results
        
        # Test 8: Mock app scenarios
        if not self.test_mock_app_scenarios():
            self.test_results["overall_status"] = "FAILED"
            return self.test_results
        
        # All tests passed
        self.test_results["overall_status"] = "PASSED"
        logger.info("🎉 All end-to-end tests passed!")
        
        return self.test_results
    
    def save_results(self, filename: str = None):
        """Save test results to file"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"e2e_test_results_{timestamp}.json"
        
        with open(filename, 'w') as f:
            json.dump(self.test_results, f, indent=2)
        
        logger.info(f"💾 Test results saved to: {filename}")
        return filename
    
    def print_summary(self):
        """Print test summary"""
        logger.info("\n📊 Test Summary")
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
    """Main test runner"""
    tester = CompleteWorkflowTest()
    
    try:
        results = tester.run_all_tests()
        tester.print_summary()
        tester.save_results()
        
        if results["overall_status"] == "PASSED":
            logger.info("🎉 All end-to-end tests passed! System is working correctly.")
            return True
        else:
            logger.error("❌ Some end-to-end tests failed! System needs attention.")
            return False
            
    except Exception as e:
        logger.error(f"❌ Test suite failed with error: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
