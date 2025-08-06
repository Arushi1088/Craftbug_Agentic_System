#!/usr/bin/env python3
"""
Test suite for Orchestrator Agent
"""

import pytest
import asyncio
import json
from unittest.mock import Mock, patch, AsyncMock
from pathlib import Path
import sys

# Add orchestrator to path
sys.path.append(str(Path(__file__).parent.parent))

from main import OrchestratorAgent, AnalysisResult, CoderTask

class TestOrchestratorAgent:
    """Test cases for OrchestratorAgent"""
    
    @pytest.fixture
    def orchestrator(self):
        """Create orchestrator instance for testing"""
        return OrchestratorAgent()
    
    @pytest.fixture
    def sample_analysis_result(self):
        """Sample analysis result for testing"""
        return AnalysisResult(
            analysis_id="test_analysis_123",
            url="https://example.com",
            overall_score=75,
            issues=[
                {
                    "type": "accessibility",
                    "severity": "high",
                    "message": "Missing alt text on images",
                    "element": "img.hero-banner",
                    "recommendation": "Add descriptive alt text"
                },
                {
                    "type": "performance",
                    "severity": "medium",
                    "message": "Large bundle size",
                    "file": "main.js",
                    "recommendation": "Optimize bundle"
                }
            ],
            recommendations=["Fix accessibility", "Optimize performance"],
            timestamp="2025-08-06T10:00:00",
            severity_counts={"high": 1, "medium": 1, "low": 0}
        )
    
    def test_orchestrator_initialization(self, orchestrator):
        """Test orchestrator initializes correctly"""
        assert orchestrator is not None
        assert orchestrator.config is not None
        assert orchestrator.logger is not None
        assert orchestrator.active_tasks == {}
        assert orchestrator.analysis_history == []
    
    def test_config_loading(self):
        """Test configuration loading"""
        orchestrator = OrchestratorAgent()
        config = orchestrator.config
        
        # Check default config structure
        assert "ux_analyzer" in config
        assert "coder_agent" in config
        assert "orchestrator" in config
        
        # Check specific defaults
        assert config["ux_analyzer"]["api_endpoint"] == "http://localhost:8000"
        assert config["orchestrator"]["severity_threshold"] == "medium"
        assert config["coder_agent"]["auto_fix_enabled"] is False
    
    @pytest.mark.asyncio
    async def test_analyze_website(self, orchestrator):
        """Test website analysis"""
        url = "https://example.com"
        
        result = await orchestrator.analyze_website(url)
        
        assert isinstance(result, AnalysisResult)
        assert result.url == url
        assert result.analysis_id.startswith("ux_")
        assert isinstance(result.overall_score, int)
        assert isinstance(result.issues, list)
        assert len(orchestrator.analysis_history) == 1
    
    @pytest.mark.asyncio
    async def test_create_coder_tasks(self, orchestrator, sample_analysis_result):
        """Test coder task creation from analysis results"""
        tasks = await orchestrator.create_coder_tasks(sample_analysis_result)
        
        assert isinstance(tasks, list)
        assert len(tasks) == 2  # Should create tasks for high and medium severity
        
        # Check first task (high severity)
        high_task = tasks[0]
        assert isinstance(high_task, CoderTask)
        assert high_task.priority == "high"
        assert high_task.bug_type == "accessibility"
        assert "img.hero-banner" in high_task.description or "alt text" in high_task.description
    
    def test_should_create_task(self, orchestrator):
        """Test task creation threshold logic"""
        # High severity should always create task
        high_issue = {"severity": "high", "type": "accessibility"}
        assert orchestrator._should_create_task(high_issue, "medium") is True
        
        # Medium severity should create task with medium threshold
        medium_issue = {"severity": "medium", "type": "performance"}
        assert orchestrator._should_create_task(medium_issue, "medium") is True
        
        # Low severity should not create task with medium threshold
        low_issue = {"severity": "low", "type": "style"}
        assert orchestrator._should_create_task(low_issue, "medium") is False
    
    def test_identify_files_to_fix(self, orchestrator):
        """Test file identification for different issue types"""
        # Accessibility issue
        accessibility_issue = {
            "type": "accessibility",
            "element": "img.hero-banner"
        }
        files = orchestrator._identify_files_to_fix(accessibility_issue)
        assert "index.html" in files
        assert "style.css" in files
        
        # Performance issue with specific file
        performance_issue = {
            "type": "performance",
            "file": "main.js"
        }
        files = orchestrator._identify_files_to_fix(performance_issue)
        assert "main.js" in files
        assert "package.json" in files
    
    @pytest.mark.asyncio
    async def test_execute_coder_tasks(self, orchestrator):
        """Test coder task execution"""
        tasks = [
            CoderTask(
                task_id="test_task_1",
                description="Fix accessibility",
                priority="high",
                files_to_fix=["index.html"],
                bug_type="accessibility",
                analysis_context={}
            ),
            CoderTask(
                task_id="test_task_2", 
                description="Fix performance",
                priority="medium",
                files_to_fix=["main.js"],
                bug_type="performance",
                analysis_context={}
            )
        ]
        
        results = await orchestrator.execute_coder_tasks(tasks)
        
        assert "completed" in results
        assert "failed" in results
        assert "task_results" in results
        assert results["completed"] == 2  # Both tasks should complete (simulated)
        assert len(results["task_results"]) == 2
    
    @pytest.mark.asyncio
    async def test_full_orchestration_cycle(self, orchestrator):
        """Test complete orchestration workflow"""
        url = "https://example.com"
        
        # Mock auto-fix disabled for safety
        orchestrator.config["orchestrator"]["auto_trigger_fixes"] = False
        
        result = await orchestrator.orchestrate_full_cycle(url)
        
        assert "orchestration_id" in result
        assert result["url"] == url
        assert "analysis" in result
        assert "tasks" in result
        assert "recommendations" in result
        
        # Check analysis section
        analysis = result["analysis"]
        assert "analysis_id" in analysis
        assert "overall_score" in analysis
        assert "issues_found" in analysis
        
        # Check tasks section
        tasks = result["tasks"]
        assert "created" in tasks
        assert "task_details" in tasks
    
    def test_get_status(self, orchestrator):
        """Test status reporting"""
        status = orchestrator.get_status()
        
        assert "agents" in status
        assert "active_tasks" in status
        assert "analysis_history" in status
        assert "config" in status
        assert "timestamp" in status
        
        # Check agent status
        agents = status["agents"]
        assert "ux_analyzer" in agents
        assert "coder_agent" in agents
    
    def test_count_severities(self, orchestrator):
        """Test severity counting"""
        issues = [
            {"severity": "high"},
            {"severity": "high"},
            {"severity": "medium"},
            {"severity": "low"}
        ]
        
        counts = orchestrator._count_severities(issues)
        
        assert counts["high"] == 2
        assert counts["medium"] == 1
        assert counts["low"] == 1

