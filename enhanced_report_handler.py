#!/usr/bin/env python3
"""
Enhanced Report Handler
Persistent storage and retrieval of UX analysis reports with comprehensive indexing
"""

import json
import os
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, List, Optional
import uuid
import shutil

logger = logging.getLogger(__name__)

class EnhancedReportHandler:
    """Enhanced report handler with persistent storage and indexing"""
    
    def __init__(self, reports_dir: str = "reports"):
        self.reports_dir = Path(reports_dir)
        self.reports_dir.mkdir(exist_ok=True)
        
        # Create subdirectories
        (self.reports_dir / "analysis").mkdir(exist_ok=True)
        (self.reports_dir / "screenshots").mkdir(exist_ok=True)
        (self.reports_dir / "scenarios").mkdir(exist_ok=True)
        (self.reports_dir / "backups").mkdir(exist_ok=True)
        
        # Index file for quick lookups and analytics
        self.index_file = self.reports_dir / "analysis_index.json"
        self.load_index()
    
    def load_index(self):
        """Load or create report index"""
        try:
            if self.index_file.exists():
                with open(self.index_file, 'r') as f:
                    self.index = json.load(f)
                    
                # Ensure required structure
                if "reports" not in self.index:
                    self.index["reports"] = {}
                if "statistics" not in self.index:
                    self.index["statistics"] = {}
                    
            else:
                self.index = {
                    "version": "2.0",
                    "created": datetime.now().isoformat(),
                    "reports": {},
                    "statistics": {
                        "total_reports": 0,
                        "total_craft_bugs": 0,
                        "avg_score": 0,
                        "last_cleanup": None
                    },
                    "last_updated": None
                }
                self.save_index()
                
        except Exception as e:
            logger.warning(f"Could not load index, creating new: {e}")
            self.index = {
                "version": "2.0",
                "created": datetime.now().isoformat(),
                "reports": {},
                "statistics": {
                    "total_reports": 0,
                    "total_craft_bugs": 0,
                    "avg_score": 0,
                    "last_cleanup": None
                },
                "last_updated": None
            }
    
    def save_index(self):
        """Save report index to disk with backup"""
        try:
            # Create backup of existing index
            if self.index_file.exists():
                backup_path = self.reports_dir / "backups" / f"index_backup_{int(datetime.now().timestamp())}.json"
                shutil.copy2(self.index_file, backup_path)
                
                # Keep only last 5 backups
                backups = sorted((self.reports_dir / "backups").glob("index_backup_*.json"))
                if len(backups) > 5:
                    for old_backup in backups[:-5]:
                        old_backup.unlink()
            
            # Update metadata
            self.index["last_updated"] = datetime.now().isoformat()
            
            # Save index
            with open(self.index_file, 'w') as f:
                json.dump(self.index, f, indent=2, default=str)
                
        except Exception as e:
            logger.error(f"Failed to save index: {e}")
    
    def save_report(self, analysis_id: str, report_data: Dict[str, Any]) -> str:
        """Save report to disk and update index with comprehensive metadata"""
        try:
            # Generate filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"analysis_{analysis_id}_{timestamp}.json"
            file_path = self.reports_dir / "analysis" / filename
            
            # Enhance report data with storage metadata
            enhanced_report = {
                **report_data,
                "storage_metadata": {
                    "analysis_id": analysis_id,
                    "saved_timestamp": datetime.now().isoformat(),
                    "file_path": str(file_path),
                    "filename": filename,
                    "version": "2.0",
                    "file_size_bytes": 0  # Will be updated after saving
                }
            }
            
            # Save to disk
            with open(file_path, 'w') as f:
                json.dump(enhanced_report, f, indent=2, default=str)
            
            # Update file size
            file_size = file_path.stat().st_size
            enhanced_report["storage_metadata"]["file_size_bytes"] = file_size
            
            # Re-save with correct file size
            with open(file_path, 'w') as f:
                json.dump(enhanced_report, f, indent=2, default=str)
            
            # Update index with comprehensive metadata
            craft_bugs_count = 0
            pattern_issues_count = 0
            
            # Extract craft bug counts
            if "craft_bugs_detected" in report_data:
                craft_bugs_count = len(report_data["craft_bugs_detected"])
            elif "craft_bugs" in report_data:
                craft_bugs_count = len(report_data["craft_bugs"])
            
            # Extract pattern issues count
            if "pattern_issues" in report_data:
                pattern_issues_count = len(report_data["pattern_issues"])
            
            # Calculate comprehensive metadata
            metadata = {
                "analysis_id": analysis_id,
                "file_path": str(file_path),
                "filename": filename,
                "created_at": datetime.now().isoformat(),
                "file_size": file_size,
                
                # Analysis metadata
                "analysis_type": report_data.get("type", "unknown"),
                "scenario_type": report_data.get("scenario_type", "unknown"),
                "url": report_data.get("url"),
                "scenario_path": report_data.get("scenario_path"),
                "app_path": report_data.get("app_path"),
                
                # Scoring and results
                "overall_score": report_data.get("overall_score", 0),
                "status": report_data.get("status", "unknown"),
                
                # Craft bug analysis
                "craft_bugs_count": craft_bugs_count,
                "pattern_issues_count": pattern_issues_count,
                "total_issues": craft_bugs_count + pattern_issues_count,
                
                # Performance metrics
                "total_duration_ms": report_data.get("total_duration_ms", 0),
                "successful_steps": 0,
                "total_steps": 0,
                
                # Enhanced metadata
                "has_screenshots": bool(self._count_screenshots(report_data)),
                "browser_automation": report_data.get("type") == "realistic_scenario",
                "modules_analyzed": list(report_data.get("modules", {}).keys()) if "modules" in report_data else [],
            }
            
            # Extract step information if available
            if "steps" in report_data:
                metadata["total_steps"] = len(report_data["steps"])
                metadata["successful_steps"] = len([s for s in report_data["steps"] if s.get("status") == "success"])
                metadata["step_success_rate"] = metadata["successful_steps"] / metadata["total_steps"] if metadata["total_steps"] > 0 else 0
            elif "scenario_results" in report_data:
                metadata["total_steps"] = len(report_data["scenario_results"])
                metadata["successful_steps"] = len([s for s in report_data["scenario_results"] if s.get("status") in ["success", "passed"]])
                metadata["step_success_rate"] = metadata["successful_steps"] / metadata["total_steps"] if metadata["total_steps"] > 0 else 0
            
            # Add to index
            self.index["reports"][analysis_id] = metadata
            
            # Update global statistics
            self._update_statistics()
            
            # Save updated index
            self.save_index()
            
            logger.info(f"✅ Report saved: {filename} ({file_size} bytes, {craft_bugs_count} craft bugs)")
            return str(file_path)
            
        except Exception as e:
            logger.error(f"❌ Failed to save report {analysis_id}: {e}")
            raise
    
    def _count_screenshots(self, report_data: Dict[str, Any]) -> int:
        """Count screenshots in the report"""
        count = 0
        
        # Check in steps
        for step in report_data.get("steps", []):
            if step.get("screenshot_path"):
                count += 1
        
        # Check in scenario results
        for scenario in report_data.get("scenario_results", []):
            for step in scenario.get("steps", []):
                if step.get("screenshot_path"):
                    count += 1
        
        return count
    
    def _update_statistics(self):
        """Update global statistics in index"""
        try:
            reports = self.index["reports"]
            total_reports = len(reports)
            
            if total_reports == 0:
                self.index["statistics"] = {
                    "total_reports": 0,
                    "total_craft_bugs": 0,
                    "avg_score": 0,
                    "last_cleanup": self.index["statistics"].get("last_cleanup")
                }
                return
            
            # Calculate statistics
            total_craft_bugs = sum(r.get("craft_bugs_count", 0) for r in reports.values())
            total_pattern_issues = sum(r.get("pattern_issues_count", 0) for r in reports.values())
            scores = [r.get("overall_score", 0) for r in reports.values()]
            avg_score = sum(scores) / len(scores) if scores else 0
            
            # Analysis type distribution
            type_counts = {}
            for report in reports.values():
                analysis_type = report.get("analysis_type", "unknown")
                type_counts[analysis_type] = type_counts.get(analysis_type, 0) + 1
            
            # Recent activity (last 7 days)
            recent_cutoff = (datetime.now() - timedelta(days=7)).isoformat()
            recent_reports = [r for r in reports.values() if r.get("created_at", "") > recent_cutoff]
            
            self.index["statistics"] = {
                "total_reports": total_reports,
                "total_craft_bugs": total_craft_bugs,
                "total_pattern_issues": total_pattern_issues,
                "total_issues": total_craft_bugs + total_pattern_issues,
                "avg_score": round(avg_score, 1),
                "min_score": min(scores) if scores else 0,
                "max_score": max(scores) if scores else 0,
                "analysis_type_distribution": type_counts,
                "recent_reports_count": len(recent_reports),
                "last_cleanup": self.index["statistics"].get("last_cleanup"),
                "total_file_size_mb": round(sum(r.get("file_size", 0) for r in reports.values()) / (1024 * 1024), 2)
            }
            
        except Exception as e:
            logger.error(f"Failed to update statistics: {e}")
    
    def load_report(self, analysis_id: str) -> Optional[Dict[str, Any]]:
        """Load report from disk"""
        try:
            if analysis_id not in self.index["reports"]:
                logger.warning(f"Report {analysis_id} not found in index")
                return None
            
            file_path = Path(self.index["reports"][analysis_id]["file_path"])
            
            if not file_path.exists():
                logger.warning(f"Report file not found: {file_path}")
                # Remove from index if file is missing
                del self.index["reports"][analysis_id]
                self.save_index()
                return None
            
            with open(file_path, 'r') as f:
                report_data = json.load(f)
            
            logger.info(f"📊 Report loaded: {analysis_id}")
            return report_data
            
        except Exception as e:
            logger.error(f"❌ Failed to load report {analysis_id}: {e}")
            return None
    
    def list_reports(self, limit: int = 50, offset: int = 0, filters: Optional[Dict] = None) -> Dict[str, Any]:
        """List reports with pagination and filtering"""
        try:
            reports_list = list(self.index["reports"].values())
            
            # Apply filters
            if filters:
                if "analysis_type" in filters:
                    reports_list = [r for r in reports_list if r.get("analysis_type") == filters["analysis_type"]]
                
                if "min_score" in filters:
                    reports_list = [r for r in reports_list if r.get("overall_score", 0) >= filters["min_score"]]
                
                if "max_score" in filters:
                    reports_list = [r for r in reports_list if r.get("overall_score", 100) <= filters["max_score"]]
                
                if "has_craft_bugs" in filters and filters["has_craft_bugs"]:
                    reports_list = [r for r in reports_list if r.get("craft_bugs_count", 0) > 0]
                
                if "url_contains" in filters:
                    search_term = filters["url_contains"].lower()
                    reports_list = [r for r in reports_list if search_term in (r.get("url") or "").lower()]
                
                if "date_from" in filters:
                    date_from = filters["date_from"]
                    reports_list = [r for r in reports_list if r.get("created_at", "") >= date_from]
                
                if "date_to" in filters:
                    date_to = filters["date_to"]
                    reports_list = [r for r in reports_list if r.get("created_at", "") <= date_to]
            
            # Sort by creation date (newest first)
            reports_list.sort(key=lambda x: x.get("created_at", ""), reverse=True)
            
            # Apply pagination
            total_count = len(reports_list)
            paginated_reports = reports_list[offset:offset + limit]
            
            return {
                "reports": paginated_reports,
                "pagination": {
                    "total": total_count,
                    "limit": limit,
                    "offset": offset,
                    "has_more": offset + limit < total_count
                },
                "filters_applied": filters or {},
                "statistics": self.index["statistics"]
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to list reports: {e}")
            return {
                "reports": [],
                "pagination": {"total": 0, "limit": limit, "offset": offset, "has_more": False},
                "error": str(e)
            }
    
    def search_reports(self, query: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Advanced search functionality"""
        try:
            results = []
            
            for analysis_id, metadata in self.index["reports"].items():
                match = True
                
                # Search in URL
                if "url" in query and query["url"]:
                    if not metadata.get("url") or query["url"].lower() not in metadata["url"].lower():
                        match = False
                
                # Score range
                if "score_min" in query and metadata.get("overall_score", 0) < query["score_min"]:
                    match = False
                
                if "score_max" in query and metadata.get("overall_score", 100) > query["score_max"]:
                    match = False
                
                # Craft bugs filter
                if "has_craft_bugs" in query and query["has_craft_bugs"]:
                    if metadata.get("craft_bugs_count", 0) == 0:
                        match = False
                
                # Analysis type
                if "analysis_type" in query and query["analysis_type"]:
                    if metadata.get("analysis_type") != query["analysis_type"]:
                        match = False
                
                # Date range
                if "date_from" in query and metadata.get("created_at", "") < query["date_from"]:
                    match = False
                
                if "date_to" in query and metadata.get("created_at", "") > query["date_to"]:
                    match = False
                
                if match:
                    results.append(metadata)
            
            # Sort by relevance (score descending, then date descending)
            results.sort(key=lambda x: (x.get("overall_score", 0), x.get("created_at", "")), reverse=True)
            
            return results
            
        except Exception as e:
            logger.error(f"❌ Search failed: {e}")
            return []
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get comprehensive analysis statistics"""
        return {
            "index_statistics": self.index["statistics"],
            "storage_info": {
                "reports_directory": str(self.reports_dir),
                "index_file_size": self.index_file.stat().st_size if self.index_file.exists() else 0,
                "total_files": len(list(self.reports_dir.rglob("*.json"))),
                "disk_usage_mb": round(sum(f.stat().st_size for f in self.reports_dir.rglob("*") if f.is_file()) / (1024 * 1024), 2)
            },
            "system_info": {
                "version": self.index.get("version", "1.0"),
                "created": self.index.get("created"),
                "last_updated": self.index.get("last_updated")
            }
        }
    
    def cleanup_old_reports(self, days_to_keep: int = 30) -> Dict[str, Any]:
        """Clean up reports older than specified days"""
        try:
            cutoff_date = datetime.now() - timedelta(days=days_to_keep)
            cutoff_str = cutoff_date.isoformat()
            
            removed_reports = []
            total_size_freed = 0
            
            for analysis_id, metadata in list(self.index["reports"].items()):
                if metadata.get("created_at", "") < cutoff_str:
                    file_path = Path(metadata.get("file_path", ""))
                    
                    # Remove file
                    if file_path.exists():
                        file_size = file_path.stat().st_size
                        file_path.unlink()
                        total_size_freed += file_size
                        
                        # Also remove associated screenshots
                        if "screenshots" in str(file_path):
                            screenshot_dir = self.reports_dir / "screenshots"
                            for screenshot in screenshot_dir.glob(f"*{analysis_id}*"):
                                screenshot.unlink()
                    
                    # Remove from index
                    removed_reports.append({
                        "analysis_id": analysis_id,
                        "created_at": metadata.get("created_at"),
                        "file_size": metadata.get("file_size", 0)
                    })
                    del self.index["reports"][analysis_id]
            
            # Update statistics and save index
            if removed_reports:
                self._update_statistics()
                self.index["statistics"]["last_cleanup"] = datetime.now().isoformat()
                self.save_index()
            
            logger.info(f"🧹 Cleaned up {len(removed_reports)} old reports, freed {total_size_freed / (1024*1024):.2f} MB")
            
            return {
                "removed_count": len(removed_reports),
                "size_freed_mb": round(total_size_freed / (1024*1024), 2),
                "removed_reports": removed_reports[:10],  # Show first 10 for reference
                "cutoff_date": cutoff_str
            }
            
        except Exception as e:
            logger.error(f"❌ Cleanup failed: {e}")
            return {"error": str(e)}
    
    def delete_report(self, analysis_id: str) -> bool:
        """Delete a specific report"""
        try:
            if analysis_id not in self.index["reports"]:
                return False
            
            metadata = self.index["reports"][analysis_id]
            file_path = Path(metadata.get("file_path", ""))
            
            # Remove file
            if file_path.exists():
                file_path.unlink()
            
            # Remove from index
            del self.index["reports"][analysis_id]
            
            # Update statistics and save
            self._update_statistics()
            self.save_index()
            
            logger.info(f"🗑️ Report {analysis_id} deleted")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to delete report {analysis_id}: {e}")
            return False
    
    def export_reports(self, analysis_ids: List[str], export_path: str) -> str:
        """Export specific reports to a ZIP file"""
        try:
            import zipfile
            
            export_file = Path(export_path)
            export_file.parent.mkdir(parents=True, exist_ok=True)
            
            with zipfile.ZipFile(export_file, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                for analysis_id in analysis_ids:
                    if analysis_id in self.index["reports"]:
                        metadata = self.index["reports"][analysis_id]
                        file_path = Path(metadata.get("file_path", ""))
                        
                        if file_path.exists():
                            zip_file.write(file_path, f"{analysis_id}.json")
                
                # Add index for reference
                zip_file.writestr("export_index.json", json.dumps({
                    "exported_reports": analysis_ids,
                    "export_timestamp": datetime.now().isoformat(),
                    "total_reports": len(analysis_ids)
                }, indent=2))
            
            logger.info(f"📦 Exported {len(analysis_ids)} reports to {export_file}")
            return str(export_file)
            
        except Exception as e:
            logger.error(f"❌ Export failed: {e}")
            raise

# Global report handler instance
_report_handler = None

def get_report_handler() -> EnhancedReportHandler:
    """Get or create the global report handler instance"""
    global _report_handler
    if _report_handler is None:
        _report_handler = EnhancedReportHandler()
    return _report_handler

def save_analysis_to_disk(analysis_id: str, report_data: Dict[str, Any]) -> str:
    """Save analysis report to disk"""
    return get_report_handler().save_report(analysis_id, report_data)

def load_analysis_from_disk(analysis_id: str) -> Optional[Dict[str, Any]]:
    """Load analysis report from disk"""
    return get_report_handler().load_report(analysis_id)

def list_saved_reports(limit: int = 50, offset: int = 0, filters: Optional[Dict] = None) -> Dict[str, Any]:
    """List saved reports with pagination and filtering"""
    return get_report_handler().list_reports(limit, offset, filters)

def get_report_statistics() -> Dict[str, Any]:
    """Get comprehensive report statistics"""
    return get_report_handler().get_statistics()

def search_saved_reports(query: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Search saved reports"""
    return get_report_handler().search_reports(query)

def cleanup_old_reports(days_to_keep: int = 30) -> Dict[str, Any]:
    """Clean up old reports"""
    return get_report_handler().cleanup_old_reports(days_to_keep)
