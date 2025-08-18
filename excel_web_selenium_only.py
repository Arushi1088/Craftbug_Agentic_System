"""
Excel Web Selenium-Only Automation Module
Uses Selenium for both authentication and automation
"""

import asyncio
import time
import json
from datetime import datetime
from typing import Optional, Dict, Any, List
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from excel_web_config import get_excel_web_config
from excel_web_session import SessionManager, ExcelWebSession


class SeleniumExcelWebNavigator:
    """Excel Web navigator using only Selenium"""
    
    def __init__(self):
        self.config = get_excel_web_config()
        self.session_manager = SessionManager()
        self.driver = None
        self.current_session = None
        self.is_authenticated = False
    
    async def initialize(self) -> bool:
        """Initialize the Selenium navigator"""
        try:
            print("🚀 Initializing Selenium Excel Web Navigator...")
            
            # Cleanup expired sessions
            await self.session_manager.cleanup_expired_sessions()
            
            print("✅ Selenium Excel Web Navigator initialized")
            return True
            
        except Exception as e:
            print(f"❌ Failed to initialize navigator: {e}")
            return False
    
    async def ensure_authenticated(self) -> bool:
        """Ensure we have a valid authenticated session"""
        try:
            # Check if we have a valid session
            valid_session = await self.session_manager.get_valid_session()
            
            if valid_session:
                print(f"✅ Found valid session: {valid_session.session_id}")
                
                # Restore session to browser
                if await self.restore_session_to_browser(valid_session):
                    self.current_session = valid_session
                    self.is_authenticated = True
                    print("✅ Successfully restored session")
                    return True
                else:
                    print("⚠️  Session restoration failed, will re-authenticate")
                    await self.session_manager.invalidate_session(valid_session)
            
            # No valid session, need to authenticate
            return await self.authenticate()
            
        except Exception as e:
            print(f"❌ Authentication check failed: {e}")
            return False
    
    async def authenticate(self) -> bool:
        """Perform manual authentication"""
        try:
            print("🔐 Starting manual authentication...")
            
            # Setup Chrome options
            chrome_options = Options()
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-blink-features=AutomationControlled")
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            
            # Create driver
            self.driver = webdriver.Chrome(options=chrome_options)
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            # Navigate to Excel Web
            print("🌐 Navigating to Excel Web...")
            self.driver.get("https://excel.cloud.microsoft/")
            
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
                current_url = self.driver.current_url
                print(f"Current URL: {current_url}")
                
                # Check for success indicators
                try:
                    excel_indicators = ['Excel', 'Workbook', 'New', 'OneDrive', 'Office']
                    page_source = self.driver.page_source
                    
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
                return False
            
            # Capture session
            session = await self.capture_session()
            
            if session:
                self.current_session = session
                self.is_authenticated = True
                print("✅ Authentication successful")
                return True
            else:
                print("❌ Failed to capture session")
                return False
                
        except Exception as e:
            print(f"❌ Authentication failed: {e}")
            return False
    
    async def capture_session(self) -> Optional[ExcelWebSession]:
        """Capture session data from current browser"""
        try:
            if not self.driver:
                return None
            
            # Create session
            session = ExcelWebSession()
            session.session_id = f"selenium_session_{int(time.time() * 1000)}"
            session.created_at = datetime.now()
            session.last_used = datetime.now()
            session.is_valid = True
            
            # Capture cookies
            try:
                selenium_cookies = self.driver.get_cookies()
                session.cookies = {cookie['name']: cookie for cookie in selenium_cookies}
                print(f"✅ Captured {len(selenium_cookies)} cookies")
            except Exception as e:
                print(f"⚠️  Failed to capture cookies: {e}")
            
            # Capture local storage
            try:
                local_storage = self.driver.execute_script("return Object.entries(localStorage);")
                session.local_storage = dict(local_storage)
                print(f"✅ Captured {len(local_storage)} local storage items")
            except Exception as e:
                print(f"⚠️  Failed to capture local storage: {e}")
            
            # Capture session storage
            try:
                session_storage = self.driver.execute_script("return Object.entries(sessionStorage);")
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
    
    async def restore_session_to_browser(self, session: ExcelWebSession) -> bool:
        """Restore session to browser"""
        try:
            if not self.driver:
                # Create new driver
                chrome_options = Options()
                chrome_options.add_argument("--no-sandbox")
                chrome_options.add_argument("--disable-dev-shm-usage")
                chrome_options.add_argument("--disable-blink-features=AutomationControlled")
                chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
                chrome_options.add_experimental_option('useAutomationExtension', False)
                
                self.driver = webdriver.Chrome(options=chrome_options)
                self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            # Navigate to Excel Web first
            self.driver.get("https://excel.office.com")
            
            # Restore cookies
            if session.cookies:
                for cookie in session.cookies.values():
                    try:
                        self.driver.add_cookie(cookie)
                    except:
                        pass
                print("✅ Restored cookies")
            
            # Restore local storage
            if session.local_storage:
                for key, value in session.local_storage.items():
                    try:
                        self.driver.execute_script(f"localStorage.setItem('{key}', '{value}')")
                    except:
                        pass
                print("✅ Restored local storage")
            
            # Restore session storage
            if session.session_data:
                for key, value in session.session_data.items():
                    try:
                        self.driver.execute_script(f"sessionStorage.setItem('{key}', '{value}')")
                    except:
                        pass
                print("✅ Restored session storage")
            
            # Refresh page to apply session
            self.driver.refresh()
            
            # Wait for page to load
            time.sleep(3)
            
            # Check if authentication is still valid
            current_url = self.driver.current_url
            if 'login.microsoftonline.com' in current_url or 'login.live.com' in current_url:
                print("❌ Session restoration failed - still on login page")
                return False
            
            print("✅ Session restored successfully")
            return True
            
        except Exception as e:
            print(f"❌ Failed to restore session: {e}")
            return False
    
    async def navigate_to_excel_web(self) -> bool:
        """Navigate to Excel Web with authentication"""
        try:
            if not await self.ensure_authenticated():
                return False
            
            return True
            
        except Exception as e:
            print(f"❌ Navigation failed: {e}")
            return False
    
    async def click_element(self, selector: str, timeout: int = 10) -> bool:
        """Click an element on the page using CSS selector"""
        try:
            if not self.driver:
                return False
            
            # Wait for element and click
            wait = WebDriverWait(self.driver, timeout)
            element = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, selector)))
            element.click()
            
            print(f"✅ Clicked element: {selector}")
            return True
            
        except TimeoutException:
            print(f"❌ Element not found for clicking: {selector}")
            return False
        except Exception as e:
            print(f"❌ Failed to click element {selector}: {e}")
            return False
    
    async def click_element_by_xpath(self, xpath: str, timeout: int = 10) -> bool:
        """Click an element on the page using XPath"""
        try:
            if not self.driver:
                return False
            
            # Wait for element and click
            wait = WebDriverWait(self.driver, timeout)
            element = wait.until(EC.element_to_be_clickable((By.XPATH, xpath)))
            element.click()
            
            print(f"✅ Clicked element by XPath: {xpath}")
            return True
            
        except TimeoutException:
            print(f"❌ Element not found for clicking by XPath: {xpath}")
            return False
        except Exception as e:
            print(f"❌ Failed to click element by XPath {xpath}: {e}")
            return False
    
    async def fill_input(self, selector: str, value: str, timeout: int = 10) -> bool:
        """Fill an input field"""
        try:
            if not self.driver:
                return False
            
            # Wait for element and fill
            wait = WebDriverWait(self.driver, timeout)
            element = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))
            element.clear()
            element.send_keys(value)
            
            print(f"✅ Filled input {selector}: {value}")
            return True
            
        except TimeoutException:
            print(f"❌ Input element not found: {selector}")
            return False
        except Exception as e:
            print(f"❌ Failed to fill input {selector}: {e}")
            return False
    
    async def wait_for_element(self, selector: str, timeout: int = 10) -> bool:
        """Wait for an element to appear on the page"""
        try:
            if not self.driver:
                return False
            
            wait = WebDriverWait(self.driver, timeout)
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))
            return True
            
        except TimeoutException:
            print(f"⚠️  Element not found: {selector}")
            return False
        except Exception as e:
            print(f"❌ Error waiting for element {selector}: {e}")
            return False
    
    async def take_screenshot(self, name: str = "screenshot") -> Optional[str]:
        """Take a screenshot of the current page"""
        try:
            if not self.driver:
                return None
            
            timestamp = int(time.time())
            filename = f"{name}_{timestamp}.png"
            filepath = f"{self.config.screenshot_dir}/{filename}"
            
            self.driver.save_screenshot(filepath)
            print(f"📸 Screenshot saved: {filepath}")
            return filepath
            
        except Exception as e:
            print(f"❌ Failed to take screenshot: {e}")
            return None
    
    async def get_page_title(self) -> str:
        """Get the current page title"""
        try:
            if not self.driver:
                return ""
            
            return self.driver.title
            
        except Exception as e:
            print(f"❌ Failed to get page title: {e}")
            return ""
    
    async def get_page_url(self) -> str:
        """Get the current page URL"""
        try:
            if not self.driver:
                return ""
            
            return self.driver.current_url
            
        except Exception as e:
            print(f"❌ Failed to get page URL: {e}")
            return ""
    
    async def close(self):
        """Close the navigator and cleanup"""
        try:
            if self.driver:
                self.driver.quit()
                self.driver = None
            print("✅ Selenium navigator closed")
        except Exception as e:
            print(f"⚠️  Error during cleanup: {e}")


# Global navigator instance
selenium_navigator = SeleniumExcelWebNavigator()


async def get_selenium_navigator() -> SeleniumExcelWebNavigator:
    """Get the global Selenium navigator"""
    return selenium_navigator
