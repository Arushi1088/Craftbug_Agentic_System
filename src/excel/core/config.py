"""
Unified Configuration Management for Excel Analysis System

This module provides centralized configuration management for all Excel-related
components, consolidating environment variables and providing type-safe access
to configuration settings.
"""

import os
from typing import Optional, Dict, Any
from pathlib import Path
from dataclasses import dataclass
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


@dataclass
class ExcelWebConfig:
    """Configuration for Excel Web integration"""
    base_url: str = "https://www.office.com/launch/excel"
    timeout: int = 30
    headless: bool = True
    window_size: str = "1920x1080"
    user_agent: str = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
    
    # Session management
    session_timeout: int = 3600  # 1 hour
    session_storage_path: str = "sessions/excel_web"
    
    # Screenshot settings
    screenshot_dir: str = "screenshots/excel_web"
    screenshot_format: str = "png"
    screenshot_quality: int = 90


@dataclass
class AuthenticationConfig:
    """Configuration for authentication"""
    microsoft_email: Optional[str] = None
    microsoft_password: Optional[str] = None
    use_manual_auth: bool = False
    auth_timeout: int = 60
    
    def __post_init__(self):
        # Load from environment if not provided
        if not self.microsoft_email:
            self.microsoft_email = os.getenv("MICROSOFT_EMAIL")
        if not self.microsoft_password:
            self.microsoft_password = os.getenv("MICROSOFT_PASSWORD")


@dataclass
class AnalysisConfig:
    """Configuration for analysis components"""
    openai_api_key: Optional[str] = None
    openai_model: str = "gpt-4"
    openai_max_tokens: int = 2000
    openai_temperature: float = 0.7
    
    # Analysis settings
    enable_craft_bug_detection: bool = True
    enable_visual_analysis: bool = True
    enable_performance_analysis: bool = True
    
    # Prompt engineering
    prompt_template_dir: str = "prompt_templates"
    enable_prompt_optimization: bool = False
    
    def __post_init__(self):
        if not self.openai_api_key:
            self.openai_api_key = os.getenv("OPENAI_API_KEY")


@dataclass
class ReportingConfig:
    """Configuration for reporting system"""
    report_output_dir: str = "reports/excel_ux"
    report_template_dir: str = "templates"
    enable_html_reports: bool = True
    enable_json_reports: bool = True
    enable_screenshot_embedding: bool = True
    
    # Report customization
    company_name: str = "CraftBug Analysis"
    report_title: str = "Excel UX Analysis Report"
    include_timestamps: bool = True


@dataclass
class APIConfig:
    """Configuration for API endpoints"""
    host: str = "localhost"
    port: int = 8000
    debug: bool = False
    cors_origins: list = None
    api_version: str = "v1"
    
    def __post_init__(self):
        if self.cors_origins is None:
            self.cors_origins = ["http://localhost:8080", "http://localhost:3000"]


@dataclass
class DatabaseConfig:
    """Configuration for database connections"""
    database_url: Optional[str] = None
    enable_persistence: bool = False
    backup_enabled: bool = False
    backup_interval: int = 24  # hours
    
    def __post_init__(self):
        if not self.database_url:
            self.database_url = os.getenv("DATABASE_URL", "sqlite:///excel_analysis.db")


@dataclass
class LoggingConfig:
    """Configuration for logging"""
    log_level: str = "INFO"
    log_file: Optional[str] = None
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    enable_console_logging: bool = True
    enable_file_logging: bool = False


class ExcelAnalysisConfig:
    """
    Main configuration class that consolidates all Excel analysis settings.
    
    This class provides a single point of access to all configuration settings
    and ensures proper validation and defaults.
    """
    
    def __init__(self):
        self.excel_web = ExcelWebConfig()
        self.auth = AuthenticationConfig()
        self.analysis = AnalysisConfig()
        self.reporting = ReportingConfig()
        self.api = APIConfig()
        self.database = DatabaseConfig()
        self.logging = LoggingConfig()
        
        # Validate configuration
        self._validate_config()
    
    def _validate_config(self):
        """Validate configuration settings and provide warnings for missing values"""
        warnings = []
        
        # Check required environment variables
        if not self.analysis.openai_api_key:
            warnings.append("OPENAI_API_KEY not set - AI analysis features may not work")
        
        if not self.auth.microsoft_email:
            warnings.append("MICROSOFT_EMAIL not set - manual authentication may be required")
        
        # Check directory existence
        required_dirs = [
            self.excel_web.session_storage_path,
            self.excel_web.screenshot_dir,
            self.reporting.report_output_dir
        ]
        
        for directory in required_dirs:
            Path(directory).mkdir(parents=True, exist_ok=True)
        
        # Print warnings
        for warning in warnings:
            print(f"⚠️  Configuration Warning: {warning}")
    
    def get_excel_web_config(self) -> ExcelWebConfig:
        """Get Excel Web configuration"""
        return self.excel_web
    
    def get_auth_config(self) -> AuthenticationConfig:
        """Get authentication configuration"""
        return self.auth
    
    def get_analysis_config(self) -> AnalysisConfig:
        """Get analysis configuration"""
        return self.analysis
    
    def get_reporting_config(self) -> ReportingConfig:
        """Get reporting configuration"""
        return self.reporting
    
    def get_api_config(self) -> APIConfig:
        """Get API configuration"""
        return self.api
    
    def get_database_config(self) -> DatabaseConfig:
        """Get database configuration"""
        return self.database
    
    def get_logging_config(self) -> LoggingConfig:
        """Get logging configuration"""
        return self.logging
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary"""
        return {
            "excel_web": self.excel_web.__dict__,
            "auth": {k: v for k, v in self.auth.__dict__.items() if k != "microsoft_password"},
            "analysis": {k: v for k, v in self.analysis.__dict__.items() if k != "openai_api_key"},
            "reporting": self.reporting.__dict__,
            "api": self.api.__dict__,
            "database": self.database.__dict__,
            "logging": self.logging.__dict__
        }
    
    def update_from_env(self):
        """Update configuration from environment variables"""
        # Update Excel Web config
        if os.getenv("EXCEL_WEB_TIMEOUT"):
            self.excel_web.timeout = int(os.getenv("EXCEL_WEB_TIMEOUT"))
        
        if os.getenv("EXCEL_WEB_HEADLESS"):
            self.excel_web.headless = os.getenv("EXCEL_WEB_HEADLESS").lower() == "true"
        
        # Update API config
        if os.getenv("API_HOST"):
            self.api.host = os.getenv("API_HOST")
        
        if os.getenv("API_PORT"):
            self.api.port = int(os.getenv("API_PORT"))
        
        # Update logging config
        if os.getenv("LOG_LEVEL"):
            self.logging.log_level = os.getenv("LOG_LEVEL")


# Global configuration instance
_config: Optional[ExcelAnalysisConfig] = None


def get_config() -> ExcelAnalysisConfig:
    """
    Get the global configuration instance.
    
    Returns:
        ExcelAnalysisConfig: The global configuration instance
    """
    global _config
    if _config is None:
        _config = ExcelAnalysisConfig()
    return _config


def reset_config():
    """Reset the global configuration instance"""
    global _config
    _config = None


# Convenience functions for backward compatibility
def get_excel_web_config() -> ExcelWebConfig:
    """Get Excel Web configuration (backward compatibility)"""
    return get_config().get_excel_web_config()


def get_excel_web_credentials() -> Dict[str, str]:
    """Get Excel Web credentials (backward compatibility)"""
    auth_config = get_config().get_auth_config()
    return {
        "email": auth_config.microsoft_email,
        "password": auth_config.microsoft_password
    }
