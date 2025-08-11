#!/usr/bin/env python3
"""
Quick test to see what our detector is actually getting
"""

import asyncio
from playwright.async_api import async_playwright

async def test_detector_evaluation():
    """Test what the detector evaluation is getting"""
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        
        # Navigate to the enhanced mock file directly
        file_path = "file:///Users/arushitandon/Desktop/analyzer/web-ui/public/mocks/word/basic-doc.html"
        
        try:
            await page.goto(file_path)
            await page.wait_for_load_state('networkidle')
            
            # Trigger some craft bugs
            start_button = await page.query_selector('.start-button')
            if start_button:
                await start_button.click()
                await page.wait_for_timeout(4000)
            
            textarea = await page.query_selector('textarea')
            if textarea:
                await textarea.click()
                await textarea.type("Testing", delay=50)
                await page.wait_for_timeout(1000)
            
            # Test the exact evaluation from our detector
            print("🔍 Testing detector evaluation...")
            
            # First, test the animation metrics evaluation
            animation_result = await page.evaluate("""
                () => {
                    const metrics = window.craftBugMetrics || window.excelCraftBugMetrics || window.pptCraftBugMetrics || {};
                    console.log('Raw metrics in detector evaluation:', metrics);
                    
                    const result = {
                        layoutThrashCount: (metrics.layoutShifts ? metrics.layoutShifts.length : 0),
                        animationConflicts: (metrics.animationConflicts ? metrics.animationConflicts.length : 0),
                        judderEvents: 0,
                        frameTimes: [],
                        layoutShifts: metrics.layoutShifts || [],
                        animationConflictList: metrics.animationConflicts || [],
                        rawLayoutShiftsCount: metrics.layoutShifts ? metrics.layoutShifts.length : 0,
                        rawAnimationConflictsCount: metrics.animationConflicts ? metrics.animationConflicts.length : 0
                    };
                    
                    console.log('Processed metrics in detector evaluation:', result);
                    return result;
                }
            """)
            print(f"Animation result: {animation_result}")
            
            # Test input metrics evaluation
            input_result = await page.evaluate("""
                () => {
                    const metrics = window.craftBugMetrics || window.excelCraftBugMetrics || window.pptCraftBugMetrics || {};
                    const result = {
                        inputLagEvents: (metrics.inputDelays ? metrics.inputDelays.length : 0),
                        delayedResponses: (metrics.buttonResponseTimes ? metrics.buttonResponseTimes.length : 0),
                        textBoxLagEvents: 0,
                        inputDelays: metrics.inputDelays || [],
                        buttonResponseTimes: metrics.buttonResponseTimes || [],
                        rawInputDelaysCount: metrics.inputDelays ? metrics.inputDelays.length : 0,
                        rawButtonResponseCount: metrics.buttonResponseTimes ? metrics.buttonResponseTimes.length : 0
                    };
                    console.log('Input metrics in detector evaluation:', result);
                    return result;
                }
            """)
            print(f"Input result: {input_result}")
            
        except Exception as e:
            print(f"❌ Test failed: {e}")
        
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(test_detector_evaluation())
