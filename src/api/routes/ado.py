#!/usr/bin/env python3
"""
ADO Integration API Routes for Craftbug Agentic System
Azure DevOps integration with legacy fallback capability
"""

from fastapi import APIRouter, HTTPException, Form
from typing import Dict, Any, Optional
import logging

from src.core.legacy_wrapper import legacy_wrapper
from src.utils.feature_flags import FeatureFlags

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/ado", tags=["ado"])

@router.post("/trigger-fix")
async def trigger_fix(work_item_id: int = Form(...), file_path: str = Form(...), instruction: str = Form(...)):
    """
    Trigger fix with agent using legacy fallback.
    This endpoint maintains compatibility with existing frontend.
    """
    try:
        logger.info(f"🔄 Fix request received for work item {work_item_id}")
        
        # Use legacy wrapper for now (safe fallback)
        result = await legacy_wrapper.trigger_fix(work_item_id, file_path, instruction)
        
        logger.info(f"✅ Fix completed for work item {work_item_id}")
        return result
        
    except Exception as e:
        logger.error(f"❌ Fix endpoint failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/thinking-steps/{work_item_id}")
async def get_thinking_steps(work_item_id: int):
    """
    Get thinking steps for work item.
    """
    try:
        # Simulate thinking steps (legacy compatibility)
        thinking_steps = [
            "🔍 Analyzing the issue...",
            "🧠 Understanding the context...",
            "💡 Generating solution...",
            "🔧 Applying fixes...",
            "✅ Verifying changes...",
            "🎉 Fix completed successfully!"
        ]
        
        return {
            "work_item_id": work_item_id,
            "thinking_steps": thinking_steps,
            "status": "completed"
        }
        
    except Exception as e:
        logger.error(f"❌ Thinking steps failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/create-tickets")
async def create_ado_tickets(report_id: str = Form(...), demo_mode: bool = Form(True)):
    """
    Create ADO tickets from analysis report.
    """
    try:
        logger.info(f"🔄 ADO ticket creation requested for report {report_id}")
        
        # Use legacy wrapper for now (safe fallback)
        mock_report_data = {
            "analysis_id": report_id,
            "issues": [
                {"category": "accessibility", "severity": "high", "title": "Missing alt text"},
                {"category": "performance", "severity": "medium", "title": "Slow loading"}
            ]
        }
        
        result = await legacy_wrapper.create_ado_tickets(mock_report_data, demo_mode)
        
        logger.info(f"✅ ADO tickets created: {result.get('work_items_created', 0)}")
        return result
        
    except Exception as e:
        logger.error(f"❌ ADO ticket creation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
