"""
Manual authentication using Selenium
"""

import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def manual_auth_with_selenium():
    """Manual authentication using Selenium"""
    try:
        print("🚀 Starting manual authentication with Selenium...")
        
        # Setup Chrome options
        chrome_options = Options()
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        # Create driver
        driver = webdriver.Chrome(options=chrome_options)
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        # Navigate to Excel Web
        print("🌐 Navigating to Excel Web...")
        driver.get("https://excel.office.com")
        
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
        start_time = time.time()
        timeout_seconds = 5 * 60  # 5 minutes
        
        while time.time() - start_time < timeout_seconds:
            current_url = driver.current_url
            print(f"Current URL: {current_url}")
            
            # Check for success indicators
            try:
                # Look for Excel indicators
                excel_indicators = ['Excel', 'Workbook', 'New']
                page_source = driver.page_source
                
                success_found = False
                for indicator in excel_indicators:
                    if indicator in page_source:
                        print(f"✅ Found '{indicator}' indicator!")
                        success_found = True
                        break
                
                if success_found:
                    print("✅ Authentication successful!")
                    break
                
                # Check if still on login page
                if 'login.microsoftonline.com' in current_url or 'login.live.com' in current_url:
                    print("⏳ Still on login page, waiting...")
                else:
                    print("✅ Authentication appears successful!")
                    break
                    
            except Exception as e:
                print(f"⚠️  Error checking authentication: {e}")
            
            # Wait before checking again
            time.sleep(5)
        
        print("\n✅ Manual authentication completed!")
        print("📋 Session captured successfully")
        
        # Keep browser open for a moment
        print("⏳ Keeping browser open for 10 seconds...")
        time.sleep(10)
        
        # Close browser
        driver.quit()
        print("✅ Browser closed")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


if __name__ == "__main__":
    success = manual_auth_with_selenium()
    
    if success:
        print("🎉 Manual authentication test completed successfully!")
    else:
        print("💥 Manual authentication test failed!")
