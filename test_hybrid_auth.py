"""
Test script for Excel Web hybrid authentication
"""

import asyncio
import sys
from excel_web_hybrid_auth import get_hybrid_auth


async def test_hybrid_authentication():
    """Test the Excel Web hybrid authentication flow"""
    hybrid_auth = await get_hybrid_auth()
    
    try:
        print("🧪 Testing Excel Web Hybrid Authentication...")
        
        # Perform hybrid authentication
        session = await hybrid_auth.perform_hybrid_authentication(timeout_minutes=5)
        
        if session:
            print("✅ Hybrid authentication test passed!")
            print(f"📋 Session ID: {session.session_id}")
            
            # Test getting Playwright page with session
            print("🔧 Testing Playwright session restoration...")
            page = await hybrid_auth.get_playwright_page(session)
            
            if page:
                print("✅ Playwright session restoration successful!")
                
                # Navigate to Excel Web with restored session
                print("🌐 Navigating to Excel Web with restored session...")
                await page.goto("https://excel.office.com")
                
                # Take a screenshot to verify
                screenshot_path = f"screenshots/excel_web_hybrid_auth_{int(asyncio.get_event_loop().time())}.png"
                await page.screenshot(path=screenshot_path)
                print(f"📸 Screenshot saved: {screenshot_path}")
                
                # Close Playwright
                await hybrid_auth.auth_manager.close_playwright()
                
                return True
            else:
                print("❌ Playwright session restoration failed")
                return False
        else:
            print("❌ Hybrid authentication test failed")
            return False
            
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        return False


async def main():
    """Main test function"""
    print("🚀 Starting Excel Web Hybrid Authentication Test")
    print("=" * 60)
    
    success = await test_hybrid_authentication()
    
    print("=" * 60)
    if success:
        print("🎉 Hybrid authentication test passed!")
        print("✅ Excel Web automation is ready!")
        sys.exit(0)
    else:
        print("💥 Hybrid authentication test failed!")
        print("❌ Please try again")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
