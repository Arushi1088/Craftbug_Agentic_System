"""
System constants for Craftbug Agentic System.
This module contains all constant values used throughout the application.
"""

from typing import List, Dict, Any

# Bug Analysis Constants
BUG_TYPES: List[str] = [
    "Color", "Spacing", "Typography", "Alignment", "Component", 
    "Layout", "Hierarchy", "Design_System", "AI", "Shadow"
]

SEVERITY_LEVELS: List[str] = ["Red", "Orange", "Yellow"]
CONFIDENCE_LEVELS: List[str] = ["High", "Medium", "Low"]

SCREEN_POSITIONS: List[str] = [
    "Top-Left", "Top-Right", "Bottom-Left", "Bottom-Right", "Center"
]

# Analysis Categories
ANALYSIS_CATEGORIES: List[str] = [
    "craft_bugs", "performance", "accessibility", "visual_consistency", 
    "interaction_design", "user_experience"
]

# File Extensions
SUPPORTED_IMAGE_FORMATS: List[str] = [".png", ".jpg", ".jpeg", ".gif", ".bmp"]
SUPPORTED_REPORT_FORMATS: List[str] = [".html", ".json", ".pdf"]

# Default Values
DEFAULT_UI_PATH: str = "Not Observable"
DEFAULT_SCREEN_POSITION: str = "Center"
DEFAULT_SEVERITY: str = "Yellow"
DEFAULT_CONFIDENCE: str = "Medium"
DEFAULT_BUG_TYPE: str = "Visual"

# Prompt Templates
PROMPT_TEMPLATES: Dict[str, str] = {
    "craft_bug_analysis": "You are a senior UX designer analyzing Excel Web screenshots for *visual craft bugs only*.",
    "performance_analysis": "You are a performance analyst evaluating Excel Web interface performance.",
    "accessibility_analysis": "You are an accessibility expert analyzing Excel Web for accessibility issues."
}

# Error Messages
ERROR_MESSAGES: Dict[str, str] = {
    "missing_api_key": "OPENAI_API_KEY environment variable is required",
    "invalid_screenshot": "Invalid screenshot path or file not found",
    "analysis_failed": "Analysis failed due to an error",
    "json_parse_failed": "Failed to parse JSON response from LLM",
    "no_bugs_found": "No craft bugs detected in the analysis"
}

# Success Messages
SUCCESS_MESSAGES: Dict[str, str] = {
    "analysis_complete": "Analysis completed successfully",
    "bugs_detected": "Craft bugs detected and processed",
    "report_generated": "Report generated successfully",
    "screenshots_processed": "Screenshots processed successfully"
}

# Debug Messages
DEBUG_MESSAGES: Dict[str, str] = {
    "loading_image": "Loading image: {}",
    "processing_step": "Processing step: {}",
    "llm_response": "LLM response received: {} chars",
    "bug_parsed": "Bug parsed: {}"
}

# Configuration Keys
CONFIG_KEYS: Dict[str, str] = {
    "openai_api_key": "OPENAI_API_KEY",
    "openai_model": "OPENAI_MODEL",
    "openai_max_tokens": "OPENAI_MAX_TOKENS",
    "openai_temperature": "OPENAI_TEMPERATURE",
    "max_screenshots": "MAX_SCREENSHOTS_PER_ANALYSIS",
    "bug_target_min": "BUG_TARGET_MIN",
    "bug_target_max": "BUG_TARGET_MAX"
}

# File Paths
DEFAULT_PATHS: Dict[str, str] = {
    "screenshots": "screenshots",
    "reports": "reports",
    "telemetry": "telemetry_output",
    "logs": "logs",
    "temp": "temp"
}

# API Endpoints
API_ENDPOINTS: Dict[str, str] = {
    "analyze": "/api/analyze",
    "report": "/api/report",
    "health": "/api/health",
    "status": "/api/status"
}

# HTTP Status Codes
HTTP_STATUS: Dict[str, int] = {
    "ok": 200,
    "created": 201,
    "bad_request": 400,
    "unauthorized": 401,
    "not_found": 404,
    "internal_error": 500
}

# Timeout Values (in seconds)
TIMEOUTS: Dict[str, int] = {
    "api_call": 30,
    "image_processing": 10,
    "report_generation": 60,
    "screenshot_capture": 5
}

# Retry Configuration
RETRY_CONFIG: Dict[str, Any] = {
    "max_retries": 3,
    "backoff_factor": 2,
    "max_backoff": 60
}
