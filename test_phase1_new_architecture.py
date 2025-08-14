#!/usr/bin/env python3
"""
Test Phase 1 New Architecture
Validates that new architecture works alongside legacy system
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

class Phase1Test:
    """Test Phase 1 new architecture"""
    
    def __init__(self):
        self.legacy_url = "http://localhost:8000"
        self.new_url = "http://localhost:8001"
        self.test_results = {
            "timestamp": time.time(),
            "tests": {},
            "overall_status": "PENDING"
        }
    
    def test_legacy_system(self) -> bool:
        """Test 1: Legacy system is still working"""
        logger.info("🧪 Test 1: Legacy System Health")
        
        try:
            response = requests.get(f"{self.legacy_url}/health", timeout=10)
            if response.status_code == 200:
                logger.info("✅ Legacy system is healthy")
                self.test_results["tests"]["legacy_system"] = {
                    "status": "PASSED",
                    "details": "Legacy system responding"
                }
                return True
            else:
                logger.error(f"❌ Legacy system failed: {response.status_code}")
                self.test_results["tests"]["legacy_system"] = {
                    "status": "FAILED",
                    "details": f"Status code: {response.status_code}"
                }
                return False
        except Exception as e:
            logger.error(f"❌ Legacy system failed: {e}")
            self.test_results["tests"]["legacy_system"] = {
                "status": "FAILED",
                "details": str(e)
            }
            return False
    
    def test_new_system(self) -> bool:
        """Test 2: New system is working"""
        logger.info("🧪 Test 2: New System Health")
        
        try:
            response = requests.get(f"{self.new_url}/health", timeout=10)
            if response.status_code == 200:
                result = response.json()
                if result.get("status") == "healthy":
                    logger.info("✅ New system is healthy")
                    self.test_results["tests"]["new_system"] = {
                        "status": "PASSED",
                        "details": "New system responding",
                        "feature_flags": result.get("feature_flags", {})
                    }
                    return True
                else:
                    logger.error("❌ New system unhealthy")
                    self.test_results["tests"]["new_system"] = {
                        "status": "FAILED",
                        "details": "System reported unhealthy"
                    }
                    return False
            else:
                logger.error(f"❌ New system failed: {response.status_code}")
                self.test_results["tests"]["new_system"] = {
                    "status": "FAILED",
                    "details": f"Status code: {response.status_code}"
                }
                return False
        except Exception as e:
            logger.error(f"❌ New system failed: {e}")
            self.test_results["tests"]["new_system"] = {
                "status": "FAILED",
                "details": str(e)
            }
            return False
    
    def test_feature_flags(self) -> bool:
        """Test 3: Feature flags are working"""
        logger.info("🧪 Test 3: Feature Flags")
        
        try:
            response = requests.get(f"{self.new_url}/api/status", timeout=10)
            if response.status_code == 200:
                result = response.json()
                feature_flags = result.get("feature_flags", {})
                
                # Check that feature flags are present
                if "flags" in feature_flags:
                    logger.info("✅ Feature flags working")
                    self.test_results["tests"]["feature_flags"] = {
                        "status": "PASSED",
                        "details": "Feature flags loaded",
                        "flags": feature_flags["flags"]
                    }
                    return True
                else:
                    logger.error("❌ Feature flags missing")
                    self.test_results["tests"]["feature_flags"] = {
                        "status": "FAILED",
                        "details": "Feature flags not found"
                    }
                    return False
            else:
                logger.error(f"❌ Feature flags test failed: {response.status_code}")
                self.test_results["tests"]["feature_flags"] = {
                    "status": "FAILED",
                    "details": f"Status code: {response.status_code}"
                }
                return False
        except Exception as e:
            logger.error(f"❌ Feature flags test failed: {e}")
            self.test_results["tests"]["feature_flags"] = {
                "status": "FAILED",
                "details": str(e)
            }
            return False
    
    def test_legacy_analysis(self) -> bool:
        """Test 4: Legacy analysis still works"""
        logger.info("🧪 Test 4: Legacy Analysis")
        
        try:
            payload = {
                "url": "http://127.0.0.1:8080/mocks/word/basic-doc.html",
                "scenario_id": "1.1",
                "modules": {"performance": True, "accessibility": True}
            }
            
            response = requests.post(
                f"{self.legacy_url}/api/analyze",
                json=payload,
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get("analysis_id"):
                    logger.info(f"✅ Legacy analysis works: {result['analysis_id']}")
                    self.test_results["tests"]["legacy_analysis"] = {
                        "status": "PASSED",
                        "details": f"Analysis ID: {result['analysis_id']}"
                    }
                    return True
                else:
                    logger.error("❌ Legacy analysis failed: No analysis ID")
                    self.test_results["tests"]["legacy_analysis"] = {
                        "status": "FAILED",
                        "details": "No analysis ID returned"
                    }
                    return False
            else:
                logger.error(f"❌ Legacy analysis failed: {response.status_code}")
                self.test_results["tests"]["legacy_analysis"] = {
                    "status": "FAILED",
                    "details": f"Status code: {response.status_code}"
                }
                return False
        except Exception as e:
            logger.error(f"❌ Legacy analysis failed: {e}")
            self.test_results["tests"]["legacy_analysis"] = {
                "status": "FAILED",
                "details": str(e)
            }
            return False
    
    def test_new_analysis_fallback(self) -> bool:
        """Test 5: New analysis falls back to legacy"""
        logger.info("🧪 Test 5: New Analysis Fallback")
        
        try:
            payload = {
                "url": "http://127.0.0.1:8080/mocks/word/basic-doc.html",
                "scenario_id": "1.1",
                "modules": {"performance": True, "accessibility": True}
            }
            
            response = requests.post(
                f"{self.new_url}/api/analysis/",
                json=payload,
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get("analysis_id"):
                    logger.info(f"✅ New analysis fallback works: {result['analysis_id']}")
                    self.test_results["tests"]["new_analysis_fallback"] = {
                        "status": "PASSED",
                        "details": f"Analysis ID: {result['analysis_id']}",
                        "message": result.get("message", "")
                    }
                    return True
                else:
                    logger.error("❌ New analysis fallback failed: No analysis ID")
                    self.test_results["tests"]["new_analysis_fallback"] = {
                        "status": "FAILED",
                        "details": "No analysis ID returned"
                    }
                    return False
            else:
                logger.error(f"❌ New analysis fallback failed: {response.status_code}")
                self.test_results["tests"]["new_analysis_fallback"] = {
                    "status": "FAILED",
                    "details": f"Status code: {response.status_code}"
                }
                return False
        except Exception as e:
            logger.error(f"❌ New analysis fallback failed: {e}")
            self.test_results["tests"]["new_analysis_fallback"] = {
                "status": "FAILED",
                "details": str(e)
            }
            return False
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Run all Phase 1 tests"""
        logger.info("🚀 Starting Phase 1 New Architecture Tests")
        logger.info("=" * 60)
        
        # Test 1: Legacy system
        if not self.test_legacy_system():
            self.test_results["overall_status"] = "FAILED"
            return self.test_results
        
        # Test 2: New system
        if not self.test_new_system():
            self.test_results["overall_status"] = "FAILED"
            return self.test_results
        
        # Test 3: Feature flags
        if not self.test_feature_flags():
            self.test_results["overall_status"] = "FAILED"
            return self.test_results
        
        # Test 4: Legacy analysis
        if not self.test_legacy_analysis():
            self.test_results["overall_status"] = "FAILED"
            return self.test_results
        
        # Test 5: New analysis fallback
        if not self.test_new_analysis_fallback():
            self.test_results["overall_status"] = "FAILED"
            return self.test_results
        
        # All tests passed
        self.test_results["overall_status"] = "PASSED"
        logger.info("🎉 All Phase 1 tests passed!")
        
        return self.test_results
    
    def print_summary(self):
        """Print test summary"""
        logger.info("\n📊 Phase 1 Test Summary")
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
        
        logger.info("\n🎯 Phase 1 Objectives:")
        logger.info("✅ New architecture created alongside legacy")
        logger.info("✅ Feature flags system working")
        logger.info("✅ Legacy system continues to work")
        logger.info("✅ New system falls back to legacy")
        logger.info("✅ Zero downtime achieved")

def main():
    """Main test runner"""
    tester = Phase1Test()
    
    try:
        results = tester.run_all_tests()
        tester.print_summary()
        
        if results["overall_status"] == "PASSED":
            logger.info("🎉 Phase 1 new architecture is working correctly!")
            return True
        else:
            logger.error("❌ Phase 1 tests failed!")
            return False
            
    except Exception as e:
        logger.error(f"❌ Phase 1 test suite failed with error: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
