#!/usr/bin/env python3
"""
Test Enhanced Media Reporting - Screenshots and Videos with Issues
"""

import asyncio
import json
import os
from datetime import datetime
from pathlib import Path
from enhanced_report_generator import EnhancedReportGenerator
from scenario_executor import ScenarioExecutor

async def test_enhanced_media_reporting():
    """Test that screenshots and videos are properly associated with findings"""
    
    print("🧪 Testing Enhanced Media Reporting with Screenshots and Videos")
    print("=" * 60)
    
    # Initialize components
    enhanced_generator = EnhancedReportGenerator()
    scenario_executor = ScenarioExecutor()
    
    # Test analysis ID
    analysis_id = f"test_media_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    print(f"📋 Analysis ID: {analysis_id}")
    
    # Create sample analysis data with findings
    sample_analysis = {
        "analysis_id": analysis_id,
        "timestamp": datetime.now().isoformat(),
        "url": "http://127.0.0.1:8080/mocks/word/basic-doc.html",
        "mode": "real_browser",
        "overall_score": 75,
        "modules": {
            "performance": {
                "score": 90,
                "findings": []
            },
            "accessibility": {
                "score": 70,
                "findings": [
                    {
                        "type": "accessibility",
                        "severity": "high",
                        "message": "Form input missing accessible label",
                        "element": "input[type='text']",
                        "recommendation": "Add aria-label or associated label element"
                    }
                ]
            },
            "ux_heuristics": {
                "score": 60,
                "findings": [
                    {
                        "type": "craft_bug",
                        "severity": "high",
                        "message": "Craft Bug (Category B): Layout thrash detected: 10 events",
                        "element": "layout_system",
                        "craft_bug": True,
                        "category": "Craft Bug Category B",
                        "recommendation": "Optimize layout calculations to prevent thrashing"
                    },
                    {
                        "type": "craft_bug",
                        "severity": "medium",
                        "message": "Craft Bug (Category C): Input lag detected: 67ms delay",
                        "element": "input[type='text']",
                        "craft_bug": True,
                        "category": "Craft Bug Category C",
                        "recommendation": "Reduce input processing time"
                    }
                ]
            }
        }
    }
    
    # Create sample screenshots (simulating captured screenshots)
    sample_screenshots = [
        {
            "filename": f"{analysis_id}_issue_accessibility_high_20250812_143000.png",
            "file_path": f"reports/enhanced/screenshots/{analysis_id}_issue_accessibility_high_20250812_143000.png",
            "base64": "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg==",  # 1x1 transparent PNG
            "timestamp": "20250812_143000"
        },
        {
            "filename": f"{analysis_id}_issue_craft_bug_high_20250812_143100.png",
            "file_path": f"reports/enhanced/screenshots/{analysis_id}_issue_craft_bug_high_20250812_143100.png",
            "base64": "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg==",
            "timestamp": "20250812_143100"
        },
        {
            "filename": f"{analysis_id}_issue_craft_bug_medium_20250812_143200.png",
            "file_path": f"reports/enhanced/screenshots/{analysis_id}_issue_craft_bug_medium_20250812_143200.png",
            "base64": "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg==",
            "timestamp": "20250812_143200"
        }
    ]
    
    # Create sample video data
    sample_video = {
        "filename": f"{analysis_id}_recording_20250812_143000.webm",
        "file_path": f"reports/enhanced/videos/{analysis_id}_recording_20250812_143000.webm",
        "base64": "dGVzdCB2aWRlbyBkYXRh",  # base64 encoded "test video data"
        "timestamp": "20250812_143000"
    }
    
    print("📸 Sample screenshots created:")
    for screenshot in sample_screenshots:
        print(f"   - {screenshot['filename']}")
    
    print(f"🎥 Sample video created: {sample_video['filename']}")
    
    # Generate enhanced report
    print("\n🔧 Generating enhanced report...")
    enhanced_report = enhanced_generator.generate_enhanced_report(
        sample_analysis, 
        sample_screenshots, 
        sample_video
    )
    
    # Save enhanced report
    enhanced_filepath = enhanced_generator.save_enhanced_report(enhanced_report)
    print(f"💾 Enhanced report saved: {enhanced_filepath}")
    
    # Generate HTML report
    html_filepath = enhanced_generator.generate_html_report(enhanced_report)
    print(f"🌐 HTML report generated: {html_filepath}")
    
    # Verify media association
    print("\n🔍 Verifying media association with findings...")
    
    findings_with_media = 0
    total_findings = 0
    
    for module_name, module_data in enhanced_report['modules'].items():
        findings = module_data.get('findings', [])
        for finding in findings:
            total_findings += 1
            if finding.get('screenshot') or finding.get('screenshot_base64'):
                findings_with_media += 1
                print(f"✅ Finding '{finding.get('message', 'Unknown')}' has media:")
                if finding.get('screenshot'):
                    print(f"   📸 Screenshot: {finding['screenshot']}")
                if finding.get('screenshot_base64'):
                    print(f"   📸 Base64 Screenshot: Available")
                if finding.get('video'):
                    print(f"   🎥 Video: {finding['video']}")
            else:
                print(f"❌ Finding '{finding.get('message', 'Unknown')}' has NO media")
    
    print(f"\n📊 Media Association Summary:")
    print(f"   Total findings: {total_findings}")
    print(f"   Findings with media: {findings_with_media}")
    print(f"   Media coverage: {(findings_with_media/total_findings)*100:.1f}%")
    
    # Test web UI compatibility
    print("\n🌐 Testing Web UI compatibility...")
    
    # Create a sample report structure that the web UI expects
    web_ui_report = {
        "analysis_id": analysis_id,
        "url": sample_analysis["url"],
        "status": "completed",
        "total_issues": total_findings,
        "modules": [],
        "timestamp": sample_analysis["timestamp"],
        "overall_score": sample_analysis["overall_score"],
        "has_screenshots": True
    }
    
    # Convert findings to web UI format
    for module_name, module_data in enhanced_report['modules'].items():
        web_ui_module = {
            "key": module_name,
            "title": module_name.title(),
            "score": module_data.get('score', 0),
            "findings": []
        }
        
        for finding in module_data.get('findings', []):
            web_ui_finding = {
                "type": finding.get('type', 'unknown'),
                "message": finding.get('message', ''),
                "severity": finding.get('severity', 'medium'),
                "element": finding.get('element', ''),
                "recommendation": finding.get('recommendation', ''),
                "screenshot": finding.get('screenshot', ''),
                "screenshot_base64": finding.get('screenshot_base64', ''),
                "video": finding.get('video', '')
            }
            web_ui_module["findings"].append(web_ui_finding)
        
        web_ui_report["modules"].append(web_ui_module)
    
    # Save web UI compatible report
    web_ui_filepath = f"reports/enhanced/{analysis_id}_web_ui.json"
    with open(web_ui_filepath, 'w') as f:
        json.dump(web_ui_report, f, indent=2)
    
    print(f"💾 Web UI compatible report saved: {web_ui_filepath}")
    
    print("\n✅ Enhanced Media Reporting Test Complete!")
    print(f"📁 Reports available in: reports/enhanced/")
    print(f"🌐 Open HTML report: {html_filepath}")
    
    return {
        "analysis_id": analysis_id,
        "enhanced_report": enhanced_filepath,
        "html_report": html_filepath,
        "web_ui_report": web_ui_filepath,
        "findings_with_media": findings_with_media,
        "total_findings": total_findings,
        "media_coverage": (findings_with_media/total_findings)*100
    }

if __name__ == "__main__":
    result = asyncio.run(test_enhanced_media_reporting())
    print(f"\n🎯 Test Results: {result}")
