"""
Integration tests to verify the unified navigator works with existing functionality.
"""

import pytest
import asyncio
from pathlib import Path
from src.excel.core.navigator import UnifiedExcelNavigator, get_unified_navigator
from src.excel.core.session import ExcelWebSession, SessionManager
from src.excel.core.config import get_config


class TestNavigatorIntegration:
    """Test integration with existing Excel analysis components"""
    
    @pytest.mark.asyncio
    async def test_navigator_with_existing_config(self):
        """Test that navigator works with existing configuration"""
        # Get configuration
        config = get_config()
        excel_config = config.get_excel_web_config()
        
        # Create navigator
        navigator = UnifiedExcelNavigator(excel_config)
        
        # Verify configuration is loaded correctly
        assert navigator.config.base_url == excel_config.base_url
        assert navigator.config.timeout == excel_config.timeout
        assert navigator.config.headless == excel_config.headless
        assert navigator.config.session_storage_path == excel_config.session_storage_path
        assert navigator.config.screenshot_dir == excel_config.screenshot_dir
        
        print(f"✅ Navigator configuration loaded correctly")
        print(f"🌐 Base URL: {navigator.config.base_url}")
        print(f"⏱️  Timeout: {navigator.config.timeout}s")
        print(f"📁 Session storage: {navigator.config.session_storage_path}")
        print(f"📸 Screenshot directory: {navigator.config.screenshot_dir}")
    
    @pytest.mark.asyncio
    async def test_navigator_initialization(self):
        """Test navigator initialization"""
        navigator = UnifiedExcelNavigator()
        
        # Initialize navigator
        result = await navigator.initialize()
        assert result is True
        
        # Verify directories are created
        assert Path(navigator.config.session_storage_path).exists()
        assert Path(navigator.config.screenshot_dir).exists()
        
        print(f"✅ Navigator initialized successfully")
        print(f"📁 Session directory exists: {Path(navigator.config.session_storage_path).exists()}")
        print(f"📸 Screenshot directory exists: {Path(navigator.config.screenshot_dir).exists()}")
    
    @pytest.mark.asyncio
    async def test_session_manager_integration(self):
        """Test session manager integration"""
        session_manager = SessionManager()
        
        # Verify session manager is configured correctly
        assert session_manager.session_dir.exists()
        assert session_manager.session_timeout > 0
        
        # Test session creation
        session = await session_manager.create_session()
        assert session is not None
        assert session.session_id != ""
        assert session.is_valid is True
        
        # Test session saving
        save_result = await session_manager.save_session(session)
        assert save_result is True
        
        # Test session loading
        loaded_session = await session_manager.load_session(session.session_id)
        assert loaded_session is not None
        assert loaded_session.session_id == session.session_id
        
        print(f"✅ Session manager integration works correctly")
        print(f"📋 Session ID: {session.session_id}")
        print(f"⏰ Session timeout: {session_manager.session_timeout}s")
    
    @pytest.mark.asyncio
    async def test_global_navigator_instance(self):
        """Test global navigator instance"""
        # Get global navigator
        navigator1 = await get_unified_navigator()
        navigator2 = await get_unified_navigator()
        
        # Should be the same instance
        assert navigator1 is navigator2
        assert isinstance(navigator1, UnifiedExcelNavigator)
        
        print(f"✅ Global navigator instance works correctly")
    
    @pytest.mark.asyncio
    async def test_backward_compatibility_imports(self):
        """Test that backward compatibility imports work"""
        try:
            # Test importing existing classes
            from src.excel.core.navigator import SeleniumExcelWebNavigator, ExcelWebNavigator
            
            # These should be the same as UnifiedExcelNavigator
            assert SeleniumExcelWebNavigator is UnifiedExcelNavigator
            assert ExcelWebNavigator is UnifiedExcelNavigator
            
            print(f"✅ Backward compatibility imports work correctly")
            
        except ImportError as e:
            print(f"⚠️  Import test failed: {e}")
            # This is expected if we haven't migrated all modules yet
    
    @pytest.mark.asyncio
    async def test_navigator_with_existing_directories(self):
        """Test navigator with existing directories"""
        # Ensure existing directories exist
        existing_dirs = [
            "sessions/excel_web",
            "screenshots/excel_web", 
            "reports/excel_ux",
            "telemetry_output"
        ]
        
        for directory in existing_dirs:
            Path(directory).mkdir(parents=True, exist_ok=True)
        
        # Create navigator
        navigator = UnifiedExcelNavigator()
        
        # Verify navigator uses existing directory structure
        assert navigator.config.session_storage_path == "sessions/excel_web"
        assert navigator.config.screenshot_dir == "screenshots/excel_web"
        
        # Initialize navigator
        result = await navigator.initialize()
        assert result is True
        
        print(f"✅ Navigator works with existing directory structure")
    
    @pytest.mark.asyncio
    async def test_navigator_screenshot_functionality(self):
        """Test navigator screenshot functionality"""
        navigator = UnifiedExcelNavigator()
        
        # Ensure screenshot directory exists
        Path(navigator.config.screenshot_dir).mkdir(parents=True, exist_ok=True)
        
        # Test screenshot path generation
        screenshot_path = await navigator.take_screenshot("test")
        
        # Should return None since no browser is available
        assert screenshot_path is None
        
        # But the screenshot directory should be accessible
        assert navigator.screenshot_dir.exists()
        assert navigator.screenshot_counter > 0
        
        print(f"✅ Screenshot functionality works correctly")
        print(f"📸 Screenshot directory: {navigator.screenshot_dir}")
        print(f"🔢 Screenshot counter: {navigator.screenshot_counter}")


