#!/usr/bin/env python3
"""
Comprehensive test script to demonstrate craft bug detection capabilities
using Playwright and Chromium with the UX Analyzer system
"""

import asyncio
import json
import requests
from playwright.async_api import async_playwright
import time
from datetime import datetime

async def test_craft_bug_detection():
    """Test craft bug detection capabilities"""
    
    print("🔍 Testing Craft Bug Detection")
    print("=" * 50)
    
    # Test URLs with craft bugs
    test_urls = [
        {
            "url": "http://localhost:5173/public/mocks/word/basic-doc.html",
            "name": "Word Mock with Craft Bugs",
            "expected_bugs": ["input_delays", "animation_conflicts", "feedback_failures"]
        },
        {
            "url": "http://localhost:5173/public/mocks/excel/open-format.html", 
            "name": "Excel Mock with Craft Bugs",
            "expected_bugs": ["loading_delays", "layout_shifts"]
        },
        {
            "url": "http://localhost:5173/public/mocks/powerpoint/basic-deck.html",
            "name": "PowerPoint Mock with Craft Bugs", 
            "expected_bugs": ["motion_issues", "performance_problems"]
        }
    ]
    
    async with async_playwright() as p:
        # Launch Chromium browser
        print("🌐 Launching Chromium browser...")
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        
        # Enable performance monitoring
        await page.route("**/*", lambda route: route.continue_())
        
        for i, test_case in enumerate(test_urls, 1):
            print(f"\n📱 Testing {i}: {test_case['name']}")
            print(f"🔗 URL: {test_case['url']}")
            print("-" * 50)
            
            try:
                # Start performance monitoring
                await page.goto("about:blank")
                await page.evaluate("window.performance.mark('test-start')")
                
                # Navigate to the test page
                print(f"📍 Navigating to test page...")
                start_time = time.time()
                await page.goto(test_case['url'], wait_until='domcontentloaded', timeout=30000)
                load_time = time.time() - start_time
                print(f"⏱️ Page load time: {load_time:.2f}s")
                
                # Wait for craft bug metrics to be available
                await page.wait_for_function("""
                    () => window.craftBugMetrics || window.excelCraftBugMetrics || window.pptCraftBugMetrics || document.readyState === 'complete'
                """, timeout=10000)
                
                # Take screenshot
                screenshot_path = f"craft_bug_test_{i}.png"
                await page.screenshot(path=screenshot_path, full_page=True)
                print(f"📸 Screenshot saved: {screenshot_path}")
                
                # Extract craft bug metrics
                craft_bug_data = await page.evaluate("""
                    () => {
                        const metrics = {
                            craftBugMetrics: window.craftBugMetrics || null,
                            excelCraftBugMetrics: window.excelCraftBugMetrics || null,
                            pptCraftBugMetrics: window.pptCraftBugMetrics || null,
                            performance: window.performance || null,
                            readyState: document.readyState
                        };
                        
                        // Collect performance metrics
                        if (window.performance) {
                            const navigation = performance.getEntriesByType('navigation')[0];
                            metrics.loadMetrics = {
                                domContentLoaded: navigation.domContentLoadedEventEnd - navigation.domContentLoadedEventStart,
                                loadComplete: navigation.loadEventEnd - navigation.loadEventStart,
                                totalLoadTime: navigation.loadEventEnd - navigation.fetchStart
                            };
                        }
                        
                        return metrics;
                    }
                """)
                
                print(f"🔍 Craft Bug Metrics: {json.dumps(craft_bug_data, indent=2)}")
                
                # Test interactive elements for craft bugs
                print("🖱️ Testing interactive elements...")
                
                # Find all interactive elements
                buttons = await page.query_selector_all('button')
                inputs = await page.query_selector_all('input')
                links = await page.query_selector_all('a')
                
                print(f"🔘 Found {len(buttons)} buttons")
                print(f"📝 Found {len(inputs)} inputs")
                print(f"🔗 Found {len(links)} links")
                
                # Test button interactions for response delays
                if buttons:
                    print("🔘 Testing button response times...")
                    for j, button in enumerate(buttons[:3]):  # Test first 3 buttons
                        try:
                            # Get button text
                            button_text = await button.text_content() or f"Button {j+1}"
                            
                            # Test click response time
                            start_time = time.time()
                            await button.click()
                            response_time = time.time() - start_time
                            
                            print(f"   {button_text}: {response_time:.3f}s response time")
                            
                            # Check if response time indicates a craft bug
                            if response_time > 0.1:  # 100ms threshold
                                print(f"   ⚠️ Potential craft bug: Slow button response ({response_time:.3f}s)")
                            
                            # Wait a bit between clicks
                            await asyncio.sleep(0.5)
                            
                        except Exception as e:
                            print(f"   ❌ Error testing button {j+1}: {e}")
                
                # Test input interactions for delays
                if inputs:
                    print("📝 Testing input response times...")
                    for j, input_field in enumerate(inputs[:2]):  # Test first 2 inputs
                        try:
                            # Focus the input
                            start_time = time.time()
                            await input_field.focus()
                            focus_time = time.time() - start_time
                            
                            print(f"   Input {j+1} focus time: {focus_time:.3f}s")
                            
                            # Type some text
                            start_time = time.time()
                            await input_field.type("test")
                            type_time = time.time() - start_time
                            
                            print(f"   Input {j+1} type time: {type_time:.3f}s")
                            
                            # Check for craft bugs
                            if focus_time > 0.05 or type_time > 0.1:
                                print(f"   ⚠️ Potential craft bug: Slow input response")
                            
                        except Exception as e:
                            print(f"   ❌ Error testing input {j+1}: {e}")
                
                # Check for layout shifts
                print("📐 Checking for layout shifts...")
                layout_shifts = await page.evaluate("""
                    () => {
                        if (window.craftBugMetrics && window.craftBugMetrics.layoutShifts) {
                            return window.craftBugMetrics.layoutShifts;
                        }
                        return [];
                    }
                """)
                
                if layout_shifts:
                    print(f"   📐 Found {len(layout_shifts)} layout shifts")
                    for shift in layout_shifts[:3]:  # Show first 3
                        print(f"   - Layout shift: {shift}")
                else:
                    print("   ✅ No layout shifts detected")
                
                # Check for animation conflicts
                print("🎬 Checking for animation conflicts...")
                animation_conflicts = await page.evaluate("""
                    () => {
                        if (window.craftBugMetrics && window.craftBugMetrics.animationConflicts) {
                            return window.craftBugMetrics.animationConflicts;
                        }
                        return [];
                    }
                """)
                
                if animation_conflicts:
                    print(f"   🎬 Found {len(animation_conflicts)} animation conflicts")
                    for conflict in animation_conflicts[:3]:  # Show first 3
                        print(f"   - Animation conflict: {conflict}")
                else:
                    print("   ✅ No animation conflicts detected")
                
                # Generate craft bug report
                craft_bug_report = {
                    "test_case": test_case['name'],
                    "url": test_case['url'],
                    "timestamp": datetime.now().isoformat(),
                    "load_time": load_time,
                    "craft_bug_metrics": craft_bug_data,
                    "interactive_elements": {
                        "buttons": len(buttons),
                        "inputs": len(inputs),
                        "links": len(links)
                    },
                    "detected_issues": {
                        "layout_shifts": len(layout_shifts),
                        "animation_conflicts": len(animation_conflicts),
                        "slow_responses": load_time > 2.0
                    }
                }
                
                # Save report
                report_filename = f"craft_bug_report_{i}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                with open(report_filename, 'w') as f:
                    json.dump(craft_bug_report, f, indent=2)
                print(f"📄 Craft bug report saved: {report_filename}")
                
                # Wait before next test
                await asyncio.sleep(2)
                
            except Exception as e:
                print(f"❌ Error testing {test_case['name']}: {e}")
        
        # Close browser
        await browser.close()
        print("\n✅ Craft bug detection testing completed!")

