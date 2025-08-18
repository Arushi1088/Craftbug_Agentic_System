"""
Simple browser test
"""

import asyncio
from playwright.async_api import async_playwright


async def test_browser():
    """Simple test to open browser and navigate"""
    try:
        print("🚀 Opening browser...")
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=False)
            page = await browser.new_page()
            
            print("🌐 Navigating to Excel Web...")
            await page.goto("https://excel.office.com")
            
            print("✅ Browser opened and navigated successfully!")
            print("🔐 Please complete authentication in the browser window...")
            print("⏳ Waiting 30 seconds for you to authenticate...")
            
            # Wait for user to authenticate
            await asyncio.sleep(30)
            
            print("✅ Test completed!")
            await browser.close()
            
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    asyncio.run(test_browser())
