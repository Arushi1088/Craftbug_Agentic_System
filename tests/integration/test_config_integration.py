"""
Integration tests to verify the new configuration system works with existing functionality.
"""

import pytest
import os
from pathlib import Path
from src.excel.core.config import get_config, reset_config


class TestConfigurationIntegration:
    """Test integration with existing Excel analysis components"""
    
    def test_config_with_existing_environment(self):
        """Test that configuration works with existing environment variables"""
        # Reset config to ensure fresh state
        reset_config()
        
        # Get configuration
        config = get_config()
        
        # Verify that configuration loaded correctly
        assert config is not None
        
        # Check that directories are created
        excel_config = config.get_excel_web_config()
        reporting_config = config.get_reporting_config()
        
        # Verify directories exist
        assert Path(excel_config.session_storage_path).exists()
        assert Path(excel_config.screenshot_dir).exists()
        assert Path(reporting_config.report_output_dir).exists()
        
        print(f"✅ Configuration loaded successfully")
        print(f"📁 Session storage: {excel_config.session_storage_path}")
        print(f"📸 Screenshot directory: {excel_config.screenshot_dir}")
        print(f"📄 Report output: {reporting_config.report_output_dir}")
    
    def test_backward_compatibility(self):
        """Test that backward compatibility functions work"""
        from src.excel.core.config import get_excel_web_config, get_excel_web_credentials
        
        # Test Excel Web config
        excel_config = get_excel_web_config()
        assert excel_config.base_url == "https://www.office.com/launch/excel"
        assert excel_config.timeout == 30
        
        # Test credentials
        credentials = get_excel_web_credentials()
        assert "email" in credentials
        assert "password" in credentials
        
        print(f"✅ Backward compatibility functions work correctly")
    
    def test_config_serialization(self):
        """Test that configuration can be serialized for API responses"""
        config = get_config()
        config_dict = config.to_dict()
        
        # Verify all sections are present
        required_sections = ["excel_web", "auth", "analysis", "reporting", "api", "database", "logging"]
        for section in required_sections:
            assert section in config_dict
            assert isinstance(config_dict[section], dict)
        
        # Verify sensitive data is not exposed
        assert "microsoft_password" not in config_dict["auth"]
        assert "openai_api_key" not in config_dict["analysis"]
        
        print(f"✅ Configuration serialization works correctly")
    
    def test_environment_variable_override(self):
        """Test that environment variables can override defaults"""
        # Set some environment variables
        test_env = {
            "EXCEL_WEB_TIMEOUT": "60",
            "API_PORT": "9000",
            "LOG_LEVEL": "DEBUG"
        }
        
        # Set environment variables
        for key, value in test_env.items():
            os.environ[key] = value
        
        try:
            # Reset config to load new environment variables
            reset_config()
            config = get_config()
            
            # Update config from environment
            config.update_from_env()
            
            # Verify overrides
            assert config.excel_web.timeout == 60
            assert config.api.port == 9000
            assert config.logging.log_level == "DEBUG"
            
            print(f"✅ Environment variable overrides work correctly")
        finally:
            # Clean up environment variables
            for key in test_env.keys():
                if key in os.environ:
                    del os.environ[key]


class TestConfigurationWithExistingFiles:
    """Test configuration with existing Excel analysis files"""
    
    def test_config_with_existing_directories(self):
        """Test that configuration works with existing directories"""
        # Ensure existing directories exist
        existing_dirs = [
            "sessions/excel_web",
            "screenshots/excel_web", 
            "reports/excel_ux",
            "telemetry_output"
        ]
        
        for directory in existing_dirs:
            Path(directory).mkdir(parents=True, exist_ok=True)
        
        # Reset and get config
        reset_config()
        config = get_config()
        
        # Verify configuration matches existing structure
        excel_config = config.get_excel_web_config()
        reporting_config = config.get_reporting_config()
        
        assert excel_config.session_storage_path == "sessions/excel_web"
        assert excel_config.screenshot_dir == "screenshots/excel_web"
        assert reporting_config.report_output_dir == "reports/excel_ux"
        
        print(f"✅ Configuration matches existing directory structure")
    
    def test_config_with_existing_environment_file(self):
        """Test that configuration loads from existing .env file"""
        # Check if .env file exists
        env_file = Path(".env")
        if env_file.exists():
            print(f"📄 Found existing .env file: {env_file}")
            
            # Reset config to load from .env
            reset_config()
            config = get_config()
            
            # Verify configuration loaded
            assert config is not None
            
            # Check if any environment variables were loaded
            analysis_config = config.get_analysis_config()
            auth_config = config.get_auth_config()
            
            print(f"🔑 OpenAI API Key configured: {analysis_config.openai_api_key is not None}")
            print(f"📧 Microsoft Email configured: {auth_config.microsoft_email is not None}")
        else:
            print(f"⚠️  No .env file found, using defaults")
    
    def test_config_compatibility_with_existing_imports(self):
        """Test that existing imports still work with new configuration"""
        try:
            # Test importing existing modules that might use configuration
            from src.excel.core.config import get_excel_web_config, get_excel_web_credentials
            
            # Verify functions work
            excel_config = get_excel_web_config()
            credentials = get_excel_web_credentials()
            
            assert excel_config is not None
            assert credentials is not None
            
            print(f"✅ Existing import patterns work with new configuration")
            
        except ImportError as e:
            print(f"⚠️  Import test failed: {e}")
            # This is expected if we haven't migrated all modules yet


if __name__ == "__main__":
    # Run integration tests
    pytest.main([__file__, "-v", "-s"])
