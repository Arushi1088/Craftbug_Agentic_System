#!/usr/bin/env python3
"""
Comprehensive test that actually triggers craft bugs in the enhanced mock
"""

import asyncio
from playwright.async_api import async_playwright
from craft_bug_detector import CraftBugDetector

async def test_craft_bugs_with_interactions():
    """Test craft bug detection with proper user interactions"""
    detector = CraftBugDetector()
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        
        # Navigate to the enhanced mock file directly
        file_path = "file:///Users/arushitandon/Desktop/analyzer/web-ui/public/mocks/word/basic-doc.html"
        print(f"🔍 Testing craft bug detection with user interactions...")
        print(f"   File: {file_path}")
        
        try:
            await page.goto(file_path)
            await page.wait_for_load_state('networkidle', timeout=10000)
            
            # Check page content
            title = await page.title()
            print(f"   Page title: {title}")
            
            # STEP 1: Trigger the loading delay craft bug
            print("\n🔧 Step 1: Triggering loading delay craft bug...")
            start_button = await page.query_selector('.start-button')
            if start_button:
                await start_button.click()
                print("   ✅ Clicked start button - this should trigger loading delay")
                await page.wait_for_timeout(4000)  # Wait for the 3-second delay
            
            # STEP 2: Trigger layout thrash by interacting with elements
            print("\n🔧 Step 2: Triggering layout thrash...")
            toolbar_buttons = await page.query_selector_all('.toolbar button')
            for i, button in enumerate(toolbar_buttons[:3]):
                await button.click()
                await page.wait_for_timeout(500)
                print(f"   ✅ Clicked toolbar button {i+1}")
            
            # STEP 3: Trigger input lag by typing in the textarea
            print("\n🔧 Step 3: Triggering input lag...")
            textarea = await page.query_selector('textarea')
            if textarea:
                await textarea.click()
                # Type multiple characters to trigger input lag detection
                await textarea.type("This is a test of input lag detection in the craft bug system", delay=10)
                await page.wait_for_timeout(2000)
                print("   ✅ Typed in textarea - this should trigger input lag")
            
            # STEP 4: Trigger feedback issues by hovering over craft-bug elements
            print("\n🔧 Step 4: Triggering feedback issues...")
            craft_buttons = await page.query_selector_all('button.craft-bug-hover')
            for i, button in enumerate(craft_buttons):
                await button.hover()
                await page.wait_for_timeout(500)
                await button.click()
                await page.wait_for_timeout(500)
                print(f"   ✅ Hovered and clicked craft-bug button {i+1}")
            
            # STEP 5: Try to trigger animation conflicts
            print("\n🔧 Step 5: Triggering animation conflicts...")
            comments_tab = await page.query_selector('#comments-tab')
            if comments_tab:
                await comments_tab.click()
                await page.wait_for_timeout(1000)
                print("   ✅ Clicked comments tab - this should trigger animations")
            
            # STEP 6: Insert image to trigger more interactions
            print("\n🔧 Step 6: Triggering image insertion...")
            image_btn = await page.query_selector('.image-insert-btn')
            if image_btn:
                await image_btn.click()
                await page.wait_for_timeout(1000)
                print("   ✅ Clicked image insert button")
            
            # STEP 7: Check current metrics
            print("\n📊 Checking craft bug metrics after interactions...")
            current_metrics = await page.evaluate("""
                () => {
                    const metrics = window.craftBugMetrics || {};
                    return {
                        buttonResponseTimes: metrics.buttonResponseTimes || [],
                        layoutShifts: metrics.layoutShifts || [],
                        animationConflicts: metrics.animationConflicts || [],
                        inputDelays: metrics.inputDelays || [],
                        feedbackFailures: metrics.feedbackFailures || []
                    };
                }
            """)
            
            print(f"   Button Response Times: {len(current_metrics['buttonResponseTimes'])}")
            print(f"   Layout Shifts: {len(current_metrics['layoutShifts'])}")
            print(f"   Animation Conflicts: {len(current_metrics['animationConflicts'])}")
            print(f"   Input Delays: {len(current_metrics['inputDelays'])}")
            print(f"   Feedback Failures: {len(current_metrics['feedbackFailures'])}")
            
            # STEP 8: Now run craft bug analysis
            print("\n🐛 Running craft bug analysis after interactions...")
            result = await detector.analyze_craft_bugs(page, file_path)
            
            print(f"\n📊 Final Analysis Results:")
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
                print("\n⚠️ No craft bugs detected - this indicates an issue with detection logic")
                
                # Debug: Show what metrics are available
                print("\n🔍 Debug - Available window objects:")
                available_objects = await page.evaluate("""
                    () => {
                        return Object.keys(window).filter(key => 
                            key.includes('craft') || key.includes('bug') || key.includes('metrics')
                        );
                    }
                """)
                print(f"   Available objects: {available_objects}")
                
        except Exception as e:
            print(f"❌ Test failed: {e}")
            import traceback
            traceback.print_exc()
        
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(test_craft_bugs_with_interactions())
