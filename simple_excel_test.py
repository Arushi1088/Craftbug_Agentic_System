"""
Simple Excel Web Test
Just authenticates and takes screenshots to verify functionality
"""

import asyncio
from excel_web_selenium_only import get_selenium_navigator


async def simple_excel_test():
    """Simple test that just authenticates and takes screenshots"""
    navigator = await get_selenium_navigator()
    
    try:
        print("🧪 Simple Excel Web Test...")
        
        # Initialize and authenticate
        if not await navigator.initialize():
            print("❌ Failed to initialize navigator")
            return False
        
        if not await navigator.ensure_authenticated():
            print("❌ Failed to authenticate")
            return False
        
        print("✅ Successfully authenticated to Excel Web")
        
        # Take screenshots
        screenshot1 = await navigator.take_screenshot("excel_web_simple_test_1")
        print(f"📸 Screenshot 1: {screenshot1}")
        
        # Get page info
        title = await navigator.get_page_title()
        url = await navigator.get_page_url()
        print(f"📄 Page Title: {title}")
        print(f"🌐 Page URL: {url}")
        
        # Wait a moment
        await asyncio.sleep(2)
        
        # Take another screenshot
        screenshot2 = await navigator.take_screenshot("excel_web_simple_test_2")
        print(f"📸 Screenshot 2: {screenshot2}")
        
        print("✅ Simple Excel Web test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False
    finally:
        await navigator.close()


if __name__ == "__main__":
    success = asyncio.run(simple_excel_test())
    if success:
        print("🎉 Test passed!")
    else:
        print("💥 Test failed!")
