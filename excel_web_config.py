"""
Excel Web Configuration Module
Handles configuration for Excel Web automation and integration
"""

import os
from typing import Optional, Dict, Any
from dataclasses import dataclass
from pathlib import Path


@dataclass
class ExcelWebConfig:
    """Configuration for Excel Web automation"""
    
    # Excel Web URLs
    excel_web_url: str = "https://excel.office.com"
    login_url: str = "https://login.microsoftonline.com"
    
    # Session configuration
    session_timeout_minutes: int = 120
    max_retry_attempts: int = 3
    retry_delay_seconds: int = 5
    
    # Browser configuration
    headless: bool = False
    browser_timeout_seconds: int = 30
    page_load_timeout_seconds: int = 60
    
    # Screenshot configuration
    screenshot_dir: str = "screenshots/excel_web"
    video_dir: str = "videos/excel_web"
    
    # Analysis configuration
    enable_performance_monitoring: bool = True
    enable_accessibility_testing: bool = True
    enable_ui_analysis: bool = True
    
    def __post_init__(self):
        """Create necessary directories after initialization"""
        Path(self.screenshot_dir).mkdir(parents=True, exist_ok=True)
        Path(self.video_dir).mkdir(parents=True, exist_ok=True)


class ExcelWebCredentials:
    """Handles Excel Web credentials securely"""
    
    def __init__(self):
        self.username: Optional[str] = None
        self.password: Optional[str] = None
        self.session_data: Optional[Dict[str, Any]] = None
    
    def set_credentials(self, username: str, password: str):
        """Set credentials (in memory only)"""
        self.username = username
        self.password = password
    
    def clear_credentials(self):
        """Clear credentials from memory"""
        self.username = None
        self.password = None
        self.session_data = None
    
    def has_credentials(self) -> bool:
        """Check if credentials are set"""
        return self.username is not None and self.password is not None


# Global configuration instance
excel_web_config = ExcelWebConfig()
excel_web_credentials = ExcelWebCredentials()


def get_excel_web_config() -> ExcelWebConfig:
    """Get the global Excel Web configuration"""
    return excel_web_config


def get_excel_web_credentials() -> ExcelWebCredentials:
    """Get the global Excel Web credentials"""
    return excel_web_credentials
