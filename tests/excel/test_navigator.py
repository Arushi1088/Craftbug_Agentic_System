"""
Tests for the unified Excel navigator system.
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from src.excel.core.navigator import (
    UnifiedExcelNavigator,
    NavigationResult,
    AuthenticationResult,
    get_unified_navigator
)
from src.excel.core.session import ExcelWebSession, SessionManager
from src.excel.core.config import get_config


class TestUnifiedExcelNavigator:
    """Test the unified Excel navigator"""
    
    @pytest.fixture
    def navigator(self):
        """Create a navigator instance for testing"""
        return UnifiedExcelNavigator()
    
    def test_navigator_initialization(self, navigator):
        """Test that navigator initializes correctly"""
        assert navigator.config is not None
        assert navigator.session_manager is not None
        assert navigator.selenium_driver is None
        assert navigator.playwright_browser is None
        assert navigator.current_session is None
        assert navigator.is_authenticated is False
        assert navigator.screenshot_dir.exists()
    
    @pytest.mark.asyncio
    async def test_navigator_initialize(self, navigator):
        """Test navigator initialization"""
        result = await navigator.initialize()
        assert result is True
    
    @pytest.mark.asyncio
    async def test_ensure_authenticated_no_session(self, navigator):
        """Test authentication when no valid session exists"""
        with patch.object(navigator.session_manager, 'get_valid_session', return_value=None):
            with patch.object(navigator, '_authenticate') as mock_authenticate:
                mock_authenticate.return_value = AuthenticationResult(
                    success=True,
                    session=ExcelWebSession(),
                    message="Authentication successful"
                )
                
                result = await navigator.ensure_authenticated()
                
                assert result.success is True
                assert result.session is not None
                assert result.message == "Authentication successful"
                mock_authenticate.assert_called_once_with("auto")
    
    @pytest.mark.asyncio
    async def test_ensure_authenticated_with_valid_session(self, navigator):
        """Test authentication with valid session"""
        mock_session = ExcelWebSession()
        mock_session.session_id = "test_session"
        
        with patch.object(navigator.session_manager, 'get_valid_session', return_value=mock_session):
            with patch.object(navigator, '_restore_session_to_browser', return_value=True):
                result = await navigator.ensure_authenticated()
                
                assert result.success is True
                assert result.session == mock_session
                assert result.message == "Session restored successfully"
                assert navigator.current_session == mock_session
                assert navigator.is_authenticated is True
    
    @pytest.mark.asyncio
    async def test_ensure_authenticated_session_restore_fails(self, navigator):
        """Test authentication when session restoration fails"""
        mock_session = ExcelWebSession()
        mock_session.session_id = "test_session"
        
        with patch.object(navigator.session_manager, 'get_valid_session', return_value=mock_session):
            with patch.object(navigator, '_restore_session_to_browser', return_value=False):
                with patch.object(navigator.session_manager, 'invalidate_session') as mock_invalidate:
                    with patch.object(navigator, '_authenticate') as mock_authenticate:
                        mock_authenticate.return_value = AuthenticationResult(
                            success=True,
                            session=ExcelWebSession(),
                            message="Re-authentication successful"
                        )
                        
                        result = await navigator.ensure_authenticated()
                        
                        assert result.success is True
                        mock_invalidate.assert_called_once_with(mock_session)
                        mock_authenticate.assert_called_once_with("auto")
    
    @pytest.mark.asyncio
    async def test_authenticate_selenium(self, navigator):
        """Test Selenium authentication"""
        with patch('selenium.webdriver.Chrome') as mock_chrome:
            with patch.object(navigator, '_wait_for_manual_authentication_selenium') as mock_wait:
                mock_session = ExcelWebSession()
                mock_wait.return_value = mock_session
                
                result = await navigator._authenticate_selenium()
                
                assert result.success is True
                assert result.session == mock_session
                assert result.message == "Selenium authentication successful"
                assert navigator.selenium_driver is not None
                assert navigator.current_session == mock_session
                assert navigator.is_authenticated is True
    
    @pytest.mark.asyncio
    async def test_authenticate_selenium_timeout(self, navigator):
        """Test Selenium authentication timeout"""
        with patch('selenium.webdriver.Chrome') as mock_chrome:
            with patch.object(navigator, '_wait_for_manual_authentication_selenium', return_value=None):
                result = await navigator._authenticate_selenium()
                
                assert result.success is False
                assert result.error == "Selenium authentication timeout"
    
    @pytest.mark.asyncio
    async def test_take_screenshot_selenium(self, navigator):
        """Test taking screenshot with Selenium"""
        with patch('selenium.webdriver.Chrome') as mock_chrome:
            mock_driver = Mock()
            mock_driver.save_screenshot = Mock()
            navigator.selenium_driver = mock_driver
            
            result = await navigator.take_screenshot("test")
            
            assert result is not None
            assert "excel_test_" in result
            assert result.endswith(".png")
            mock_driver.save_screenshot.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_take_screenshot_no_browser(self, navigator):
        """Test taking screenshot when no browser is available"""
        result = await navigator.take_screenshot("test")
        assert result is None
    
    @pytest.mark.asyncio
    async def test_close_selenium(self, navigator):
        """Test closing Selenium browser"""
        mock_driver = Mock()
        mock_driver.quit = Mock()
        navigator.selenium_driver = mock_driver
        
        await navigator.close()
        
        mock_driver.quit.assert_called_once()
        assert navigator.selenium_driver is None
    
    @pytest.mark.asyncio
    async def test_close_playwright(self, navigator):
        """Test closing Playwright browser"""
        mock_page = AsyncMock()
        mock_browser = AsyncMock()
        mock_playwright = AsyncMock()
        
        navigator.playwright_page = mock_page
        navigator.playwright_browser = mock_browser
        navigator.playwright = mock_playwright
        
        await navigator.close()
        
        mock_page.close.assert_called_once()
        mock_browser.close.assert_called_once()
        mock_playwright.stop.assert_called_once()
        assert navigator.playwright_page is None
        assert navigator.playwright_browser is None


class TestGlobalNavigator:
    """Test global navigator functions"""
    
    @pytest.mark.asyncio
    async def test_get_unified_navigator(self):
        """Test getting the global navigator instance"""
        # Reset global instance
        import src.excel.core.navigator as nav_module
        nav_module._unified_navigator = None
        
        navigator1 = await get_unified_navigator()
        navigator2 = await get_unified_navigator()
        
        # Should return the same instance
        assert navigator1 is navigator2
        assert isinstance(navigator1, UnifiedExcelNavigator)


class TestBackwardCompatibility:
    """Test backward compatibility aliases"""
    
    def test_backward_compatibility_aliases(self):
        """Test that backward compatibility aliases work"""
        from src.excel.core.navigator import SeleniumExcelWebNavigator, ExcelWebNavigator
        
        # These should be the same class
        assert SeleniumExcelWebNavigator is UnifiedExcelNavigator
        assert ExcelWebNavigator is UnifiedExcelNavigator


class TestNavigationResult:
    """Test NavigationResult dataclass"""
    
    def test_navigation_result_creation(self):
        """Test creating NavigationResult"""
        result = NavigationResult(
            success=True,
            message="Test message",
            data={"key": "value"},
            screenshot_path="/path/to/screenshot.png"
        )
        
        assert result.success is True
        assert result.message == "Test message"
        assert result.data == {"key": "value"}
        assert result.screenshot_path == "/path/to/screenshot.png"
        assert result.error is None
    
    def test_navigation_result_with_error(self):
        """Test NavigationResult with error"""
        result = NavigationResult(
            success=False,
            message="Test error",
            error="Something went wrong"
        )
        
        assert result.success is False
        assert result.message == "Test error"
        assert result.error == "Something went wrong"
        assert result.data is None
        assert result.screenshot_path is None


class TestAuthenticationResult:
    """Test AuthenticationResult dataclass"""
    
    def test_authentication_result_creation(self):
        """Test creating AuthenticationResult"""
        session = ExcelWebSession()
        result = AuthenticationResult(
            success=True,
            session=session,
            message="Authentication successful"
        )
        
        assert result.success is True
        assert result.session == session
        assert result.message == "Authentication successful"
        assert result.error is None
    
    def test_authentication_result_with_error(self):
        """Test AuthenticationResult with error"""
        result = AuthenticationResult(
            success=False,
            message="Authentication failed",
            error="Invalid credentials"
        )
        
        assert result.success is False
        assert result.message == "Authentication failed"
        assert result.error == "Invalid credentials"
        assert result.session is None


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])
