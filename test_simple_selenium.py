#!/usr/bin/env python3
"""
Simple Selenium test to check if browser automation is working
"""

import asyncio
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

async def test_simple_selenium():
    """Test if Selenium WebDriver works"""
    print("🧪 Testing simple Selenium setup...")
    
    try:
        # Create Chrome options
        chrome_options = Options()
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        print("🚀 Starting Chrome browser...")
        driver = webdriver.Chrome(options=chrome_options)
        
        print("✅ Chrome browser started successfully")
        
        # Navigate to a simple page
        print("🌐 Navigating to Google...")
        driver.get("https://www.google.com")
        
        print("✅ Successfully navigated to Google")
        
        # Get page title
        title = driver.title
        print(f"📄 Page title: {title}")
        
        # Take a screenshot
        screenshot_path = "test_simple_selenium.png"
        driver.save_screenshot(screenshot_path)
        print(f"📸 Screenshot saved: {screenshot_path}")
        
        # Close browser
        driver.quit()
        print("✅ Browser closed successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_simple_selenium())
    if success:
        print("🎉 Simple Selenium test passed!")
    else:
        print("💥 Simple Selenium test failed!")

