"""
Schema normalizer for UX analysis reports
Ensures consistent report structure and handles failed analyses gracefully
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

def normalize_report_schema(data: Any) -> Dict[str, Any]:
    """
    Normalize report schema to ensure consistent structure.
    Always returns a dict with safe defaults, even for failed analyses.
    """
    # Always return a dict with safe defaults
    if not isinstance(data, dict):
        logger.warning(f"normalize_report_schema received non-dict data: {type(data)}")
        return {
            "status": "failed",
            "error": "Empty/invalid report data",
            "module_results": {},
            "scenario_results": [],
            "overall_score": 0,
            "total_issues": 0,
            "timestamp": datetime.now().isoformat(),
            "ui_error": "Report data was empty or invalid"
        }

    # If it's a failure payload, enrich it so UI can render a proper error
    if data.get("status") == "failed" or data.get("error"):
        logger.info(f"Normalizing failed report with error: {data.get('error', 'Unknown error')}")
        return {
            **data,
            "module_results": data.get("module_results", {}),
            "scenario_results": data.get("scenario_results", []),
            "overall_score": data.get("overall_score", 0),
            "total_issues": data.get("total_issues", 0),
            "ui_error": data.get("error") or data.get("ui_error") or "Analysis failed",
            "timestamp": data.get("timestamp", datetime.now().isoformat())
        }

    # Normal report processing - ensure all required fields exist
    normalized = dict(data)  # Create a copy
    
    # Set safe defaults for missing fields
    normalized.setdefault("module_results", {})
    normalized.setdefault("scenario_results", [])
    normalized.setdefault("overall_score", 0)
    normalized.setdefault("total_issues", 0)
    normalized.setdefault("status", "completed")
    normalized.setdefault("timestamp", datetime.now().isoformat())
    
    # Ensure arrays are actually arrays
    if not isinstance(normalized["scenario_results"], list):
        normalized["scenario_results"] = []
    
    # Ensure module_results is a dict
    if not isinstance(normalized["module_results"], dict):
        normalized["module_results"] = {}
    
    # Calculate total_issues if not set
    if normalized["total_issues"] == 0 and normalized["module_results"]:
        total = 0
        for module_data in normalized["module_results"].values():
            if isinstance(module_data, dict) and "findings" in module_data:
                if isinstance(module_data["findings"], list):
                    total += len(module_data["findings"])
        normalized["total_issues"] = total
    
    logger.debug(f"Normalized report with {len(normalized.get('module_results', {}))} modules and {normalized['total_issues']} total issues")
    
    return normalized

def migrate_reports_on_startup() -> int:
    """
    Migrate existing reports to new schema format.
    Returns number of files updated.
    """
    import os
    import json
    import glob
    
    changed_count = 0
    reports_dir = "reports/analysis"
    
    if not os.path.exists(reports_dir):
        logger.info("Reports directory doesn't exist, skipping migration")
        return 0
    
    # Find all analysis JSON files
    pattern = os.path.join(reports_dir, "analysis_*.json")
    report_files = glob.glob(pattern)
    
    logger.info(f"Found {len(report_files)} report files for potential migration")
    
    for file_path in report_files:
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
            
            # Normalize the data
            normalized = normalize_report_schema(data)
            
            # Check if normalization made changes
            if normalized != data:
                # Back up original file
                backup_path = f"{file_path}.backup"
                if not os.path.exists(backup_path):
                    with open(backup_path, 'w') as f:
                        json.dump(data, f, indent=2)
                
                # Write normalized version
                with open(file_path, 'w') as f:
                    json.dump(normalized, f, indent=2)
                
                changed_count += 1
                logger.info(f"Migrated report: {os.path.basename(file_path)}")
        
        except Exception as e:
            logger.error(f"Failed to migrate {file_path}: {e}")
    
    logger.info(f"Schema migration complete: {changed_count} files updated")
    return changed_count

def iterate_all_report_files() -> List[str]:
    """
    Get list of all report files for iteration.
    """
    import os
    import glob
    
    reports_dir = "reports/analysis"
    if not os.path.exists(reports_dir):
        return []
    
    pattern = os.path.join(reports_dir, "analysis_*.json")
    return glob.glob(pattern)
