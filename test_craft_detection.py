#!/usr/bin/env python3
"""
Test craft bug detection directly on mock apps
"""

import asyncio
from playwright.async_api import async_playwright
from craft_bug_detector import CraftBugDetector

async def test_craft_bug_detection():
    """Test craft bug detection directly"""
    detector = CraftBugDetector()
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        
        # Test on Word mock app
        print("🔍 Testing craft bug detection on Word mock app...")
        url = "http://localhost:8080/mocks/word/basic-doc.html"
        
        try:
            # Navigate to the page
            await page.goto(url)
            await page.wait_for_load_state('networkidle')
            
            # Run craft bug analysis
            print("🐛 Running craft bug analysis...")
            result = await detector.analyze_craft_bugs(page, url)
            
            print(f"\n📊 Analysis Results:")
            print(f"   URL: {result.url}")
            print(f"   Duration: {result.analysis_duration:.2f}s")
            print(f"   Total bugs found: {result.total_bugs_found}")
            print(f"   Bugs by category: {result.bugs_by_category}")
            
            if result.findings:
                print(f"\n🐛 Detected Craft Bugs:")
                for i, finding in enumerate(result.findings, 1):
                    print(f"   {i}. Category {finding.category}: {finding.bug_type}")
                    print(f"      Severity: {finding.severity}")
                    print(f"      Description: {finding.description}")
                    print(f"      Location: {finding.location}")
                    print(f"      Metrics: {finding.metrics}")
                    print()
            else:
                print("\n⚠️ No craft bugs detected")
                
            # Test interactions
            print("\n🖱️ Testing page interactions...")
            
            # Try clicking buttons and inputs
            buttons = await page.query_selector_all('button')
            inputs = await page.query_selector_all('input')
            
            print(f"   Found {len(buttons)} buttons and {len(inputs)} inputs")
            
            # Test some interactions
            if buttons:
                print("   Testing button click...")
                try:
                    await buttons[0].click()
                    await page.wait_for_timeout(1000)
                    print("   ✅ Button click successful")
                except Exception as e:
                    print(f"   ❌ Button click failed: {e}")
            
            if inputs:
                print("   Testing input typing...")
                try:
                    await inputs[0].click()
                    await inputs[0].type("Test text", delay=50)
                    await page.wait_for_timeout(1000)
                    print("   ✅ Input typing successful")
                except Exception as e:
                    print(f"   ❌ Input typing failed: {e}")
            
        except Exception as e:
            print(f"❌ Test failed: {e}")
            import traceback
            traceback.print_exc()
        
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(test_craft_bug_detection())
