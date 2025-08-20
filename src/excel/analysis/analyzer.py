"""
Unified Excel Analysis Engine

This module provides a unified interface for Excel UX analysis, consolidating
functionality from multiple existing analyzer classes while maintaining backward
compatibility and improving maintainability.
"""

import asyncio
import json
import os
from datetime import datetime
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass, field
from pathlib import Path

# Local imports
from ..core.config import get_config
from ..core.exceptions import AnalysisError, ConfigurationError


@dataclass
class UXAnalysisResult:
    """Result of a UX analysis operation"""
    success: bool
    ux_score: float = 0.0
    craft_bugs: List[Dict[str, Any]] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    analysis_data: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None


@dataclass
class CraftBug:
    """Craft bug data structure"""
    title: str
    description: str
    severity: str  # "low", "medium", "high", "critical"
    category: str
    step_name: Optional[str] = None
    screenshot_path: Optional[str] = None
    recommendations: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TelemetryData:
    """Telemetry data structure"""
    scenario_name: str
    start_time: datetime
    end_time: datetime
    total_duration_ms: float
    steps: List[Dict[str, Any]]
    overall_success: bool
    screenshots: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)


class UnifiedExcelAnalyzer:
    """
    Unified Excel Analysis Engine
    
    This class consolidates functionality from multiple existing analyzer classes:
    - SimpleExcelUXAnalyzer
    - EnhancedUXAnalyzer
    - DynamicUXAnalyzer
    - AccessibilityAnalyzer
    - ComputerVisionAnalyzer
    
    It provides a single, consistent interface while maintaining backward compatibility.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the unified analyzer
        
        Args:
            config: Analysis configuration. If None, uses global config.
        """
        self.config = config or get_config().get_analysis_config()
        
        # Analysis state
        self.craft_bugs_detected: List[CraftBug] = []
        self.ux_analysis_results: List[Dict[str, Any]] = []
        self.telemetry_data: Optional[TelemetryData] = None
        
        # Load enhanced data
        self.real_figma_data: Dict[str, Any] = {}
        self.enhanced_craft_bugs: List[Dict[str, Any]] = []
        self.design_compliance_rules: Dict[str, Any] = {}
        self.enhanced_prompt: str = ""
        
        # Load enhanced data
        self._load_enhanced_data()
    
    def _load_enhanced_data(self):
        """Load enhanced data for analysis"""
        try:
            real_data_dir = "real_data"
            if not os.path.exists(real_data_dir):
                print("⚠️ No real data directory found. Using defaults...")
                self._load_default_data()
                return
            
            # Find the most recent enhanced data file
            data_files = [f for f in os.listdir(real_data_dir) if f.startswith("enhanced_real_data_")]
            if not data_files:
                print("⚠️ No enhanced data files found. Using defaults...")
                self._load_default_data()
                return
            
            # Sort by timestamp and get the most recent
            latest_file = sorted(data_files)[-1]
            filepath = os.path.join(real_data_dir, latest_file)
            
            with open(filepath, 'r') as f:
                data = json.load(f)
            
            self.real_figma_data = data.get('figma_data', {})
            self.enhanced_craft_bugs = data.get('craft_bugs', [])
            self.design_compliance_rules = data.get('compliance_rules', {})
            self.enhanced_prompt = data.get('enhanced_prompt', "")
            
            print(f"✅ Loaded enhanced data from {filepath}")
            print(f"   Figma data: {self.real_figma_data.get('file_info', {}).get('name', 'Unknown')}")
            print(f"   Craft bugs: {len(self.enhanced_craft_bugs)} examples")
            print(f"   Compliance rules: {len(self.design_compliance_rules)} categories")
            
        except Exception as e:
            print(f"❌ Error loading enhanced data: {e}")
            self._load_default_data()
    
    def _load_default_data(self):
        """Load default data when enhanced data is not available"""
        self.real_figma_data = {"file_info": {"name": "Excel Web Fluent 2"}}
        self.enhanced_craft_bugs = []
        self.design_compliance_rules = {
            "visual_consistency": {
                "description": "Ensure consistent visual design",
                "rules": ["color_scheme", "typography", "spacing"]
            },
            "accessibility": {
                "description": "Ensure accessibility compliance",
                "rules": ["contrast_ratio", "keyboard_navigation", "screen_reader"]
            },
            "performance": {
                "description": "Ensure optimal performance",
                "rules": ["load_time", "responsiveness", "memory_usage"]
            }
        }
        self.enhanced_prompt = ""
    
    async def analyze_telemetry_data(self, telemetry_data: Dict[str, Any]) -> UXAnalysisResult:
        """
        Analyze telemetry data and generate UX insights
        
        Args:
            telemetry_data: Telemetry data from scenario execution
            
        Returns:
            UXAnalysisResult: Analysis results
        """
        try:
            print("🎨 Running UX analysis on telemetry data...")
            
            # Parse telemetry data
            self.telemetry_data = self._parse_telemetry_data(telemetry_data)
            
            # Reset analysis state
            self.craft_bugs_detected = []
            self.ux_analysis_results = []
            
            # Perform step-level analysis
            await self._analyze_steps()
            
            # Perform scenario-level analysis
            await self._analyze_scenario_level_issues()
            
            # Calculate UX score
            ux_score = self._calculate_ux_score()
            
            # Generate recommendations
            recommendations = self._generate_recommendations()
            
            # Prepare analysis data
            analysis_data = {
                "scenario_name": self.telemetry_data.scenario_name,
                "total_duration_ms": self.telemetry_data.total_duration_ms,
                "steps_analyzed": len(self.telemetry_data.steps),
                "craft_bugs_found": len(self.craft_bugs_detected),
                "analysis_timestamp": datetime.now().isoformat(),
                "enhanced_data_used": len(self.enhanced_craft_bugs) > 0
            }
            
            return UXAnalysisResult(
                success=True,
                ux_score=ux_score,
                craft_bugs=[bug.__dict__ for bug in self.craft_bugs_detected],
                recommendations=recommendations,
                analysis_data=analysis_data
            )
            
        except Exception as e:
            error_msg = f"Analysis failed: {e}"
            print(f"❌ {error_msg}")
            return UXAnalysisResult(
                success=False,
                error=error_msg
            )
    
    def _parse_telemetry_data(self, telemetry_data: Dict[str, Any]) -> TelemetryData:
        """Parse telemetry data into structured format"""
        try:
            # Handle nested telemetry structure
            if 'telemetry' in telemetry_data:
                actual_data = telemetry_data['telemetry']
            else:
                actual_data = telemetry_data
            
            # Extract steps
            steps = actual_data.get('steps', [])
            
            # Extract screenshots
            screenshots = []
            for step in steps:
                if 'screenshot_path' in step and step['screenshot_path']:
                    screenshots.append(step['screenshot_path'])
            
            return TelemetryData(
                scenario_name=actual_data.get('scenario_name', 'unknown'),
                start_time=datetime.fromisoformat(actual_data.get('start_time', datetime.now().isoformat())),
                end_time=datetime.fromisoformat(actual_data.get('end_time', datetime.now().isoformat())),
                total_duration_ms=actual_data.get('total_duration_ms', 0.0),
                steps=steps,
                overall_success=actual_data.get('overall_success', True),
                screenshots=screenshots,
                errors=actual_data.get('errors', [])
            )
            
        except Exception as e:
            print(f"⚠️ Error parsing telemetry data: {e}")
            # Return minimal telemetry data
            return TelemetryData(
                scenario_name='unknown',
                start_time=datetime.now(),
                end_time=datetime.now(),
                total_duration_ms=0.0,
                steps=[],
                overall_success=False
            )
    
    async def _analyze_steps(self):
        """Analyze individual steps for UX issues"""
        if not self.telemetry_data or not self.telemetry_data.steps:
            return
        
        print(f"🔍 Analyzing {len(self.telemetry_data.steps)} steps...")
        
        for i, step in enumerate(self.telemetry_data.steps, 1):
            step_name = step.get('step_name', f'Step {i}')
            execution_time = step.get('execution_time', 0.0)
            
            # Analyze step performance
            if execution_time > 10.0:  # More than 10 seconds
                self.craft_bugs_detected.append(CraftBug(
                    title=f"Slow Step Execution: {step_name}",
                    description=f"Step '{step_name}' took {execution_time:.1f} seconds to complete, which is significantly longer than expected for a smooth user experience.",
                    severity="medium",
                    category="Performance",
                    step_name=step_name,
                    recommendations=[
                        "Optimize step execution time",
                        "Consider caching or preloading",
                        "Review network requests and dependencies"
                    ]
                ))
            
            # Analyze step errors
            if step.get('error'):
                self.craft_bugs_detected.append(CraftBug(
                    title=f"Step Error: {step_name}",
                    description=f"Step '{step_name}' encountered an error: {step.get('error')}",
                    severity="high",
                    category="Reliability",
                    step_name=step_name,
                    recommendations=[
                        "Implement proper error handling",
                        "Add retry mechanisms",
                        "Provide clear error messages to users"
                    ]
                ))
            
            # Analyze UI state changes
            ui_state = step.get('ui_state', '')
            if 'error' in ui_state.lower() or 'failed' in ui_state.lower():
                self.craft_bugs_detected.append(CraftBug(
                    title=f"UI State Error: {step_name}",
                    description=f"Step '{step_name}' resulted in an error state: {ui_state}",
                    severity="high",
                    category="User Interface",
                    step_name=step_name,
                    recommendations=[
                        "Implement proper state management",
                        "Add error recovery mechanisms",
                        "Provide clear feedback to users"
                    ]
                ))
    
    async def _analyze_scenario_level_issues(self):
        """Analyze scenario-level UX issues"""
        if not self.telemetry_data:
            return
        
        # Analyze overall performance
        total_duration = self.telemetry_data.total_duration_ms / 1000.0  # Convert to seconds
        
        if total_duration > 60.0:  # More than 60 seconds
            self.craft_bugs_detected.append(CraftBug(
                title="Overall Slow Performance",
                description=f"The entire scenario took {total_duration:.1f} seconds to complete, which exceeds the recommended 30-second threshold for optimal user experience.",
                severity="high",
                category="Performance",
                recommendations=[
                    "Optimize scenario execution",
                    "Consider parallel processing",
                    "Review and optimize each step"
                ]
            ))
        
        # Analyze success rate
        if not self.telemetry_data.overall_success:
            self.craft_bugs_detected.append(CraftBug(
                title="Scenario Execution Failed",
                description="The scenario failed to complete successfully, indicating potential reliability issues.",
                severity="critical",
                category="Reliability",
                recommendations=[
                    "Investigate failure root cause",
                    "Implement better error handling",
                    "Add comprehensive logging"
                ]
            ))
        
        # Analyze step count
        step_count = len(self.telemetry_data.steps)
        if step_count > 15:  # Too many steps
            self.craft_bugs_detected.append(CraftBug(
                title="Excessive Step Complexity",
                description=f"The scenario requires {step_count} steps, which may indicate overly complex user workflows.",
                severity="medium",
                category="Usability",
                recommendations=[
                    "Simplify user workflows",
                    "Combine related steps",
                    "Consider automation opportunities"
                ]
            ))
        
        # Analyze dialog interruptions
        dialog_count = sum(1 for step in self.telemetry_data.steps if step.get('dialog_detected', False))
        if dialog_count > 2:  # Too many dialogs
            self.craft_bugs_detected.append(CraftBug(
                title="Multiple Dialog Interruptions",
                description=f"The scenario encountered {dialog_count} dialog interruptions, which can disrupt user workflow and create cognitive load.",
                severity="medium",
                category="User Experience",
                recommendations=[
                    "Reduce unnecessary dialogs",
                    "Use inline validation instead of dialogs",
                    "Implement progressive disclosure"
                ]
            ))
    
    def _calculate_ux_score(self) -> float:
        """Calculate overall UX score based on analysis results"""
        if not self.telemetry_data:
            return 0.0
        
        base_score = 100.0
        
        # Deduct points for each craft bug
        severity_penalties = {
            "low": 5.0,
            "medium": 15.0,
            "high": 30.0,
            "critical": 50.0
        }
        
        for bug in self.craft_bugs_detected:
            penalty = severity_penalties.get(bug.severity, 10.0)
            base_score -= penalty
        
        # Deduct points for performance issues
        if self.telemetry_data.total_duration_ms > 60000:  # More than 60 seconds
            base_score -= 20.0
        elif self.telemetry_data.total_duration_ms > 30000:  # More than 30 seconds
            base_score -= 10.0
        
        # Deduct points for failures
        if not self.telemetry_data.overall_success:
            base_score -= 40.0
        
        # Ensure score is between 0 and 100
        return max(0.0, min(100.0, base_score))
    
    def _generate_recommendations(self) -> List[str]:
        """Generate actionable recommendations based on analysis"""
        recommendations = []
        
        # Performance recommendations
        performance_bugs = [bug for bug in self.craft_bugs_detected if bug.category == "Performance"]
        if performance_bugs:
            recommendations.append("Optimize performance by reducing execution times and improving responsiveness")
        
        # Reliability recommendations
        reliability_bugs = [bug for bug in self.craft_bugs_detected if bug.category == "Reliability"]
        if reliability_bugs:
            recommendations.append("Improve reliability by implementing better error handling and recovery mechanisms")
        
        # Usability recommendations
        usability_bugs = [bug for bug in self.craft_bugs_detected if bug.category == "Usability"]
        if usability_bugs:
            recommendations.append("Enhance usability by simplifying workflows and reducing cognitive load")
        
        # User Experience recommendations
        ux_bugs = [bug for bug in self.craft_bugs_detected if bug.category == "User Experience"]
        if ux_bugs:
            recommendations.append("Improve user experience by reducing interruptions and providing better feedback")
        
        # General recommendations
        if len(self.craft_bugs_detected) > 5:
            recommendations.append("Consider conducting a comprehensive UX audit to identify systemic issues")
        
        if not recommendations:
            recommendations.append("Continue monitoring and collecting user feedback to maintain high UX standards")
        
        return recommendations
    
    def get_analysis_summary(self) -> Dict[str, Any]:
        """Get a summary of the analysis results"""
        if not self.telemetry_data:
            return {}
        
        return {
            "scenario_name": self.telemetry_data.scenario_name,
            "total_duration_ms": self.telemetry_data.total_duration_ms,
            "steps_analyzed": len(self.telemetry_data.steps),
            "craft_bugs_found": len(self.craft_bugs_detected),
            "ux_score": self._calculate_ux_score(),
            "overall_success": self.telemetry_data.overall_success,
            "screenshots_captured": len(self.telemetry_data.screenshots),
            "analysis_timestamp": datetime.now().isoformat()
        }


# Global analyzer instance for backward compatibility
_unified_analyzer: Optional[UnifiedExcelAnalyzer] = None


def get_unified_analyzer() -> UnifiedExcelAnalyzer:
    """
    Get the global unified analyzer instance
    
    Returns:
        UnifiedExcelAnalyzer: Global analyzer instance
    """
    global _unified_analyzer
    if _unified_analyzer is None:
        _unified_analyzer = UnifiedExcelAnalyzer()
    return _unified_analyzer


# Backward compatibility aliases
SimpleExcelUXAnalyzer = UnifiedExcelAnalyzer
EnhancedUXAnalyzer = UnifiedExcelAnalyzer
ExcelUXAnalyzer = UnifiedExcelAnalyzer