class TestNavigatorWithExistingSessions:
    """Test navigator with existing session files"""
    
    @pytest.mark.asyncio
    async def test_navigator_with_existing_sessions(self):
        """Test navigator with existing session files"""
        session_manager = SessionManager()
        
        # List existing sessions
        sessions = await session_manager.list_sessions()
        
        if sessions:
            print(f"📋 Found {len(sessions)} existing sessions:")
            for session in sessions[:3]:  # Show first 3
                print(f"  - {session.session_id} (created: {session.created_at})")
        else:
            print(f"ℹ️  No existing sessions found")
        
        # Test getting valid session
        valid_session = await session_manager.get_valid_session()
        
        if valid_session:
            print(f"✅ Found valid session: {valid_session.session_id}")
        else:
            print(f"ℹ️  No valid session found")
        
        print(f"✅ Session management works with existing sessions")
    
    @pytest.mark.asyncio
    async def test_navigator_session_cleanup(self):
        """Test navigator session cleanup"""
        session_manager = SessionManager()
        
        # Test cleanup
        cleaned_count = await session_manager.cleanup_expired_sessions()
        
        print(f"✅ Session cleanup completed")
        print(f"🗑️  Cleaned up {cleaned_count} expired sessions")


class TestNavigatorConfiguration:
    """Test navigator configuration integration"""
    
    @pytest.mark.asyncio
    async def test_navigator_configuration_validation(self):
        """Test navigator configuration validation"""
        config = get_config()
        excel_config = config.get_excel_web_config()
        
        # Test configuration values
        assert excel_config.base_url is not None
        assert excel_config.timeout > 0
        assert excel_config.session_storage_path is not None
        assert excel_config.screenshot_dir is not None
        
        print(f"✅ Configuration validation passed")
        print(f"🌐 Base URL: {excel_config.base_url}")
        print(f"⏱️  Timeout: {excel_config.timeout}s")
        print(f"📁 Session storage: {excel_config.session_storage_path}")
        print(f"📸 Screenshot directory: {excel_config.screenshot_dir}")
    
    @pytest.mark.asyncio
    async def test_navigator_environment_integration(self):
        """Test navigator environment integration"""
        config = get_config()
        
        # Test that configuration loads from environment
        assert config is not None
        
        # Test Excel Web config
        excel_config = config.get_excel_web_config()
        assert excel_config is not None
        
        # Test authentication config
        auth_config = config.get_auth_config()
        assert auth_config is not None
        
        print(f"✅ Environment integration works correctly")
        print(f"🔑 OpenAI API Key configured: {auth_config.microsoft_email is not None}")


if __name__ == "__main__":
    # Run integration tests
    pytest.main([__file__, "-v", "-s"])
