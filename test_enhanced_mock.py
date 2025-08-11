#!/usr/bin/env python3
"""
Test craft bug detection directly on the enhanced mock file
"""

import asyncio
from playwright.async_api import async_playwright
from craft_bug_detector import CraftBugDetector

async def test_enhanced_mock():
    """Test craft bug detection on the enhanced mock file directly"""
    detector = CraftBugDetector()
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        
        # Navigate to the enhanced mock file directly
        file_path = "file:///Users/arushitandon/Desktop/analyzer/web-ui/public/mocks/word/basic-doc.html"
        print(f"🔍 Testing craft bug detection on enhanced mock file...")
        print(f"   File: {file_path}")
        
        try:
            await page.goto(file_path)
            await page.wait_for_load_state('networkidle', timeout=10000)
            
            # Check page content
            title = await page.title()
            print(f"   Page title: {title}")
            
            # Look for craft bug indicators
            body_data = await page.get_attribute('body', 'data-craft-bugs')
            print(f"   Craft bugs data attribute: {body_data}")
            
            # Run craft bug analysis
            print("🐛 Running craft bug analysis...")
            result = await detector.analyze_craft_bugs(page, file_path)
            
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
            
            # Test some interactions to trigger bugs
            print("\n🖱️ Testing interactions to trigger craft bugs...")
            
            # Look for buttons with craft-bug-hover class
            craft_buttons = await page.query_selector_all('button.craft-bug-hover')
            print(f"   Found {len(craft_buttons)} buttons with craft-bug-hover class")
            
            if craft_buttons:
                print("   Testing craft bug button hover...")
                await craft_buttons[0].hover()
                await page.wait_for_timeout(1000)
                
                print("   Testing craft bug button click...")
                await craft_buttons[0].click()
                await page.wait_for_timeout(2000)
            
            # Look for elements that trigger layout thrash
            layout_elements = await page.query_selector_all('.layout-thrash')
            print(f"   Found {len(layout_elements)} layout-thrash elements")
            
            # Test textarea input lag
            textarea = await page.query_selector('textarea')
            if textarea:
                print("   Testing textarea input (looking for input lag)...")
                await textarea.click()
                await textarea.type("Testing craft bugs", delay=50)
                await page.wait_for_timeout(2000)
            
        except Exception as e:
            print(f"❌ Test failed: {e}")
            import traceback
            traceback.print_exc()
        
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(test_enhanced_mock())
