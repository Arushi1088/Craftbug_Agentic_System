#!/usr/bin/env python3
"""
Comprehensive Test Script for UX Analyzer System
Tests all components: Dashboard, Backend, Mocks, and Analysis
"""

import asyncio
import json
import requests
import time
from datetime import datetime
from playwright.async_api import async_playwright

def test_backend_health():
    """Test backend health and basic functionality"""
    print("🔌 Testing Backend Health...")
    print("=" * 40)
    
    try:
        # Test health endpoint
        response = requests.get("http://localhost:8000/health")
        if response.status_code == 200:
            health_data = response.json()
            print(f"✅ Backend Health: {health_data.get('status')}")
            print(f"   Version: {health_data.get('version')}")
            print(f"   Features: {health_data.get('features', {})}")
        else:
            print(f"❌ Backend Health Failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Backend Health Error: {e}")
        return False
    
    return True

def test_scenarios_endpoint():
    """Test scenarios endpoint"""
    print("\n📋 Testing Scenarios Endpoint...")
    print("=" * 40)
    
    try:
        response = requests.get("http://localhost:8000/api/scenarios")
        if response.status_code == 200:
            data = response.json()
            scenarios = data.get('scenarios', [])
            print(f"✅ Scenarios Loaded: {len(scenarios)} scenarios")
            
            # Group by app type
            word_scenarios = [s for s in scenarios if s.get('app_type') == 'word']
            excel_scenarios = [s for s in scenarios if s.get('app_type') == 'excel']
            powerpoint_scenarios = [s for s in scenarios if s.get('app_type') == 'powerpoint']
            
            print(f"   📄 Word: {len(word_scenarios)} scenarios")
            print(f"   📊 Excel: {len(excel_scenarios)} scenarios")
            print(f"   📽️ PowerPoint: {len(powerpoint_scenarios)} scenarios")
            
            # Show some example scenarios
            if word_scenarios:
                print(f"   Example Word scenario: {word_scenarios[0].get('name')}")
            if excel_scenarios:
                print(f"   Example Excel scenario: {excel_scenarios[0].get('name')}")
            if powerpoint_scenarios:
                print(f"   Example PowerPoint scenario: {powerpoint_scenarios[0].get('name')}")
                
            return scenarios
        else:
            print(f"❌ Scenarios Failed: {response.status_code}")
            return []
    except Exception as e:
        print(f"❌ Scenarios Error: {e}")
        return []

def test_mock_applications():
    """Test mock applications accessibility"""
    print("\n📱 Testing Mock Applications...")
    print("=" * 40)
    
    mock_urls = {
        "Word": "http://localhost:5173/mocks/word/basic-doc.html",
        "Excel": "http://localhost:5173/mocks/excel/open-format.html",
        "PowerPoint": "http://localhost:5173/mocks/powerpoint/basic-deck.html"
    }
    
    results = {}
    for app_name, url in mock_urls.items():
        try:
            response = requests.get(url)
            if response.status_code == 200:
                print(f"✅ {app_name}: Accessible")
                results[app_name] = True
            else:
                print(f"❌ {app_name}: Failed ({response.status_code})")
                results[app_name] = False
        except Exception as e:
            print(f"❌ {app_name}: Error - {e}")
            results[app_name] = False
    
    return results

async def test_playwright_analysis():
    """Test Playwright analysis with mock applications"""
    print("\n🔍 Testing Playwright Analysis...")
    print("=" * 40)
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        test_url = "http://localhost:5173/mocks/word/basic-doc.html"
        
        try:
            print(f"📍 Testing URL: {test_url}")
            
            # Navigate to the page
            await page.goto(test_url, wait_until='domcontentloaded', timeout=30000)
            
            # Take screenshot
            screenshot_path = "test_analysis_screenshot.png"
            await page.screenshot(path=screenshot_path, full_page=True)
            print(f"📸 Screenshot saved: {screenshot_path}")
            
            # Check for craft bug metrics
            craft_bug_metrics = await page.evaluate("""
                () => {
                    return {
                        craftBugMetrics: window.craftBugMetrics || null,
                        excelCraftBugMetrics: window.excelCraftBugMetrics || null,
                        pptCraftBugMetrics: window.pptCraftBugMetrics || null,
                        readyState: document.readyState
                    }
                }
            """)
            
            print(f"🔍 Craft Bug Metrics: {json.dumps(craft_bug_metrics, indent=2)}")
            
            # Test basic interactions
            buttons = await page.query_selector_all('button')
            inputs = await page.query_selector_all('input')
            
            print(f"🖱️ Interactive Elements: {len(buttons)} buttons, {len(inputs)} inputs")
            
            await browser.close()
            return True
            
        except Exception as e:
            print(f"❌ Playwright Analysis Error: {e}")
            await browser.close()
            return False

