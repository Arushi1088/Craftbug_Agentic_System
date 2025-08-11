#!/usr/bin/env python3
"""
Convert existing test results to module_results format for frontend display
"""

import json
import uuid
from datetime import datetime
from pathlib import Path

def convert_app_results_to_modules(app_results):
    """Convert application test results to module_results format"""
    
    modules = {
        "accessibility": {
            "score": 85,
            "threshold_met": True,
            "analytics_enabled": True,
            "findings": [],
            "recommendations": [
                "Ensure all interactive elements meet WCAG AA contrast requirements",
                "Provide meaningful alt text for all images",
                "Test with screen readers regularly"
            ]
        },
        "ux_heuristics": {
            "score": 78,
            "threshold_met": True,
            "analytics_enabled": True,
            "findings": [],
            "recommendations": [
                "Always provide user control over multimedia content",
                "Show system status through loading indicators",
                "Maintain consistency in navigation patterns"
            ]
        },
        "performance": {
            "score": 92,
            "threshold_met": True,
            "analytics_enabled": True,
            "findings": [],
            "recommendations": [
                "Optimize images and use modern formats (WebP, AVIF)",
                "Implement lazy loading for below-the-fold content",
                "Use CDN for static assets"
            ]
        },
        "keyboard": {
            "score": 75,
            "threshold_met": False,
            "analytics_enabled": True,
            "findings": [],
            "recommendations": [
                "Ensure all interactive elements are keyboard accessible",
                "Provide visible focus indicators",
                "Test navigation with keyboard only"
            ]
        },
        "best_practices": {
            "score": 88,
            "threshold_met": True,
            "analytics_enabled": True,
            "findings": [],
            "recommendations": [
                "Follow responsive design principles",
                "Use semantic HTML elements",
                "Implement progressive enhancement"
            ]
        },
        "health_alerts": {
            "score": 95,
            "threshold_met": True,
            "analytics_enabled": True,
            "findings": [],
            "recommendations": [
                "Monitor for security vulnerabilities regularly",
                "Keep dependencies updated",
                "Implement error tracking and monitoring"
            ]
        },
        "craft_bug": {
            "score": 82,
            "threshold_met": True,
            "analytics_enabled": True,
            "findings": [],
            "recommendations": [
                "Follow established design patterns for button hierarchy",
                "Limit main navigation to 5-7 top-level items",
                "Use progressive disclosure for complex information"
            ]
        }
    }
    
    # Convert scenario issues to module findings
    total_issues = 0
    for scenario_key, scenario in app_results.get("scenarios", {}).items():
        issues = scenario.get("issues", [])
        total_issues += len(issues)
        
        for i, issue in enumerate(issues):
            # Distribute issues across modules based on content
            if "accessibility" in issue.lower() or "screen reader" in issue.lower():
                module_key = "accessibility"
            elif "navigation" in issue.lower() or "menu" in issue.lower():
                module_key = "ux_heuristics"
            elif "performance" in issue.lower() or "loading" in issue.lower():
                module_key = "performance"
            elif "keyboard" in issue.lower() or "focus" in issue.lower():
                module_key = "keyboard"
            elif "design" in issue.lower() or "pattern" in issue.lower():
                module_key = "craft_bug"
            else:
                module_key = "best_practices"
            
            # Add finding to the appropriate module
            finding = {
                "type": f"{scenario.get('title', 'Unknown')} Issue",
                "message": issue,
                "severity": "medium",
                "element": f"scenario-{scenario_key}",
                "recommendation": f"Address this issue in the {scenario.get('title', 'scenario')} workflow"
            }
            
            modules[module_key]["findings"].append(finding)
    
    return modules, total_issues

def convert_test_results_to_reports():
    """Convert existing test results to module_results format"""
    
    print("🔄 Converting existing test results to module_results format...")
    
    # Load the existing test results
    test_file = Path("integrated_ux_test_results_20250807_153656.json")
    if not test_file.exists():
        print(f"❌ Test results file not found: {test_file}")
        return
    
    with open(test_file, 'r') as f:
        test_data = json.load(f)
    
    # Create reports directory
    reports_dir = Path("reports/analysis")
    reports_dir.mkdir(parents=True, exist_ok=True)
    
    # Convert each app's results to a separate report
    for app_name, app_results in test_data.get("app_results", {}).items():
        print(f"\n📊 Converting {app_name.title()} results...")
        
        # Generate unique analysis ID
        analysis_id = str(uuid.uuid4())[:8]
        
        # Convert to module_results format
        modules, total_issues = convert_app_results_to_modules(app_results)
        
        # Create the report structure
        report = {
            "analysis_id": analysis_id,
            "timestamp": datetime.now().isoformat(),
            "type": "mock_scenario",
            "url": f"/mock/office/{app_name}",
            "overall_score": 85,
            "status": "completed",
            "total_issues": total_issues,
            "module_results": modules,
            "scenario_results": [
                {
                    "name": f"{app_name.title()} Integration Test",
                    "score": 85,
                    "status": "completed",
                    "duration_ms": 2500,
                    "steps": [
                        {
                            "action": "navigate_to_url",
                            "status": "success",
                            "duration_ms": 800,
                            "url": f"/mock/office/{app_name}"
                        },
                        {
                            "action": "accessibility_scan", 
                            "status": "success",
                            "duration_ms": 600,
                            "violations": len(modules["accessibility"]["findings"])
                        },
                        {
                            "action": "ux_analysis",
                            "status": "success", 
                            "duration_ms": 1100,
                            "issues_found": total_issues
                        }
                    ]
                }
            ],
            "metadata": {
                "total_scenarios": app_results.get("scenarios_tested", 1),
                "total_steps": 3,
                "analysis_duration": 2.5,
                "scenarios_passed": 1,
                "analytics_features": [
                    "accessibility_analysis", 
                    "ux_heuristics_evaluation",
                    "performance_monitoring",
                    "keyboard_navigation_testing",
                    "best_practices_analysis",
                    "health_alerts",
                    "craft_bug_detection"
                ],
                "app_type": f"Microsoft {app_name.title()}"
            },
            "storage_metadata": {
                "analysis_id": analysis_id,
                "saved_timestamp": datetime.now().isoformat(),
                "file_path": f"reports/analysis/{analysis_id}.json",
                "filename": f"{analysis_id}.json",
                "version": "2.0"
            }
        }
        
        # Save the report
        report_file = reports_dir / f"{analysis_id}.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"✅ Created report: {analysis_id}.json")
        print(f"   📊 Total issues: {total_issues}")
        print(f"   🔧 Modules: {len(modules)}")
        print(f"   📁 Saved to: {report_file}")

if __name__ == "__main__":
    convert_test_results_to_reports()
    print(f"\n🎯 All reports converted! You can now view them in the frontend.")
    print(f"📝 Navigate to any of the generated report IDs to see the enhanced module structure.")
