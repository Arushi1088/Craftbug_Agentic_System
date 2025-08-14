#!/usr/bin/env python3
"""
Git Integration API Routes for Craftbug Agentic System
Git operations with legacy fallback capability
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any, Optional
import logging
import subprocess
import os

from src.core.legacy_wrapper import legacy_wrapper
from src.utils.feature_flags import FeatureFlags

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/git", tags=["git"])

@router.get("/status")
async def get_git_status():
    """
    Get Git repository status.
    """
    try:
        logger.info("🔄 Git status request received")
        
        # Use legacy wrapper for now (safe fallback)
        result = await legacy_wrapper.commit_git_changes(999, "Status check")
        
        # Get actual Git status
        try:
            git_status = subprocess.run(
                ["git", "status", "--porcelain"],
                capture_output=True,
                text=True,
                check=True
            )
            
            return {
                "status": "success",
                "git_status": git_status.stdout.strip(),
                "branch": subprocess.run(
                    ["git", "branch", "--show-current"],
                    capture_output=True,
                    text=True,
                    check=True
                ).stdout.strip(),
                "message": "Git status retrieved successfully"
            }
        except subprocess.CalledProcessError as e:
            return {
                "status": "error",
                "message": f"Git command failed: {e.stderr}",
                "git_status": "",
                "branch": ""
            }
        
    except Exception as e:
        logger.error(f"❌ Git status failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/commit-changes")
async def commit_changes(work_item_id: int, commit_message: str = None):
    """
    Commit and push changes for work item.
    """
    try:
        logger.info(f"🔄 Git commit request received for work item {work_item_id}")
        
        # Use legacy wrapper for now (safe fallback)
        result = await legacy_wrapper.commit_git_changes(work_item_id, commit_message)
        
        logger.info(f"✅ Git commit completed for work item {work_item_id}")
        return result
        
    except Exception as e:
        logger.error(f"❌ Git commit failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/push")
async def push_changes():
    """
    Push changes to remote repository.
    """
    try:
        logger.info("🔄 Git push request received")
        
        # Execute Git push
        try:
            result = subprocess.run(
                ["git", "push"],
                capture_output=True,
                text=True,
                check=True
            )
            
            return {
                "status": "success",
                "message": "Changes pushed successfully",
                "output": result.stdout
            }
        except subprocess.CalledProcessError as e:
            return {
                "status": "error",
                "message": f"Git push failed: {e.stderr}",
                "output": e.stdout
            }
        
    except Exception as e:
        logger.error(f"❌ Git push failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
