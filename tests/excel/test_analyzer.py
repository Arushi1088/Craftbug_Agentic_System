"""
Tests for the unified Excel analysis engine.
"""

import pytest
import asyncio
from datetime import datetime
from unittest.mock import Mock, patch
from src.excel.analysis.analyzer import (
    UnifiedExcelAnalyzer,
    UXAnalysisResult,
    CraftBug,
    TelemetryData,
    get_unified_analyzer
)


class TestUnifiedExcelAnalyzer:
    """Test the unified Excel analyzer"""
    
    @pytest.fixture
    def analyzer(self):
        """Create an analyzer instance for testing"""
        return UnifiedExcelAnalyzer()
    
    @pytest.fixture
    def sample_telemetry_data(self):
        """Sample telemetry data for testing"""
        return {
            "scenario_name": "test_scenario",
            "start_time": "2025-08-20T12:00:00",
            "end_time": "2025-08-20T12:01:00",
            "total_duration_ms": 60000.0,
            "overall_success": True,
            "steps": [
                {
                    "step_name": "Navigate to Excel Web",
                    "execution_time": 2.5,
                    "success": True,
                    "screenshot_path": "screenshots/step1.png"
                },
                {
                    "step_name": "Click New Workbook",
                    "execution_time": 15.0,  # Slow step
                    "success": True,
                    "screenshot_path": "screenshots/step2.png"
                },
                {
                    "step_name": "Save Workbook",
                    "execution_time": 3.0,
                    "success": False,  # Failed step
                    "error": "Save failed",
                    "screenshot_path": "screenshots/step3.png"
                }
            ]
        }
    
    def test_analyzer_initialization(self, analyzer):
        """Test that analyzer initializes correctly"""
        assert analyzer.config is not None
        assert analyzer.craft_bugs_detected == []
        assert analyzer.ux_analysis_results == []
        assert analyzer.telemetry_data is None
        assert analyzer.real_figma_data is not None
        assert analyzer.enhanced_craft_bugs is not None
        assert analyzer.design_compliance_rules is not None
    
    @pytest.mark.asyncio
    async def test_analyze_telemetry_data_success(self, analyzer, sample_telemetry_data):
        """Test successful telemetry data analysis"""
        result = await analyzer.analyze_telemetry_data(sample_telemetry_data)
        
        assert result.success is True
        assert result.ux_score > 0
        assert len(result.craft_bugs) > 0
        assert len(result.recommendations) > 0
        assert result.analysis_data is not None
        assert result.error is None
        
        # Check that craft bugs were detected
        assert len(analyzer.craft_bugs_detected) > 0
        
        # Check that telemetry data was parsed
        assert analyzer.telemetry_data is not None
        assert analyzer.telemetry_data.scenario_name == "test_scenario"
        assert len(analyzer.telemetry_data.steps) == 3
    
    @pytest.mark.asyncio
    async def test_analyze_telemetry_data_with_nested_structure(self, analyzer):
        """Test analysis with nested telemetry structure"""
        nested_telemetry = {
            "telemetry": {
                "scenario_name": "nested_scenario",
                "start_time": "2025-08-20T12:00:00",
                "end_time": "2025-08-20T12:00:30",
                "total_duration_ms": 30000.0,
                "overall_success": True,
                "steps": [
                    {
                        "step_name": "Test Step",
                        "execution_time": 5.0,
                        "success": True
                    }
                ]
            }
        }
        
        result = await analyzer.analyze_telemetry_data(nested_telemetry)
        
        assert result.success is True
        assert analyzer.telemetry_data.scenario_name == "nested_scenario"
        assert len(analyzer.telemetry_data.steps) == 1
    
    @pytest.mark.asyncio
    async def test_analyze_telemetry_data_failure(self, analyzer):
        """Test analysis with invalid telemetry data"""
        invalid_telemetry = None
        
        result = await analyzer.analyze_telemetry_data(invalid_telemetry)
        
        # The analyzer handles None gracefully by creating minimal telemetry data
        assert result.success is True
        assert result.error is None
        assert analyzer.telemetry_data is not None
        assert analyzer.telemetry_data.scenario_name == "unknown"
        assert analyzer.telemetry_data.overall_success is False
    
    @pytest.mark.asyncio
    async def test_step_level_analysis(self, analyzer, sample_telemetry_data):
        """Test step-level analysis"""
        await analyzer.analyze_telemetry_data(sample_telemetry_data)
        
        # Should detect slow step execution
        slow_step_bugs = [bug for bug in analyzer.craft_bugs_detected 
                         if "Slow Step Execution" in bug.title]
        assert len(slow_step_bugs) > 0
        
        # Should detect step error
        error_bugs = [bug for bug in analyzer.craft_bugs_detected 
                     if "Step Error" in bug.title]
        assert len(error_bugs) > 0
    
    @pytest.mark.asyncio
    async def test_scenario_level_analysis(self, analyzer):
        """Test scenario-level analysis"""
        slow_scenario_data = {
            "scenario_name": "slow_scenario",
            "start_time": "2025-08-20T12:00:00",
            "end_time": "2025-08-20T12:02:00",  # 2 minutes
            "total_duration_ms": 120000.0,  # 2 minutes
            "overall_success": True,
            "steps": [
                {
                    "step_name": "Test Step",
                    "execution_time": 5.0,
                    "success": True
                }
            ]
        }
        
        await analyzer.analyze_telemetry_data(slow_scenario_data)
        
        # Should detect overall slow performance
        performance_bugs = [bug for bug in analyzer.craft_bugs_detected 
                           if "Overall Slow Performance" in bug.title]
        assert len(performance_bugs) > 0
    
    @pytest.mark.asyncio
    async def test_failed_scenario_analysis(self, analyzer):
        """Test analysis of failed scenario"""
        failed_scenario_data = {
            "scenario_name": "failed_scenario",
            "start_time": "2025-08-20T12:00:00",
            "end_time": "2025-08-20T12:00:30",
            "total_duration_ms": 30000.0,
            "overall_success": False,  # Failed scenario
            "steps": [
                {
                    "step_name": "Test Step",
                    "execution_time": 5.0,
                    "success": True
                }
            ]
        }
        
        await analyzer.analyze_telemetry_data(failed_scenario_data)
        
        # Should detect scenario execution failure
        failure_bugs = [bug for bug in analyzer.craft_bugs_detected 
                       if "Scenario Execution Failed" in bug.title]
        assert len(failure_bugs) > 0
    
    @pytest.mark.asyncio
    async def test_dialog_interruption_analysis(self, analyzer):
        """Test dialog interruption analysis"""
        dialog_scenario_data = {
            "scenario_name": "dialog_scenario",
            "start_time": "2025-08-20T12:00:00",
            "end_time": "2025-08-20T12:00:30",
            "total_duration_ms": 30000.0,
            "overall_success": True,
            "steps": [
                {
                    "step_name": "Step 1",
                    "execution_time": 5.0,
                    "success": True,
                    "dialog_detected": True
                },
                {
                    "step_name": "Step 2",
                    "execution_time": 5.0,
                    "success": True,
                    "dialog_detected": True
                },
                {
                    "step_name": "Step 3",
                    "execution_time": 5.0,
                    "success": True,
                    "dialog_detected": True
                }
            ]
        }
        
        await analyzer.analyze_telemetry_data(dialog_scenario_data)
        
        # Should detect multiple dialog interruptions
        dialog_bugs = [bug for bug in analyzer.craft_bugs_detected 
                      if "Multiple Dialog Interruptions" in bug.title]
        assert len(dialog_bugs) > 0
    
    def test_ux_score_calculation(self, analyzer):
        """Test UX score calculation"""
        # Create telemetry data with known issues
        analyzer.telemetry_data = TelemetryData(
            scenario_name="test",
            start_time=datetime.now(),
            end_time=datetime.now(),
            total_duration_ms=70000.0,  # 70 seconds (slow)
            steps=[],
            overall_success=True
        )
        
        # Add some craft bugs
        analyzer.craft_bugs_detected = [
            CraftBug(
                title="Test Bug 1",
                description="Test description",
                severity="medium",
                category="Performance"
            ),
            CraftBug(
                title="Test Bug 2",
                description="Test description",
                severity="high",
                category="Reliability"
            )
        ]
        
        score = analyzer._calculate_ux_score()
        
        # Score should be reduced due to bugs and performance issues
        assert score < 100.0
        assert score >= 0.0
    
    def test_recommendation_generation(self, analyzer):
        """Test recommendation generation"""
        # Add craft bugs of different categories
        analyzer.craft_bugs_detected = [
            CraftBug(
                title="Performance Bug",
                description="Test description",
                severity="medium",
                category="Performance"
            ),
            CraftBug(
                title="Reliability Bug",
                description="Test description",
                severity="high",
                category="Reliability"
            )
        ]
        
        recommendations = analyzer._generate_recommendations()
        
        assert len(recommendations) > 0
        assert any("performance" in rec.lower() for rec in recommendations)
        assert any("reliability" in rec.lower() for rec in recommendations)
    
    def test_analysis_summary(self, analyzer):
        """Test analysis summary generation"""
        # Set up telemetry data
        analyzer.telemetry_data = TelemetryData(
            scenario_name="test_scenario",
            start_time=datetime.now(),
            end_time=datetime.now(),
            total_duration_ms=45000.0,
            steps=[{"step_name": "Test Step"}],
            overall_success=True,
            screenshots=["screenshot1.png", "screenshot2.png"]
        )
        
        # Add some craft bugs
        analyzer.craft_bugs_detected = [
            CraftBug(
                title="Test Bug",
                description="Test description",
                severity="medium",
                category="Performance"
            )
        ]
        
        summary = analyzer.get_analysis_summary()
        
        assert summary["scenario_name"] == "test_scenario"
        assert summary["total_duration_ms"] == 45000.0
        assert summary["steps_analyzed"] == 1
        assert summary["craft_bugs_found"] == 1
        assert summary["screenshots_captured"] == 2
        assert "analysis_timestamp" in summary


