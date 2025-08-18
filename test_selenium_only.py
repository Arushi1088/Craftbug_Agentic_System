"""
Test script for Selenium-only Excel Web automation
"""

import asyncio
import sys
from excel_web_selenium_only import get_selenium_navigator


async def test_selenium_automation():
    """Test the Selenium-only Excel Web automation"""
    navigator = await get_selenium_navigator()
    
    try:
        print("🧪 Testing Selenium-only Excel Web Automation...")
        
        # Initialize navigator
        if not await navigator.initialize():
            print("❌ Failed to initialize navigator")
            return False
        
        # Test authentication
        if await navigator.ensure_authenticated():
            print("✅ Authentication test passed!")
            
            # Take a screenshot to verify we're logged in
            screenshot_path = await navigator.take_screenshot("excel_web_authenticated")
            if screenshot_path:
                print(f"📸 Authentication verified with screenshot: {screenshot_path}")
            
            # Get page info
            title = await navigator.get_page_title()
            url = await navigator.get_page_url()
            print(f"📄 Page Title: {title}")
            print(f"🌐 Page URL: {url}")
            
            return True
        else:
            print("❌ Authentication test failed")
            return False
            
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        return False
    finally:
        # Cleanup
        await navigator.close()


async def main():
    """Main test function"""
    print("🚀 Starting Selenium-only Excel Web Automation Test")
    print("=" * 60)
    
    success = await test_selenium_automation()
    
    print("=" * 60)
    if success:
        print("🎉 Selenium-only automation test passed!")
        print("✅ Excel Web automation is working correctly!")
        sys.exit(0)
    else:
        print("💥 Selenium-only automation test failed!")
        print("❌ Excel Web automation needs debugging")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
