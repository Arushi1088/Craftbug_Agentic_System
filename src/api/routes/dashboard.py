#!/usr/bin/env python3
"""
Dashboard API Routes for Craftbug Agentic System
Dashboard functionality with legacy fallback capability
"""

from fastapi import APIRouter, HTTPException, Form
from typing import Dict, Any, List
import logging
import json
import os
from datetime import datetime

from src.core.legacy_wrapper import legacy_wrapper
from src.utils.feature_flags import FeatureFlags

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])

@router.get("/analytics")
async def get_dashboard_analytics():
    """
    Get dashboard analytics data.
    """
    try:
        logger.info("🔄 Dashboard analytics request received")
        
        # Mock analytics data (legacy compatibility)
        analytics_data = {
            "total_analyses": 15,
            "total_issues": 42,
            "issues_by_severity": {
                "high": 8,
                "medium": 20,
                "low": 14
            },
            "issues_by_category": {
                "accessibility": 12,
                "performance": 8,
                "ux_heuristics": 15,
                "craft_bugs": 7
            },
            "recent_analyses": [
                {
                    "id": "abc123",
                    "url": "http://127.0.0.1:8080/mocks/word/basic-doc.html",
                    "score": 85,
                    "timestamp": datetime.now().isoformat()
                }
            ],
            "trends": {
                "weekly_issues": [10, 12, 8, 15, 9, 11, 13],
                "weekly_analyses": [3, 4, 2, 5, 3, 4, 3]
            }
        }
        
        logger.info("✅ Dashboard analytics retrieved")
        return analytics_data
        
    except Exception as e:
        logger.error(f"❌ Dashboard analytics failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/reports")
async def get_dashboard_reports():
    """
    Get list of available reports.
    """
    try:
        logger.info("🔄 Dashboard reports request received")
        
        # Mock reports data (legacy compatibility)
        reports_data = [
            {
                "id": "abc123",
                "url": "http://127.0.0.1:8080/mocks/word/basic-doc.html",
                "score": 85,
                "total_issues": 3,
                "timestamp": datetime.now().isoformat(),
                "status": "completed"
            },
            {
                "id": "def456",
                "url": "http://127.0.0.1:8080/mocks/excel/basic-doc.html",
                "score": 78,
                "total_issues": 5,
                "timestamp": datetime.now().isoformat(),
                "status": "completed"
            }
        ]
        
        logger.info(f"✅ Dashboard reports retrieved: {len(reports_data)} reports")
        return reports_data
        
    except Exception as e:
        logger.error(f"❌ Dashboard reports failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/create-ado-tickets")
async def create_ado_tickets(report_id: str = Form(...), demo_mode: bool = Form(True)):
    """
    Create ADO tickets from dashboard.
    """
    try:
        logger.info(f"🔄 Dashboard ADO ticket creation for report {report_id}")
        
        # Use legacy wrapper for now (safe fallback)
        mock_report_data = {
            "analysis_id": report_id,
            "issues": [
                {"category": "accessibility", "severity": "high", "title": "Missing alt text"},
                {"category": "performance", "severity": "medium", "title": "Slow loading"}
            ]
        }
        
        result = await legacy_wrapper.create_ado_tickets(mock_report_data, demo_mode)
        
        logger.info(f"✅ Dashboard ADO tickets created: {result.get('work_items_created', 0)}")
        return result
        
    except Exception as e:
        logger.error(f"❌ Dashboard ADO ticket creation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/alerts")
async def get_dashboard_alerts():
    """
    Get dashboard alerts.
    """
    try:
        logger.info("🔄 Dashboard alerts request received")
        
        # Mock alerts data (legacy compatibility)
        alerts_data = {
            "critical_alerts": 0,
            "warnings": 2,
            "alerts": [
                {
                    "type": "warning",
                    "message": "High number of accessibility issues detected",
                    "timestamp": datetime.now().isoformat()
                },
                {
                    "type": "info",
                    "message": "New analysis completed successfully",
                    "timestamp": datetime.now().isoformat()
                }
            ]
        }
        
        logger.info("✅ Dashboard alerts retrieved")
        return alerts_data
        
    except Exception as e:
        logger.error(f"❌ Dashboard alerts failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
