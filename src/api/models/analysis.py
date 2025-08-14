#!/usr/bin/env python3
"""
Analysis Models for Craftbug Agentic System
Pydantic models for analysis requests and responses
"""

from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any
from datetime import datetime
from enum import Enum

class ModuleType(str, Enum):
    """Analysis module types"""
    PERFORMANCE = "performance"
    ACCESSIBILITY = "accessibility"
    UX_HEURISTICS = "ux_heuristics"
    KEYBOARD = "keyboard"
    BEST_PRACTICES = "best_practices"
    HEALTH_ALERTS = "health_alerts"

class AnalysisRequest(BaseModel):
    """Request model for analysis"""
    url: str = Field(..., description="URL to analyze")
    scenario_id: Optional[str] = Field(None, description="Scenario ID to execute")
    modules: Dict[str, bool] = Field(
        default_factory=lambda: {
            "performance": True,
            "accessibility": True,
            "ux_heuristics": True,
            "keyboard": True,
            "best_practices": True,
            "health_alerts": True
        },
        description="Analysis modules to enable"
    )
    
    class Config:
        schema_extra = {
            "example": {
                "url": "http://127.0.0.1:8080/mocks/word/basic-doc.html",
                "scenario_id": "1.1",
                "modules": {
                    "performance": True,
                    "accessibility": True,
                    "ux_heuristics": True
                }
            }
        }

class AnalysisResponse(BaseModel):
    """Response model for analysis"""
    analysis_id: str = Field(..., description="Unique analysis ID")
    status: str = Field(..., description="Analysis status")
    message: str = Field(..., description="Status message")
    url: str = Field(..., description="Analyzed URL")
    timestamp: datetime = Field(default_factory=datetime.now, description="Analysis timestamp")
    
    class Config:
        schema_extra = {
            "example": {
                "analysis_id": "abc123",
                "status": "completed",
                "message": "Analysis completed successfully",
                "url": "http://127.0.0.1:8080/mocks/word/basic-doc.html",
                "timestamp": "2025-08-13T10:00:00"
            }
        }

class Issue(BaseModel):
    """Model for individual issues"""
    id: str = Field(..., description="Issue ID")
    category: str = Field(..., description="Issue category")
    severity: str = Field(..., description="Issue severity (high/medium/low)")
    title: str = Field(..., description="Issue title")
    description: str = Field(..., description="Issue description")
    selector: Optional[str] = Field(None, description="CSS selector")
    line_number: Optional[int] = Field(None, description="Line number")
    column_number: Optional[int] = Field(None, description="Column number")
    suggestions: List[str] = Field(default_factory=list, description="Fix suggestions")
    
    class Config:
        schema_extra = {
            "example": {
                "id": "issue_1",
                "category": "accessibility",
                "severity": "high",
                "title": "Missing alt text",
                "description": "Image missing alt text for accessibility",
                "selector": "img.logo",
                "line_number": 15,
                "column_number": 5,
                "suggestions": ["Add alt text to image"]
            }
        }

class ModuleResult(BaseModel):
    """Model for module analysis results"""
    module: str = Field(..., description="Module name")
    score: int = Field(..., description="Module score (0-100)")
    issues: List[Issue] = Field(default_factory=list, description="Issues found")
    passed: bool = Field(..., description="Whether module passed")
    
    class Config:
        schema_extra = {
            "example": {
                "module": "accessibility",
                "score": 85,
                "issues": [],
                "passed": True
            }
        }

class AnalysisReport(BaseModel):
    """Complete analysis report model"""
    analysis_id: str = Field(..., description="Analysis ID")
    status: str = Field(..., description="Report status")
    url: str = Field(..., description="Analyzed URL")
    overall_score: int = Field(..., description="Overall score (0-100)")
    total_issues: int = Field(..., description="Total issues found")
    modules: List[ModuleResult] = Field(..., description="Module results")
    craft_bugs: List[Issue] = Field(default_factory=list, description="Craft bugs found")
    ux_issues: List[Issue] = Field(default_factory=list, description="UX issues found")
    timestamp: datetime = Field(..., description="Analysis timestamp")
    duration: float = Field(..., description="Analysis duration in seconds")
    
    class Config:
        schema_extra = {
            "example": {
                "analysis_id": "abc123",
                "status": "completed",
                "url": "http://127.0.0.1:8080/mocks/word/basic-doc.html",
                "overall_score": 85,
                "total_issues": 3,
                "modules": [],
                "craft_bugs": [],
                "ux_issues": [],
                "timestamp": "2025-08-13T10:00:00",
                "duration": 2.5
            }
        }
