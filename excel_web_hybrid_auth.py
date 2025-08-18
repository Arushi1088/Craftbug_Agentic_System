"""
Excel Web Hybrid Authentication Module
Uses Selenium for manual authentication and Playwright for automation
"""

import asyncio
import time
import json
from datetime import datetime
from typing import Optional, Dict, Any
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from playwright.async_api import async_playwright, Browser, Page
from excel_web_config import get_excel_web_config
from excel_web_session import SessionManager, ExcelWebSession


class HybridAuthenticationManager:
    """Manages hybrid authentication (Selenium for manual, Playwright for automation)"""
    
    def __init__(self):
        self.config = get_excel_web_config()
        self.session_manager = SessionManager()
        self.selenium_driver = None
        self.playwright_browser = None
        self.playwright_page = None
    
    async def perform_manual_authentication(self, timeout_minutes: int = 5) -> Optional[ExcelWebSession]:
        """Perform manual authentication using Selenium"""
        try:
            print("🚀 Starting manual authentication with Selenium...")
            
            # Setup Chrome options
            chrome_options = Options()
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-blink-features=AutomationControlled")
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            
            # Create Selenium driver
            self.selenium_driver = webdriver.Chrome(options=chrome_options)
            self.selenium_driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            # Navigate to Excel Web
            print("🌐 Navigating to Excel Web...")
            self.selenium_driver.get("https://excel.office.com")
            
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
            print(f"⏱️  You have {timeout_minutes} minutes to complete authentication.")
            print("The system will wait for you to finish...")
            print("=" * 60)
            
            # Wait for user to complete authentication
            start_time = time.time()
            timeout_seconds = timeout_minutes * 60
            
            while time.time() - start_time < timeout_seconds:
                current_url = self.selenium_driver.current_url
                print(f"Current URL: {current_url}")
                
                # Check for success indicators
                try:
                    excel_indicators = ['Excel', 'Workbook', 'New', 'OneDrive', 'Office']
                    page_source = self.selenium_driver.page_source
                    
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
            
            if time.time() - start_time >= timeout_seconds:
                print("⏰ Timeout reached")
                return None
            
            # Capture session data from Selenium
            session = await self.capture_selenium_session()
            
            # Close Selenium browser
            self.selenium_driver.quit()
            self.selenium_driver = None
            
            print("✅ Manual authentication completed!")
            return session
            
        except Exception as e:
            print(f"❌ Manual authentication failed: {e}")
            if self.selenium_driver:
                self.selenium_driver.quit()
            return None
    
    async def capture_selenium_session(self) -> Optional[ExcelWebSession]:
        """Capture session data from Selenium driver"""
        try:
            if not self.selenium_driver:
                return None
            
            # Create session
            session = ExcelWebSession()
            session.session_id = f"selenium_session_{int(time.time() * 1000)}"
            session.created_at = datetime.now()
            session.last_used = datetime.now()
            session.is_valid = True
            
            # Capture cookies
            try:
                selenium_cookies = self.selenium_driver.get_cookies()
                session.cookies = {cookie['name']: cookie for cookie in selenium_cookies}
                print(f"✅ Captured {len(selenium_cookies)} cookies")
            except Exception as e:
                print(f"⚠️  Failed to capture cookies: {e}")
            
            # Capture local storage
            try:
                local_storage = self.selenium_driver.execute_script("return Object.entries(localStorage);")
                session.local_storage = dict(local_storage)
                print(f"✅ Captured {len(local_storage)} local storage items")
            except Exception as e:
                print(f"⚠️  Failed to capture local storage: {e}")
            
            # Capture session storage
            try:
                session_storage = self.selenium_driver.execute_script("return Object.entries(sessionStorage);")
                session.session_data = dict(session_storage)
                print(f"✅ Captured {len(session_storage)} session storage items")
            except Exception as e:
                print(f"⚠️  Failed to capture session storage: {e}")
            
            # Save session
            await self.session_manager.save_session(session)
            
            return session
            
        except Exception as e:
            print(f"❌ Failed to capture session: {e}")
            return None
    
    async def setup_playwright_for_automation(self) -> bool:
        """Setup Playwright for automation after manual authentication"""
        try:
            print("🔧 Setting up Playwright for automation...")
            
            self.playwright = await async_playwright().start()
            
            self.playwright_browser = await self.playwright.chromium.launch(
                headless=self.config.headless,
                args=[
                    '--no-sandbox',
                    '--disable-dev-shm-usage',
                    '--disable-web-security',
                    '--disable-features=VizDisplayCompositor'
                ]
            )
            
            self.playwright_page = await self.playwright_browser.new_page()
            self.playwright_page.set_default_timeout(self.config.page_load_timeout_seconds * 1000)
            
            print("✅ Playwright setup for automation")
            return True
            
        except Exception as e:
            print(f"❌ Failed to setup Playwright: {e}")
            return False
    
    async def restore_session_to_playwright(self, session: ExcelWebSession) -> bool:
        """Restore session from Selenium to Playwright"""
        try:
            if not self.playwright_page:
                await self.setup_playwright_for_automation()
            
            # Restore cookies
            if session.cookies:
                cookies = list(session.cookies.values())
                await self.playwright_page.context.add_cookies(cookies)
                print("✅ Restored cookies to Playwright")
            
            # Restore local storage
            if session.local_storage:
                for key, value in session.local_storage.items():
                    await self.playwright_page.evaluate(f"localStorage.setItem('{key}', '{value}')")
                print("✅ Restored local storage to Playwright")
            
            # Restore session storage
            if session.session_data:
                for key, value in session.session_data.items():
                    await self.playwright_page.evaluate(f"sessionStorage.setItem('{key}', '{value}')")
                print("✅ Restored session storage to Playwright")
            
            return True
            
        except Exception as e:
            print(f"❌ Failed to restore session to Playwright: {e}")
            return False
    
    async def close_playwright(self):
        """Close Playwright browser"""
        try:
            if self.playwright_page:
                await self.playwright_page.close()
            if self.playwright_browser:
                await self.playwright_browser.close()
            if hasattr(self, 'playwright'):
                await self.playwright.stop()
            print("✅ Playwright closed")
        except Exception as e:
            print(f"⚠️  Error closing Playwright: {e}")