class TestAsyncIntegration:
    """Test async integration and error handling"""
    
    @pytest.mark.asyncio
    async def test_agent_initialization(self):
        """Test agent initialization process"""
        orchestrator = OrchestratorAgent()
        
        # Should not raise exception even if agents aren't available
        await orchestrator.initialize_agents()
        
        # Check that initialization completed
        assert orchestrator.ux_analyzer is not None or orchestrator.coder_agent is not None
    
    @pytest.mark.asyncio
    async def test_error_handling_in_analysis(self):
        """Test error handling during analysis"""
        orchestrator = OrchestratorAgent()
        
        # Test with invalid URL
        with patch.object(orchestrator, '_init_ux_analyzer', side_effect=Exception("Network error")):
            try:
                await orchestrator.initialize_agents()
            except Exception:
                pass  # Expected to handle gracefully
    
    @pytest.mark.asyncio
    async def test_concurrent_task_execution(self):
        """Test concurrent task processing"""
        orchestrator = OrchestratorAgent()
        
        # Create multiple tasks
        tasks = [
            CoderTask(
                task_id=f"task_{i}",
                description=f"Fix issue {i}",
                priority="medium",
                files_to_fix=[f"file_{i}.js"],
                bug_type="performance",
                analysis_context={}
            ) for i in range(5)
        ]
        
        # Execute concurrently
        results = await orchestrator.execute_coder_tasks(tasks)
        
        assert results["completed"] == 5
        assert len(results["task_results"]) == 5

def test_config_file_loading():
    """Test loading configuration from file"""
    # Create temporary config
    test_config = {
        "orchestrator": {
            "severity_threshold": "high",
            "auto_trigger_fixes": True
        }
    }
    
    config_path = "/tmp/test_config.json"
    with open(config_path, 'w') as f:
        json.dump(test_config, f)
    
    try:
        orchestrator = OrchestratorAgent(config_path=config_path)
        assert orchestrator.config["orchestrator"]["severity_threshold"] == "high"
        assert orchestrator.config["orchestrator"]["auto_trigger_fixes"] is True
    finally:
        # Cleanup
        Path(config_path).unlink(missing_ok=True)

if __name__ == "__main__":
    # Run tests directly
    pytest.main([__file__, "-v"])
