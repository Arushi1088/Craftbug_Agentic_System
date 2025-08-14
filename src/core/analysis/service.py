#!/usr/bin/env python3
"""
Analysis Service for Craftbug Agentic System
New analysis service with legacy fallback
"""

import logging
import asyncio
from typing import Dict, Any, Optional
from datetime import datetime
import uuid

from src.api.models.analysis import AnalysisRequest, AnalysisResponse, AnalysisReport
from src.utils.feature_flags import FeatureFlags
from src.core.legacy_wrapper import legacy_wrapper

logger = logging.getLogger(__name__)

class AnalysisService:
    """
    Analysis service with legacy fallback capability.
    Uses new architecture when available, falls back to legacy system.
    """
    
    def __init__(self):
        self.legacy_wrapper = legacy_wrapper
        logger.info("✅ Analysis service initialized")
    
    async def analyze(self, request: AnalysisRequest) -> AnalysisResponse:
        """
        Perform analysis with fallback to legacy system.
        This is the main entry point for analysis requests.
        """
        analysis_id = str(uuid.uuid4())[:8]
        
        try:
            logger.info(f"🔄 Starting analysis {analysis_id} for {request.url}")
            
            # Check if we should use new architecture
            if FeatureFlags.should_use_new_system('analysis'):
                try:
                    logger.info("🆕 Using new analysis architecture")
                    result = await self._analyze_with_new_system(request, analysis_id)
                    return result
                except Exception as e:
                    logger.warning(f"❌ New analysis system failed, falling back to legacy: {e}")
            
            # Fallback to legacy system
            logger.info("🔄 Using legacy analysis system")
            result = await self._analyze_with_legacy_system(request, analysis_id)
            return result
            
        except Exception as e:
            logger.error(f"❌ Analysis failed: {e}")
            return AnalysisResponse(
                analysis_id=analysis_id,
                status="error",
                message=f"Analysis failed: {str(e)}",
                url=request.url
            )
    
    async def _analyze_with_new_system(self, request: AnalysisRequest, analysis_id: str) -> AnalysisResponse:
        """
        Analyze using new architecture (to be implemented).
        For now, this is a placeholder that will be developed in later phases.
        """
        # TODO: Implement new analysis system in Phase 2
        # For now, this raises an exception to trigger legacy fallback
        raise NotImplementedError("New analysis system not yet implemented")
    
    async def _analyze_with_legacy_system(self, request: AnalysisRequest, analysis_id: str) -> AnalysisResponse:
        """
        Analyze using legacy system via wrapper.
        This ensures current functionality continues to work.
        """
        try:
            # Convert request to legacy format
            legacy_request = {
                "url": request.url,
                "scenario_id": request.scenario_id or "1.1",
                "modules": request.modules
            }
            
            # Use legacy wrapper
            result = await self.legacy_wrapper.analyze_url(legacy_request)
            
            # Convert result to new format
            return AnalysisResponse(
                analysis_id=analysis_id,
                status="completed",
                message="Analysis completed successfully using legacy system",
                url=request.url
            )
            
        except Exception as e:
            logger.error(f"❌ Legacy analysis failed: {e}")
            raise
    
    async def get_report(self, analysis_id: str) -> Optional[AnalysisReport]:
        """
        Get analysis report with fallback to legacy system.
        """
        try:
            logger.info(f"🔄 Retrieving report for {analysis_id}")
            
            # Check if we should use new architecture
            if FeatureFlags.should_use_new_system('reports'):
                try:
                    logger.info("🆕 Using new report system")
                    report = await self._get_report_with_new_system(analysis_id)
                    return report
                except Exception as e:
                    logger.warning(f"❌ New report system failed, falling back to legacy: {e}")
            
            # Fallback to legacy system
            logger.info("🔄 Using legacy report system")
            report = await self._get_report_with_legacy_system(analysis_id)
            return report
            
        except Exception as e:
            logger.error(f"❌ Report retrieval failed: {e}")
            return None
    
    async def _get_report_with_new_system(self, analysis_id: str) -> Optional[AnalysisReport]:
        """
        Get report using new system (to be implemented).
        """
        # TODO: Implement new report system in Phase 2
        raise NotImplementedError("New report system not yet implemented")
    
    async def _get_report_with_legacy_system(self, analysis_id: str) -> Optional[AnalysisReport]:
        """
        Get report using legacy system via wrapper.
        """
        try:
            # Use legacy wrapper
            legacy_report = await self.legacy_wrapper.get_report(analysis_id)
            
            if not legacy_report:
                return None
            
            # Convert legacy report to new format
            return AnalysisReport(
                analysis_id=analysis_id,
                status=legacy_report.get("status", "completed"),
                url=legacy_report.get("url", ""),
                overall_score=legacy_report.get("overall_score", 0),
                total_issues=legacy_report.get("total_issues", 0),
                modules=[],  # TODO: Convert legacy modules
                craft_bugs=[],  # TODO: Convert legacy craft bugs
                ux_issues=[],  # TODO: Convert legacy UX issues
                timestamp=datetime.now(),
                duration=legacy_report.get("duration", 0.0)
            )
            
        except Exception as e:
            logger.error(f"❌ Legacy report retrieval failed: {e}")
            return None
    
    async def get_scenarios(self) -> list:
        """
        Get available scenarios with fallback to legacy system.
        """
        try:
            logger.info("🔄 Retrieving scenarios")
            
            # Check if we should use new architecture
            if FeatureFlags.should_use_new_system('scenarios'):
                try:
                    logger.info("🆕 Using new scenario system")
                    scenarios = await self._get_scenarios_with_new_system()
                    return scenarios
                except Exception as e:
                    logger.warning(f"❌ New scenario system failed, falling back to legacy: {e}")
            
            # Fallback to legacy system
            logger.info("🔄 Using legacy scenario system")
            scenarios = await self._get_scenarios_with_legacy_system()
            return scenarios
            
        except Exception as e:
            logger.error(f"❌ Scenario retrieval failed: {e}")
            return []
    
    async def _get_scenarios_with_new_system(self) -> list:
        """
        Get scenarios using new system (to be implemented).
        """
        # TODO: Implement new scenario system in Phase 2
        raise NotImplementedError("New scenario system not yet implemented")
    
    async def _get_scenarios_with_legacy_system(self) -> list:
        """
        Get scenarios using legacy system via wrapper.
        """
        try:
            # Use legacy wrapper
            scenarios = await self.legacy_wrapper.get_scenarios()
            return scenarios
            
        except Exception as e:
            logger.error(f"❌ Legacy scenario retrieval failed: {e}")
            return []
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get service status for monitoring.
        """
        return {
            "service": "analysis",
            "status": "healthy",
            "legacy_wrapper_available": self.legacy_wrapper.is_available(),
            "feature_flags": {
                "use_new_analysis": FeatureFlags.should_use_new_system('analysis'),
                "use_new_reports": FeatureFlags.should_use_new_system('reports'),
                "use_new_scenarios": FeatureFlags.should_use_new_system('scenarios')
            },
            "timestamp": datetime.now().isoformat()
        }

# Global service instance
analysis_service = AnalysisService()