def test_api_craft_bug_analysis():
    """Test the API craft bug analysis endpoints"""
    
    print("\n🔌 Testing API Craft Bug Analysis")
    print("=" * 40)
    
    base_url = "http://localhost:8000"
    
    # Test craft bug analysis endpoint
    test_data = {
        "mode": "url",
        "url": "http://localhost:5173/public/mocks/word/basic-doc.html",
        "modules": ["craft_bug_detection", "accessibility", "performance"],
        "scenario": "word_craft_bug_scenarios"
    }
    
    try:
        print("🔍 Sending craft bug analysis request...")
        response = requests.post(f"{base_url}/analyze", json=test_data, timeout=60)
        print(f"📊 Analysis response: {response.status_code}")
        
        if response.status_code == 200:
            analysis_data = response.json()
            print(f"   Analysis ID: {analysis_data.get('analysis_id')}")
            print(f"   Status: {analysis_data.get('status')}")
            
            # Check for craft bug findings
            if 'findings' in analysis_data:
                findings = analysis_data['findings']
                print(f"   Craft bug findings: {len(findings)}")
                for finding in findings[:3]:  # Show first 3
                    print(f"   - {finding.get('category')}: {finding.get('description')}")
        else:
            print(f"   Error response: {response.text}")
            
    except Exception as e:
        print(f"❌ API analysis failed: {e}")

async def main():
    """Main test function"""
    print("🎯 UX Analyzer - Craft Bug Detection Test")
    print("=" * 50)
    
    # Test API endpoints
    test_api_craft_bug_analysis()
    
    # Test Playwright craft bug detection
    await test_craft_bug_detection()
    
    print("\n🎉 Craft bug detection testing completed!")
    print("\n📊 Available Services:")
    print("   🌐 Frontend Dashboard: http://localhost:5173")
    print("   🔌 Backend API: http://localhost:8000")
    print("   📱 Mock Applications: http://localhost:3001")
    print("   📚 API Documentation: http://localhost:8000/docs")
    print("\n🔍 Test Results:")
    print("   - Screenshots saved as: craft_bug_test_*.png")
    print("   - Reports saved as: craft_bug_report_*.json")

if __name__ == "__main__":
    asyncio.run(main())
