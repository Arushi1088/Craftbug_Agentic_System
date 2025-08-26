"""
Custom exceptions for Craftbug Agentic System.
This module defines all custom exceptions used throughout the application.
"""


class CraftbugError(Exception):
    """Base exception for all Craftbug Agentic System errors."""
    pass


class ConfigurationError(CraftbugError):
    """Raised when there's a configuration error."""
    pass


class AnalysisError(CraftbugError):
    """Raised when analysis fails."""
    pass


class LLMError(CraftbugError):
    """Raised when LLM interaction fails."""
    pass


class ScreenshotError(CraftbugError):
    """Raised when screenshot processing fails."""
    pass


class ValidationError(CraftbugError):
    """Raised when data validation fails."""
    pass


class ReportGenerationError(CraftbugError):
    """Raised when report generation fails."""
    pass


class APIError(CraftbugError):
    """Raised when API interaction fails."""
    pass


class FileNotFoundError(CraftbugError):
    """Raised when a required file is not found."""
    pass


class ParsingError(CraftbugError):
    """Raised when parsing fails."""
    pass


class DeduplicationError(CraftbugError):
    """Raised when deduplication fails."""
    pass
