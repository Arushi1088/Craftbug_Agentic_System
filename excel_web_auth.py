"""
Excel Web Authentication Module
Handles interactive credential management and authentication flow
"""

import asyncio
import getpass
from typing import Optional, Dict, Any, Tuple
from playwright.async_api import async_playwright, Browser, Page
from excel_web_config import get_excel_web_config, get_excel_web_credentials


class InteractiveCredentialManager:
    """Manages interactive credential input for Excel Web"""
    
    def __init__(self):
        self.config = get_excel_web_config()
        self.credentials = get_excel_web_credentials()
    
    async def get_credentials_interactive(self) -> Tuple[str, str]:
        """Get credentials interactively from user"""
        print("\n=== Excel Web Authentication ===")
        print("Please enter your Excel Web credentials:")
        
        username = input("Username/Email: ").strip()
        password = getpass.getpass("Password: ").strip()
        
        if not username or not password:
            raise ValueError("Username and password are required")
        
        # Store credentials in memory
        self.credentials.set_credentials(username, password)
        
        print("✅ Credentials captured successfully")
        return username, password
    
    def validate_credentials(self, username: str, password: str) -> bool:
        """Basic validation of credentials format"""
        if not username or not password:
            return False
        
        # Basic email format validation
        if '@' not in username:
            print("⚠️  Warning: Username should be an email address")
            return False
        
        if len(password) < 6:
            print("⚠️  Warning: Password seems too short")
            return False
        
        return True
    
    def clear_credentials(self):
        """Clear stored credentials"""
        self.credentials.clear_credentials()
        print("✅ Credentials cleared from memory")


