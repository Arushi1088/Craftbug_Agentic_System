"""
Unified Excel Web Navigator

This module provides a unified interface for Excel Web navigation, consolidating
functionality from multiple existing navigator classes while maintaining backward
compatibility and improving maintainability.
"""

import asyncio
import time
import json
from datetime import datetime
from typing import Optional, Dict, Any, List, Union
from pathlib import Path
from dataclasses import dataclass

# Selenium imports
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# Playwright imports (for hybrid approach)
try:
    from playwright.async_api import async_playwright, Browser, Page
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False

# Local imports
from .config import get_config, ExcelWebConfig
from .session import ExcelWebSession, SessionManager
from .exceptions import ExcelNavigationError, AuthenticationError


@dataclass
class NavigationResult:
    """Result of a navigation operation"""
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None
    screenshot_path: Optional[str] = None
    error: Optional[str] = None


@dataclass
class AuthenticationResult:
    """Result of an authentication operation"""
    success: bool
    session: Optional[ExcelWebSession] = None
    message: str = ""
    error: Optional[str] = None


class UnifiedExcelNavigator:
    """
    Unified Excel Web Navigator
    
    This class consolidates functionality from multiple existing navigator classes:
    - SeleniumExcelWebNavigator
    - EnhancedExcelWebNavigator
    - FinalExcelWebNavigator
    - ExcelWebNavigator
    
    It provides a single, consistent interface while maintaining backward compatibility.
    """
    
    def __init__(self, config: Optional[ExcelWebConfig] = None):
        """
        Initialize the unified navigator
        
        Args:
            config: Excel Web configuration. If None, uses global config.
        """
        self.config = config or get_config().get_excel_web_config()
        self.session_manager = SessionManager()
        
        # Browser instances
        self.selenium_driver: Optional[webdriver.Chrome] = None
        self.playwright_browser: Optional[Browser] = None
        self.playwright_page: Optional[Page] = None
        
        # Session state
        self.current_session: Optional[ExcelWebSession] = None
        self.is_authenticated = False
        
        # Navigation state
        self.current_url: Optional[str] = None
        self.last_action_time = datetime.now()
        
        # Screenshot management
        self.screenshot_counter = 0
        self.screenshot_dir = Path(self.config.screenshot_dir)
        self.screenshot_dir.mkdir(parents=True, exist_ok=True)
    
    async def initialize(self) -> bool:
        """
        Initialize the navigator
        
        Returns:
            bool: True if initialization successful
        """
        try:
            print("🚀 Initializing Unified Excel Web Navigator...")
            
            # Cleanup expired sessions
            await self.session_manager.cleanup_expired_sessions()
            
            # Ensure screenshot directory exists
            self.screenshot_dir.mkdir(parents=True, exist_ok=True)
            
            print("✅ Unified Excel Web Navigator initialized")
            return True
            
        except Exception as e:
            print(f"❌ Failed to initialize navigator: {e}")
            return False
    
    async def ensure_authenticated(self, method: str = "auto") -> AuthenticationResult:
        """
        Ensure we have a valid authenticated session
        
        Args:
            method: Authentication method ("auto", "manual", "selenium", "playwright")
            
        Returns:
            AuthenticationResult: Result of authentication attempt
        """
        try:
            # Check if we have a valid session
            valid_session = await self.session_manager.get_valid_session()
            
            if valid_session:
                print(f"✅ Found valid session: {valid_session.session_id}")
                
                # Restore session to browser
                if await self._restore_session_to_browser(valid_session, method):
                    self.current_session = valid_session
                    self.is_authenticated = True
                    return AuthenticationResult(
                        success=True,
                        session=valid_session,
                        message="Session restored successfully"
                    )
                else:
                    print("⚠️  Session restoration failed, will re-authenticate")
                    await self.session_manager.invalidate_session(valid_session)
            
            # No valid session, need to authenticate
            return await self._authenticate(method)
            
        except Exception as e:
            error_msg = f"Authentication check failed: {e}"
            print(f"❌ {error_msg}")
            return AuthenticationResult(
                success=False,
                error=error_msg
            )
    
    async def _authenticate(self, method: str) -> AuthenticationResult:
        """
        Perform authentication using the specified method
        
        Args:
            method: Authentication method
            
        Returns:
            AuthenticationResult: Result of authentication
        """
        try:
            if method == "selenium" or (method == "auto" and not PLAYWRIGHT_AVAILABLE):
                return await self._authenticate_selenium()
            elif method == "playwright" or (method == "auto" and PLAYWRIGHT_AVAILABLE):
                return await self._authenticate_playwright()
            elif method == "manual":
                return await self._authenticate_manual()
            else:
                # Fallback to selenium
                return await self._authenticate_selenium()
                
        except Exception as e:
            error_msg = f"Authentication failed: {e}"
            print(f"❌ {error_msg}")
            return AuthenticationResult(
                success=False,
                error=error_msg
            )
    
    async def _authenticate_selenium(self) -> AuthenticationResult:
        """Perform authentication using Selenium"""
        try:
            print("🔐 Starting Selenium authentication...")
            
            # Setup Chrome options
            chrome_options = Options()
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-blink-features=AutomationControlled")
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            
            if self.config.headless:
                chrome_options.add_argument("--headless")
            
            # Create driver
            self.selenium_driver = webdriver.Chrome(options=chrome_options)
            self.selenium_driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            # Navigate to Excel Web
            print("🌐 Navigating to Excel Web...")
            self.selenium_driver.get(self.config.base_url)
            
            # Wait for manual authentication
            session = await self._wait_for_manual_authentication_selenium()
            
            if session:
                self.current_session = session
                self.is_authenticated = True
                return AuthenticationResult(
                    success=True,
                    session=session,
                    message="Selenium authentication successful"
                )
            else:
                return AuthenticationResult(
                    success=False,
                    error="Selenium authentication timeout"
                )
                
        except Exception as e:
            error_msg = f"Selenium authentication failed: {e}"
            print(f"❌ {error_msg}")
            return AuthenticationResult(
                success=False,
                error=error_msg
            )
    
    async def _authenticate_playwright(self) -> AuthenticationResult:
        """Perform authentication using Playwright"""
        if not PLAYWRIGHT_AVAILABLE:
            return AuthenticationResult(
                success=False,
                error="Playwright not available"
            )
        
        try:
            print("🔐 Starting Playwright authentication...")
            
            # Setup Playwright
            self.playwright = await async_playwright().start()
            self.playwright_browser = await self.playwright.chromium.launch(
                headless=not self.config.headless
            )
            self.playwright_page = await self.playwright_browser.new_page()
            
            # Navigate to Excel Web
            print("🌐 Navigating to Excel Web...")
            await self.playwright_page.goto(self.config.base_url)
            
            # Wait for manual authentication
            session = await self._wait_for_manual_authentication_playwright()
            
            if session:
                self.current_session = session
                self.is_authenticated = True
                return AuthenticationResult(
                    success=True,
                    session=session,
                    message="Playwright authentication successful"
                )
            else:
                return AuthenticationResult(
                    success=False,
                    error="Playwright authentication timeout"
                )
                
        except Exception as e:
            error_msg = f"Playwright authentication failed: {e}"
            print(f"❌ {error_msg}")
            return AuthenticationResult(
                success=False,
                error=error_msg
            )
    
    async def _authenticate_manual(self) -> AuthenticationResult:
        """Perform manual authentication (hybrid approach)"""
        try:
            print("🔐 Starting manual authentication...")
            
            # Use Selenium for manual auth (most reliable for user interaction)
            return await self._authenticate_selenium()
            
        except Exception as e:
            error_msg = f"Manual authentication failed: {e}"
            print(f"❌ {error_msg}")
            return AuthenticationResult(
                success=False,
                error=error_msg
            )
    
    async def _wait_for_manual_authentication_selenium(self, timeout_minutes: int = 5) -> Optional[ExcelWebSession]:
        """Wait for manual authentication in Selenium browser"""
        try:
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
                await asyncio.sleep(5)
            
            if time.time() - start_time >= timeout_seconds:
                print("⏰ Timeout reached")
                return None
            
            # Capture session
            return await self._capture_session_selenium()
            
        except Exception as e:
            print(f"❌ Error during manual authentication: {e}")
            return None
    
    async def _wait_for_manual_authentication_playwright(self, timeout_minutes: int = 5) -> Optional[ExcelWebSession]:
        """Wait for manual authentication in Playwright browser"""
        try:
            print("\n" + "=" * 60)
            print("🔐 MANUAL AUTHENTICATION REQUIRED (Playwright)")
            print("=" * 60)
            print("Please complete the authentication process in the browser window.")
            print(f"⏱️  You have {timeout_minutes} minutes to complete authentication.")
            print("=" * 60)
            
            # Wait for user to complete authentication
            start_time = time.time()
            timeout_seconds = timeout_minutes * 60
            
            while time.time() - start_time < timeout_seconds:
                current_url = self.playwright_page.url
                print(f"Current URL: {current_url}")
                
                # Check for success indicators
                try:
                    content = await self.playwright_page.content()
                    excel_indicators = ['Excel', 'Workbook', 'New', 'OneDrive', 'Office']
                    
                    success_found = False
                    for indicator in excel_indicators:
                        if indicator in content:
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
                await asyncio.sleep(5)
            
            if time.time() - start_time >= timeout_seconds:
                print("⏰ Timeout reached")
                return None
            
            # Capture session
            return await self._capture_session_playwright()
            
        except Exception as e:
            print(f"❌ Error during manual authentication: {e}")
            return None
    
    async def _capture_session_selenium(self) -> Optional[ExcelWebSession]:
        """Capture session data from Selenium browser"""
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
            print(f"✅ Session saved: {session.session_id}")
            
            return session
            
        except Exception as e:
            print(f"❌ Failed to capture session: {e}")
            return None
    
    async def _capture_session_playwright(self) -> Optional[ExcelWebSession]:
        """Capture session data from Playwright browser"""
        try:
            if not self.playwright_page:
                return None
            
            # Create session
            session = ExcelWebSession()
            session.session_id = f"playwright_session_{int(time.time() * 1000)}"
            session.created_at = datetime.now()
            session.last_used = datetime.now()
            session.is_valid = True
            
            # Capture cookies
            try:
                cookies = await self.playwright_page.context.cookies()
                session.cookies = {cookie['name']: cookie for cookie in cookies}
                print(f"✅ Captured {len(cookies)} cookies")
            except Exception as e:
                print(f"⚠️  Failed to capture cookies: {e}")
            
            # Capture local storage
            try:
                local_storage = await self.playwright_page.evaluate("() => Object.entries(localStorage)")
                session.local_storage = dict(local_storage)
                print(f"✅ Captured {len(local_storage)} local storage items")
            except Exception as e:
                print(f"⚠️  Failed to capture local storage: {e}")
            
            # Capture session storage
            try:
                session_storage = await self.playwright_page.evaluate("() => Object.entries(sessionStorage)")
                session.session_data = dict(session_storage)
                print(f"✅ Captured {len(session_storage)} session storage items")
            except Exception as e:
                print(f"⚠️  Failed to capture session storage: {e}")
            
            # Save session
            await self.session_manager.save_session(session)
            print(f"✅ Session saved: {session.session_id}")
            
            return session
            
        except Exception as e:
            print(f"❌ Failed to capture session: {e}")
            return None
    
    async def _restore_session_to_browser(self, session: ExcelWebSession, method: str) -> bool:
        """Restore session to browser"""
        try:
            if method == "selenium" or (method == "auto" and not PLAYWRIGHT_AVAILABLE):
                return await self._restore_session_to_selenium(session)
            elif method == "playwright" or (method == "auto" and PLAYWRIGHT_AVAILABLE):
                return await self._restore_session_to_playwright(session)
            else:
                # Fallback to selenium
                return await self._restore_session_to_selenium(session)
                
        except Exception as e:
            print(f"❌ Failed to restore session: {e}")
            return False
    
    async def _restore_session_to_selenium(self, session: ExcelWebSession) -> bool:
        """Restore session to Selenium browser"""
        try:
            if not self.selenium_driver:
                # Create new driver
                chrome_options = Options()
                chrome_options.add_argument("--no-sandbox")
                chrome_options.add_argument("--disable-dev-shm-usage")
                chrome_options.add_argument("--disable-blink-features=AutomationControlled")
                chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
                chrome_options.add_experimental_option('useAutomationExtension', False)
                
                if self.config.headless:
                    chrome_options.add_argument("--headless")
                
                self.selenium_driver = webdriver.Chrome(options=chrome_options)
                self.selenium_driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            # Navigate to Excel Web
            self.selenium_driver.get(self.config.base_url)
            
            # Restore cookies
            if session.cookies:
                for cookie_name, cookie_data in session.cookies.items():
                    try:
                        self.selenium_driver.add_cookie(cookie_data)
                    except Exception as e:
                        print(f"⚠️  Failed to restore cookie {cookie_name}: {e}")
            
            # Restore local storage
            if session.local_storage:
                for key, value in session.local_storage.items():
                    try:
                        self.selenium_driver.execute_script(f"localStorage.setItem('{key}', '{value}');")
                    except Exception as e:
                        print(f"⚠️  Failed to restore localStorage {key}: {e}")
            
            # Restore session storage
            if session.session_data:
                for key, value in session.session_data.items():
                    try:
                        self.selenium_driver.execute_script(f"sessionStorage.setItem('{key}', '{value}');")
                    except Exception as e:
                        print(f"⚠️  Failed to restore sessionStorage {key}: {e}")
            
            # Refresh page to apply session data
            self.selenium_driver.refresh()
            
            # Wait for page to load
            await asyncio.sleep(2)
            
            print("✅ Session restored to Selenium browser")
            return True
            
        except Exception as e:
            print(f"❌ Failed to restore session to Selenium: {e}")
            return False
    
    async def _restore_session_to_playwright(self, session: ExcelWebSession) -> bool:
        """Restore session to Playwright browser"""
        try:
            if not self.playwright_page:
                # Create new browser and page
                self.playwright = await async_playwright().start()
                self.playwright_browser = await self.playwright.chromium.launch(
                    headless=self.config.headless
                )
                self.playwright_page = await self.playwright_browser.new_page()
            
            # Navigate to Excel Web
            await self.playwright_page.goto(self.config.base_url)
            
            # Restore cookies
            if session.cookies:
                await self.playwright_page.context.add_cookies(list(session.cookies.values()))
            
            # Restore local storage
            if session.local_storage:
                for key, value in session.local_storage.items():
                    try:
                        await self.playwright_page.evaluate(f"localStorage.setItem('{key}', '{value}');")
                    except Exception as e:
                        print(f"⚠️  Failed to restore localStorage {key}: {e}")
            
            # Restore session storage
            if session.session_data:
                for key, value in session.session_data.items():
                    try:
                        await self.playwright_page.evaluate(f"sessionStorage.setItem('{key}', '{value}');")
                    except Exception as e:
                        print(f"⚠️  Failed to restore sessionStorage {key}: {e}")
            
            # Refresh page to apply session data
            await self.playwright_page.reload()
            
            # Wait for page to load
            await asyncio.sleep(2)
            
            print("✅ Session restored to Playwright browser")
            return True
            
        except Exception as e:
            print(f"❌ Failed to restore session to Playwright: {e}")
            return False
    
    async def take_screenshot(self, reason: str = "debug") -> Optional[str]:
        """
        Take a screenshot of the current browser state
        
        Args:
            reason: Reason for taking screenshot
            
        Returns:
            Optional[str]: Path to screenshot file
        """
        try:
            self.screenshot_counter += 1
            timestamp = int(time.time())
            filename = f"excel_{reason}_{timestamp}_{self.screenshot_counter}.png"
            filepath = self.screenshot_dir / filename
            
            if self.selenium_driver:
                self.selenium_driver.save_screenshot(str(filepath))
            elif self.playwright_page:
                await self.playwright_page.screenshot(path=str(filepath))
            else:
                print("⚠️  No browser instance available for screenshot")
                return None
            
            print(f"📸 Screenshot saved: {filepath}")
            return str(filepath)
            
        except Exception as e:
            print(f"❌ Failed to take screenshot: {e}")
            return None
    
    async def close(self):
        """Close browser instances and cleanup"""
        try:
            if self.selenium_driver:
                self.selenium_driver.quit()
                self.selenium_driver = None
            
            if self.playwright_page:
                await self.playwright_page.close()
                self.playwright_page = None
            
            if self.playwright_browser:
                await self.playwright_browser.close()
                self.playwright_browser = None
            
            if hasattr(self, 'playwright'):
                await self.playwright.stop()
            
            print("✅ Browser instances closed")
            
        except Exception as e:
            print(f"⚠️  Error during cleanup: {e}")


# Global instance for backward compatibility
_unified_navigator: Optional[UnifiedExcelNavigator] = None


async def get_unified_navigator() -> UnifiedExcelNavigator:
    """
    Get the global unified navigator instance
    
    Returns:
        UnifiedExcelNavigator: Global navigator instance
    """
    global _unified_navigator
    if _unified_navigator is None:
        _unified_navigator = UnifiedExcelNavigator()
        await _unified_navigator.initialize()
    return _unified_navigator


# Backward compatibility aliases
SeleniumExcelWebNavigator = UnifiedExcelNavigator
ExcelWebNavigator = UnifiedExcelNavigator
