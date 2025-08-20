"""
Tests for the unified configuration management system.
"""

import os
import pytest
from unittest.mock import patch
from src.excel.core.config import (
    ExcelAnalysisConfig,
    get_config,
    get_excel_web_config,
    get_excel_web_credentials,
    reset_config
)


class TestExcelAnalysisConfig:
    """Test the main configuration class"""
    
    def test_config_initialization(self):
        """Test that configuration initializes correctly"""
        config = ExcelAnalysisConfig()
        
        # Check that all sub-configs are initialized
        assert config.excel_web is not None
        assert config.auth is not None
        assert config.analysis is not None
        assert config.reporting is not None
        assert config.api is not None
        assert config.database is not None
        assert config.logging is not None
    
    def test_excel_web_config_defaults(self):
        """Test Excel Web configuration defaults"""
        config = ExcelAnalysisConfig()
        excel_config = config.get_excel_web_config()
        
        assert excel_config.base_url == "https://www.office.com/launch/excel"
        assert excel_config.timeout == 30
        assert excel_config.headless is True
        assert excel_config.window_size == "1920x1080"
        assert excel_config.session_storage_path == "sessions/excel_web"
        assert excel_config.screenshot_dir == "screenshots/excel_web"
    
    def test_analysis_config_defaults(self):
        """Test analysis configuration defaults"""
        config = ExcelAnalysisConfig()
        analysis_config = config.get_analysis_config()
        
        assert analysis_config.openai_model == "gpt-4"
        assert analysis_config.openai_max_tokens == 2000
        assert analysis_config.openai_temperature == 0.7
        assert analysis_config.enable_craft_bug_detection is True
        assert analysis_config.enable_visual_analysis is True
        assert analysis_config.enable_performance_analysis is True
    
    def test_reporting_config_defaults(self):
        """Test reporting configuration defaults"""
        config = ExcelAnalysisConfig()
        reporting_config = config.get_reporting_config()
        
        assert reporting_config.report_output_dir == "reports/excel_ux"
        assert reporting_config.company_name == "CraftBug Analysis"
        assert reporting_config.report_title == "Excel UX Analysis Report"
        assert reporting_config.enable_html_reports is True
        assert reporting_config.enable_screenshot_embedding is True
    
    def test_api_config_defaults(self):
        """Test API configuration defaults"""
        config = ExcelAnalysisConfig()
        api_config = config.get_api_config()
        
        assert api_config.host == "localhost"
        assert api_config.port == 8000
        assert api_config.debug is False
        assert api_config.api_version == "v1"
        assert "http://localhost:8080" in api_config.cors_origins
    
    def test_config_to_dict(self):
        """Test configuration serialization to dictionary"""
        config = ExcelAnalysisConfig()
        config_dict = config.to_dict()
        
        # Check that all sections are present
        assert "excel_web" in config_dict
        assert "auth" in config_dict
        assert "analysis" in config_dict
        assert "reporting" in config_dict
        assert "api" in config_dict
        assert "database" in config_dict
        assert "logging" in config_dict
        
        # Check that sensitive data is not exposed
        assert "microsoft_password" not in config_dict["auth"]
        assert "openai_api_key" not in config_dict["analysis"]


class TestGlobalConfig:
    """Test global configuration functions"""
    
    def test_get_config_singleton(self):
        """Test that get_config returns the same instance"""
        config1 = get_config()
        config2 = get_config()
        assert config1 is config2
    
    def test_reset_config(self):
        """Test that reset_config creates a new instance"""
        config1 = get_config()
        reset_config()
        config2 = get_config()
        assert config1 is not config2
    
    def test_backward_compatibility_functions(self):
        """Test backward compatibility functions"""
        # Test get_excel_web_config
        excel_config = get_excel_web_config()
        assert excel_config.base_url == "https://www.office.com/launch/excel"
        
        # Test get_excel_web_credentials
        credentials = get_excel_web_credentials()
        assert "email" in credentials
        assert "password" in credentials


class TestEnvironmentVariableIntegration:
    """Test integration with environment variables"""
    
    @patch.dict(os.environ, {
        "OPENAI_API_KEY": "test-openai-key",
        "MICROSOFT_EMAIL": "test@example.com",
        "MICROSOFT_PASSWORD": "test-password"
    })
    def test_environment_variable_loading(self):
        """Test that environment variables are loaded correctly"""
        reset_config()  # Reset to ensure fresh config
        config = get_config()
        
        # Check that environment variables are loaded
        assert config.analysis.openai_api_key == "test-openai-key"
        assert config.auth.microsoft_email == "test@example.com"
        assert config.auth.microsoft_password == "test-password"
    
    @patch.dict(os.environ, {
        "EXCEL_WEB_TIMEOUT": "60",
        "EXCEL_WEB_HEADLESS": "false",
        "API_HOST": "0.0.0.0",
        "API_PORT": "9000",
        "LOG_LEVEL": "DEBUG"
    })
    def test_config_update_from_env(self):
        """Test that configuration can be updated from environment variables"""
        config = get_config()
        config.update_from_env()
        
        # Check that environment variables are applied
        assert config.excel_web.timeout == 60
        assert config.excel_web.headless is False
        assert config.api.host == "0.0.0.0"
        assert config.api.port == 9000
        assert config.logging.log_level == "DEBUG"


class TestConfigurationValidation:
    """Test configuration validation"""
    
    def test_missing_openai_key_warning(self):
        """Test that missing OpenAI key generates a warning"""
        with patch.dict(os.environ, {}, clear=True):
            reset_config()
            # The warning should be printed during initialization
            # We can't easily test the print output, but we can verify the config still works
            config = get_config()
            assert config.analysis.openai_api_key is None
    
    def test_missing_microsoft_credentials_warning(self):
        """Test that missing Microsoft credentials generates a warning"""
        with patch.dict(os.environ, {}, clear=True):
            reset_config()
            config = get_config()
            assert config.auth.microsoft_email is None
            assert config.auth.microsoft_password is None


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])
