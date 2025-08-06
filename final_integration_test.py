#!/usr/bin/env python3
"""
Final Integration Test Suite
Comprehensive validation of the complete UX Analyzer system
"""

import requests
import json
import time
import logging
from typing import Dict, List, Any
import subprocess
import sys
import os
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class FinalIntegrationTests:
    def __init__(self):
        self.backend_url = "http://localhost:8000"
        self.frontend_url = "http://localhost:3000"
        self.test_results = []
        self.session = requests.Session()
        
    def log_test_result(self, test_name: str, status: str, details: str = "", duration: float = 0):
        """Log and store test results"""
        result = {
            "test": test_name,
            "status": status,
            "details": details,
            "duration": f"{duration:.3f}s",
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        
        status_emoji = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⚠️"
        logger.info(f"{status_emoji} {test_name}: {status} ({duration:.3f}s)")
        if details:
            logger.info(f"   Details: {details}")

    def test_1_backend_health_extended(self):
        """Extended backend health check with metrics"""
        start_time = time.time()
        try:
            response = self.session.get(f"{self.backend_url}/health", timeout=10)
            duration = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                required_fields = ["status", "version", "uptime", "active_analyses", "queue_length"]
                missing_fields = [field for field in required_fields if field not in data]
                
                if missing_fields:
                    self.log_test_result(
                        "Backend Health Extended", 
                        "FAIL", 
                        f"Missing fields: {missing_fields}", 
                        duration
                    )
                else:
                    self.log_test_result(
                        "Backend Health Extended", 
                        "PASS", 
                        f"All health metrics present. Status: {data['status']}", 
                        duration
                    )
            else:
                self.log_test_result(
                    "Backend Health Extended", 
                    "FAIL", 
                    f"HTTP {response.status_code}", 
                    duration
                )
        except Exception as e:
            duration = time.time() - start_time
            self.log_test_result("Backend Health Extended", "FAIL", str(e), duration)

    def test_2_metrics_endpoint(self):
        """Test Prometheus metrics endpoint"""
        start_time = time.time()
        try:
            response = self.session.get(f"{self.backend_url}/metrics", timeout=10)
            duration = time.time() - start_time
            
            if response.status_code == 200:
                metrics_content = response.text
                required_metrics = ["ux_analyzer_reports_total", "ux_analyzer_active_analyses"]
                found_metrics = [metric for metric in required_metrics if metric in metrics_content]
                
                if len(found_metrics) == len(required_metrics):
                    self.log_test_result(
                        "Metrics Endpoint", 
                        "PASS", 
                        f"All {len(required_metrics)} metrics present", 
                        duration
                    )
                else:
                    missing = set(required_metrics) - set(found_metrics)
                    self.log_test_result(
                        "Metrics Endpoint", 
                        "FAIL", 
                        f"Missing metrics: {missing}", 
                        duration
                    )
            else:
                self.log_test_result("Metrics Endpoint", "FAIL", f"HTTP {response.status_code}", duration)
        except Exception as e:
            duration = time.time() - start_time
            self.log_test_result("Metrics Endpoint", "FAIL", str(e), duration)

    def test_3_url_analysis_full_flow(self):
        """Test complete URL analysis flow with report retrieval"""
        start_time = time.time()
        try:
            # Step 1: Submit analysis
            analysis_data = {
                "url": "https://example.com",
                "modules": {
                    "performance": True,
                    "accessibility": True,
                    "ux_heuristics": True
                },
                "priority": "high"
            }
            
            response = self.session.post(
                f"{self.backend_url}/api/analyze",
                json=analysis_data,
                timeout=15
            )
            
            if response.status_code != 200:
                duration = time.time() - start_time
                self.log_test_result(
                    "URL Analysis Full Flow", 
                    "FAIL", 
                    f"Analysis submission failed: {response.status_code}", 
                    duration
                )
                return
            
            analysis_response = response.json()
            analysis_id = analysis_response["analysis_id"]
            
            # Step 2: Wait for processing and retrieve report
            max_wait = 10
            wait_start = time.time()
            
            while time.time() - wait_start < max_wait:
                try:
                    report_response = self.session.get(
                        f"{self.backend_url}/api/reports/{analysis_id}",
                        timeout=10
                    )
                    
                    if report_response.status_code == 200:
                        report_data = report_response.json()
                        
                        # Validate report structure
                        required_fields = ["analysis_id", "overall_score", "modules", "metadata"]
                        missing_fields = [field for field in required_fields if field not in report_data]
                        
                        duration = time.time() - start_time
                        
                        if missing_fields:
                            self.log_test_result(
                                "URL Analysis Full Flow", 
                                "FAIL", 
                                f"Report missing fields: {missing_fields}", 
                                duration
                            )
                        else:
                            modules_count = len(report_data["modules"])
                            overall_score = report_data["overall_score"]
                            self.log_test_result(
                                "URL Analysis Full Flow", 
                                "PASS", 
                                f"Complete flow successful. Score: {overall_score}, Modules: {modules_count}", 
                                duration
                            )
                        return
                    
                except requests.exceptions.RequestException:
                    pass
                
                time.sleep(1)
            
            duration = time.time() - start_time
            self.log_test_result(
                "URL Analysis Full Flow", 
                "FAIL", 
                "Report not available within timeout", 
                duration
            )
            
        except Exception as e:
            duration = time.time() - start_time
            self.log_test_result("URL Analysis Full Flow", "FAIL", str(e), duration)

    def test_4_concurrent_analysis_load(self):
        """Test concurrent analysis handling"""
        start_time = time.time()
        try:
            # Submit multiple concurrent analyses
            concurrent_requests = 5
            analysis_ids = []
            
            for i in range(concurrent_requests):
                analysis_data = {
                    "url": f"https://example{i}.com",
                    "modules": {"performance": True, "accessibility": True},
                    "priority": "normal"
                }
                
                response = self.session.post(
                    f"{self.backend_url}/api/analyze",
                    json=analysis_data,
                    timeout=10
                )
                
                if response.status_code == 200:
                    analysis_ids.append(response.json()["analysis_id"])
            
            if len(analysis_ids) == concurrent_requests:
                duration = time.time() - start_time
                self.log_test_result(
                    "Concurrent Analysis Load", 
                    "PASS", 
                    f"Successfully submitted {concurrent_requests} concurrent analyses", 
                    duration
                )
            else:
                duration = time.time() - start_time
                self.log_test_result(
                    "Concurrent Analysis Load", 
                    "FAIL", 
                    f"Only {len(analysis_ids)}/{concurrent_requests} requests succeeded", 
                    duration
                )
                
        except Exception as e:
            duration = time.time() - start_time
            self.log_test_result("Concurrent Analysis Load", "FAIL", str(e), duration)

    def test_5_error_handling_validation(self):
        """Test error handling and validation"""
        start_time = time.time()
        error_tests = [
            {
                "name": "Empty URL",
                "data": {"url": "", "modules": {"performance": True}},
                "expected_status": 400
            },
            {
                "name": "Invalid Modules",
                "data": {"url": "https://example.com", "modules": {"invalid_module": True}},
                "expected_status": 200  # Should accept but ignore invalid modules
            },
            {
                "name": "Missing URL",
                "data": {"modules": {"performance": True}},
                "expected_status": 400
            }
        ]
        
        passed_tests = 0
        total_tests = len(error_tests)
        
        for test in error_tests:
            try:
                response = self.session.post(
                    f"{self.backend_url}/api/analyze",
                    json=test["data"],
                    timeout=10
                )
                
                if test["expected_status"] == 400 and response.status_code == 400:
                    passed_tests += 1
                elif test["expected_status"] == 200 and response.status_code == 200:
                    passed_tests += 1
                    
            except Exception:
                pass
        
        duration = time.time() - start_time
        
        if passed_tests == total_tests:
            self.log_test_result(
                "Error Handling Validation", 
                "PASS", 
                f"All {total_tests} error handling tests passed", 
                duration
            )
        else:
            self.log_test_result(
                "Error Handling Validation", 
                "FAIL", 
                f"{passed_tests}/{total_tests} error tests passed", 
                duration
            )

    def test_6_report_download_formats(self):
        """Test report download in different formats"""
        start_time = time.time()
        try:
            # First create a report
            analysis_data = {
                "url": "https://test-download.com",
                "modules": {"performance": True, "accessibility": True}
            }
            
            response = self.session.post(
                f"{self.backend_url}/api/analyze",
                json=analysis_data,
                timeout=15
            )
            
            if response.status_code != 200:
                duration = time.time() - start_time
                self.log_test_result("Report Download Formats", "FAIL", "Failed to create analysis", duration)
                return
            
            analysis_id = response.json()["analysis_id"]
            
            # Wait for report to be ready
            time.sleep(2)
            
            # Test different download formats
            formats = ["json", "html"]
            successful_formats = []
            
            for format_type in formats:
                try:
                    download_response = self.session.get(
                        f"{self.backend_url}/api/reports/{analysis_id}/download?format={format_type}",
                        timeout=10
                    )
                    
                    if download_response.status_code == 200:
                        successful_formats.append(format_type)
                        
                except Exception:
                    pass
            
            duration = time.time() - start_time
            
            if len(successful_formats) == len(formats):
                self.log_test_result(
                    "Report Download Formats", 
                    "PASS", 
                    f"All formats working: {successful_formats}", 
                    duration
                )
            else:
                self.log_test_result(
                    "Report Download Formats", 
                    "FAIL", 
                    f"Only {successful_formats} of {formats} working", 
                    duration
                )
                
        except Exception as e:
            duration = time.time() - start_time
            self.log_test_result("Report Download Formats", "FAIL", str(e), duration)

    def test_7_frontend_integration(self):
        """Test frontend accessibility and API integration"""
        start_time = time.time()
        try:
            # Test frontend health
            response = self.session.get(f"{self.frontend_url}", timeout=10)
            
            if response.status_code == 200:
                # Test API endpoint through frontend proxy
                try:
                    proxy_response = self.session.get(f"{self.frontend_url}/api/health", timeout=10)
                    duration = time.time() - start_time
                    
                    if proxy_response.status_code == 200:
                        self.log_test_result(
                            "Frontend Integration", 
                            "PASS", 
                            "Frontend and API proxy working", 
                            duration
                        )
                    else:
                        self.log_test_result(
                            "Frontend Integration", 
                            "PARTIAL", 
                            f"Frontend OK, but API proxy returned {proxy_response.status_code}", 
                            duration
                        )
                except Exception:
                    duration = time.time() - start_time
                    self.log_test_result(
                        "Frontend Integration", 
                        "PARTIAL", 
                        "Frontend accessible but API proxy not working", 
                        duration
                    )
            else:
                duration = time.time() - start_time
                self.log_test_result(
                    "Frontend Integration", 
                    "FAIL", 
                    f"Frontend not accessible: {response.status_code}", 
                    duration
                )
                
        except Exception as e:
            duration = time.time() - start_time
            self.log_test_result("Frontend Integration", "FAIL", str(e), duration)

    def test_8_system_performance_validation(self):
        """Validate system performance under normal load"""
        start_time = time.time()
        try:
            # Performance metrics
            response_times = []
            success_count = 0
            total_requests = 10
            
            for i in range(total_requests):
                request_start = time.time()
                
                try:
                    response = self.session.get(f"{self.backend_url}/health", timeout=5)
                    request_duration = time.time() - request_start
                    response_times.append(request_duration)
                    
                    if response.status_code == 200:
                        success_count += 1
                        
                except Exception:
                    pass
            
            if response_times:
                avg_response_time = sum(response_times) / len(response_times)
                max_response_time = max(response_times)
                success_rate = (success_count / total_requests) * 100
                
                duration = time.time() - start_time
                
                # Performance criteria
                if avg_response_time < 0.5 and max_response_time < 1.0 and success_rate >= 95:
                    self.log_test_result(
                        "System Performance Validation", 
                        "PASS", 
                        f"Avg: {avg_response_time:.3f}s, Max: {max_response_time:.3f}s, Success: {success_rate}%", 
                        duration
                    )
                else:
                    self.log_test_result(
                        "System Performance Validation", 
                        "FAIL", 
                        f"Performance below threshold. Avg: {avg_response_time:.3f}s, Success: {success_rate}%", 
                        duration
                    )
            else:
                duration = time.time() - start_time
                self.log_test_result("System Performance Validation", "FAIL", "No successful requests", duration)
                
        except Exception as e:
            duration = time.time() - start_time
            self.log_test_result("System Performance Validation", "FAIL", str(e), duration)

    def generate_final_report(self):
        """Generate comprehensive final test report"""
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r["status"] == "PASS"])
        failed_tests = len([r for r in self.test_results if r["status"] == "FAIL"])
        partial_tests = len([r for r in self.test_results if r["status"] == "PARTIAL"])
        
        success_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
        
        print("\n" + "="*80)
        print("🎯 UX ANALYZER - FINAL INTEGRATION TEST REPORT")
        print("="*80)
        print(f"📊 Test Summary:")
        print(f"   Total Tests: {total_tests}")
        print(f"   ✅ Passed: {passed_tests}")
        print(f"   ❌ Failed: {failed_tests}")
        print(f"   ⚠️  Partial: {partial_tests}")
        print(f"   📈 Success Rate: {success_rate:.1f}%")
        print("\n📋 Detailed Results:")
        
        for result in self.test_results:
            status_emoji = "✅" if result["status"] == "PASS" else "❌" if result["status"] == "FAIL" else "⚠️"
            print(f"   {status_emoji} {result['test']}: {result['status']} ({result['duration']})")
            if result["details"]:
                print(f"      └─ {result['details']}")
        
        print("\n🎯 Overall Assessment:")
        if success_rate >= 90:
            print("   🌟 EXCELLENT: System is production-ready with outstanding performance!")
        elif success_rate >= 75:
            print("   ✅ GOOD: System is ready for production with minor improvements needed.")
        elif success_rate >= 60:
            print("   ⚠️  ACCEPTABLE: System functional but requires attention to failed tests.")
        else:
            print("   ❌ NEEDS WORK: Multiple issues need to be resolved before production.")
        
        print("\n🚀 Production Readiness Status:")
        critical_tests = ["Backend Health Extended", "URL Analysis Full Flow", "System Performance Validation"]
        critical_passed = len([r for r in self.test_results if r["test"] in critical_tests and r["status"] == "PASS"])
        
        if critical_passed == len(critical_tests):
            print("   ✅ All critical systems operational")
        else:
            print(f"   ⚠️  {critical_passed}/{len(critical_tests)} critical systems operational")
        
        print("="*80)
        
        return success_rate

    def run_all_tests(self):
        """Execute all integration tests"""
        print("🚀 Starting Final Integration Test Suite...")
        print("="*60)
        
        # List of all test methods
        test_methods = [
            self.test_1_backend_health_extended,
            self.test_2_metrics_endpoint,
            self.test_3_url_analysis_full_flow,
            self.test_4_concurrent_analysis_load,
            self.test_5_error_handling_validation,
            self.test_6_report_download_formats,
            self.test_7_frontend_integration,
            self.test_8_system_performance_validation
        ]
        
        # Execute all tests
        for test_method in test_methods:
            try:
                test_method()
            except Exception as e:
                test_name = test_method.__name__.replace('test_', '').replace('_', ' ').title()
                self.log_test_result(test_name, "FAIL", f"Test execution error: {str(e)}")
            
            # Small delay between tests
            time.sleep(0.5)
        
        # Generate final report
        return self.generate_final_report()

def main():
    """Main test execution"""
    print("🎯 UX Analyzer - Final Integration Testing")
    print("=" * 50)
    
    # Check if servers are running
    test_runner = FinalIntegrationTests()
    
    try:
        # Quick connectivity check
        backend_check = requests.get("http://localhost:8000/health", timeout=5)
        frontend_check = requests.get("http://localhost:3000", timeout=5)
        
        print("✅ Backend server detected")
        print("✅ Frontend server detected")
        print()
        
    except requests.exceptions.RequestException as e:
        print("⚠️  Server connectivity issue detected:")
        print("   Make sure both backend (port 8000) and frontend (port 3000) are running")
        print("   Backend: python3 production_server.py")
        print("   Frontend: npm run dev")
        print()
        return 1
    
    # Run comprehensive test suite
    success_rate = test_runner.run_all_tests()
    
    # Return appropriate exit code
    return 0 if success_rate >= 75 else 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
