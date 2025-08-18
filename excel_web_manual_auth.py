"""
Excel Web Manual Authentication Module
Handles manual authentication flow for biometric/passkey authentication
"""

import asyncio
import time
from typing import Optional, Dict, Any
from playwright.async_api import Page, Browser
from excel_web_config import get_excel_web_config
from excel_web_session import SessionManager, ExcelWebSession


class ManualAuthenticationManager:
    """Manages manual authentication flow for Excel Web"""
    
    def __init__(self):
        self.config = get_excel_web_config()
        self.session_manager = SessionManager()
        self.browser: Optional[Browser] = None
        self.page: Optional[Page] = None
    
    async def setup_browser_for_manual_auth(self) -> bool:
        """Setup browser for manual authentication"""
        try:
            from playwright.async_api import async_playwright
            
            self.playwright = await async_playwright().start()
            
            # Launch browser in non-headless mode so user can see it
            self.browser = await self.playwright.chromium.launch(
                headless=False,  # Always show browser for manual auth
                args=[
                    '--no-sandbox',
                    '--disable-dev-shm-usage',
                    '--disable-web-security',
                    '--disable-features=VizDisplayCompositor',
                    '--disable-blink-features=AutomationControlled'
                ]
            )
            
            self.page = await self.browser.new_page()
            self.page.set_default_timeout(self.config.page_load_timeout_seconds * 1000)
            
            print("✅ Browser setup for manual authentication")
            return True
            
        except Exception as e:
            print(f"❌ Failed to setup browser: {e}")
            return False
    
    async def navigate_to_excel_web(self) -> bool:
        """Navigate to Excel Web for manual authentication"""
        try:
            print(f"🌐 Navigating to Excel Web: {self.config.excel_web_url}")
            await self.page.goto(self.config.excel_web_url)
            await self.page.wait_for_load_state('networkidle')
            print("✅ Successfully navigated to Excel Web")
            return True
            
        except Exception as e:
            print(f"❌ Failed to navigate to Excel Web: {e}")
            return False
    
    async def wait_for_manual_authentication(self, timeout_minutes: int = 5) -> bool:
        """Wait for user to complete manual authentication"""
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
                # Check if we're successfully authenticated
                if await self.verify_authentication_success():
                    print("\n✅ Manual authentication completed successfully!")
                    return True
                
                # Wait a bit before checking again
                await asyncio.sleep(2)
            
            print(f"\n⏰ Timeout reached ({timeout_minutes} minutes)")
            print("❌ Manual authentication timeout")
            return False
            
        except Exception as e:
            print(f"❌ Error during manual authentication: {e}")
            return False
    
    async def verify_authentication_success(self) -> bool:
        """Verify that authentication was successful"""
        try:
            # Check for common success indicators
            success_indicators = [
                'text=Excel',
                'text=Workbook',
                'text=New',
                '[data-testid="excel-app"]',
                '.excel-app',
                'text=OneDrive',
                'text=Office'
            ]
            
            for indicator in success_indicators:
                try:
                    await self.page.wait_for_selector(indicator, timeout=2000)
                    return True
                except:
                    continue
            
            # Check if we're still on login page (failure indicator)
            failure_indicators = [
                'text=Sign in',
                'text=Login',
                'input[type="password"]',
                'text=Enter your password'
            ]
            
            for indicator in failure_indicators:
                try:
                    await self.page.wait_for_selector(indicator, timeout=1000)
                    return False
                except:
                    continue
            
            # If we can't determine, check URL
            current_url = self.page.url
            if 'login.microsoftonline.com' in current_url or 'login.live.com' in current_url:
                return False
            
            # If we're on Excel Web or Office, assume success
            if 'excel.office.com' in current_url or 'office.com' in current_url:
                return True
            
            return False
            
        except Exception as e:
            print(f"⚠️  Authentication verification error: {e}")
            return False
    
    async def capture_session_after_auth(self) -> Optional[ExcelWebSession]:
        """Capture session data after successful authentication"""
        try:
            if not self.page:
                return None
            
            # Create new session
            session = await self.session_manager.create_session(self.page)
            
            print(f"✅ Session captured: {session.session_id}")
            return session
            
        except Exception as e:
            print(f"❌ Failed to capture session: {e}")
            return None
    
    async def close_browser(self):
        """Close browser and cleanup"""
        try:
            if self.page:
                await self.page.close()
            if self.browser:
                await self.browser.close()
            if hasattr(self, 'playwright'):
                await self.playwright.stop()
            print("✅ Browser closed")
        except Exception as e:
            print(f"⚠️  Error during browser cleanup: {e}")


class ExcelWebManualAuth:
    """Main class for Excel Web manual authentication"""
    
    def __init__(self):
        self.auth_manager = ManualAuthenticationManager()
        self.session_manager = SessionManager()
    
    async def perform_manual_authentication(self, timeout_minutes: int = 5) -> Optional[ExcelWebSession]:
        """Perform complete manual authentication flow"""
        try:
            print("🚀 Starting Excel Web Manual Authentication...")
            
            # Setup browser
            if not await self.auth_manager.setup_browser_for_manual_auth():
                return None
            
            # Navigate to Excel Web
            if not await self.auth_manager.navigate_to_excel_web():
                return None
            
            # Wait for manual authentication
            if not await self.auth_manager.wait_for_manual_authentication(timeout_minutes):
                return None
            
            # Capture session
            session = await self.auth_manager.capture_session_after_auth()
            
            if session:
                print("🎉 Manual authentication completed successfully!")
                print(f"📋 Session ID: {session.session_id}")
                return session
            else:
                print("❌ Failed to capture session after authentication")
                return None
                
        except Exception as e:
            print(f"❌ Manual authentication failed: {e}")
            return None
        finally:
            # Keep browser open for a moment so user can see the result
            print("⏳ Keeping browser open for 5 seconds...")
            await asyncio.sleep(5)
            await self.auth_manager.close_browser()
    
    async def verify_existing_session(self) -> Optional[ExcelWebSession]:
        """Check if we have a valid existing session"""
        try:
            valid_session = await self.session_manager.get_valid_session()
            if valid_session:
                print(f"✅ Found valid existing session: {valid_session.session_id}")
                return valid_session
            else:
                print("ℹ️  No valid session found")
                return None
        except Exception as e:
            print(f"❌ Error checking existing session: {e}")
            return None


# Global instance
manual_auth = ExcelWebManualAuth()


async def get_manual_auth() -> ExcelWebManualAuth:
    """Get the global manual authentication instance"""
    return manual_auth