def test_analysis_api():
    """Test the analysis API endpoint"""
    print("\n🚀 Testing Analysis API...")
    print("=" * 40)
    
    # Test data
    test_data = {
        "url": "http://localhost:5173/mocks/word/basic-doc.html",
        "scenario_id": "1.1",
        "use_real_browser": False
    }
    
    try:
        print(f"📤 Sending analysis request...")
        response = requests.post(
            "http://localhost:8000/api/analyze",
            headers={"Content-Type": "application/json"},
            json=test_data,
            timeout=60
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Analysis Completed!")
            print(f"   Analysis ID: {result.get('analysis_id')}")
            print(f"   Status: {result.get('status')}")
            print(f"   Message: {result.get('message')}")
            
            # Check for issues
            ux_issues = result.get('ux_issues', [])
            craft_bugs = result.get('craft_bugs', [])
            total_issues = result.get('total_issues', 0)
            
            print(f"   UX Issues: {len(ux_issues)}")
            print(f"   Craft Bugs: {len(craft_bugs)}")
            print(f"   Total Issues: {total_issues}")
            
            # Show some issues if any
            if ux_issues:
                print(f"   Example UX Issue: {ux_issues[0].get('message')}")
            if craft_bugs:
                print(f"   Example Craft Bug: {craft_bugs[0]}")
                
            return result
        else:
            print(f"❌ Analysis Failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Analysis API Error: {e}")
        return None

def test_dashboard_access():
    """Test dashboard accessibility"""
    print("\n🌐 Testing Dashboard Access...")
    print("=" * 40)
    
    try:
        response = requests.get("http://localhost:5173")
        if response.status_code == 200:
            print("✅ Dashboard: Accessible")
            
            # Check if it's a React app
            if "react" in response.text.lower() or "vite" in response.text.lower():
                print("✅ Dashboard: React/Vite application detected")
            else:
                print("⚠️ Dashboard: May not be React app")
                
            return True
        else:
            print(f"❌ Dashboard: Failed ({response.status_code})")
            return False
    except Exception as e:
        print(f"❌ Dashboard Error: {e}")
        return False

async def main():
    """Main test function"""
    print("🎯 Comprehensive UX Analyzer System Test")
    print("=" * 50)
    print(f"📅 Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Test results
    results = {
        "backend_health": False,
        "scenarios": [],
        "mock_apps": {},
        "playwright": False,
        "analysis_api": None,
        "dashboard": False
    }
    
    # Step 1: Test Backend Health
    results["backend_health"] = test_backend_health()
    
    # Step 2: Test Scenarios
    results["scenarios"] = test_scenarios_endpoint()
    
    # Step 3: Test Mock Applications
    results["mock_apps"] = test_mock_applications()
    
    # Step 4: Test Playwright Analysis
    results["playwright"] = await test_playwright_analysis()
    
    # Step 5: Test Analysis API
    results["analysis_api"] = test_analysis_api()
    
    # Step 6: Test Dashboard
    results["dashboard"] = test_dashboard_access()
    
    # Summary
    print("\n📊 Test Summary")
    print("=" * 50)
    
    print(f"🔌 Backend Health: {'✅ PASS' if results['backend_health'] else '❌ FAIL'}")
    print(f"📋 Scenarios: {'✅ PASS' if results['scenarios'] else '❌ FAIL'} ({len(results['scenarios'])} loaded)")
    print(f"📱 Mock Apps: {'✅ PASS' if all(results['mock_apps'].values()) else '❌ FAIL'}")
    print(f"🔍 Playwright: {'✅ PASS' if results['playwright'] else '❌ FAIL'}")
    print(f"🚀 Analysis API: {'✅ PASS' if results['analysis_api'] else '❌ FAIL'}")
    print(f"🌐 Dashboard: {'✅ PASS' if results['dashboard'] else '❌ FAIL'}")
    
    # Overall status
    all_passed = all([
        results['backend_health'],
        results['scenarios'],
        all(results['mock_apps'].values()),
        results['playwright'],
        results['analysis_api'],
        results['dashboard']
    ])
    
    print(f"\n🎯 Overall Status: {'✅ ALL TESTS PASSED' if all_passed else '❌ SOME TESTS FAILED'}")
    
    # Save results
    with open(f"test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json", 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"\n📄 Test results saved to: test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
    
    # Next steps
    print(f"\n🎯 Next Steps:")
    print(f"   1. Open Dashboard: http://localhost:5173")
    print(f"   2. Select an application (Word/Excel/PowerPoint)")
    print(f"   3. Choose a scenario")
    print(f"   4. Click 'Start Analysis'")
    print(f"   5. View the generated report")
    
    return all_passed

if __name__ == "__main__":
    asyncio.run(main())
