#!/usr/bin/env python3
"""
Direct test of browser automation to isolate issues
"""

from scenario_executor import ScenarioExecutor
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_direct_browser_automation():
    """Test browser automation directly"""
    
    # Create scenario executor
    executor = ScenarioExecutor()
    
    # Test data
    url = "http://localhost:4173"
    scenario_id = "1.1"
    modules = {
        "performance": True,
        "accessibility": True
    }
    
    print(f"🧪 Testing direct browser automation for scenario {scenario_id}")
    print(f"🔗 URL: {url}")
    
    try:
        # Execute scenario by ID (should trigger real browser automation)
        result = executor.execute_scenario_by_id(url, scenario_id, modules)
        
        print(f"✅ Execution completed")
        print(f"📊 Overall score: {result.get('overall_score', 'N/A')}")
        print(f"🔍 Mode: {result.get('mode', 'N/A')}")
        print(f"📝 Total issues: {result.get('total_issues', 0)}")
        
        # Check if it used real browser automation or fallback
        if 'fallback mode' in str(result):
            print("⚠️ USING FALLBACK MODE - Real browser automation failed")
        else:
            print("✅ REAL BROWSER AUTOMATION SUCCESSFUL")
            
        # Show performance findings
        perf_findings = result.get('modules', {}).get('performance', {}).get('findings', [])
        print(f"🎯 Performance findings: {len(perf_findings)}")
        for i, finding in enumerate(perf_findings[:3]):
            print(f"  {i+1}. {finding.get('message', 'No message')}")
            
        # Show UX issues 
        ux_issues = result.get('ux_issues', [])
        print(f"🐛 UX Issues found: {len(ux_issues)}")
        for i, issue in enumerate(ux_issues):
            print(f"  {i+1}. [{issue.get('severity', 'unknown')}] {issue.get('message', 'No message')}")
            
        # Show accessibility findings
        acc_findings = result.get('modules', {}).get('accessibility', {}).get('findings', [])
        print(f"♿ Accessibility findings: {len(acc_findings)}")
        for i, finding in enumerate(acc_findings[:3]):
            print(f"  {i+1}. {finding.get('message', 'No message')}")
            
        return result
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    test_direct_browser_automation()
