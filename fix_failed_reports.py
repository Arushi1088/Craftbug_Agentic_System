#!/usr/bin/env python3
"""
Fix existing failed reports to have proper module structure
"""

import json
import os
from pathlib import Path
from datetime import datetime

def fix_failed_report(report_data):
    """Convert a failed report to proper module structure"""
    if report_data.get("status") != "failed":
        return report_data  # Already in good shape
    
    # Create a proper module structure for failed reports
    fixed_report = {
        "analysis_id": report_data.get("analysis_id", "unknown"),
        "status": "failed",
        "error": report_data.get("error", "Unknown error"),
        "timestamp": report_data.get("timestamp", datetime.now().isoformat()),
        "type": "error_report",
        "url": report_data.get("url", ""),
        "scenario_path": report_data.get("scenario_path", ""),
        "overall_score": 0,
        "total_issues": 1,
        "module_results": {
            "error_report": {
                "title": "Analysis Error",
                "score": 0,
                "findings": [
                    {
                        "type": "error",
                        "message": f"Analysis failed: {report_data.get('error', 'Unknown error')}",
                        "severity": "high",
                        "recommendation": "Check server logs and try again. Verify scenario file and target URL are valid."
                    }
                ],
                "recommendations": [
                    "Verify the target URL is accessible",
                    "Check that the scenario file exists and is valid",
                    "Ensure required dependencies are installed"
                ],
                "threshold_met": False,
                "analytics_enabled": False
            }
        },
        "scenario_results": [],
        "craft_bugs_detected": [],
        "performance_summary": {
            "total_steps": 0,
            "successful_steps": 0,
            "total_craft_bugs": 0
        }
    }
    
    # Preserve any existing storage metadata
    if "storage_metadata" in report_data:
        fixed_report["storage_metadata"] = report_data["storage_metadata"]
    
    return fixed_report

def main():
    """Fix all failed reports in the analysis directory"""
    reports_dir = Path("reports/analysis")
    if not reports_dir.exists():
        print("❌ Reports directory not found")
        return
    
    fixed_count = 0
    total_count = 0
    
    for report_file in reports_dir.glob("analysis_*.json"):
        if "demo" in report_file.name:
            continue  # Skip demo files
            
        total_count += 1
        
        try:
            with open(report_file, 'r') as f:
                report_data = json.load(f)
            
            if report_data.get("status") == "failed" and "module_results" not in report_data:
                print(f"🔧 Fixing failed report: {report_file.name}")
                
                fixed_report = fix_failed_report(report_data)
                
                # Write back the fixed report
                with open(report_file, 'w') as f:
                    json.dump(fixed_report, f, indent=2)
                
                fixed_count += 1
                print(f"✅ Fixed: {report_file.name}")
            else:
                print(f"✅ Already good: {report_file.name}")
                
        except Exception as e:
            print(f"❌ Error processing {report_file.name}: {e}")
    
    print(f"\n📊 Summary:")
    print(f"   Total reports: {total_count}")
    print(f"   Fixed reports: {fixed_count}")
    print(f"   Status: {'✅ All reports fixed' if fixed_count > 0 else '✅ No fixes needed'}")

if __name__ == "__main__":
    main()
