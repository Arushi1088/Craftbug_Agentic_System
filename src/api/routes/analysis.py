#!/usr/bin/env python3
"""
Analysis API Routes for Craftbug Agentic System
New API routes with legacy fallback capability
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Any
import logging

from src.api.models.analysis import AnalysisRequest, AnalysisResponse, AnalysisReport
from src.core.analysis.service import analysis_service
from src.utils.feature_flags import FeatureFlags

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/analysis", tags=["analysis"])

@router.post("/", response_model=AnalysisResponse)
async def analyze_url(request: AnalysisRequest):
    """
    Analyze a URL with fallback to legacy system.
    This endpoint maintains compatibility with existing frontend.
    """
    try:
        logger.info(f"🔄 Analysis request received for {request.url}")
        
        # Use analysis service with fallback
        result = await analysis_service.analyze(request)
        
        logger.info(f"✅ Analysis completed: {result.analysis_id}")
        return result
        
    except Exception as e:
        logger.error(f"❌ Analysis endpoint failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/reports/{analysis_id}", response_model=AnalysisReport)
async def get_report(analysis_id: str):
    """
    Get analysis report with fallback to legacy system.
    """
    try:
        logger.info(f"🔄 Report request received for {analysis_id}")
        
        # Use analysis service with fallback
        report = await analysis_service.get_report(analysis_id)
        
        if not report:
            raise HTTPException(status_code=404, detail="Report not found")
        
        logger.info(f"✅ Report retrieved: {analysis_id}")
        return report
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Report endpoint failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/scenarios", response_model=List[Dict[str, Any]])
async def get_scenarios():
    """
    Get available scenarios with fallback to legacy system.
    """
    try:
        logger.info("🔄 Scenarios request received")
        
        # Use analysis service with fallback
        scenarios = await analysis_service.get_scenarios()
        
        logger.info(f"✅ Scenarios retrieved: {len(scenarios)} found")
        return scenarios
        
    except Exception as e:
        logger.error(f"❌ Scenarios endpoint failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/status")
async def get_analysis_status():
    """
    Get analysis service status for monitoring.
    """
    try:
        status = analysis_service.get_status()
        return status
        
    except Exception as e:
        logger.error(f"❌ Status endpoint failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Legacy compatibility endpoints
@router.post("/analyze", response_model=AnalysisResponse)
async def analyze_url_legacy(request: AnalysisRequest):
    """
    Legacy analysis endpoint for backward compatibility.
    """
    return await analyze_url(request)

@router.get("/reports/{analysis_id}/json")
async def get_report_json(analysis_id: str):
    """
    Legacy report endpoint for backward compatibility.
    """
    try:
        logger.info(f"🔄 Legacy report request received for {analysis_id}")
        
        # Use analysis service with fallback
        report = await analysis_service.get_report(analysis_id)
        
        if not report:
            raise HTTPException(status_code=404, detail="Report not found")
        
        # Convert to legacy format
        legacy_report = {
            "analysis_id": report.analysis_id,
            "status": report.status,
            "url": report.url,
            "overall_score": report.overall_score,
            "total_issues": report.total_issues,
            "craft_bugs": [bug.dict() for bug in report.craft_bugs],
            "ux_issues": [issue.dict() for issue in report.ux_issues],
            "timestamp": report.timestamp.isoformat(),
            "duration": report.duration
        }
        
        logger.info(f"✅ Legacy report retrieved: {analysis_id}")
        return legacy_report
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Legacy report endpoint failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
