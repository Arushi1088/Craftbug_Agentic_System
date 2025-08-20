"""
Unified Exceptions for Excel Analysis System

This module provides centralized exception handling for all Excel-related
components, consolidating error handling from multiple existing classes.
"""

from typing import Optional, Dict, Any


class ExcelAnalysisError(Exception):
    """Base exception for Excel analysis errors"""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        self.message = message
        self.details = details or {}
        super().__init__(self.message)


class ExcelNavigationError(ExcelAnalysisError):
    """Exception for Excel navigation errors"""
    
    def __init__(self, message: str, url: Optional[str] = None, step: Optional[str] = None):
        details = {}
        if url:
            details['url'] = url
        if step:
            details['step'] = step
        super().__init__(message, details)


class AuthenticationError(ExcelAnalysisError):
    """Exception for authentication errors"""
    
    def __init__(self, message: str, method: Optional[str] = None, session_id: Optional[str] = None):
        details = {}
        if method:
            details['method'] = method
        if session_id:
            details['session_id'] = session_id
        super().__init__(message, details)


class SessionError(ExcelAnalysisError):
    """Exception for session management errors"""
    
    def __init__(self, message: str, session_id: Optional[str] = None, operation: Optional[str] = None):
        details = {}
        if session_id:
            details['session_id'] = session_id
        if operation:
            details['operation'] = operation
        super().__init__(message, details)


class ConfigurationError(ExcelAnalysisError):
    """Exception for configuration errors"""
    
    def __init__(self, message: str, config_key: Optional[str] = None, config_value: Optional[Any] = None):
        details = {}
        if config_key:
            details['config_key'] = config_key
        if config_value is not None:
            details['config_value'] = config_value
        super().__init__(message, details)


class ScreenshotError(ExcelAnalysisError):
    """Exception for screenshot capture errors"""
    
    def __init__(self, message: str, screenshot_path: Optional[str] = None, reason: Optional[str] = None):
        details = {}
        if screenshot_path:
            details['screenshot_path'] = screenshot_path
        if reason:
            details['reason'] = reason
        super().__init__(message, details)


class ScenarioError(ExcelAnalysisError):
    """Exception for scenario execution errors"""
    
    def __init__(self, message: str, scenario_name: Optional[str] = None, step_number: Optional[int] = None):
        details = {}
        if scenario_name:
            details['scenario_name'] = scenario_name
        if step_number is not None:
            details['step_number'] = step_number
        super().__init__(message, details)


class AnalysisError(ExcelAnalysisError):
    """Exception for analysis errors"""
    
    def __init__(self, message: str, analysis_type: Optional[str] = None, data_source: Optional[str] = None):
        details = {}
        if analysis_type:
            details['analysis_type'] = analysis_type
        if data_source:
            details['data_source'] = data_source
        super().__init__(message, details)


class ReportError(ExcelAnalysisError):
    """Exception for report generation errors"""
    
    def __init__(self, message: str, report_type: Optional[str] = None, template: Optional[str] = None):
        details = {}
        if report_type:
            details['report_type'] = report_type
        if template:
            details['template'] = template
        super().__init__(message, details)


class BrowserError(ExcelAnalysisError):
    """Exception for browser automation errors"""
    
    def __init__(self, message: str, browser_type: Optional[str] = None, action: Optional[str] = None):
        details = {}
        if browser_type:
            details['browser_type'] = browser_type
        if action:
            details['action'] = action
        super().__init__(message, details)


class TimeoutError(ExcelAnalysisError):
    """Exception for timeout errors"""
    
    def __init__(self, message: str, timeout_seconds: Optional[float] = None, operation: Optional[str] = None):
        details = {}
        if timeout_seconds is not None:
            details['timeout_seconds'] = timeout_seconds
        if operation:
            details['operation'] = operation
        super().__init__(message, details)


class ElementNotFoundError(ExcelAnalysisError):
    """Exception for element not found errors"""
    
    def __init__(self, message: str, selector: Optional[str] = None, element_type: Optional[str] = None):
        details = {}
        if selector:
            details['selector'] = selector
        if element_type:
            details['element_type'] = element_type
        super().__init__(message, details)


class NetworkError(ExcelAnalysisError):
    """Exception for network-related errors"""
    
    def __init__(self, message: str, url: Optional[str] = None, status_code: Optional[int] = None):
        details = {}
        if url:
            details['url'] = url
        if status_code is not None:
            details['status_code'] = status_code
        super().__init__(message, details)


# Backward compatibility aliases
ExcelWebError = ExcelAnalysisError
ExcelError = ExcelAnalysisError
