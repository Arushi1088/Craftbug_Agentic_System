#!/usr/bin/env python3
"""
Test browser automation step execution to debug scenario issues
"""

import asyncio
import logging
from playwright.async_api import async_playwright

# Configure logging to see detailed output
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_craft_bug_scenario():
    """Test the craft bug scenario step by step"""
    
    logger.info("🚀 Starting browser automation test...")
    
    async with async_playwright() as p:
        # Launch browser in non-headless mode so we can see what's happening
        browser = await p.chromium.launch(headless=False, args=['--no-sandbox'])
        page = await browser.new_page()
        
        try:
            # Set a larger viewport
            await page.set_viewport_size({"width": 1280, "height": 720})
            
            # Step 1: Navigate to Word mock
            url = "http://127.0.0.1:9000/mocks/word/basic-doc.html"
            logger.info(f"🔗 Navigating to: {url}")
            await page.goto(url, wait_until='domcontentloaded', timeout=15000)
            
            # Wait a bit for page to fully load
            await page.wait_for_timeout(2000)
            logger.info("✅ Page loaded successfully")
            
            # Check if start button exists
            start_button = await page.query_selector('.start-button')
            if start_button:
                logger.info("✅ Start button found")
                
                # Step 2: Click start button
                logger.info("🖱️ Clicking start button...")
                await start_button.click()
                logger.info("✅ Start button clicked")
                
                # Wait for loading delay (4 seconds as per scenario)
                logger.info("⏳ Waiting for loading delay...")
                await page.wait_for_timeout(4000)
                
            else:
                logger.error("❌ Start button not found!")
                return
            
            # Step 3: Check for textarea
            textarea = await page.query_selector('textarea')
            if textarea:
                logger.info("✅ Textarea found")
                
                # Step 4: Type text
                text_to_type = "This is a comprehensive test of the document editing system"
                logger.info(f"⌨️ Typing text: {text_to_type}")
                await textarea.fill(text_to_type)
                logger.info("✅ Text typed successfully")
                
                # Wait between actions
                await page.wait_for_timeout(2000)
                
            else:
                logger.error("❌ Textarea not found!")
                return
            
            # Step 5: Click toolbar buttons
            toolbar_buttons = await page.query_selector_all('.toolbar button')
            logger.info(f"🔧 Found {len(toolbar_buttons)} toolbar buttons")
            
            if len(toolbar_buttons) >= 3:
                for i in range(3):
                    logger.info(f"🖱️ Clicking toolbar button {i+1}")
                    await toolbar_buttons[i].click()
                    await page.wait_for_timeout(1000)
                    logger.info(f"✅ Toolbar button {i+1} clicked")
            
            # Step 6: Test hover elements
            hover_elements = await page.query_selector_all('.craft-bug-hover')
            logger.info(f"🎯 Found {len(hover_elements)} craft-bug-hover elements")
            
            if hover_elements:
                logger.info("🖱️ Testing hover on first craft-bug element")
                await hover_elements[0].hover()
                await page.wait_for_timeout(800)
                logger.info("✅ Hover test completed")
            
            # Wait a bit more to observe the results
            logger.info("⏳ Waiting to observe final state...")
            await page.wait_for_timeout(3000)
            
            logger.info("🎉 Browser automation test completed successfully!")
            
        except Exception as e:
            logger.error(f"❌ Browser automation test failed: {e}")
            import traceback
            logger.error(f"Full traceback: {traceback.format_exc()}")
            
        finally:
            logger.info("🔄 Closing browser...")
            await browser.close()

if __name__ == "__main__":
    asyncio.run(test_craft_bug_scenario())
