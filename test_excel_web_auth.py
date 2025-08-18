"""
Test script for Excel Web authentication
"""

import asyncio
import sys
from excel_web_navigator import get_excel_web_navigator


async def test_excel_web_authentication():
    """Test the Excel Web authentication flow"""
    navigator = await get_excel_web_navigator()
    
    try:
        print("🧪 Testing Excel Web Authentication...")
        
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
    print("🚀 Starting Excel Web Authentication Test")
    print("=" * 50)
    
    success = await test_excel_web_authentication()
    
    print("=" * 50)
    if success:
        print("🎉 All tests passed!")
        sys.exit(0)
    else:
        print("💥 Tests failed!")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
