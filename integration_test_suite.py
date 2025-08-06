#!/usr/bin/env python3
"""
Comprehensive Integration Test Suite for UX Analyzer
Tests the full stack: FastAPI backend, React frontend, and proxy integration
"""

import requests
import json
import time
from typing import Dict, List, Any
import subprocess
import sys
from pathlib import Path

class UXAnalyzerTestSuite:
    def __init__(self):
        self.backend_url = "http://127.0.0.1:8000"
        self.frontend_url = "http://localhost:3000"
        self.test_results = []
        
    def log_test(self, test_name: str, status: str, details: str = ""):
        """Log test results"""
        result = {
            "test": test_name,
            "status": status,
            "timestamp": time.strftime("%H:%M:%S"),
            "details": details
        }
        self.test_results.append(result)
        
        status_emoji = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⚠️"
        print(f"{status_emoji} {test_name}: {status}")
        if details:
            print(f"   {details}")

    def test_backend_health(self):
        """Test backend server health"""
        try:
            response = requests.get(f"{self.backend_url}/health", timeout=5)
            if response.status_code == 200:
                data = response.json()
                if "status" in data and data["status"] == "healthy":
                    self.log_test("Backend Health", "PASS", f"Response time: {response.elapsed.total_seconds():.3f}s")
                else:
                    self.log_test("Backend Health", "FAIL", "Invalid health response format")
            else:
                self.log_test("Backend Health", "FAIL", f"Status code: {response.status_code}")
        except Exception as e:
            self.log_test("Backend Health", "FAIL", str(e))

    def test_frontend_availability(self):
        """Test frontend server availability"""
        try:
            response = requests.get(self.frontend_url, timeout=5)
            if response.status_code == 200:
                self.log_test("Frontend Availability", "PASS", f"Response time: {response.elapsed.total_seconds():.3f}s")
            else:
                self.log_test("Frontend Availability", "FAIL", f"Status code: {response.status_code}")
        except Exception as e:
            self.log_test("Frontend Availability", "FAIL", str(e))

    def test_proxy_integration(self):
        """Test Vite proxy forwarding to backend"""
        try:
            # Test through frontend proxy
            response = requests.post(
                f"{self.frontend_url}/api/analyze",
                json={
                    "url": "https://example.com",
                    "modules": {"performance": True, "accessibility": True},
                    "output_format": "json"
                },
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if "analysis_id" in data and "status" in data:
                    self.log_test("Proxy Integration", "PASS", f"Analysis ID: {data['analysis_id']}")
                    return data["analysis_id"]
                else:
                    self.log_test("Proxy Integration", "FAIL", "Invalid response format")
            else:
                self.log_test("Proxy Integration", "FAIL", f"Status code: {response.status_code}")
        except Exception as e:
            self.log_test("Proxy Integration", "FAIL", str(e))
        return None

    def test_all_analysis_endpoints(self):
        """Test all analysis endpoint types"""
        endpoints = [
            {
                "name": "URL Analysis",
                "endpoint": "/api/analyze",
                "data": {
                    "url": "https://google.com",
                    "modules": {"performance": True, "accessibility": True},
                    "output_format": "html"
                }
            },
            {
                "name": "Scenario Analysis", 
                "endpoint": "/api/analyze/scenario",
                "data": {
                    "scenario": "User logs in and navigates to dashboard",
                    "modules": {"ux_heuristics": True, "functional": True},
                    "output_format": "json"
                }
            },
            {
                "name": "Mock App Analysis",
                "endpoint": "/api/analyze/mock-app", 
                "data": {
                    "app_path": "localhost:8080",
                    "modules": {"performance": True, "keyboard": True},
                    "output_format": "html"
                }
            }
        ]
        
        analysis_ids = []
        for endpoint_test in endpoints:
            try:
                response = requests.post(
                    f"{self.backend_url}{endpoint_test['endpoint']}",
                    json=endpoint_test['data'],
                    timeout=10
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if "analysis_id" in data:
                        analysis_ids.append(data["analysis_id"])
                        self.log_test(endpoint_test['name'], "PASS", f"ID: {data['analysis_id']}")
                    else:
                        self.log_test(endpoint_test['name'], "FAIL", "No analysis_id in response")
                else:
                    self.log_test(endpoint_test['name'], "FAIL", f"Status: {response.status_code}")
            except Exception as e:
                self.log_test(endpoint_test['name'], "FAIL", str(e))
        
        return analysis_ids

    def test_report_retrieval(self, analysis_ids: List[str]):
        """Test report retrieval for generated analyses"""
        for analysis_id in analysis_ids:
            try:
                response = requests.get(f"{self.backend_url}/api/reports/{analysis_id}", timeout=5)
                if response.status_code == 200:
                    data = response.json()
                    if "overall_score" in data and "modules" in data:
                        self.log_test(f"Report Retrieval ({analysis_id[:8]})", "PASS", 
                                    f"Score: {data['overall_score']}, Modules: {len(data['modules'])}")
                    else:
                        self.log_test(f"Report Retrieval ({analysis_id[:8]})", "FAIL", "Invalid report format")
                else:
                    self.log_test(f"Report Retrieval ({analysis_id[:8]})", "FAIL", f"Status: {response.status_code}")
            except Exception as e:
                self.log_test(f"Report Retrieval ({analysis_id[:8]})", "FAIL", str(e))

    def test_download_endpoints(self, analysis_ids: List[str]):
        """Test report download in different formats"""
        if not analysis_ids:
            self.log_test("Download Endpoints", "SKIP", "No analysis IDs available")
            return
            
        analysis_id = analysis_ids[0]
        formats = ["json", "html"]
        
        for fmt in formats:
            try:
                response = requests.get(
                    f"{self.backend_url}/api/reports/{analysis_id}/download?format={fmt}",
                    timeout=5
                )
                if response.status_code == 200:
                    content_length = len(response.content)
                    self.log_test(f"Download {fmt.upper()}", "PASS", f"Size: {content_length} bytes")
                else:
                    self.log_test(f"Download {fmt.upper()}", "FAIL", f"Status: {response.status_code}")
            except Exception as e:
                self.log_test(f"Download {fmt.upper()}", "FAIL", str(e))

    def test_performance_benchmarks(self):
        """Test performance benchmarks"""
        # Test response times for multiple requests
        start_time = time.time()
        successful_requests = 0
        
        for i in range(5):
            try:
                response = requests.post(
                    f"{self.backend_url}/api/analyze",
                    json={"url": f"https://example{i}.com", "modules": {"performance": True}},
                    timeout=10
                )
                if response.status_code == 200:
                    successful_requests += 1
            except:
                pass
        
        total_time = time.time() - start_time
        avg_time = total_time / 5
        
        if successful_requests >= 4 and avg_time < 2.0:
            self.log_test("Performance Benchmark", "PASS", 
                         f"Avg: {avg_time:.3f}s, Success: {successful_requests}/5")
        else:
            self.log_test("Performance Benchmark", "FAIL", 
                         f"Avg: {avg_time:.3f}s, Success: {successful_requests}/5")

    def test_error_handling(self):
        """Test error handling for invalid requests"""
        error_tests = [
            {
                "name": "Missing URL",
                "endpoint": "/api/analyze",
                "data": {"modules": {"performance": True}},
                "expected_status": 400
            },
            {
                "name": "Invalid Report ID",
                "endpoint": "/api/reports/invalid-id",
                "method": "GET",
                "expected_status": 404
            },
            {
                "name": "Invalid JSON",
                "endpoint": "/api/analyze",
                "data": "invalid-json",
                "expected_status": 422
            }
        ]
        
        for test in error_tests:
            try:
                if test.get("method") == "GET":
                    response = requests.get(f"{self.backend_url}{test['endpoint']}", timeout=5)
                else:
                    response = requests.post(
                        f"{self.backend_url}{test['endpoint']}",
                        json=test['data'],
                        timeout=5
                    )
                
                if response.status_code == test['expected_status']:
                    self.log_test(f"Error Handling: {test['name']}", "PASS", 
                                f"Expected {test['expected_status']}, got {response.status_code}")
                else:
                    self.log_test(f"Error Handling: {test['name']}", "FAIL", 
                                f"Expected {test['expected_status']}, got {response.status_code}")
            except Exception as e:
                self.log_test(f"Error Handling: {test['name']}", "FAIL", str(e))

    def run_all_tests(self):
        """Run the complete test suite"""
        print("🧪 Starting UX Analyzer Comprehensive Test Suite")
        print("=" * 60)
        
        # Basic connectivity
        self.test_backend_health()
        self.test_frontend_availability()
        
        # Integration tests
        proxy_analysis_id = self.test_proxy_integration()
        
        # API endpoint tests
        analysis_ids = self.test_all_analysis_endpoints()
        
        # Report functionality
        if analysis_ids:
            self.test_report_retrieval(analysis_ids)
            self.test_download_endpoints(analysis_ids)
        
        # Performance and error handling
        self.test_performance_benchmarks()
        self.test_error_handling()
        
        # Summary
        self.print_summary()

    def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 60)
        print("🧪 TEST SUMMARY")
        print("=" * 60)
        
        passed = len([t for t in self.test_results if t["status"] == "PASS"])
        failed = len([t for t in self.test_results if t["status"] == "FAIL"])
        skipped = len([t for t in self.test_results if t["status"] == "SKIP"])
        total = len(self.test_results)
        
        print(f"✅ PASSED: {passed}")
        print(f"❌ FAILED: {failed}")
        print(f"⚠️ SKIPPED: {skipped}")
        print(f"📊 TOTAL: {total}")
        
        success_rate = (passed / total * 100) if total > 0 else 0
        print(f"🎯 SUCCESS RATE: {success_rate:.1f}%")
        
        if failed > 0:
            print("\n❌ FAILED TESTS:")
            for test in self.test_results:
                if test["status"] == "FAIL":
                    print(f"   • {test['test']}: {test['details']}")
        
        print("\n" + "=" * 60)
        
        # Export results
        with open("test_results.json", "w") as f:
            json.dump(self.test_results, f, indent=2)
        print("📄 Full results saved to: test_results.json")

if __name__ == "__main__":
    suite = UXAnalyzerTestSuite()
    suite.run_all_tests()