class ExcelWebHybridAuth:
    """Main class for Excel Web hybrid authentication"""
    
    def __init__(self):
        self.auth_manager = HybridAuthenticationManager()
        self.session_manager = SessionManager()
    
    async def perform_hybrid_authentication(self, timeout_minutes: int = 5) -> Optional[ExcelWebSession]:
        """Perform hybrid authentication (manual + automation)"""
        try:
            print("🚀 Starting Excel Web Hybrid Authentication...")
            
            # Check for existing session first
            existing_session = await self.session_manager.get_valid_session()
            if existing_session:
                print(f"✅ Found valid existing session: {existing_session.session_id}")
                return existing_session
            
            # Perform manual authentication
            session = await self.auth_manager.perform_manual_authentication(timeout_minutes)
            
            if session:
                print("🎉 Hybrid authentication completed successfully!")
                print(f"📋 Session ID: {session.session_id}")
                return session
            else:
                print("❌ Hybrid authentication failed")
                return None
                
        except Exception as e:
            print(f"❌ Hybrid authentication failed: {e}")
            return None
    
    async def get_playwright_page(self, session: ExcelWebSession) -> Optional[Page]:
        """Get Playwright page with restored session"""
        try:
            # Setup Playwright
            if not await self.auth_manager.setup_playwright_for_automation():
                return None
            
            # Restore session to Playwright
            if not await self.auth_manager.restore_session_to_playwright(session):
                return None
            
            return self.auth_manager.playwright_page
            
        except Exception as e:
            print(f"❌ Failed to get Playwright page: {e}")
            return None


# Global instance
hybrid_auth = ExcelWebHybridAuth()


async def get_hybrid_auth() -> ExcelWebHybridAuth:
    """Get the global hybrid authentication instance"""
    return hybrid_auth