class ExcelWebAuthenticator:
    """Handles Excel Web authentication flow"""
    
    def __init__(self):
        self.config = get_excel_web_config()
        self.credentials = get_excel_web_credentials()
        self.browser: Optional[Browser] = None
        self.page: Optional[Page] = None
    
    async def setup_browser(self) -> Browser:
        """Setup browser for Excel Web automation"""
        self.playwright = await async_playwright().start()
        
        self.browser = await self.playwright.chromium.launch(
            headless=self.config.headless,
            args=[
                '--no-sandbox',
                '--disable-dev-shm-usage',
                '--disable-web-security',
                '--disable-features=VizDisplayCompositor'
            ]
        )
        
        return self.browser
    
    async def create_page(self) -> Page:
        """Create a new page for Excel Web"""
        if not self.browser:
            await self.setup_browser()
        
        self.page = await self.browser.new_page()
        
        # Set timeouts
        self.page.set_default_timeout(self.config.page_load_timeout_seconds * 1000)
        
        return self.page
    
    async def navigate_to_excel_web(self) -> bool:
        """Navigate to Excel Web"""
        try:
            if not self.page:
                await self.create_page()
            
            print(f"🌐 Navigating to Excel Web: {self.config.excel_web_url}")
            await self.page.goto(self.config.excel_web_url)
            
            # Wait for page to load
            await self.page.wait_for_load_state('networkidle')
            
            print("✅ Successfully navigated to Excel Web")
            return True
            
        except Exception as e:
            print(f"❌ Failed to navigate to Excel Web: {e}")
            return False
    
    async def login_to_excel_web(self, username: str, password: str) -> bool:
        """Login to Excel Web with provided credentials"""
        try:
            if not self.page:
                await self.create_page()
            
            print("🔐 Starting Excel Web login process...")
            
            # Navigate to Excel Web first
            await self.navigate_to_excel_web()
            
            # Look for login button or sign-in link
            login_selectors = [
                'a[href*="login"]',
                'button:has-text("Sign in")',
                'button:has-text("Login")',
                '[data-testid="signin-button"]',
                '.signin-button'
            ]
            
            login_button = None
            for selector in login_selectors:
                try:
                    login_button = await self.page.wait_for_selector(selector, timeout=5000)
                    if login_button:
                        break
                except:
                    continue
            
            if login_button:
                await login_button.click()
                print("✅ Clicked login button")
            else:
                print("ℹ️  No login button found, proceeding with direct login")
            
            # Wait for login page to load
            await self.page.wait_for_load_state('networkidle')
            
            # Fill in username
            username_selectors = [
                'input[type="email"]',
                'input[name="loginfmt"]',
                'input[placeholder*="email"]',
                'input[placeholder*="Email"]'
            ]
            
            username_input = None
            for selector in username_selectors:
                try:
                    username_input = await self.page.wait_for_selector(selector, timeout=5000)
                    if username_input:
                        break
                except:
                    continue
            
            if username_input:
                await username_input.fill(username)
                print("✅ Entered username")
            else:
                print("❌ Could not find username input field")
                return False
            
            # Click Next or continue
            next_selectors = [
                'input[type="submit"]',
                'button:has-text("Next")',
                'button:has-text("Continue")',
                'input[value="Next"]'
            ]
            
            next_button = None
            for selector in next_selectors:
                try:
                    next_button = await self.page.wait_for_selector(selector, timeout=5000)
                    if next_button:
                        break
                except:
                    continue
            
            if next_button:
                await next_button.click()
                print("✅ Clicked Next button")
            
            # Wait for password page
            await self.page.wait_for_load_state('networkidle')
            
            # Fill in password
            password_selectors = [
                'input[type="password"]',
                'input[name="passwd"]',
                'input[placeholder*="password"]',
                'input[placeholder*="Password"]'
            ]
            
            password_input = None
            for selector in password_selectors:
                try:
                    password_input = await self.page.wait_for_selector(selector, timeout=5000)
                    if password_input:
                        break
                except:
                    continue
            
            if password_input:
                await password_input.fill(password)
                print("✅ Entered password")
            else:
                print("❌ Could not find password input field")
                return False
            
            # Click Sign in
            signin_selectors = [
                'input[type="submit"]',
                'button:has-text("Sign in")',
                'button:has-text("Login")',
                'input[value="Sign in"]'
            ]
            
            signin_button = None
            for selector in signin_selectors:
                try:
                    signin_button = await self.page.wait_for_selector(selector, timeout=5000)
                    if signin_button:
                        break
                except:
                    continue
            
            if signin_button:
                await signin_button.click()
                print("✅ Clicked Sign in button")
            
            # Wait for login to complete
            await self.page.wait_for_load_state('networkidle')
            
            # Check if login was successful
            if await self.verify_login_success():
                print("✅ Successfully logged into Excel Web")
                return True
            else:
                print("❌ Login verification failed")
                return False
                
        except Exception as e:
            print(f"❌ Login failed: {e}")
            return False
    
    async def verify_login_success(self) -> bool:
        """Verify that login was successful"""
        try:
            # Wait a bit for redirect to complete
            await asyncio.sleep(3)
            
            # Check for common success indicators
            success_indicators = [
                'text=Excel',
                'text=Workbook',
                'text=New',
                '[data-testid="excel-app"]',
                '.excel-app'
            ]
            
            for indicator in success_indicators:
                try:
                    await self.page.wait_for_selector(indicator, timeout=5000)
                    return True
                except:
                    continue
            
            # Check if we're still on login page (failure indicator)
            failure_indicators = [
                'text=Sign in',
                'text=Login',
                'input[type="password"]'
            ]
            
            for indicator in failure_indicators:
                try:
                    await self.page.wait_for_selector(indicator, timeout=2000)
                    return False
                except:
                    continue
            
            # If we can't determine, assume success
            return True
            
        except Exception as e:
            print(f"⚠️  Login verification error: {e}")
            return False
    
    async def close_browser(self):
        """Close browser and cleanup"""
        if self.page:
            await self.page.close()
        if self.browser:
            await self.browser.close()
        if hasattr(self, 'playwright'):
            await self.playwright.stop()
        print("✅ Browser closed")


# Global instances
credential_manager = InteractiveCredentialManager()
authenticator = ExcelWebAuthenticator()


async def get_excel_web_authenticator() -> ExcelWebAuthenticator:
    """Get the global Excel Web authenticator"""
    return authenticator


async def get_credential_manager() -> InteractiveCredentialManager:
    """Get the global credential manager"""
    return credential_manager
