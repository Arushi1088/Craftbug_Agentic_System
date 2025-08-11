#!/usr/bin/env python3
"""
Test the full detector with debugging to see where the logic fails
"""

import asyncio
from playwright.async_api import async_playwright
from craft_bug_detector import CraftBugDetector

async def test_full_detector_with_debug():
    """Test the full detector with debugging"""
    detector = CraftBugDetector()
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        
        # Navigate to the enhanced mock file directly
        file_path = "file:///Users/arushitandon/Desktop/analyzer/web-ui/public/mocks/word/basic-doc.html"
        
        try:
            await page.goto(file_path)
            await page.wait_for_load_state('networkidle')
            
            # Trigger craft bugs
            print("🔧 Triggering craft bugs...")
            start_button = await page.query_selector('.start-button')
            if start_button:
                await start_button.click()
                await page.wait_for_timeout(4000)
            
            textarea = await page.query_selector('textarea')
            if textarea:
                await textarea.click()
                await textarea.type("Testing", delay=50)
                await page.wait_for_timeout(1000)
            
            # Now run the full detector analysis
            print("\n🐛 Running full detector analysis...")
            result = await detector.analyze_craft_bugs(page, file_path)
            
            print(f"\n📊 Final Analysis Results:")
            print(f"   Total bugs found: {result.total_bugs_found}")
            print(f"   Bugs by category: {result.bugs_by_category}")
            
            if result.findings:
                print(f"\n🐛 Detected Craft Bugs:")
                for i, finding in enumerate(result.findings, 1):
                    print(f"   {i}. Category {finding.category}: {finding.bug_type}")
                    print(f"      Severity: {finding.severity}")
                    print(f"      Description: {finding.description}")
            else:
                print("\n⚠️ No craft bugs detected - check debugging output above")
                
        except Exception as e:
            print(f"❌ Test failed: {e}")
            import traceback
            traceback.print_exc()
        
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(test_full_detector_with_debug())
