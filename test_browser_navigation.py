#!/usr/bin/env python3
"""
Test script to verify Chromium navigation works without 404 errors
"""

import asyncio
import json
from playwright.async_api import async_playwright

async def test_browser_navigation():
    """Test that Chromium can navigate to mock applications without 404 errors"""
    
    print("🔍 Testing Chromium Navigation (No 404 Errors)")
    print("=" * 50)
    
    async with async_playwright() as p:
        # Launch Chromium browser in non-headless mode so you can see it
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        
        # Test URLs
        test_urls = [
            {
                "name": "Word Mock",
                "url": "http://localhost:5173/mocks/word/basic-doc.html"
            },
            {
                "name": "Excel Mock", 
                "url": "http://localhost:5173/mocks/excel/open-format.html"
            },
            {
                "name": "PowerPoint Mock",
                "url": "http://localhost:5173/mocks/powerpoint/basic-deck.html"
            }
        ]
        
        for test_case in test_urls:
            print(f"\n📱 Testing {test_case['name']}...")
            print(f"🔗 URL: {test_case['url']}")
            
            try:
                # Navigate to the page
                print("📍 Navigating...")
                response = await page.goto(test_case['url'], wait_until='domcontentloaded', timeout=30000)
                
                # Check if navigation was successful
                if response.status == 200:
                    print(f"✅ Success! Status: {response.status}")
                    
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
                    
                    # Count interactive elements
                    buttons = await page.query_selector_all('button')
                    inputs = await page.query_selector_all('input')
                    print(f"🖱️ Interactive Elements: {len(buttons)} buttons, {len(inputs)} inputs")
                    
                elif response.status == 404:
                    print(f"❌ 404 Error! Status: {response.status}")
                    print(f"   This indicates the URL is not accessible")
                else:
                    print(f"⚠️ Unexpected status: {response.status}")
                    
                # Wait a bit before next test
                await asyncio.sleep(2)
                
            except Exception as e:
                print(f"❌ Error testing {test_case['name']}: {e}")
        
        # Close browser
        await browser.close()
        print("\n✅ Browser navigation test completed!")

async def test_analysis_with_browser():
    """Test the full analysis process with browser automation"""
    
    print("\n🚀 Testing Full Analysis Process")
    print("=" * 40)
    
    import requests
    
    # Test the analysis API
    test_data = {
        "url": "http://localhost:5173/mocks/word/basic-doc.html",
        "scenario_id": "1.1",
        "use_real_browser": True  # Use real browser automation
    }
    
    try:
        print("📤 Sending analysis request...")
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
            
            # Show issues
            for i, issue in enumerate(ux_issues[:3]):
                print(f"   Issue {i+1}: {issue.get('message')}")
                
        else:
            print(f"❌ Analysis Failed: {response.status_code}")
            print(f"   Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Analysis Error: {e}")

async def main():
    """Main test function"""
    print("🎯 Chromium Navigation Test")
    print("=" * 50)
    
    # Test basic navigation
    await test_browser_navigation()
    
    # Test full analysis
    await test_analysis_with_browser()
    
    print("\n🎉 All tests completed!")
    print("\n📊 Summary:")
    print("   ✅ Chromium should navigate without 404 errors")
    print("   ✅ Mock applications should load correctly")
    print("   ✅ Analysis should complete successfully")
    print("   ✅ Craft bugs should be detected")

if __name__ == "__main__":
    asyncio.run(main())
