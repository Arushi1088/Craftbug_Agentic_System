#!/usr/bin/env python3
"""
Test script to demonstrate Playwright and Chromium analysis capabilities
with the running UX Analyzer services
"""

import asyncio
import json
import requests
from playwright.async_api import async_playwright
import time

async def test_playwright_analysis():
    """Test the Playwright analysis capabilities"""
    
    print("🚀 Testing Playwright and Chromium Analysis")
    print("=" * 50)
    
    # Test URLs
    test_urls = [
        "http://localhost:3001/mock_scenario_59f72380_20250730_161715.html",
        "http://localhost:3001/mock_scenario_cdf657b7_20250730_160241.html",
        "http://localhost:5173/public/mocks/word/basic-doc.html"
    ]
    
    async with async_playwright() as p:
        # Launch Chromium browser
        print("🌐 Launching Chromium browser...")
        browser = await p.chromium.launch(headless=False)  # Set to True for headless mode
        page = await browser.new_page()
        
        for i, url in enumerate(test_urls, 1):
            print(f"\n📱 Testing URL {i}: {url}")
            print("-" * 40)
            
            try:
                # Navigate to the page
                print(f"📍 Navigating to: {url}")
                await page.goto(url, wait_until='domcontentloaded', timeout=30000)
                
                # Wait for page to load
                await page.wait_for_load_state('networkidle')
                
                # Take a screenshot
                screenshot_path = f"test_screenshot_{i}.png"
                await page.screenshot(path=screenshot_path, full_page=True)
                print(f"📸 Screenshot saved: {screenshot_path}")
                
                # Get page title
                title = await page.title()
                print(f"📄 Page title: {title}")
                
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
                print("🖱️ Testing basic interactions...")
                
                # Try to find and click buttons
                buttons = await page.query_selector_all('button')
                print(f"🔘 Found {len(buttons)} buttons")
                
                # Try to find links
                links = await page.query_selector_all('a')
                print(f"🔗 Found {len(links)} links")
                
                # Test form inputs
                inputs = await page.query_selector_all('input')
                print(f"📝 Found {len(inputs)} input fields")
                
                # Check for accessibility issues
                print("♿ Checking accessibility...")
                accessibility_info = await page.evaluate("""
                    () => {
                        const issues = [];
                        
                        // Check for images without alt text
                        const images = document.querySelectorAll('img');
                        images.forEach((img, index) => {
                            if (!img.alt) {
                                issues.push(`Image ${index + 1} missing alt text`);
                            }
                        });
                        
                        // Check for form labels
                        const inputs = document.querySelectorAll('input');
                        inputs.forEach((input, index) => {
                            if (!input.id || !document.querySelector(`label[for="${input.id}"]`)) {
                                issues.push(`Input ${index + 1} missing label`);
                            }
                        });
                        
                        return {
                            totalImages: images.length,
                            totalInputs: inputs.length,
                            accessibilityIssues: issues
                        };
                    }
                """)
                
                print(f"♿ Accessibility check: {json.dumps(accessibility_info, indent=2)}")
                
                # Wait a bit before next test
                await asyncio.sleep(2)
                
            except Exception as e:
                print(f"❌ Error testing {url}: {e}")
        
        # Close browser
        await browser.close()
        print("\n✅ Playwright analysis completed!")

def test_api_endpoints():
    """Test the API endpoints"""
    
    print("\n🔌 Testing API Endpoints")
    print("=" * 30)
    
    base_url = "http://localhost:8000"
    
    # Test health endpoint
    try:
        response = requests.get(f"{base_url}/health")
        print(f"🏥 Health check: {response.status_code}")
        if response.status_code == 200:
            health_data = response.json()
            print(f"   Status: {health_data.get('status')}")
            print(f"   Version: {health_data.get('version')}")
    except Exception as e:
        print(f"❌ Health check failed: {e}")
    
    # Test available scenarios
    try:
        response = requests.get(f"{base_url}/scenarios")
        print(f"📋 Scenarios: {response.status_code}")
        if response.status_code == 200:
            scenarios = response.json()
            print(f"   Available scenarios: {len(scenarios)}")
            for scenario in scenarios[:3]:  # Show first 3
                print(f"   - {scenario.get('name', 'Unknown')}")
    except Exception as e:
        print(f"❌ Scenarios check failed: {e}")
    
    # Test analysis endpoint
    try:
        test_data = {
            "mode": "url",
            "url": "http://localhost:3001/mock_scenario_59f72380_20250730_161715.html",
            "scenario": "basic_navigation"
        }
        response = requests.post(f"{base_url}/analyze", json=test_data)
        print(f"🔍 Analysis request: {response.status_code}")
        if response.status_code == 200:
            analysis_data = response.json()
            print(f"   Analysis ID: {analysis_data.get('analysis_id')}")
            print(f"   Status: {analysis_data.get('status')}")
    except Exception as e:
        print(f"❌ Analysis request failed: {e}")

async def main():
    """Main test function"""
    print("🎯 UX Analyzer - Playwright & Chromium Test")
    print("=" * 50)
    
    # Test API endpoints first
    test_api_endpoints()
    
    # Test Playwright analysis
    await test_playwright_analysis()
    
    print("\n🎉 All tests completed!")
    print("\n📊 Available Services:")
    print("   🌐 Frontend Dashboard: http://localhost:5173")
    print("   🔌 Backend API: http://localhost:8000")
    print("   📱 Mock Applications: http://localhost:3001")
    print("   📚 API Documentation: http://localhost:8000/docs")

if __name__ == "__main__":
    asyncio.run(main())
