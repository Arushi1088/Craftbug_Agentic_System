"""
Analysis Orchestrator for Craftbug Agentic System.
This module provides a unified interface for running analyses with performance monitoring.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass

from config.settings import get_settings
from src.core.exceptions import AnalysisError, ConfigurationError
from src.core.types import AnalysisResult, BugData
from src.analyzers.analyzer_factory import create_analyzer, get_available_analyzers
from src.services.performance_service import PerformanceService


@dataclass
class AnalysisRequest:
    """Data structure for analysis requests."""
    analyzer_type: str
    data: Dict[str, Any]
    options: Dict[str, Any] = None


@dataclass
class AnalysisResponse:
    """Data structure for analysis responses."""
    success: bool
    result: Optional[AnalysisResult] = None
    performance_metrics: Dict[str, Any] = None
    error_message: Optional[str] = None


class AnalysisOrchestrator:
    """Orchestrator for managing and running analyses."""
    
    def __init__(self, settings=None):
        """Initialize the analysis orchestrator."""
        self.settings = settings or get_settings()
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Initialize services
        self.performance_service = PerformanceService(settings)
        
        # Analysis history
        self.analysis_history: List[AnalysisResponse] = []
        
        # Get available analyzers
        self.available_analyzers = get_available_analyzers(settings)
        
        self.logger.info(f"Initialized orchestrator with {len(self.available_analyzers)} available analyzers")
    
    async def run_analysis(self, request: AnalysisRequest) -> AnalysisResponse:
        """Run an analysis using the specified analyzer."""
        try:
            # Validate request
            if request.analyzer_type not in self.available_analyzers:
                raise ConfigurationError(f"Unknown analyzer type: {request.analyzer_type}")
            
            self.logger.info(f"Starting analysis with {request.analyzer_type} analyzer")
            
            # Create analyzer with performance monitoring
            async with self.performance_service.async_timer("analyzer_creation") as timer_id:
                analyzer = create_analyzer(request.analyzer_type, self.settings)
                self.performance_service.stop_timer(timer_id, metadata={"analyzer_type": request.analyzer_type})
            
            # Run analysis with performance monitoring
            async with self.performance_service.async_timer("analysis_execution") as timer_id:
                result = await analyzer.analyze(request.data)
                self.performance_service.stop_timer(timer_id, metadata={
                    "analyzer_type": request.analyzer_type,
                    "bugs_detected": len(result.bugs),
                    "success": result.success
                })
            
            # Create response
            response = AnalysisResponse(
                success=result.success,
                result=result,
                performance_metrics=self._get_performance_metrics(),
                error_message=result.error_message
            )
            
            # Store in history
            self.analysis_history.append(response)
            
            self.logger.info(f"Analysis completed: {len(result.bugs)} bugs detected")
            return response
            
        except Exception as e:
            self.logger.error(f"Analysis failed: {e}")
            
            response = AnalysisResponse(
                success=False,
                performance_metrics=self._get_performance_metrics(),
                error_message=str(e)
            )
            
            self.analysis_history.append(response)
            return response
    
    async def run_comparative_analysis(self, data: Dict[str, Any], analyzer_types: List[str] = None) -> Dict[str, AnalysisResponse]:
        """Run analysis with multiple analyzers for comparison."""
        if analyzer_types is None:
            analyzer_types = list(self.available_analyzers.keys())
        
        results = {}
        
        for analyzer_type in analyzer_types:
            if analyzer_type not in self.available_analyzers:
                self.logger.warning(f"Skipping unknown analyzer type: {analyzer_type}")
                continue
            
            request = AnalysisRequest(
                analyzer_type=analyzer_type,
                data=data
            )
            
            response = await self.run_analysis(request)
            results[analyzer_type] = response
        
        return results
    
    def get_analysis_history(self, limit: int = 50) -> List[AnalysisResponse]:
        """Get recent analysis history."""
        return self.analysis_history[-limit:] if self.analysis_history else []
    
    def get_analysis_stats(self) -> Dict[str, Any]:
        """Get statistics about all analyses."""
        if not self.analysis_history:
            return {"total_analyses": 0}
        
        total_analyses = len(self.analysis_history)
        successful_analyses = sum(1 for r in self.analysis_history if r.success)
        failed_analyses = total_analyses - successful_analyses
        
        # Count bugs by analyzer type
        bugs_by_analyzer = {}
        for response in self.analysis_history:
            if response.success and response.result:
                analyzer_type = "unknown"
                # Try to extract analyzer type from performance metrics
                if response.performance_metrics:
                    for metric in response.performance_metrics.get("recent_metrics", []):
                        if "analyzer_type" in metric.get("metadata", {}):
                            analyzer_type = metric["metadata"]["analyzer_type"]
                            break
                
                if analyzer_type not in bugs_by_analyzer:
                    bugs_by_analyzer[analyzer_type] = 0
                bugs_by_analyzer[analyzer_type] += len(response.result.bugs)
        
        return {
            "total_analyses": total_analyses,
            "successful_analyses": successful_analyses,
            "failed_analyses": failed_analyses,
            "success_rate": successful_analyses / total_analyses if total_analyses > 0 else 0,
            "bugs_by_analyzer": bugs_by_analyzer,
            "total_bugs_detected": sum(bugs_by_analyzer.values())
        }
    
    def _get_performance_metrics(self) -> Dict[str, Any]:
        """Get current performance metrics."""
        return {
            "recent_metrics": self.performance_service.get_performance_stats(time_window=300),
            "operation_breakdown": self.performance_service.get_operation_breakdown(),
            "slowest_operations": self.performance_service.get_slowest_operations(5),
            "health_check": self.performance_service.check_performance_health()
        }
    
    def get_system_health(self) -> Dict[str, Any]:
        """Get overall system health information."""
        return {
            "available_analyzers": self.available_analyzers,
            "analysis_stats": self.get_analysis_stats(),
            "performance_health": self.performance_service.check_performance_health(),
            "memory_usage": self.performance_service.get_memory_usage()
        }
    
    def clear_history(self):
        """Clear analysis history."""
        self.analysis_history.clear()
        self.logger.info("Analysis history cleared")
    
    def clear_performance_metrics(self, older_than: float = None):
        """Clear performance metrics."""
        self.performance_service.clear_metrics(older_than)


# Global orchestrator instance
_orchestrator: Optional[AnalysisOrchestrator] = None


def get_orchestrator(settings=None) -> AnalysisOrchestrator:
    """Get the global analysis orchestrator instance."""
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = AnalysisOrchestrator(settings)
    return _orchestrator


async def run_analysis(analyzer_type: str, data: Dict[str, Any], options: Dict[str, Any] = None) -> AnalysisResponse:
    """Run an analysis using the global orchestrator."""
    orchestrator = get_orchestrator()
    request = AnalysisRequest(analyzer_type=analyzer_type, data=data, options=options or {})
    return await orchestrator.run_analysis(request)


async def run_comparative_analysis(data: Dict[str, Any], analyzer_types: List[str] = None) -> Dict[str, AnalysisResponse]:
    """Run comparative analysis using the global orchestrator."""
    orchestrator = get_orchestrator()
    return await orchestrator.run_comparative_analysis(data, analyzer_types)


def get_system_health() -> Dict[str, Any]:
    """Get system health using the global orchestrator."""
    orchestrator = get_orchestrator()
    return orchestrator.get_system_health()
