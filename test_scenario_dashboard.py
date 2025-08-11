#!/usr/bin/env python3
"""
Comprehensive Scenario Testing Dashboard
Test all available scenarios to verify reports are successfully rendered
"""

import os
import sys
import json
import time
import requests
from pathlib import Path
from datetime import datetime
import subprocess
from typing import Dict, List, Any, Optional

# Add current directory to path for imports
sys.path.append(os.getcwd())

# Color codes for output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    END = '\033[0m'

def print_header(text: str):
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text:^60}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.END}")

def print_success(text: str):
    print(f"{Colors.GREEN}✅ {text}{Colors.END}")

def print_error(text: str):
    print(f"{Colors.RED}❌ {text}{Colors.END}")

def print_warning(text: str):
    print(f"{Colors.YELLOW}⚠️  {text}{Colors.END}")

def print_info(text: str):
    print(f"{Colors.CYAN}ℹ️  {text}{Colors.END}")

def check_server_running(port: int = 8000) -> bool:
    """Check if the server is running on the specified port"""
    try:
        response = requests.get(f"http://localhost:{port}/health", timeout=5)
        return response.status_code == 200
    except:
        return False

def start_server_if_needed(port: int = 8000) -> Optional[subprocess.Popen]:
    """Start the server if it's not already running"""
    if check_server_running(port):
        print_success(f"Server already running on port {port}")
        return None
    
    print_info(f"Starting server on port {port}...")
    try:
        # Start server in background
        process = subprocess.Popen(
            ["python", "enhanced_fastapi_server.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Wait a bit for server to start
        time.sleep(3)
        
        if check_server_running(port):
            print_success("Server started successfully")
            return process
        else:
            print_error("Server failed to start")
            return None
    except Exception as e:
        print_error(f"Failed to start server: {e}")
        return None

def discover_scenarios() -> Dict[str, List[str]]:
    """Discover all available scenario files"""
    scenarios_dir = Path("scenarios")
    if not scenarios_dir.exists():
        print_error("scenarios/ directory not found")
        return {}
    
    scenario_files = {}
    
    for yaml_file in scenarios_dir.glob("*.yaml"):
        try:
            # Try to parse and determine format
            from utils.scenario_resolver import resolve_scenario
            
            # Test if we can resolve it
            try:
                resolved = resolve_scenario(str(yaml_file))
                scenario_files[str(yaml_file)] = ["resolvable"]
                print_success(f"Found valid scenario: {yaml_file.name}")
            except Exception as e:
                scenario_files[str(yaml_file)] = [f"error: {str(e)[:50]}..."]
                print_warning(f"Scenario {yaml_file.name} has issues: {str(e)[:50]}...")
                
        except Exception as e:
            print_error(f"Failed to check {yaml_file.name}: {e}")
    
    return scenario_files

def test_scenario_analysis(scenario_path: str, test_url: str = "http://localhost:3001/mocks/word/basic-doc.html") -> Dict[str, Any]:
    """Test a specific scenario analysis"""
    print_info(f"Testing scenario: {Path(scenario_path).name}")
    
    # Prepare request payload
    payload = {
        "url": test_url,
        "scenario_path": scenario_path,
        "modules": {
            "performance": True,
            "accessibility": True,
            "keyboard": True,
            "ux_heuristics": True,
            "best_practices": True,
            "health_alerts": True,
            "functional": False
        }
    }
    
    try:
        # Make analysis request
        print_info("  📡 Sending analysis request...")
        response = requests.post(
            "http://localhost:8000/api/analyze/url-scenario",
            json=payload,
            timeout=30
        )
        
        if response.status_code != 200:
            return {
                "status": "failed",
                "error": f"Request failed with status {response.status_code}",
                "response": response.text[:200]
            }
        
        result = response.json()
        analysis_id = result.get("analysis_id")
        
        if not analysis_id:
            return {
                "status": "failed", 
                "error": "No analysis_id returned",
                "response": result
            }
        
        print_info(f"  🔍 Analysis ID: {analysis_id}")
        
        # Wait a moment for processing
        time.sleep(2)
        
        # Fetch the report
        print_info("  📊 Fetching report...")
        report_response = requests.get(
            f"http://localhost:8000/api/reports/{analysis_id}",
            timeout=10
        )
        
        if report_response.status_code != 200:
            return {
                "status": "failed",
                "error": f"Report fetch failed with status {report_response.status_code}",
                "analysis_id": analysis_id,
                "report_response": report_response.text[:200]
            }
        
        report_data = report_response.json()
        
        # Analyze the report
        report_status = report_data.get("status", "unknown")
        overall_score = report_data.get("overall_score", "N/A")
        total_issues = report_data.get("total_issues", "N/A")
        error_message = report_data.get("error", "")
        ui_error = report_data.get("ui_error", "")
        
        return {
            "status": "success",
            "analysis_id": analysis_id,
            "report_status": report_status,
            "overall_score": overall_score,
            "total_issues": total_issues,
            "error_message": error_message,
            "ui_error": ui_error,
            "has_module_results": bool(report_data.get("module_results")),
            "has_scenario_results": bool(report_data.get("scenario_results")),
            "report_size": len(json.dumps(report_data))
        }
        
    except requests.exceptions.RequestException as e:
        return {
            "status": "failed",
            "error": f"Network error: {str(e)}"
        }
    except Exception as e:
        return {
            "status": "failed",
            "error": f"Unexpected error: {str(e)}"
        }

def test_all_scenarios(scenarios: Dict[str, List[str]]) -> Dict[str, Dict[str, Any]]:
    """Test all discovered scenarios"""
    print_header("TESTING ALL SCENARIOS")
    
    test_results = {}
    
    # Test URLs for different app types
    test_urls = {
        "word": "http://localhost:3001/mocks/word/basic-doc.html",
        "excel": "http://localhost:3001/mocks/excel/open-format.html", 
        "powerpoint": "http://localhost:3001/mocks/powerpoint/basic-deck.html",
        "default": "http://localhost:3001/mocks/word/basic-doc.html"
    }
    
    for scenario_path, status_list in scenarios.items():
        scenario_name = Path(scenario_path).name
        
        # Skip scenarios that had resolution errors
        if any("error:" in status for status in status_list):
            print_warning(f"Skipping {scenario_name} (resolution error)")
            test_results[scenario_path] = {
                "status": "skipped",
                "reason": "resolution_error",
                "details": status_list[0] if status_list else "unknown error"
            }
            continue
        
        # Determine appropriate test URL
        test_url = test_urls["default"]
        if "word" in scenario_name.lower():
            test_url = test_urls["word"]
        elif "excel" in scenario_name.lower():
            test_url = test_urls["excel"]
        elif "powerpoint" in scenario_name.lower():
            test_url = test_urls["powerpoint"]
        
        print(f"\n{Colors.PURPLE}🧪 Testing: {scenario_name}{Colors.END}")
        print_info(f"   URL: {test_url}")
        
        result = test_scenario_analysis(scenario_path, test_url)
        test_results[scenario_path] = result
        
        # Print immediate result
        if result["status"] == "success":
            report_status = result.get("report_status", "unknown")
            if report_status == "failed":
                print_error(f"   Analysis completed but report shows failure")
                if result.get("ui_error"):
                    print_error(f"   UI Error: {result['ui_error']}")
            else:
                print_success(f"   Analysis completed successfully")
                print_info(f"   Report Status: {report_status}")
                print_info(f"   Overall Score: {result.get('overall_score', 'N/A')}")
                print_info(f"   Total Issues: {result.get('total_issues', 'N/A')}")
        else:
            print_error(f"   Test failed: {result.get('error', 'Unknown error')}")
    
    return test_results

def generate_summary_report(test_results: Dict[str, Dict[str, Any]]) -> None:
    """Generate a comprehensive summary report"""
    print_header("COMPREHENSIVE TEST SUMMARY")
    
    total_scenarios = len(test_results)
    successful_tests = 0
    failed_tests = 0
    skipped_tests = 0
    successful_reports = 0
    failed_reports = 0
    
    print(f"\n{Colors.BOLD}📊 OVERALL STATISTICS{Colors.END}")
    print(f"   Total Scenarios: {total_scenarios}")
    
    detailed_results = []
    
    for scenario_path, result in test_results.items():
        scenario_name = Path(scenario_path).name
        
        if result["status"] == "skipped":
            skipped_tests += 1
            detailed_results.append({
                "name": scenario_name,
                "test_status": "SKIPPED",
                "report_status": "N/A",
                "reason": result.get("reason", "unknown")
            })
        elif result["status"] == "success":
            successful_tests += 1
            report_status = result.get("report_status", "unknown")
            if report_status == "failed":
                failed_reports += 1
                detailed_results.append({
                    "name": scenario_name,
                    "test_status": "SUCCESS",
                    "report_status": "FAILED",
                    "score": result.get("overall_score", "N/A"),
                    "issues": result.get("total_issues", "N/A"),
                    "error": result.get("ui_error", result.get("error_message", ""))
                })
            else:
                successful_reports += 1
                detailed_results.append({
                    "name": scenario_name,
                    "test_status": "SUCCESS",
                    "report_status": "SUCCESS",
                    "score": result.get("overall_score", "N/A"),
                    "issues": result.get("total_issues", "N/A")
                })
        else:
            failed_tests += 1
            detailed_results.append({
                "name": scenario_name,
                "test_status": "FAILED",
                "report_status": "N/A",
                "error": result.get("error", "unknown")
            })
    
    print(f"   Tests Completed: {successful_tests}")
    print(f"   Tests Failed: {failed_tests}")
    print(f"   Tests Skipped: {skipped_tests}")
    print(f"   Reports Successful: {successful_reports}")
    print(f"   Reports Failed: {failed_reports}")
    
    # Success rates
    if total_scenarios > 0:
        test_success_rate = (successful_tests / total_scenarios) * 100
        print(f"   Test Success Rate: {test_success_rate:.1f}%")
        
        if successful_tests > 0:
            report_success_rate = (successful_reports / successful_tests) * 100
            print(f"   Report Success Rate: {report_success_rate:.1f}%")
    
    # Detailed breakdown
    print(f"\n{Colors.BOLD}📋 DETAILED RESULTS{Colors.END}")
    
    # Successful scenarios
    successful_scenarios = [r for r in detailed_results if r["test_status"] == "SUCCESS" and r["report_status"] == "SUCCESS"]
    if successful_scenarios:
        print(f"\n{Colors.GREEN}✅ FULLY SUCCESSFUL SCENARIOS ({len(successful_scenarios)}){Colors.END}")
        for result in successful_scenarios:
            print(f"   • {result['name']:<30} Score: {result['score']:<5} Issues: {result['issues']}")
    
    # Failed reports (test succeeded but report failed)
    failed_report_scenarios = [r for r in detailed_results if r["test_status"] == "SUCCESS" and r["report_status"] == "FAILED"]
    if failed_report_scenarios:
        print(f"\n{Colors.YELLOW}⚠️  SCENARIOS WITH FAILED REPORTS ({len(failed_report_scenarios)}){Colors.END}")
        for result in failed_report_scenarios:
            print(f"   • {result['name']:<30} Error: {result.get('error', 'No error message')[:50]}")
    
    # Failed tests
    failed_test_scenarios = [r for r in detailed_results if r["test_status"] == "FAILED"]
    if failed_test_scenarios:
        print(f"\n{Colors.RED}❌ FAILED TEST SCENARIOS ({len(failed_test_scenarios)}){Colors.END}")
        for result in failed_test_scenarios:
            print(f"   • {result['name']:<30} Error: {result.get('error', 'No error message')[:50]}")
    
    # Skipped tests
    skipped_scenarios = [r for r in detailed_results if r["test_status"] == "SKIPPED"]
    if skipped_scenarios:
        print(f"\n{Colors.PURPLE}⏭️  SKIPPED SCENARIOS ({len(skipped_scenarios)}){Colors.END}")
        for result in skipped_scenarios:
            print(f"   • {result['name']:<30} Reason: {result.get('reason', 'unknown')}")
    
    # Overall assessment
    print(f"\n{Colors.BOLD}🎯 OVERALL ASSESSMENT{Colors.END}")
    if successful_reports == successful_tests and failed_tests == 0:
        print_success("🎉 ALL SCENARIOS WORKING PERFECTLY!")
        print_success("   The robust fixes have successfully resolved the pipeline issues.")
    elif successful_reports > 0:
        print_warning("⚖️  MIXED RESULTS")
        print_info(f"   {successful_reports} scenarios are working correctly")
        if failed_reports > 0:
            print_warning(f"   {failed_reports} scenarios complete but with failed reports")
        if failed_tests > 0:
            print_warning(f"   {failed_tests} scenarios fail to complete")
        print_info("   Check the detailed results above for specific issues.")
    else:
        print_error("💥 MAJOR ISSUES DETECTED")
        print_error("   No scenarios are producing successful reports.")
        print_error("   Check server logs and scenario file formats.")

def main():
    """Main test execution"""
    print_header("SCENARIO DASHBOARD TESTING SUITE")
    print_info(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Check if we're in the right directory
    if not Path("enhanced_fastapi_server.py").exists():
        print_error("enhanced_fastapi_server.py not found. Make sure you're in the analyzer directory.")
        return 1
    
    # Step 1: Start server if needed
    server_process = start_server_if_needed()
    
    try:
        # Step 2: Discover scenarios
        print_header("DISCOVERING SCENARIOS")
        scenarios = discover_scenarios()
        
        if not scenarios:
            print_error("No scenarios found to test")
            return 1
        
        print_success(f"Found {len(scenarios)} scenario files")
        
        # Step 3: Test all scenarios
        test_results = test_all_scenarios(scenarios)
        
        # Step 4: Generate summary
        generate_summary_report(test_results)
        
        # Step 5: Save detailed results
        results_file = f"scenario_test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(results_file, 'w') as f:
            json.dump(test_results, f, indent=2, default=str)
        print_info(f"Detailed results saved to: {results_file}")
        
        return 0
        
    finally:
        # Clean up server if we started it
        if server_process:
            print_info("Stopping server...")
            server_process.terminate()
            server_process.wait()

if __name__ == "__main__":
    exit(main())