class TestGlobalAnalyzer:
    """Test global analyzer functions"""
    
    @pytest.mark.asyncio
    async def test_get_unified_analyzer(self):
        """Test getting the global analyzer instance"""
        # Reset global instance
        import src.excel.analysis.analyzer as analyzer_module
        analyzer_module._unified_analyzer = None
        
        analyzer1 = get_unified_analyzer()
        analyzer2 = get_unified_analyzer()
        
        # Should return the same instance
        assert analyzer1 is analyzer2
        assert isinstance(analyzer1, UnifiedExcelAnalyzer)


class TestBackwardCompatibility:
    """Test backward compatibility aliases"""
    
    def test_backward_compatibility_aliases(self):
        """Test that backward compatibility aliases work"""
        from src.excel.analysis.analyzer import (
            SimpleExcelUXAnalyzer, 
            EnhancedUXAnalyzer, 
            ExcelUXAnalyzer
        )
        
        # These should be the same class
        assert SimpleExcelUXAnalyzer is UnifiedExcelAnalyzer
        assert EnhancedUXAnalyzer is UnifiedExcelAnalyzer
        assert ExcelUXAnalyzer is UnifiedExcelAnalyzer


class TestDataStructures:
    """Test data structures"""
    
    def test_ux_analysis_result_creation(self):
        """Test creating UXAnalysisResult"""
        result = UXAnalysisResult(
            success=True,
            ux_score=85.5,
            craft_bugs=[{"title": "Test Bug"}],
            recommendations=["Test recommendation"],
            analysis_data={"key": "value"}
        )
        
        assert result.success is True
        assert result.ux_score == 85.5
        assert len(result.craft_bugs) == 1
        assert len(result.recommendations) == 1
        assert result.analysis_data["key"] == "value"
        assert result.error is None
    
    def test_craft_bug_creation(self):
        """Test creating CraftBug"""
        bug = CraftBug(
            title="Test Bug",
            description="Test description",
            severity="high",
            category="Performance",
            step_name="Test Step",
            screenshot_path="screenshot.png",
            recommendations=["Test recommendation"]
        )
        
        assert bug.title == "Test Bug"
        assert bug.description == "Test description"
        assert bug.severity == "high"
        assert bug.category == "Performance"
        assert bug.step_name == "Test Step"
        assert bug.screenshot_path == "screenshot.png"
        assert len(bug.recommendations) == 1
    
    def test_telemetry_data_creation(self):
        """Test creating TelemetryData"""
        start_time = datetime.now()
        end_time = datetime.now()
        
        telemetry = TelemetryData(
            scenario_name="test_scenario",
            start_time=start_time,
            end_time=end_time,
            total_duration_ms=30000.0,
            steps=[{"step_name": "Test Step"}],
            overall_success=True,
            screenshots=["screenshot1.png"],
            errors=["Test error"]
        )
        
        assert telemetry.scenario_name == "test_scenario"
        assert telemetry.start_time == start_time
        assert telemetry.end_time == end_time
        assert telemetry.total_duration_ms == 30000.0
        assert len(telemetry.steps) == 1
        assert telemetry.overall_success is True
        assert len(telemetry.screenshots) == 1
        assert len(telemetry.errors) == 1


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])
