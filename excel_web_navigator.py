"""
Excel Web Navigator Module
Main navigation and automation class for Excel Web
"""

import asyncio
import time
from typing import Optional, Dict, Any, Tuple
from playwright.async_api import Page, Browser
from excel_web_config import get_excel_web_config
from excel_web_auth import ExcelWebAuthenticator, InteractiveCredentialManager
from excel_web_session import SessionManager, ExcelWebSession
from excel_web_manual_auth import get_manual_auth


class ExcelWebNavigator:
    """Main navigator class for Excel Web automation"""
    
    def __init__(self):
        self.config = get_excel_web_config()
        self.authenticator = ExcelWebAuthenticator()
        self.credential_manager = InteractiveCredentialManager()
        self.session_manager = SessionManager()
        self.current_session: Optional[ExcelWebSession] = None
        self.is_authenticated = False
    
    async def initialize(self) -> bool:
        """Initialize the navigator"""
        try:
            print("🚀 Initializing Excel Web Navigator...")
            
            # Setup browser
            await self.authenticator.setup_browser()
            
            # Cleanup expired sessions
            await self.session_manager.cleanup_expired_sessions()
            
            print("✅ Excel Web Navigator initialized")
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
                if not self.authenticator.page:
                    await self.authenticator.create_page()
                
                if await self.session_manager.restore_session(self.authenticator.page, valid_session):
                    # Verify session is still valid by navigating to Excel Web
                    if await self.authenticator.navigate_to_excel_web():
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
        """Perform full authentication flow"""
        try:
            print("🔐 Starting authentication flow...")
            
            # Check if we should use manual authentication
            print("🤔 Checking authentication method...")
            print("   For biometric/passkey authentication, manual login is required.")
            print("   For username/password authentication, automated login will be used.")
            
            # Ask user for preference
            auth_method = input("Choose authentication method (manual/auto): ").strip().lower()
            
            if auth_method == "manual" or auth_method == "m":
                print("🔐 Using manual authentication...")
                return await self.authenticate_manually()
            else:
                print("🔐 Using automated authentication...")
                return await self.authenticate_automated()
                
        except Exception as e:
            print(f"❌ Authentication failed: {e}")
            return False
    
    async def authenticate_manually(self) -> bool:
        """Perform manual authentication flow"""
        try:
            manual_auth_instance = await get_manual_auth()
            
            # Perform manual authentication
            session = await manual_auth_instance.perform_manual_authentication(timeout_minutes=5)
            
            if session:
                self.current_session = session
                self.is_authenticated = True
                print("✅ Manual authentication successful")
                return True
            else:
                print("❌ Manual authentication failed")
                return False
                
        except Exception as e:
            print(f"❌ Manual authentication failed: {e}")
            return False
    
    async def authenticate_automated(self) -> bool:
        """Perform automated authentication flow"""
        try:
            # Get credentials interactively
            username, password = await self.credential_manager.get_credentials_interactive()
            
            # Validate credentials format
            if not self.credential_manager.validate_credentials(username, password):
                print("❌ Invalid credentials format")
                return False
            
            # Perform login
            if await self.authenticator.login_to_excel_web(username, password):
                # Create new session
                if self.authenticator.page:
                    self.current_session = await self.session_manager.create_session(self.authenticator.page)
                    self.is_authenticated = True
                    print("✅ Automated authentication successful")
                    return True
                else:
                    print("❌ No browser page available after login")
                    return False
            else:
                print("❌ Automated login failed")
                return False
                
        except Exception as e:
            print(f"❌ Automated authentication failed: {e}")
            return False
    
    async def navigate_to_excel_web(self) -> bool:
        """Navigate to Excel Web with authentication"""
        try:
            if not await self.ensure_authenticated():
                return False
            
            return await self.authenticator.navigate_to_excel_web()
            
        except Exception as e:
            print(f"❌ Navigation failed: {e}")
            return False
    
    async def wait_for_element(self, selector: str, timeout: int = 10) -> bool:
        """Wait for an element to appear on the page"""
        try:
            if not self.authenticator.page:
                return False
            
            await self.authenticator.page.wait_for_selector(selector, timeout=timeout * 1000)
            return True
            
        except Exception as e:
            print(f"⚠️  Element not found: {selector} - {e}")
            return False
    
    async def click_element(self, selector: str, timeout: int = 10) -> bool:
        """Click an element on the page"""
        try:
            if not self.authenticator.page:
                return False
            
            if await self.wait_for_element(selector, timeout):
                await self.authenticator.page.click(selector)
                print(f"✅ Clicked element: {selector}")
                return True
            else:
                print(f"❌ Element not found for clicking: {selector}")
                return False
                
        except Exception as e:
            print(f"❌ Failed to click element {selector}: {e}")
            return False
    
    async def fill_input(self, selector: str, value: str, timeout: int = 10) -> bool:
        """Fill an input field"""
        try:
            if not self.authenticator.page:
                return False
            
            if await self.wait_for_element(selector, timeout):
                await self.authenticator.page.fill(selector, value)
                print(f"✅ Filled input {selector}: {value}")
                return True
            else:
                print(f"❌ Input element not found: {selector}")
                return False
                
        except Exception as e:
            print(f"❌ Failed to fill input {selector}: {e}")
            return False
    
    async def take_screenshot(self, name: str = "screenshot") -> Optional[str]:
        """Take a screenshot of the current page"""
        try:
            if not self.authenticator.page:
                return None
            
            timestamp = int(time.time())
            filename = f"{name}_{timestamp}.png"
            filepath = f"{self.config.screenshot_dir}/{filename}"
            
            await self.authenticator.page.screenshot(path=filepath)
            print(f"📸 Screenshot saved: {filepath}")
            return filepath
            
        except Exception as e:
            print(f"❌ Failed to take screenshot: {e}")
            return None
    
    async def get_page_title(self) -> str:
        """Get the current page title"""
        try:
            if not self.authenticator.page:
                return ""
            
            return await self.authenticator.page.title()
            
        except Exception as e:
            print(f"❌ Failed to get page title: {e}")
            return ""
    
    async def get_page_url(self) -> str:
        """Get the current page URL"""
        try:
            if not self.authenticator.page:
                return ""
            
            return self.authenticator.page.url
            
        except Exception as e:
            print(f"❌ Failed to get page URL: {e}")
            return ""
    
    async def wait_for_page_load(self, timeout: int = 30) -> bool:
        """Wait for page to fully load"""
        try:
            if not self.authenticator.page:
                return False
            
            await self.authenticator.page.wait_for_load_state('networkidle', timeout=timeout * 1000)
            return True
            
        except Exception as e:
            print(f"❌ Page load timeout: {e}")
            return False
    
    async def refresh_page(self) -> bool:
        """Refresh the current page"""
        try:
            if not self.authenticator.page:
                return False
            
            await self.authenticator.page.reload()
            await self.wait_for_page_load()
            print("✅ Page refreshed")
            return True
            
        except Exception as e:
            print(f"❌ Failed to refresh page: {e}")
            return False
    
    async def close(self):
        """Close the navigator and cleanup"""
        try:
            # Clear credentials
            self.credential_manager.clear_credentials()
            
            # Close browser
            await self.authenticator.close_browser()
            
            print("✅ Excel Web Navigator closed")
            
        except Exception as e:
            print(f"⚠️  Error during cleanup: {e}")


# Global navigator instance
excel_web_navigator = ExcelWebNavigator()


async def get_excel_web_navigator() -> ExcelWebNavigator:
    """Get the global Excel Web navigator"""
    return excel_web_navigator
