#!/usr/bin/env python3
"""
Debug craft bug metrics to understand the timing issue
"""

import asyncio
from playwright.async_api import async_playwright

async def debug_craft_metrics():
    """Debug the craft bug metrics timing issue"""
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        
        # Navigate to the enhanced mock file directly
        file_path = "file:///Users/arushitandon/Desktop/analyzer/web-ui/public/mocks/word/basic-doc.html"
        print(f"🔍 Debugging craft bug metrics...")
        
        try:
            await page.goto(file_path)
            await page.wait_for_load_state('networkidle')
            
            # Initial check
            print("\n📊 Initial metrics check:")
            initial_metrics = await page.evaluate("() => window.craftBugMetrics")
            print(f"   Initial: {initial_metrics}")
            
            # Trigger the start button
            print("\n🔧 Triggering start button...")
            start_button = await page.query_selector('.start-button')
            if start_button:
                await start_button.click()
                await page.wait_for_timeout(4000)  # Wait for the delay
                
                # Check metrics after start button
                metrics_after_start = await page.evaluate("() => window.craftBugMetrics")
                print(f"   After start: {metrics_after_start}")
            
            # Type in textarea to trigger input delays
            print("\n🔧 Typing in textarea...")
            textarea = await page.query_selector('textarea')
            if textarea:
                await textarea.click()
                await textarea.type("Testing input delays", delay=50)
                await page.wait_for_timeout(1000)
                
                # Check metrics after typing
                metrics_after_typing = await page.evaluate("() => window.craftBugMetrics")
                print(f"   After typing: {metrics_after_typing}")
            
            # Click some toolbar buttons
            print("\n🔧 Clicking toolbar buttons...")
            toolbar_buttons = await page.query_selector_all('.toolbar button')
            for i, button in enumerate(toolbar_buttons[:2]):
                await button.click()
                await page.wait_for_timeout(800)
                
                # Check metrics after each button
                metrics_after_button = await page.evaluate("() => window.craftBugMetrics")
                print(f"   After button {i+1}: {metrics_after_button}")
            
            # Final comprehensive check
            print("\n📊 Final comprehensive metrics check:")
            final_metrics = await page.evaluate("""
                () => {
                    const metrics = window.craftBugMetrics;
                    return {
                        craftBugMetricsExists: !!window.craftBugMetrics,
                        buttonResponseTimes: metrics ? metrics.buttonResponseTimes : 'N/A',
                        layoutShifts: metrics ? metrics.layoutShifts : 'N/A',
                        animationConflicts: metrics ? metrics.animationConflicts : 'N/A',
                        inputDelays: metrics ? metrics.inputDelays : 'N/A',
                        feedbackFailures: metrics ? metrics.feedbackFailures : 'N/A',
                        buttonResponseTimesLength: metrics && metrics.buttonResponseTimes ? metrics.buttonResponseTimes.length : 0,
                        layoutShiftsLength: metrics && metrics.layoutShifts ? metrics.layoutShifts.length : 0,
                        animationConflictsLength: metrics && metrics.animationConflicts ? metrics.animationConflicts.length : 0,
                        inputDelaysLength: metrics && metrics.inputDelays ? metrics.inputDelays.length : 0,
                        feedbackFailuresLength: metrics && metrics.feedbackFailures ? metrics.feedbackFailures.length : 0
                    };
                }
            """)
            print(f"   Final comprehensive: {final_metrics}")
            
        except Exception as e:
            print(f"❌ Debug failed: {e}")
            import traceback
            traceback.print_exc()
        
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(debug_craft_metrics())
