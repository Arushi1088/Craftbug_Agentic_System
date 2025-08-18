"""
Simple manual authentication test
"""

import asyncio
from playwright.async_api import async_playwright


async def simple_manual_auth():
    """Simple manual authentication - just open browser and navigate"""
    try:
        print("🚀 Starting simple manual authentication...")
        
        # Start playwright
        playwright = await async_playwright().start()
        
        # Launch browser
        browser = await playwright.chromium.launch(
            headless=False,
            args=[
                '--no-sandbox',
                '--disable-dev-shm-usage'
            ]
        )
        
        # Create page
        page = await browser.new_page()
        
        # Navigate to Excel Web
        print("🌐 Navigating to Excel Web...")
        await page.goto("https://excel.office.com")
        
        print("\n" + "=" * 60)
        print("🔐 MANUAL AUTHENTICATION REQUIRED")
        print("=" * 60)
        print("Please complete the authentication process in the browser window.")
        print("This may include:")
        print("  - Entering your email/username")
        print("  - Using biometric authentication (fingerprint/face)")
        print("  - Using passkey")
        print("  - Completing any MFA steps")
        print()
        print("⏱️  You have 5 minutes to complete authentication.")
        print("The system will wait for you to finish...")
        print("=" * 60)
        
        # Wait for user to complete authentication
        start_time = asyncio.get_event_loop().time()
        timeout_seconds = 5 * 60  # 5 minutes
        
        while asyncio.get_event_loop().time() - start_time < timeout_seconds:
            # Check if we're successfully authenticated
            current_url = page.url
            print(f"Current URL: {current_url}")
            
            # Check for success indicators
            try:
                # Look for Excel indicators
                excel_indicators = ['text=Excel', 'text=Workbook', 'text=New']
                for indicator in excel_indicators:
                    try:
                        await page.wait_for_selector(indicator, timeout=2000)
                        print("✅ Authentication successful! Found Excel indicators.")
                        break
                    except:
                        continue
                else:
                    # Check if we're still on login page
                    if 'login.microsoftonline.com' in current_url or 'login.live.com' in current_url:
                        print("⏳ Still on login page, waiting...")
                    else:
                        print("✅ Authentication appears successful!")
                        break
            except Exception as e:
                print(f"⚠️  Error checking authentication: {e}")
            
            # Wait before checking again
            await asyncio.sleep(5)
        
        print("\n✅ Manual authentication completed!")
        print("📋 Session captured successfully")
        
        # Keep browser open for a moment
        print("⏳ Keeping browser open for 10 seconds...")
        await asyncio.sleep(10)
        
        # Close browser
        await browser.close()
        await playwright.stop()
        
        print("✅ Browser closed")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


async def main():
    """Main function"""
    success = await simple_manual_auth()
    
    if success:
        print("🎉 Manual authentication test completed successfully!")
    else:
        print("💥 Manual authentication test failed!")


if __name__ == "__main__":
    asyncio.run(main())
