#!/usr/bin/env python3
"""
Performance Testing and Optimization Suite
Tests system performance under load and identifies bottlenecks
"""

import requests
import time
import threading
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Any
import statistics

class PerformanceTestSuite:
    def __init__(self):
        self.backend_url = "http://127.0.0.1:8000"
        self.frontend_url = "http://localhost:3000"
        self.test_results = {}
        
    def log_performance(self, test_name: str, metrics: Dict[str, Any]):
        """Log performance metrics"""
        self.test_results[test_name] = metrics
        print(f"📊 {test_name}")
        for key, value in metrics.items():
            if isinstance(value, float):
                print(f"   {key}: {value:.3f}")
            else:
                print(f"   {key}: {value}")
        print()

    def single_request_benchmark(self, endpoint: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Benchmark a single request"""
        start_time = time.time()
        try:
            response = requests.post(f"{self.backend_url}{endpoint}", json=data, timeout=30)
            end_time = time.time()
            
            return {
                "response_time": end_time - start_time,
                "status_code": response.status_code,
                "success": response.status_code == 200,
                "content_length": len(response.content) if response.content else 0
            }
        except Exception as e:
            return {
                "response_time": time.time() - start_time,
                "status_code": 0,
                "success": False,
                "error": str(e),
                "content_length": 0
            }

    def load_test(self, endpoint: str, data: Dict[str, Any], concurrent_users: int = 5, requests_per_user: int = 3):
        """Perform load testing with concurrent requests"""
        print(f"🔥 Load Testing: {concurrent_users} users, {requests_per_user} requests each")
        
        all_results = []
        start_time = time.time()
        
        def user_session():
            user_results = []
            for _ in range(requests_per_user):
                result = self.single_request_benchmark(endpoint, data)
                user_results.append(result)
                time.sleep(0.1)  # Brief pause between requests
            return user_results
        
        with ThreadPoolExecutor(max_workers=concurrent_users) as executor:
            futures = [executor.submit(user_session) for _ in range(concurrent_users)]
            
            for future in as_completed(futures):
                try:
                    user_results = future.result()
                    all_results.extend(user_results)
                except Exception as e:
                    print(f"   User session failed: {e}")
        
        total_time = time.time() - start_time
        
        # Analyze results
        successful_requests = [r for r in all_results if r["success"]]
        failed_requests = [r for r in all_results if not r["success"]]
        
        if successful_requests:
            response_times = [r["response_time"] for r in successful_requests]
            metrics = {
                "total_requests": len(all_results),
                "successful_requests": len(successful_requests),
                "failed_requests": len(failed_requests),
                "success_rate": len(successful_requests) / len(all_results) * 100,
                "total_time": total_time,
                "requests_per_second": len(all_results) / total_time,
                "avg_response_time": statistics.mean(response_times),
                "min_response_time": min(response_times),
                "max_response_time": max(response_times),
                "median_response_time": statistics.median(response_times),
                "p95_response_time": sorted(response_times)[int(0.95 * len(response_times))] if len(response_times) > 1 else response_times[0]
            }
        else:
            metrics = {
                "total_requests": len(all_results),
                "successful_requests": 0,
                "failed_requests": len(failed_requests),
                "success_rate": 0,
                "total_time": total_time,
                "requests_per_second": 0,
                "errors": [r.get("error", "Unknown") for r in failed_requests]
            }
        
        return metrics

    def test_api_endpoint_performance(self):
        """Test performance of individual API endpoints"""
        endpoints = [
            {
                "name": "URL Analysis",
                "endpoint": "/api/analyze",
                "data": {
                    "url": "https://example.com",
                    "modules": {"performance": True, "accessibility": True},
                    "output_format": "json"
                }
            },
            {
                "name": "Mock App Analysis",
                "endpoint": "/api/analyze/mock-app",
                "data": {
                    "app_path": "localhost:8080",
                    "modules": {"performance": True, "keyboard": True, "ux_heuristics": True},
                    "output_format": "html"
                }
            }
        ]
        
        for endpoint_test in endpoints:
            # Single request benchmark
            single_result = self.single_request_benchmark(
                endpoint_test["endpoint"], 
                endpoint_test["data"]
            )
            self.log_performance(f"{endpoint_test['name']} - Single Request", single_result)
            
            # Load test
            load_result = self.load_test(
                endpoint_test["endpoint"], 
                endpoint_test["data"],
                concurrent_users=3,
                requests_per_user=2
            )
            self.log_performance(f"{endpoint_test['name']} - Load Test", load_result)

    def test_report_retrieval_performance(self):
        """Test report retrieval performance"""
        # First create some reports
        print("🔧 Creating test reports...")
        report_ids = []
        
        for i in range(5):
            try:
                response = requests.post(
                    f"{self.backend_url}/api/analyze",
                    json={
                        "url": f"https://test{i}.com",
                        "modules": {"performance": True},
                        "output_format": "json"
                    },
                    timeout=10
                )
                if response.status_code == 200:
                    data = response.json()
                    report_ids.append(data["analysis_id"])
            except:
                continue
        
        if not report_ids:
            print("   ⚠️ No reports created, skipping report performance tests")
            return
        
        print(f"   ✅ Created {len(report_ids)} test reports")
        
        # Test report retrieval performance
        def get_report(report_id: str):
            start_time = time.time()
            try:
                response = requests.get(f"{self.backend_url}/api/reports/{report_id}", timeout=10)
                return {
                    "response_time": time.time() - start_time,
                    "success": response.status_code == 200,
                    "content_length": len(response.content)
                }
            except Exception as e:
                return {
                    "response_time": time.time() - start_time,
                    "success": False,
                    "error": str(e)
                }
        
        # Concurrent report retrieval
        start_time = time.time()
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(get_report, report_id) for report_id in report_ids * 3]  # 3x each report
            results = [future.result() for future in as_completed(futures)]
        
        total_time = time.time() - start_time
        successful = [r for r in results if r["success"]]
        
        if successful:
            response_times = [r["response_time"] for r in successful]
            metrics = {
                "total_requests": len(results),
                "successful_requests": len(successful),
                "success_rate": len(successful) / len(results) * 100,
                "avg_response_time": statistics.mean(response_times),
                "max_response_time": max(response_times),
                "requests_per_second": len(results) / total_time
            }
            self.log_performance("Report Retrieval - Concurrent", metrics)

    def test_proxy_performance(self):
        """Test frontend proxy performance"""
        print("🌐 Testing Frontend Proxy Performance...")
        
        proxy_results = []
        direct_results = []
        
        test_data = {
            "url": "https://proxy-test.com",
            "modules": {"performance": True},
            "output_format": "json"
        }
        
        # Test direct backend requests
        for _ in range(5):
            result = self.single_request_benchmark("/api/analyze", test_data)
            direct_results.append(result["response_time"])
        
        # Test through proxy
        for _ in range(5):
            start_time = time.time()
            try:
                response = requests.post(
                    f"{self.frontend_url}/api/analyze",
                    json=test_data,
                    timeout=10
                )
                proxy_results.append(time.time() - start_time)
            except:
                proxy_results.append(999)  # High penalty for failed requests
        
        if proxy_results and direct_results:
            metrics = {
                "direct_avg": statistics.mean(direct_results),
                "proxy_avg": statistics.mean(proxy_results),
                "proxy_overhead": statistics.mean(proxy_results) - statistics.mean(direct_results),
                "proxy_overhead_percent": ((statistics.mean(proxy_results) - statistics.mean(direct_results)) / statistics.mean(direct_results)) * 100
            }
            self.log_performance("Proxy vs Direct Performance", metrics)

    def memory_usage_simulation(self):
        """Simulate high memory usage scenarios"""
        print("💾 Testing Memory Usage Under Load...")
        
        # Create multiple large analysis requests
        large_data = {
            "url": "https://large-test.com",
            "modules": {
                "performance": True,
                "accessibility": True,
                "keyboard": True,
                "ux_heuristics": True,
                "best_practices": True,
                "health_alerts": True,
                "functional": True
            },
            "output_format": "html"
        }
        
        start_time = time.time()
        active_requests = []
        
        # Launch 10 concurrent requests
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [
                executor.submit(self.single_request_benchmark, "/api/analyze", large_data)
                for _ in range(10)
            ]
            
            results = [future.result() for future in as_completed(futures)]
        
        total_time = time.time() - start_time
        successful = [r for r in results if r["success"]]
        
        if successful:
            metrics = {
                "concurrent_requests": 10,
                "successful_requests": len(successful),
                "total_time": total_time,
                "avg_response_time": statistics.mean([r["response_time"] for r in successful]),
                "memory_test_passed": len(successful) >= 8  # At least 80% success rate
            }
            self.log_performance("High Memory Load Test", metrics)

    def run_performance_tests(self):
        """Run all performance tests"""
        print("🚀 Starting Performance Test Suite")
        print("=" * 60)
        
        self.test_api_endpoint_performance()
        self.test_report_retrieval_performance()
        self.test_proxy_performance()
        self.memory_usage_simulation()
        
        # Export results
        with open("performance_results.json", "w") as f:
            json.dump(self.test_results, f, indent=2, default=str)
        
        print("=" * 60)
        print("🏁 Performance Testing Complete")
        print("📄 Results saved to: performance_results.json")
        print("=" * 60)

if __name__ == "__main__":
    suite = PerformanceTestSuite()
    suite.run_performance_tests()
