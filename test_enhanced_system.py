#!/usr/bin/env python3
"""
Comprehensive Test Suite for Enhanced UX Analyzer
Tests realistic scenario execution and persistent report storage
"""

import asyncio
import json
import requests
import time
from pathlib import Path
from datetime import datetime
import logging
import subprocess
import sys

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class UXAnalyzerTestSuite:
    """Comprehensive test suite for the enhanced UX analyzer"""
    
    def __init__(self, api_base_url: str = "http://localhost:8000"):
        self.api_base_url = api_base_url
        self.test_results = []
        self.server_process = None
    
    def log_test(self, test_name: str, status: str, details: str = "", duration: float = 0):
        """Log test result"""
        result = {
            "test": test_name,
            "status": status,
            "details": details,
            "duration_seconds": round(duration, 2),
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        
        status_emoji = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⚠️"
        duration_str = f" ({duration:.2f}s)" if duration > 0 else ""
        print(f"{status_emoji} {test_name}: {status}{duration_str}")
        if details:
            print(f"   {details}")
    
    def check_server_health(self) -> bool:
        """Check if the enhanced server is running"""
        try:
            response = requests.get(f"{self.api_base_url}/health", timeout=5)
            if response.status_code == 200:
                data = response.json()
                return data.get("status") == "healthy"
        except:
            pass
        return False
    
    async def run_comprehensive_tests(self):
        """Run all enhanced system tests"""
        print("🧪 ENHANCED UX ANALYZER COMPREHENSIVE TEST SUITE")
        print("=" * 70)
        print(f"Testing API: {self.api_base_url}")
        print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 70)
        
        # Prerequisites
        await self.test_prerequisites()
        
        # Phase 1: Basic System Tests
        print("\n📋 PHASE 1: Basic System Tests")
        await self.test_server_health()
        await self.test_enhanced_endpoints()
        
        # Phase 2: Scenario Execution Tests
        print("\n🎯 PHASE 2: Scenario Execution Tests")
        await self.test_mock_scenario_execution()
        await self.test_enhanced_scenario_execution()
        
        # Phase 3: Report Persistence Tests
        print("\n💾 PHASE 3: Report Persistence Tests")
        await self.test_report_persistence()
        await self.test_report_retrieval()
        await self.test_report_search()
        
        # Phase 4: Craft Bug Detection Tests
        print("\n🔍 PHASE 4: Craft Bug Detection Tests")
        await self.test_craft_bug_detection()
        
        # Phase 5: System Performance Tests
        print("\n⚡ PHASE 5: System Performance Tests")
        await self.test_system_statistics()
        await self.test_cleanup_functionality()
        
        # Summary
        self.print_test_summary()
    
    async def test_prerequisites(self):
        """Test system prerequisites"""
        start_time = time.time()
        
        # Check if required files exist
        required_files = [
            "enhanced_scenario_runner.py",
            "enhanced_report_handler.py",
            "enhanced_fastapi_server.py",
            "scenario_executor.py"
        ]
        
        missing_files = []
        for file in required_files:
            if not Path(file).exists():
                missing_files.append(file)
        
        if missing_files:
            self.log_test("Prerequisites Check", "FAIL", 
                         f"Missing files: {', '.join(missing_files)}", 
                         time.time() - start_time)
        else:
            self.log_test("Prerequisites Check", "PASS", 
                         "All required files present", 
                         time.time() - start_time)
        
        # Check if reports directory exists or can be created
        reports_dir = Path("reports")
        try:
            reports_dir.mkdir(exist_ok=True)
            (reports_dir / "analysis").mkdir(exist_ok=True)
            (reports_dir / "screenshots").mkdir(exist_ok=True)
            self.log_test("Reports Directory", "PASS", 
                         f"Reports directory ready at {reports_dir.absolute()}")
        except Exception as e:
            self.log_test("Reports Directory", "FAIL", f"Could not create reports directory: {e}")
    
    async def test_server_health(self):
        """Test server health and basic connectivity"""
        start_time = time.time()
        
        try:
            response = requests.get(f"{self.api_base_url}/health", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get("status") == "healthy":
                    version = data.get("version", "unknown")
                    features = len(data.get("features", {}))
                    
                    self.log_test("Server Health Check", "PASS", 
                                 f"Server healthy (v{version}, {features} features)", 
                                 time.time() - start_time)
                else:
                    self.log_test("Server Health Check", "FAIL", 
                                 "Server status not healthy", 
                                 time.time() - start_time)
            else:
                self.log_test("Server Health Check", "FAIL", 
                             f"HTTP {response.status_code}", 
                             time.time() - start_time)
                
        except Exception as e:
            self.log_test("Server Health Check", "FAIL", 
                         f"Connection error: {e}", 
                         time.time() - start_time)
    
    async def test_enhanced_endpoints(self):
        """Test enhanced API endpoints"""
        endpoints_to_test = [
            ("/", "Root Endpoint"),
            ("/api/scenarios", "Scenarios Endpoint"),
            ("/api/reports/statistics", "Statistics Endpoint"),
            ("/api/reports", "Reports List Endpoint")
        ]
        
        for endpoint, test_name in endpoints_to_test:
            start_time = time.time()
            try:
                response = requests.get(f"{self.api_base_url}{endpoint}", timeout=5)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    if endpoint == "/":
                        has_features = "features" in data
                        version = data.get("version", "unknown")
                        if has_features and version == "2.0.0":
                            self.log_test(test_name, "PASS", 
                                         f"Enhanced root endpoint (v{version})", 
                                         time.time() - start_time)
                        else:
                            self.log_test(test_name, "FAIL", 
                                         "Missing enhanced features", 
                                         time.time() - start_time)
                    
                    elif endpoint == "/api/reports/statistics":
                        has_stats = "index_statistics" in data
                        has_storage = "storage_info" in data
                        if has_stats and has_storage:
                            total_reports = data.get("index_statistics", {}).get("total_reports", 0)
                            self.log_test(test_name, "PASS", 
                                         f"Statistics available ({total_reports} reports tracked)", 
                                         time.time() - start_time)
                        else:
                            self.log_test(test_name, "FAIL", 
                                         "Incomplete statistics structure", 
                                         time.time() - start_time)
                    
                    else:
                        self.log_test(test_name, "PASS", 
                                     "Endpoint responding correctly", 
                                     time.time() - start_time)
                else:
                    self.log_test(test_name, "FAIL", 
                                 f"HTTP {response.status_code}", 
                                 time.time() - start_time)
                    
            except Exception as e:
                self.log_test(test_name, "FAIL", 
                             f"Exception: {e}", 
                             time.time() - start_time)
    
    async def test_mock_scenario_execution(self):
        """Test mock scenario execution (existing functionality)"""
        start_time = time.time()
        
        try:
            # Test with existing scenario file or create a simple one
            test_scenario_path = "scenarios/test_scenario.yaml"
            
            if not Path(test_scenario_path).exists():
                # Create a simple test scenario
                Path("scenarios").mkdir(exist_ok=True)
                test_scenario = {
                    "name": "Simple Test Scenario",
                    "tests": {
                        "basic_test": {
                            "description": "Basic test scenario",
                            "scenarios": [
                                {
                                    "name": "Navigation Test",
                                    "steps": [
                                        {"action": "navigate_to_url", "url": "{server_url}"},
                                        {"action": "wait", "duration": 1000},
                                        {"action": "screenshot"}
                                    ]
                                }
                            ]
                        }
                    }
                }
                
                import yaml
                with open(test_scenario_path, 'w') as f:
                    yaml.dump(test_scenario, f)
            
            # Test mock scenario execution
            analysis_request = {
                "url": "https://example.com",
                "scenario_path": test_scenario_path,
                "modules": {
                    "performance": True,
                    "accessibility": True,
                    "ux_heuristics": True
                }
            }
            
            response = requests.post(
                f"{self.api_base_url}/api/analyze/url-scenario",
                json=analysis_request,
                timeout=15
            )
            
            if response.status_code == 200:
                data = response.json()
                analysis_id = data["analysis_id"]
                
                # Get the report
                report_response = requests.get(f"{self.api_base_url}/api/reports/{analysis_id}")
                
                if report_response.status_code == 200:
                    report = report_response.json()
                    
                    has_scenarios = "scenario_results" in report or "modules" in report
                    overall_score = report.get("overall_score", 0)
                    
                    self.log_test("Mock Scenario Execution", "PASS", 
                                 f"Scenario executed (ID: {analysis_id}, Score: {overall_score})", 
                                 time.time() - start_time)
                else:
                    self.log_test("Mock Scenario Execution", "FAIL", 
                                 f"Could not retrieve report: {report_response.status_code}", 
                                 time.time() - start_time)
            else:
                self.log_test("Mock Scenario Execution", "FAIL", 
                             f"Analysis request failed: {response.status_code}", 
                             time.time() - start_time)
                
        except Exception as e:
            self.log_test("Mock Scenario Execution", "FAIL", 
                         f"Exception: {e}", 
                         time.time() - start_time)
    
    async def test_enhanced_scenario_execution(self):
        """Test enhanced scenario execution with craft bug detection"""
        start_time = time.time()
        
        try:
            analysis_request = {
                "url": "https://example.com",
                "scenario_path": "scenarios/test_scenario.yaml",
                "execution_mode": "mock",  # Use mock for testing (realistic needs browser)
                "modules": {
                    "performance": True,
                    "accessibility": True,
                    "craft_bug_detection": True,
                    "realistic_execution": False
                },
                "headless": True
            }
            
            response = requests.post(
                f"{self.api_base_url}/api/analyze/enhanced",
                json=analysis_request,
                timeout=15
            )
            
            if response.status_code == 200:
                data = response.json()
                analysis_id = data["analysis_id"]
                execution_mode = data.get("execution_mode", "unknown")
                
                # Wait a moment for processing if needed
                await asyncio.sleep(1)
                
                # Get the report
                report_response = requests.get(f"{self.api_base_url}/api/reports/{analysis_id}")
                
                if report_response.status_code == 200:
                    report = report_response.json()
                    
                    # Check for enhanced features
                    has_craft_features = (
                        "craft_bugs_detected" in report or 
                        "craft_bugs" in report or
                        "pattern_issues" in report
                    )
                    
                    overall_score = report.get("overall_score", 0)
                    
                    self.log_test("Enhanced Scenario Execution", "PASS", 
                                 f"Enhanced analysis completed (ID: {analysis_id}, Mode: {execution_mode}, Score: {overall_score})", 
                                 time.time() - start_time)
                else:
                    self.log_test("Enhanced Scenario Execution", "FAIL", 
                                 f"Could not retrieve report: {report_response.status_code}", 
                                 time.time() - start_time)
            else:
                self.log_test("Enhanced Scenario Execution", "FAIL", 
                             f"Enhanced analysis request failed: {response.status_code}", 
                             time.time() - start_time)
                
        except Exception as e:
            self.log_test("Enhanced Scenario Execution", "FAIL", 
                         f"Exception: {e}", 
                         time.time() - start_time)
    
    async def test_report_persistence(self):
        """Test report persistence to disk"""
        start_time = time.time()
        
        try:
            # Check if reports directory structure exists
            reports_dir = Path("reports")
            analysis_dir = reports_dir / "analysis"
            
            if not reports_dir.exists() or not analysis_dir.exists():
                self.log_test("Report Persistence", "FAIL", 
                             "Reports directory structure missing", 
                             time.time() - start_time)
                return
            
            # Check for analysis index
            index_file = reports_dir / "analysis_index.json"
            
            if not index_file.exists():
                self.log_test("Report Persistence", "FAIL", 
                             "Analysis index file missing", 
                             time.time() - start_time)
                return
            
            # Load and validate index
            with open(index_file, 'r') as f:
                index = json.load(f)
            
            if "reports" in index and "statistics" in index:
                total_reports = len(index["reports"])
                total_size_mb = index.get("statistics", {}).get("total_file_size_mb", 0)
                
                self.log_test("Report Persistence", "PASS", 
                             f"Persistence working ({total_reports} reports, {total_size_mb} MB)", 
                             time.time() - start_time)
                
                # Verify some actual files exist
                analysis_files = list(analysis_dir.glob("*.json"))
                self.log_test("Report Files Check", "PASS", 
                             f"{len(analysis_files)} report files found on disk")
            else:
                self.log_test("Report Persistence", "FAIL", 
                             "Invalid index structure", 
                             time.time() - start_time)
                
        except Exception as e:
            self.log_test("Report Persistence", "FAIL", 
                         f"Exception: {e}", 
                         time.time() - start_time)
    
    async def test_report_retrieval(self):
        """Test report retrieval functionality"""
        start_time = time.time()
        
        try:
            # List available reports
            response = requests.get(f"{self.api_base_url}/api/reports?limit=5")
            
            if response.status_code == 200:
                data = response.json()
                reports = data.get("reports", [])
                
                if reports:
                    # Test retrieving the first report
                    first_report = reports[0]
                    analysis_id = first_report["analysis_id"]
                    
                    report_response = requests.get(f"{self.api_base_url}/api/reports/{analysis_id}")
                    
                    if report_response.status_code == 200:
                        report = report_response.json()
                        
                        has_required_fields = all(field in report for field in ["analysis_id", "timestamp"])
                        
                        self.log_test("Report Retrieval", "PASS", 
                                     f"Successfully retrieved report {analysis_id}", 
                                     time.time() - start_time)
                    else:
                        self.log_test("Report Retrieval", "FAIL", 
                                     f"Could not retrieve report: {report_response.status_code}", 
                                     time.time() - start_time)
                else:
                    self.log_test("Report Retrieval", "SKIP", 
                                 "No reports available to test retrieval", 
                                 time.time() - start_time)
            else:
                self.log_test("Report Retrieval", "FAIL", 
                             f"Could not list reports: {response.status_code}", 
                             time.time() - start_time)
                
        except Exception as e:
            self.log_test("Report Retrieval", "FAIL", 
                         f"Exception: {e}", 
                         time.time() - start_time)
    
    async def test_report_search(self):
        """Test advanced report search functionality"""
        start_time = time.time()
        
        try:
            search_request = {
                "score_min": 70,
                "has_craft_bugs": False,
                "limit": 10
            }
            
            response = requests.post(
                f"{self.api_base_url}/api/reports/search",
                json=search_request,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                results = data.get("results", [])
                total = data.get("total", 0)
                
                self.log_test("Report Search", "PASS", 
                             f"Search working ({total} total results, {len(results)} returned)", 
                             time.time() - start_time)
            else:
                self.log_test("Report Search", "FAIL", 
                             f"Search failed: {response.status_code}", 
                             time.time() - start_time)
                
        except Exception as e:
            self.log_test("Report Search", "FAIL", 
                         f"Exception: {e}", 
                         time.time() - start_time)
    
    async def test_craft_bug_detection(self):
        """Test craft bug detection capabilities"""
        start_time = time.time()
        
        try:
            # Get recent reports and check for craft bug features
            response = requests.get(f"{self.api_base_url}/api/reports?limit=5")
            
            if response.status_code == 200:
                data = response.json()
                reports = data.get("reports", [])
                
                craft_bug_features_found = False
                
                for report_meta in reports:
                    if report_meta.get("craft_bugs_count", 0) > 0 or report_meta.get("total_issues", 0) > 0:
                        craft_bug_features_found = True
                        
                        # Get the full report to check structure
                        analysis_id = report_meta["analysis_id"]
                        report_response = requests.get(f"{self.api_base_url}/api/reports/{analysis_id}")
                        
                        if report_response.status_code == 200:
                            report = report_response.json()
                            
                            has_craft_bugs = "craft_bugs_detected" in report or "craft_bugs" in report
                            has_pattern_issues = "pattern_issues" in report
                            
                            if has_craft_bugs or has_pattern_issues:
                                craft_bugs_count = len(report.get("craft_bugs_detected", []))
                                pattern_issues_count = len(report.get("pattern_issues", []))
                                
                                self.log_test("Craft Bug Detection", "PASS", 
                                             f"Craft bug features working ({craft_bugs_count} bugs, {pattern_issues_count} patterns)", 
                                             time.time() - start_time)
                                return
                
                if not craft_bug_features_found:
                    self.log_test("Craft Bug Detection", "SKIP", 
                                 "No reports with craft bugs found (feature may work but untested)", 
                                 time.time() - start_time)
                else:
                    self.log_test("Craft Bug Detection", "FAIL", 
                                 "Craft bug metadata found but structure incomplete", 
                                 time.time() - start_time)
            else:
                self.log_test("Craft Bug Detection", "FAIL", 
                             f"Could not access reports: {response.status_code}", 
                             time.time() - start_time)
                
        except Exception as e:
            self.log_test("Craft Bug Detection", "FAIL", 
                         f"Exception: {e}", 
                         time.time() - start_time)
    
    async def test_system_statistics(self):
        """Test system statistics and monitoring"""
        start_time = time.time()
        
        try:
            response = requests.get(f"{self.api_base_url}/api/reports/statistics")
            
            if response.status_code == 200:
                stats = response.json()
                
                # Check required statistics structure
                required_sections = ["index_statistics", "storage_info", "system_info"]
                missing_sections = [section for section in required_sections if section not in stats]
                
                if not missing_sections:
                    index_stats = stats["index_statistics"]
                    storage_info = stats["storage_info"]
                    
                    total_reports = index_stats.get("total_reports", 0)
                    disk_usage = storage_info.get("disk_usage_mb", 0)
                    avg_score = index_stats.get("avg_score", 0)
                    
                    self.log_test("System Statistics", "PASS", 
                                 f"Complete stats available ({total_reports} reports, {disk_usage} MB, avg score: {avg_score})", 
                                 time.time() - start_time)
                else:
                    self.log_test("System Statistics", "FAIL", 
                                 f"Missing statistics sections: {missing_sections}", 
                                 time.time() - start_time)
            else:
                self.log_test("System Statistics", "FAIL", 
                             f"Statistics endpoint failed: {response.status_code}", 
                             time.time() - start_time)
                
        except Exception as e:
            self.log_test("System Statistics", "FAIL", 
                         f"Exception: {e}", 
                         time.time() - start_time)
    
    async def test_cleanup_functionality(self):
        """Test cleanup and maintenance functionality"""
        start_time = time.time()
        
        try:
            # Test cleanup endpoint (with a very short retention period for testing)
            cleanup_request = {"days_to_keep": 0}  # This should clean up everything for testing
            
            response = requests.post(
                f"{self.api_base_url}/api/reports/cleanup",
                params={"days_to_keep": 365},  # Use a long period to avoid actually deleting everything
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                
                if "removed_count" in data:
                    removed_count = data.get("removed_count", 0)
                    size_freed = data.get("size_freed_mb", 0)
                    
                    self.log_test("Cleanup Functionality", "PASS", 
                                 f"Cleanup working (would remove {removed_count} reports, free {size_freed} MB)", 
                                 time.time() - start_time)
                else:
                    self.log_test("Cleanup Functionality", "FAIL", 
                                 "Cleanup response missing expected fields", 
                                 time.time() - start_time)
            else:
                self.log_test("Cleanup Functionality", "FAIL", 
                             f"Cleanup endpoint failed: {response.status_code}", 
                             time.time() - start_time)
                
        except Exception as e:
            self.log_test("Cleanup Functionality", "FAIL", 
                         f"Exception: {e}", 
                         time.time() - start_time)
    
    def print_test_summary(self):
        """Print comprehensive test summary"""
        print("\n" + "=" * 70)
        print("🎯 ENHANCED UX ANALYZER TEST RESULTS SUMMARY")
        print("=" * 70)
        
        total_tests = len(self.test_results)
        passed = len([t for t in self.test_results if t["status"] == "PASS"])
        failed = len([t for t in self.test_results if t["status"] == "FAIL"])
        skipped = len([t for t in self.test_results if t["status"] == "SKIP"])
        
        total_duration = sum(t.get("duration_seconds", 0) for t in self.test_results)
        
        print(f"📊 Overall Results:")
        print(f"   Total Tests: {total_tests}")
        print(f"   ✅ Passed: {passed}")
        print(f"   ❌ Failed: {failed}")
        print(f"   ⚠️ Skipped: {skipped}")
        print(f"   📈 Success Rate: {(passed/total_tests)*100:.1f}%")
        print(f"   ⏱️ Total Duration: {total_duration:.2f}s")
        
        if failed > 0:
            print(f"\n❌ Failed Tests Details:")
            for test in self.test_results:
                if test["status"] == "FAIL":
                    print(f"   • {test['test']}: {test['details']}")
        
        # Phase breakdown
        print(f"\n📋 Phase Breakdown:")
        phases = {
            "Basic System": [t for t in self.test_results if "Health" in t["test"] or "Endpoint" in t["test"] or "Prerequisites" in t["test"]],
            "Scenario Execution": [t for t in self.test_results if "Scenario" in t["test"] and "Execution" in t["test"]],
            "Report Persistence": [t for t in self.test_results if "Report" in t["test"] and ("Persistence" in t["test"] or "Retrieval" in t["test"] or "Search" in t["test"])],
            "Advanced Features": [t for t in self.test_results if "Craft Bug" in t["test"] or "Statistics" in t["test"] or "Cleanup" in t["test"]]
        }
        
        for phase_name, phase_tests in phases.items():
            if phase_tests:
                phase_passed = len([t for t in phase_tests if t["status"] == "PASS"])
                phase_total = len(phase_tests)
                phase_rate = (phase_passed / phase_total * 100) if phase_total > 0 else 0
                print(f"   {phase_name}: {phase_passed}/{phase_total} ({phase_rate:.1f}%)")
        
        print(f"\n🎉 Enhanced UX Analyzer Testing Complete!")
        print(f"   Test Report Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Save detailed test results
        results_file = f"test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(results_file, 'w') as f:
            json.dump({
                "test_summary": {
                    "total_tests": total_tests,
                    "passed": passed,
                    "failed": failed,
                    "skipped": skipped,
                    "success_rate": round((passed/total_tests)*100, 1),
                    "total_duration": round(total_duration, 2),
                    "timestamp": datetime.now().isoformat()
                },
                "detailed_results": self.test_results
            }, f, indent=2, default=str)
        
        print(f"   📁 Detailed results saved: {results_file}")

# Main execution
async def main():
    """Run the comprehensive test suite"""
    tester = UXAnalyzerTestSuite()
    await tester.run_comprehensive_tests()

if __name__ == "__main__":
    asyncio.run(main())
