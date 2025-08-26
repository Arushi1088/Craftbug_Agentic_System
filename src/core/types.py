"""
Common type definitions for Craftbug Agentic System.
This module defines all common types used throughout the application.
"""

from typing import List, Dict, Optional, Union, Any
from dataclasses import dataclass
from pathlib import Path


@dataclass
class BugData:
    """Data structure for a single bug."""
    title: str
    type: str
    severity: str
    confidence: str
    description: str
    expected: str
    actual: str
    ui_path: str
    screen_position: str
    visual_analysis: Dict[str, Any]
    developer_action: Dict[str, str]
    design_system_compliance: Dict[str, Any]
    persona_impact: Dict[str, int]
    screenshot_paths: List[str]
    affected_steps: List[Dict[str, Any]]
    bug_category: Optional[str] = None


@dataclass
class StepData:
    """Data structure for a single step."""
    step_name: str
    description: str
    screenshot_path: Optional[str]
    scenario_description: str
    persona_type: str
    index: Optional[int] = None


@dataclass
class AnalysisResult:
    """Data structure for analysis results."""
    bugs: List[BugData]
    meta: Dict[str, Any]
    debug_counters: Dict[str, int]
    success: bool
    error_message: Optional[str] = None


@dataclass
class LLMResponse:
    """Data structure for LLM response."""
    content: str
    model: str
    tokens_used: int
    response_time: float
    success: bool
    error: Optional[str] = None


@dataclass
class ScreenshotData:
    """Data structure for screenshot data."""
    path: str
    base64: str
    size_bytes: int
    width: Optional[int] = None
    height: Optional[int] = None
    format: Optional[str] = None


# Type aliases for common patterns
BugList = List[BugData]
StepList = List[StepData]
ScreenshotList = List[ScreenshotData]
AnalysisContext = Dict[str, Any]
PromptTemplate = str
JSONData = Dict[str, Any]
