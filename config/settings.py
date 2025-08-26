"""
Centralized configuration settings for Craftbug Agentic System.
This module provides a single source of truth for all configuration values.
"""

import os
from typing import Optional
from dataclasses import dataclass


@dataclass
class Settings:
    """Centralized settings for the Craftbug Agentic System."""
    
    # OpenAI Configuration
    OPENAI_API_KEY: str = os.getenv('OPENAI_API_KEY', '')
    OPENAI_MODEL: str = os.getenv('OPENAI_MODEL', 'gpt-4o')
    OPENAI_MAX_TOKENS: int = int(os.getenv('OPENAI_MAX_TOKENS', '8000'))
    OPENAI_TEMPERATURE: float = float(os.getenv('OPENAI_TEMPERATURE', '0.2'))
    
    # Analysis Configuration
    MAX_SCREENSHOTS_PER_ANALYSIS: int = int(os.getenv('MAX_SCREENSHOTS_PER_ANALYSIS', '10'))
    BUG_TARGET_MIN: int = int(os.getenv('BUG_TARGET_MIN', '6'))
    BUG_TARGET_MAX: int = int(os.getenv('BUG_TARGET_MAX', '10'))
    
    # File Paths
    SCREENSHOTS_DIR: str = os.getenv('SCREENSHOTS_DIR', 'screenshots')
    REPORTS_DIR: str = os.getenv('REPORTS_DIR', 'reports')
    TELEMETRY_DIR: str = os.getenv('TELEMETRY_DIR', 'telemetry_output')
    
    # Server Configuration
    SERVER_HOST: str = os.getenv('SERVER_HOST', '127.0.0.1')
    SERVER_PORT: int = int(os.getenv('SERVER_PORT', '8000'))
    
    # Debug Configuration
    DEBUG: bool = os.getenv('DEBUG', 'False').lower() == 'true'
    LOG_LEVEL: str = os.getenv('LOG_LEVEL', 'INFO')
    
    def validate(self) -> bool:
        """Validate that required settings are present."""
        if not self.OPENAI_API_KEY:
            # For testing purposes, allow empty API key but warn
            print("⚠️ Warning: OPENAI_API_KEY not set - some features may not work")
            return False
        return True
    
    def get_openai_config(self) -> dict:
        """Get OpenAI configuration as a dictionary."""
        return {
            'api_key': self.OPENAI_API_KEY,
            'model': self.OPENAI_MODEL,
            'max_tokens': self.OPENAI_MAX_TOKENS,
            'temperature': self.OPENAI_TEMPERATURE
        }


# Global settings instance
settings = Settings()


def get_settings() -> Settings:
    """Get the global settings instance."""
    return settings


def validate_settings() -> bool:
    """Validate all settings and return True if valid."""
    try:
        return settings.validate()
    except Exception as e:
        print(f"❌ Configuration validation failed: {e}")
        return False
