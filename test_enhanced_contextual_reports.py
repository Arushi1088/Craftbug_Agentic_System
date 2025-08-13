#!/usr/bin/env python3
"""
Test script for Enhanced Contextual Media Reports
"""

import asyncio
import json
from pathlib import Path
from enhanced_report_generator import EnhancedReportGenerator

async def test_contextual_media_reports():
    """Test the enhanced report generator with contextual media"""
    
    print("🚀 Testing Enhanced Contextual Media Reports")
    print("=" * 50)
    
    # Initialize the report generator
    generator = EnhancedReportGenerator()
    
    # Sample analysis data with different types of issues
    sample_analysis = {
        "analysis_id": "test_contextual_123",
        "timestamp": "2024-01-15T10:30:00Z",
        "url": "http://127.0.0.1:8080/mocks/word/basic-doc.html",
        "mode": "real_browser",
        "overall_score": 72,
        "modules": {
            "performance": {
                "score": 85,
                "findings": [
                    {
                        "type": "performance",
                        "severity": "high",
                        "message": "Slow loading detected: Page takes 3.2 seconds to load",
                        "element": "page_load",
                        "category": "performance"
                    },
                    {
                        "type": "performance", 
                        "severity": "medium",
                        "message": "Animation lag detected during button hover",
                        "element": "button_hover",
                        "category": "performance"
                    }
                ]
            },
            "accessibility": {
                "score": 65,
                "findings": [
                    {
                        "type": "accessibility",
                        "severity": "high", 
                        "message": "Button contrast is too low (2.1:1 ratio)",
                        "element": "submit_button",
                        "category": "accessibility"
                    },
                    {
                        "type": "accessibility",
                        "severity": "medium",
                        "message": "Form input missing accessible label",
                        "element": "email_input",
                        "category": "accessibility"
                    }
                ]
            },
            "ux_heuristics": {
                "score": 70,
                "findings": [
                    {
                        "type": "craft_bug",
                        "severity": "high",
                        "message": "Craft Bug (Category B): Layout thrash detected: 8 events",
                        "element": "layout_system",
                        "craft_bug": True,
                        "category": "Craft Bug Category B"
                    },
                    {
                        "type": "ux",
                        "severity": "medium",
                        "message": "Inconsistent spacing between form elements",
                        "element": "form_layout",
                        "category": "ux"
                    }
                ]
            }
        }
    }
    
    # Sample contextual media data
    contextual_media = {
        "performance_slow_loading": {
            "category": "performance",
            "issue_type": "performance",
            "severity": "high",
            "timestamp": "2024-01-15T10:30:05Z",
            "video": "reports/enhanced/videos/test_contextual_123_issue_capture_performance_high_1705312205.webm",
            "video_filename": "test_contextual_123_issue_capture_performance_high_1705312205.webm"
        },
        "accessibility_contrast": {
            "category": "visual",
            "issue_type": "accessibility", 
            "severity": "high",
            "timestamp": "2024-01-15T10:30:10Z",
            "screenshot": "reports/enhanced/screenshots/test_contextual_123_issue_capture_accessibility_high_1705312210.png",
            "screenshot_base64": "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg==",
            "screenshot_filename": "test_contextual_123_issue_capture_accessibility_high_1705312210.png"
        },
        "ux_spacing": {
            "category": "visual",
            "issue_type": "ux",
            "severity": "medium", 
            "timestamp": "2024-01-15T10:30:15Z",
            "screenshot": "reports/enhanced/screenshots/test_contextual_123_issue_capture_ux_medium_1705312215.png",
            "screenshot_base64": "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg==",
            "screenshot_filename": "test_contextual_123_issue_capture_ux_medium_1705312215.png"
        }
    }
    
    # Generate enhanced report
    print("📊 Generating enhanced report with contextual media...")
    enhanced_report = generator.generate_enhanced_report(
        sample_analysis,
        screenshots=[],  # We'll use contextual media instead
        video_data=None,
        contextual_media=contextual_media
    )
    
    # Save the report
    print("💾 Saving enhanced report...")
    filepath = generator.save_enhanced_report(enhanced_report)
    print(f"✅ Report saved: {filepath}")
    
    # Generate HTML report
    print("🌐 Generating HTML report...")
    html_filepath = generator.generate_html_report(enhanced_report)
    print(f"✅ HTML report generated: {html_filepath}")
    
    # Display report summary
    print("\n📋 Report Summary:")
    print(f"   Analysis ID: {enhanced_report['analysis_id']}")
    print(f"   Overall Score: {enhanced_report['overall_score']}/100")
    print(f"   Contextual Media: {enhanced_report['enhanced_features']['contextual_media_count']} items")
    print(f"   Craft Bugs: {enhanced_report['enhanced_features']['craft_bugs_detected']}")
    
    # Show issue categorization
    print("\n🎯 Issue Categorization:")
    for module_name, module_data in enhanced_report['modules'].items():
        print(f"   {module_name.title()}:")
        for finding in module_data.get('findings', []):
            category = generator.categorize_issue(finding)
            has_media = 'contextual_media' in finding
            media_type = finding.get('contextual_media', {}).get('category', 'none') if has_media else 'none'
            print(f"     - {finding['message'][:50]}... ({category}, media: {media_type})")
    
    print("\n🎉 Test completed successfully!")
    print(f"📁 Check the generated reports in: {generator.output_dir}")

if __name__ == "__main__":
    asyncio.run(test_contextual_media_reports())
