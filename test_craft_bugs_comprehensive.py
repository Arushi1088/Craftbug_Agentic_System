#!/usr/bin/env python3
"""Interactive Craft Bug Testing Script"""

import asyncio
import sys
import requests
import json
from datetime import datetime

def print_header(title):
    print(f"\n{'='*60}")
    print(f"🎯 {title}")
    print('='*60)

def print_section(title):
    print(f"\n📋 {title}")
    print('-'*40)

async def run_craft_bug_test():
    """Run comprehensive craft bug test and show detailed results"""
    
    print_header("CRAFT BUG DETECTION TEST")
    
    # Test servers first
    print_section("Server Status Check")
    try:
        backend_response = requests.get('http://localhost:8000/health', timeout=5)
        print(f"✅ Backend API: {backend_response.status_code} - {backend_response.json()['status']}")
    except Exception as e:
        print(f"❌ Backend API: {e}")
        return
    
    try:
        mock_response = requests.get('http://localhost:8080/mocks/word/basic-doc.html', timeout=5)
        print(f"✅ Word Mock: {mock_response.status_code} - {len(mock_response.text)} bytes")
        
        # Check for craft bugs in mock
        if 'craftBugMetrics' in mock_response.text:
            print("🐛 Craft bug JavaScript detected in mock!")
        else:
            print("⚠️ No craft bug JavaScript found in mock")
            
        if 'craft-bug-hover' in mock_response.text:
            print("🎯 Craft bug CSS classes detected in mock!")
        else:
            print("⚠️ No craft bug CSS classes found in mock")
            
    except Exception as e:
        print(f"❌ Word Mock: {e}")
        return
    
    # Run analysis
    print_section("Running Analysis")
    analysis_payload = {
        "url": "http://localhost:8080/mocks/word/basic-doc.html",
        "scenario_id": "1.1",  # Basic scenario
        "modules": {
            "performance": True,
            "accessibility": True,
            "ux_heuristics": True
        }
    }
    
    try:
        print("🚀 Starting analysis...")
        response = requests.post(
            'http://localhost:8000/api/analyze',
            headers={'Content-Type': 'application/json'},
            json=analysis_payload,
            timeout=60
        )
        
        if response.status_code == 200:
            result = response.json()
            analysis_id = result.get('analysis_id')
            print(f"✅ Analysis completed: {analysis_id}")
            
            # Get detailed report
            print_section("Detailed Analysis Results")
            report_response = requests.get(f'http://localhost:8000/api/reports/{analysis_id}')
            
            if report_response.status_code == 200:
                report = report_response.json()
                
                print(f"📊 Overall Score: {report.get('overall_score', 'N/A')}")
                print(f"🔧 Browser Automation: {report.get('browser_automation', False)}")
                print(f"📈 Total Issues: {report.get('total_issues', 0)}")
                print(f"⏱️ Execution Time: {report.get('execution_time', 0):.2f}s")
                
                # Module breakdown
                modules = report.get('modules', {})
                for module_name, module_data in modules.items():
                    print(f"\n🔍 {module_name.upper()} Module:")
                    print(f"   Score: {module_data.get('score', 'N/A')}")
                    findings = module_data.get('findings', [])
                    print(f"   Findings: {len(findings)}")
                    
                    for i, finding in enumerate(findings[:3]):  # Show first 3
                        severity = finding.get('severity', 'unknown')
                        message = finding.get('message', 'No message')
                        print(f"   {i+1}. [{severity.upper()}] {message}")
                    
                    if len(findings) > 3:
                        print(f"   ... and {len(findings) - 3} more")
                
                # Check for craft bug specific data
                print_section("Craft Bug Detection Analysis")
                
                # Look for craft bugs in different places
                craft_bug_found = False
                
                # Check for JavaScript metrics that would indicate craft bugs
                performance_metrics = report.get('performance_metrics', {})
                if any(key in str(performance_metrics) for key in ['animation', 'layout', 'input']):
                    print("🐛 Performance metrics suggest possible craft bugs detected")
                    craft_bug_found = True
                
                # Check UX heuristics for craft bug related issues
                ux_heuristics = modules.get('ux_heuristics', {})
                ux_findings = ux_heuristics.get('findings', [])
                for finding in ux_findings:
                    message = finding.get('message', '').lower()
                    if any(word in message for word in ['animation', 'lag', 'delay', 'hover', 'interaction']):
                        print(f"🎯 UX finding suggests craft bug: {finding.get('message')}")
                        craft_bug_found = True
                
                # Check scenario results for craft bug interactions
                scenario_results = report.get('scenario_results', [])
                craft_bug_interactions = 0
                for step in scenario_results:
                    target = step.get('target', '')
                    if 'craft-bug' in target:
                        craft_bug_interactions += 1
                        status = step.get('status', 'unknown')
                        print(f"🎯 Craft bug interaction: {target} -> {status}")
                        craft_bug_found = True
                
                if not craft_bug_found:
                    print("⚠️ No craft bugs detected in this analysis")
                    print("💡 Try scenario '1.5' for interactive craft bug testing")
                
                # Show raw JSON for debugging
                print_section("Debug Information")
                print("📄 Full report available at:")
                print(f"   http://localhost:8000/api/reports/{analysis_id}")
                
                # Save detailed report
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"craft_bug_test_results_{timestamp}.json"
                with open(filename, 'w') as f:
                    json.dump(report, f, indent=2)
                print(f"💾 Detailed report saved to: {filename}")
                
            else:
                print(f"❌ Failed to get report: {report_response.status_code}")
        else:
            print(f"❌ Analysis failed: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"❌ Analysis error: {e}")

if __name__ == "__main__":
    print("🎯 Craft Bug Detection Testing Tool")
    print("This will run a comprehensive test and show you detailed results")
    print("\nPress Ctrl+C to exit at any time...")
    
    try:
        asyncio.run(run_craft_bug_test())
    except KeyboardInterrupt:
        print("\n\n👋 Test cancelled by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)
