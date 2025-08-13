#!/usr/bin/env python3
"""
Enhanced Report Generator with Contextual Screenshots, Videos, and Craft Bug Capture
"""

import json
import os
import time
import base64
import asyncio
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
from playwright.sync_api import sync_playwright
import logging

logger = logging.getLogger(__name__)

class EnhancedReportGenerator:
    def __init__(self, output_dir: str = "reports/enhanced"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.screenshots_dir = self.output_dir / "screenshots"
        self.videos_dir = self.output_dir / "videos"
        self.screenshots_dir.mkdir(exist_ok=True)
        self.videos_dir.mkdir(exist_ok=True)
        
    async def capture_screenshot_async(self, page, analysis_id: str, step_name: str, issue_type: str = "general"):
        """Capture screenshot of current page state (async version)"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{analysis_id}_{step_name}_{issue_type}_{timestamp}.png"
            filepath = self.screenshots_dir / filename
            
            # Take screenshot (async)
            screenshot_bytes = await page.screenshot(full_page=True)
            
            # Save to file
            with open(filepath, "wb") as f:
                f.write(screenshot_bytes)
            
            # Convert to base64 for embedding in report
            screenshot_b64 = base64.b64encode(screenshot_bytes).decode('utf-8')
            
            logger.info(f"📸 Screenshot captured: {filename}")
            return {
                "file_path": str(filepath),
                "base64": screenshot_b64,
                "filename": filename,
                "timestamp": timestamp
            }
        except Exception as e:
            logger.error(f"Failed to capture screenshot: {e}")
            return None
    
    def capture_screenshot(self, page, analysis_id: str, step_name: str, issue_type: str = "general") -> str:
        """Capture screenshot of current page state (sync version for compatibility)"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{analysis_id}_{step_name}_{issue_type}_{timestamp}.png"
            filepath = self.screenshots_dir / filename
            
            # Take screenshot
            screenshot_bytes = page.screenshot(full_page=True)
            
            # Save to file
            with open(filepath, "wb") as f:
                f.write(screenshot_bytes)
            
            # Convert to base64 for embedding in report
            screenshot_b64 = base64.b64encode(screenshot_bytes).decode('utf-8')
            
            logger.info(f"📸 Screenshot captured: {filename}")
            return {
                "file_path": str(filepath),
                "base64": screenshot_b64,
                "filename": filename,
                "timestamp": timestamp
            }
        except Exception as e:
            logger.error(f"Failed to capture screenshot: {e}")
            return None
    
    def start_video_recording(self, page, analysis_id: str) -> str:
        """Start video recording"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{analysis_id}_recording_{timestamp}.webm"
            filepath = self.videos_dir / filename
            
            # Start video recording
            page.video.start(path=str(filepath))
            
            logger.info(f"🎥 Video recording started: {filename}")
            return str(filepath)
        except Exception as e:
            logger.error(f"Failed to start video recording: {e}")
            return None
    
    def stop_video_recording(self, page) -> Optional[str]:
        """Stop video recording and return file path"""
        try:
            video_path = page.video.path()
            page.video.stop()
            
            if video_path and os.path.exists(video_path):
                # Convert to base64 for embedding
                with open(video_path, "rb") as f:
                    video_bytes = f.read()
                video_b64 = base64.b64encode(video_bytes).decode('utf-8')
                
                return {
                    "file_path": video_path,
                    "base64": video_b64,
                    "filename": os.path.basename(video_path),
                    "size_bytes": len(video_bytes)
                }
        except Exception as e:
            logger.error(f"Failed to stop video recording: {e}")
        return None
    
    async def capture_issue_screenshot_async(self, page, analysis_id: str, issue: Dict[str, Any]):
        """Capture screenshot for a specific issue (async version)"""
        issue_type = issue.get("type", "unknown")
        element = issue.get("element", "page")
        severity = issue.get("severity", "medium")
        
        # Try to highlight the problematic element
        try:
            if element != "page" and element != "layout_system" and element != "animation_system":
                # Try to find and highlight the element
                element_selector = issue.get("selector", element)
                if await page.query_selector(element_selector):
                    # Add highlight class temporarily
                    await page.evaluate(f"""
                        (() => {{
                            const el = document.querySelector('{element_selector}');
                            if (el) {{
                                el.style.outline = '3px solid red';
                                el.style.backgroundColor = 'rgba(255, 0, 0, 0.2)';
                            }}
                        }})();
                    """)
                    await asyncio.sleep(0.5)  # Wait for highlight to be visible
        except Exception as e:
            logger.warning(f"Could not highlight element {element}: {e}")
        
        # Capture screenshot
        screenshot_data = await self.capture_screenshot_async(
            page, analysis_id, f"issue_{issue_type}", severity
        )
        
        # Remove highlight
        try:
            await page.evaluate("""
                (() => {
                    document.querySelectorAll('*').forEach(el => {
                        el.style.outline = '';
                        el.style.backgroundColor = '';
                    });
                })();
            """)
        except:
            pass
        
        return screenshot_data
    
    def capture_issue_screenshot(self, page, analysis_id: str, issue: Dict[str, Any]) -> Dict[str, Any]:
        """Capture screenshot for a specific issue (sync version for compatibility)"""
        issue_type = issue.get("type", "unknown")
        element = issue.get("element", "page")
        severity = issue.get("severity", "medium")
        
        # Try to highlight the problematic element
        try:
            if element != "page" and element != "layout_system" and element != "animation_system":
                # Try to find and highlight the element
                element_selector = issue.get("selector", element)
                if page.query_selector(element_selector):
                    # Add highlight class temporarily
                    page.evaluate(f"""
                        (() => {{
                            const el = document.querySelector('{element_selector}');
                            if (el) {{
                                el.style.outline = '3px solid red';
                                el.style.backgroundColor = 'rgba(255, 0, 0, 0.2)';
                            }}
                        }})();
                    """)
                    time.sleep(0.5)  # Wait for highlight to be visible
        except Exception as e:
            logger.warning(f"Could not highlight element {element}: {e}")
        
        # Capture screenshot
        screenshot_data = self.capture_screenshot(
            page, analysis_id, f"issue_{issue_type}", severity
        )
        
        # Remove highlight
        try:
            page.evaluate("""
                (() => {
                    document.querySelectorAll('*').forEach(el => {
                        el.style.outline = '';
                        el.style.backgroundColor = '';
                    });
                })();
            """)
        except:
            pass
        
        return screenshot_data
    
    def categorize_issue(self, finding: Dict[str, Any]) -> str:
        """Categorize issue to determine media type needed"""
        message = finding.get('message', '').lower()
        issue_type = finding.get('type', '').lower()
        
        # Visual issues - need screenshots
        visual_keywords = ['contrast', 'spacing', 'alignment', 'color', 'layout', 'size', 'position', 'margin', 'padding']
        if any(keyword in message for keyword in visual_keywords):
            return 'visual'
        
        # Performance issues - need videos
        performance_keywords = ['lag', 'slow', 'loading', 'responsive', 'delay', 'performance', 'animation', 'transition']
        if any(keyword in message for keyword in performance_keywords):
            return 'performance'
        
        # Functional issues - screenshots or videos depending on clarity
        functional_keywords = ['broken', 'missing', 'error', 'fail', 'not working', 'click', 'interaction']
        if any(keyword in message for keyword in functional_keywords):
            return 'functional'
        
        # Default to visual for most issues
        return 'visual'
    
    async def capture_issue_specific_media(self, page, analysis_id: str, finding: Dict[str, Any], step_name: str = "issue_capture"):
        """Capture issue-specific media based on issue category"""
        try:
            issue_category = self.categorize_issue(finding)
            issue_id = f"{finding.get('type', 'issue')}_{finding.get('severity', 'medium')}_{int(time.time())}"
            
            media_data = {
                "category": issue_category,
                "timestamp": datetime.now().isoformat(),
                "issue_id": issue_id
            }
            
            if issue_category in ['visual', 'functional']:
                # Capture screenshot for visual/functional issues
                screenshot_data = await self.capture_screenshot_async(page, analysis_id, f"{step_name}_{issue_id}", "issue_specific")
                if screenshot_data:
                    media_data["screenshot"] = screenshot_data["file_path"]
                    media_data["screenshot_base64"] = screenshot_data["base64"]
                    media_data["screenshot_filename"] = screenshot_data["filename"]
                    logger.info(f"📸 Issue-specific screenshot captured: {screenshot_data['filename']}")
            
            if issue_category in ['performance', 'functional']:
                # Capture short video for performance issues
                video_data = await self.capture_issue_video(page, analysis_id, issue_id, step_name)
                if video_data:
                    media_data["video"] = video_data["file_path"]
                    media_data["video_filename"] = video_data["filename"]
                    logger.info(f"🎥 Issue-specific video captured: {video_data['filename']}")
            
            return media_data
            
        except Exception as e:
            logger.error(f"Failed to capture issue-specific media: {e}")
            return None
    
    async def capture_issue_video(self, page, analysis_id: str, issue_id: str, step_name: str) -> Optional[Dict[str, Any]]:
        """Capture a short video for performance issues"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{analysis_id}_{step_name}_{issue_id}_{timestamp}.webm"
            filepath = self.videos_dir / filename
            
            # Start video recording
            page.video.start(path=str(filepath))
            
            # Record for 3-5 seconds to capture the issue
            await asyncio.sleep(3)
            
            # Stop recording
            page.video.stop()
            
            logger.info(f"🎥 Issue-specific video captured: {filename}")
            return {
                "file_path": str(filepath),
                "filename": filename,
                "timestamp": timestamp,
                "duration": 3
            }
        except Exception as e:
            logger.error(f"Failed to capture issue video: {e}")
            return None
    
    def generate_enhanced_report(self, analysis_data: Dict[str, Any], 
                                screenshots: List[Dict[str, Any]] = None,
                                video_data: Dict[str, Any] = None,
                                contextual_media: Dict[str, Any] = None) -> Dict[str, Any]:
        """Generate enhanced report with contextual screenshots, videos, and craft bug analysis"""
        
        # Associate media with findings first
        if screenshots:
            analysis_data = self._associate_media_with_findings(analysis_data, screenshots)
        
        # Start with the original report structure
        enhanced_report = {
            "analysis_id": analysis_data.get("analysis_id"),
            "timestamp": analysis_data.get("timestamp"),
            "url": analysis_data.get("url"),
            "mode": analysis_data.get("mode"),
            "overall_score": analysis_data.get("overall_score"),
            "modules": analysis_data.get("modules", {}),
            "execution_time": analysis_data.get("execution_time"),
            "performance_metrics": analysis_data.get("performance_metrics"),
            "scenario_info": analysis_data.get("scenario_info"),
            "requested_id": analysis_data.get("requested_id"),
            "browser_automation": analysis_data.get("browser_automation"),
            "real_analysis": analysis_data.get("real_analysis"),
            
            # Enhanced features
            "enhanced_features": {
                "screenshots_captured": len(screenshots) if screenshots else 0,
                "video_recording": video_data is not None,
                "craft_bugs_detected": self._count_craft_bugs(analysis_data),
                "issue_visualization": True,
                "contextual_media": contextual_media is not None,
                "contextual_media_count": len(contextual_media) if contextual_media else 0
            },
            
            # Media attachments
            "media_attachments": {
                "screenshots": screenshots or [],
                "video": video_data,
                "contextual_media": contextual_media or {}
            },
            
            # Enhanced craft bug analysis
            "craft_bug_analysis": self._analyze_craft_bugs(analysis_data),
            
            # Issue timeline
            "issue_timeline": self._generate_issue_timeline(analysis_data),
        }
        
        # Enhance findings with contextual media
        enhanced_report = self._enhance_findings_with_contextual_media(enhanced_report, contextual_media)
        
        # Add storage metadata
        enhanced_report["storage_metadata"] = {
            "analysis_id": analysis_data.get("analysis_id"),
            "saved_timestamp": datetime.now().isoformat(),
            "file_path": f"reports/enhanced/enhanced_{analysis_data.get('analysis_id')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            "filename": f"enhanced_{analysis_data.get('analysis_id')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            "version": "3.1",
            "file_size_bytes": 0,  # Will be calculated after saving
            "enhanced_features": ["screenshots", "video_recording", "craft_bug_analysis", "issue_timeline", "contextual_media"]
        }
        
        return enhanced_report
    
    def _enhance_findings_with_contextual_media(self, enhanced_report: Dict[str, Any], contextual_media: Dict[str, Any]) -> Dict[str, Any]:
        """Enhance findings with contextual media data"""
        if not contextual_media:
            return enhanced_report
        
        modules = enhanced_report.get("modules", {})
        
        for module_name, module_data in modules.items():
            findings = module_data.get("findings", [])
            
            for finding in findings:
                # Find matching contextual media for this finding
                finding_id = f"{finding.get('type', 'issue')}_{finding.get('severity', 'medium')}"
                
                # Look for matching media by issue characteristics
                for media_id, media_data in contextual_media.items():
                    if (media_data.get('issue_type') == finding.get('type') and 
                        media_data.get('severity') == finding.get('severity')):
                        
                        # Add contextual media to finding
                        if media_data.get('screenshot'):
                            finding['screenshot'] = media_data['screenshot']
                        if media_data.get('screenshot_base64'):
                            finding['screenshot_base64'] = media_data['screenshot_base64']
                        if media_data.get('video'):
                            finding['video'] = media_data['video']
                        
                        # Add media metadata
                        finding['contextual_media'] = {
                            'category': media_data.get('category', 'unknown'),
                            'timestamp': media_data.get('timestamp'),
                            'media_id': media_id
                        }
                        break
        
        return enhanced_report
    
    def _count_craft_bugs(self, analysis_data: Dict[str, Any]) -> int:
        """Count total craft bugs across all modules"""
        count = 0
        modules = analysis_data.get("modules", {})
        
        for module_name, module_data in modules.items():
            findings = module_data.get("findings", [])
            for finding in findings:
                if finding.get("type") == "craft_bug" or finding.get("craft_bug"):
                    count += 1
        
        return count
    
    def _analyze_craft_bugs(self, analysis_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze craft bugs by category and severity"""
        craft_bugs = {
            "total_count": 0,
            "by_category": {},
            "by_severity": {"high": 0, "medium": 0, "low": 0},
            "by_module": {},
            "detailed_analysis": []
        }
        
        modules = analysis_data.get("modules", {})
        
        for module_name, module_data in modules.items():
            findings = module_data.get("findings", [])
            module_craft_bugs = []
            
            for finding in findings:
                if finding.get("type") == "craft_bug" or finding.get("craft_bug"):
                    craft_bugs["total_count"] += 1
                    
                    # Count by severity
                    severity = finding.get("severity", "medium")
                    craft_bugs["by_severity"][severity] += 1
                    
                    # Count by category
                    category = finding.get("category", "Unknown")
                    if category not in craft_bugs["by_category"]:
                        craft_bugs["by_category"][category] = 0
                    craft_bugs["by_category"][category] += 1
                    
                    # Add to module analysis
                    module_craft_bugs.append(finding)
                    
                    # Detailed analysis
                    craft_bugs["detailed_analysis"].append({
                        "module": module_name,
                        "category": category,
                        "severity": severity,
                        "message": finding.get("message"),
                        "element": finding.get("element"),
                        "metric_value": finding.get("metric_value"),
                        "recommendation": finding.get("recommendation")
                    })
            
            if module_craft_bugs:
                craft_bugs["by_module"][module_name] = len(module_craft_bugs)
        
        return craft_bugs
    
    def _associate_media_with_findings(self, analysis_data: Dict[str, Any], screenshots: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Associate screenshots and videos with specific findings"""
        enhanced_data = analysis_data.copy()
        
        # Create a mapping of issue types to screenshots
        screenshot_map = {}
        for screenshot in screenshots:
            filename = screenshot.get('filename', '')
            # Extract issue type from filename (e.g., "analysis_id_issue_craft_bug_high_timestamp.png")
            if 'issue_' in filename:
                parts = filename.split('_')
                for i, part in enumerate(parts):
                    if part == 'issue' and i + 1 < len(parts):
                        issue_type = parts[i + 1]
                        if issue_type not in screenshot_map:
                            screenshot_map[issue_type] = []
                        screenshot_map[issue_type].append(screenshot)
        
        # Associate screenshots with findings
        for module_name, module_data in enhanced_data.get('modules', {}).items():
            findings = module_data.get('findings', [])
            for finding in findings:
                finding_type = finding.get('type', '').lower()
                severity = finding.get('severity', 'medium')
                
                # Look for matching screenshots
                matching_screenshots = []
                for issue_type, screenshots_list in screenshot_map.items():
                    if (issue_type in finding_type or 
                        finding_type in issue_type or 
                        (finding.get('craft_bug') and 'craft' in issue_type)):
                        matching_screenshots.extend(screenshots_list)
                
                # Add the most relevant screenshot to the finding
                if matching_screenshots:
                    # Prefer screenshots with matching severity
                    severity_matches = [s for s in matching_screenshots if severity in s.get('filename', '')]
                    if severity_matches:
                        best_match = severity_matches[0]
                    else:
                        best_match = matching_screenshots[0]
                    
                    finding['screenshot'] = best_match.get('file_path', '')
                    finding['screenshot_base64'] = best_match.get('base64', '')
                    
                    # Also add video if available (for now, we'll add the main video to all findings)
                    # In a more sophisticated implementation, you'd match videos by timestamp
                    if 'video_data' in enhanced_data:
                        finding['video'] = enhanced_data.get('video_data', {}).get('file_path', '')
        
        return enhanced_data
    
    def _generate_issue_timeline(self, analysis_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate timeline of issues detected during analysis"""
        timeline = []
        modules = analysis_data.get("modules", {})
        
        for module_name, module_data in modules.items():
            findings = module_data.get("findings", [])
            
            for finding in findings:
                # Extract timestamp from metric_value if available
                timestamp = None
                metric_value = finding.get("metric_value", {})
                
                if isinstance(metric_value, dict):
                    # Look for timestamp in various possible locations
                    if "timestamp" in metric_value:
                        timestamp = metric_value["timestamp"]
                    elif "layoutShifts" in metric_value and metric_value["layoutShifts"]:
                        timestamp = metric_value["layoutShifts"][0].get("timestamp")
                    elif "animationConflictList" in metric_value and metric_value["animationConflictList"]:
                        timestamp = metric_value["animationConflictList"][0].get("timestamp")
                    elif "inputDelays" in metric_value and metric_value["inputDelays"]:
                        timestamp = metric_value["inputDelays"][0].get("timestamp")
                
                timeline.append({
                    "timestamp": timestamp,
                    "module": module_name,
                    "type": finding.get("type"),
                    "severity": finding.get("severity"),
                    "message": finding.get("message"),
                    "element": finding.get("element"),
                    "category": finding.get("category")
                })
        
        # Sort by timestamp if available
        timeline.sort(key=lambda x: x["timestamp"] or 0)
        return timeline
    
    def save_enhanced_report(self, enhanced_report: Dict[str, Any]) -> str:
        """Save enhanced report to file"""
        filepath = enhanced_report["storage_metadata"]["file_path"]
        
        # Calculate file size
        report_json = json.dumps(enhanced_report, indent=2)
        file_size = len(report_json.encode('utf-8'))
        enhanced_report["storage_metadata"]["file_size_bytes"] = file_size
        
        # Save to file
        with open(filepath, 'w') as f:
            json.dump(enhanced_report, f, indent=2)
        
        logger.info(f"💾 Enhanced report saved: {filepath} ({file_size} bytes)")
        return filepath
    
    def generate_html_report(self, enhanced_report: Dict[str, Any]) -> str:
        """Generate HTML version of the enhanced report"""
        html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Enhanced UX Analysis Report - {enhanced_report['analysis_id']}</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.6;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            overflow: hidden;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }}
        .header h1 {{
            margin: 0;
            font-size: 2.5em;
            font-weight: 300;
        }}
        .header .subtitle {{
            margin-top: 10px;
            opacity: 0.9;
        }}
        .content {{
            padding: 30px;
        }}
        .score-section {{
            display: flex;
            gap: 20px;
            margin-bottom: 30px;
        }}
        .score-card {{
            flex: 1;
            padding: 20px;
            border-radius: 8px;
            text-align: center;
            color: white;
        }}
        .score-card.overall {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        }}
        .score-card.performance {{
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        }}
        .score-card.accessibility {{
            background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        }}
        .score-card.ux {{
            background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
        }}
        .score-number {{
            font-size: 3em;
            font-weight: bold;
            margin-bottom: 10px;
        }}
        .module-section {{
            margin-bottom: 30px;
        }}
        .module-header {{
            background: #f8f9fa;
            padding: 15px 20px;
            border-radius: 8px 8px 0 0;
            border-bottom: 2px solid #e9ecef;
            font-weight: bold;
            font-size: 1.2em;
        }}
        .findings-list {{
            background: white;
            border: 1px solid #e9ecef;
            border-radius: 0 0 8px 8px;
        }}
        .finding-item {{
            padding: 20px;
            border-bottom: 1px solid #e9ecef;
            display: flex;
            align-items: flex-start;
            gap: 20px;
        }}
        .finding-item:last-child {{
            border-bottom: none;
        }}
        .finding-content {{
            flex: 1;
            min-width: 0;
        }}
        .finding-media-sidebar {{
            flex-shrink: 0;
            width: 350px;
            max-width: 350px;
        }}
        .media-container {{
            background: #f8f9fa;
            border: 1px solid #e9ecef;
            border-radius: 6px;
            padding: 15px;
            margin-top: 10px;
        }}
        .media-container h5 {{
            margin: 0 0 10px 0;
            color: #495057;
            font-size: 0.9em;
            font-weight: 600;
        }}
        .issue-screenshot {{
            max-width: 100%;
            height: auto;
            border: 1px solid #ddd;
            border-radius: 4px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .issue-video {{
            max-width: 100%;
            height: auto;
            border: 1px solid #ddd;
            border-radius: 4px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .media-caption {{
            font-size: 0.8em;
            color: #6c757d;
            margin-top: 8px;
            text-align: center;
        }}
        .no-media-placeholder {{
            background: #e9ecef;
            border: 2px dashed #adb5bd;
            border-radius: 4px;
            padding: 20px;
            text-align: center;
            color: #6c757d;
            font-style: italic;
        }}
        .severity-badge {{
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 0.8em;
            font-weight: bold;
            text-transform: uppercase;
        }}
        .severity-high {{ background: #dc3545; color: white; }}
        .severity-medium {{ background: #ffc107; color: black; }}
        .severity-low {{ background: #28a745; color: white; }}
        .screenshot-section {{
            margin-top: 20px;
        }}
        .screenshot {{
            max-width: 100%;
            border: 1px solid #ddd;
            border-radius: 4px;
            margin: 10px 0;
        }}
        .craft-bug-analysis {{
            background: #fff3cd;
            border: 1px solid #ffeaa7;
            border-radius: 8px;
            padding: 20px;
            margin: 20px 0;
        }}
        .timeline {{
            background: #f8f9fa;
            border-radius: 8px;
            padding: 20px;
            margin: 20px 0;
        }}
        .timeline-item {{
            display: flex;
            gap: 15px;
            padding: 10px 0;
            border-bottom: 1px solid #e9ecef;
        }}
        .timeline-item:last-child {{
            border-bottom: none;
        }}
        .timeline-time {{
            font-weight: bold;
            color: #6c757d;
            min-width: 100px;
        }}
        .finding-content {{
            flex: 1;
        }}
        .finding-media {{
            margin-top: 15px;
            padding: 15px;
            background: #f8f9fa;
            border-radius: 6px;
            border: 1px solid #e9ecef;
        }}
        .finding-media h5 {{
            margin: 0 0 10px 0;
            color: #495057;
            font-size: 0.9em;
        }}
        .media-item {{
            display: inline-block;
            margin-right: 15px;
            margin-bottom: 10px;
            text-align: center;
        }}
        .media-caption {{
            font-size: 0.8em;
            color: #6c757d;
            margin-top: 5px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Enhanced UX Analysis Report</h1>
            <div class="subtitle">
                Analysis ID: {enhanced_report['analysis_id']} | 
                {enhanced_report['timestamp']} | 
                {enhanced_report['url']}
            </div>
        </div>
        
        <div class="content">
            <div class="score-section">
                <div class="score-card overall">
                    <div class="score-number">{enhanced_report['overall_score']}</div>
                    <div>Overall Score</div>
                </div>
                <div class="score-card performance">
                    <div class="score-number">{enhanced_report['modules'].get('performance', {}).get('score', 0)}</div>
                    <div>Performance</div>
                </div>
                <div class="score-card accessibility">
                    <div class="score-number">{enhanced_report['modules'].get('accessibility', {}).get('score', 0)}</div>
                    <div>Accessibility</div>
                </div>
                <div class="score-card ux">
                    <div class="score-number">{enhanced_report['modules'].get('ux_heuristics', {}).get('score', 0)}</div>
                    <div>UX Heuristics</div>
                </div>
            </div>
            
            <div class="craft-bug-analysis">
                <h3>🎯 Craft Bug Analysis</h3>
                <p><strong>Total Craft Bugs Detected:</strong> {enhanced_report['craft_bug_analysis']['total_count']}</p>
                <p><strong>By Severity:</strong> High: {enhanced_report['craft_bug_analysis']['by_severity']['high']}, 
                   Medium: {enhanced_report['craft_bug_analysis']['by_severity']['medium']}, 
                   Low: {enhanced_report['craft_bug_analysis']['by_severity']['low']}</p>
            </div>
        """
        
        # Add modules
        for module_name, module_data in enhanced_report['modules'].items():
            html_content += f"""
            <div class="module-section">
                <div class="module-header">
                    {module_name.title()} (Score: {module_data.get('score', 0)})
                </div>
                <div class="findings-list">
            """
            
            findings = module_data.get('findings', [])
            for finding in findings:
                severity = finding.get('severity', 'medium')
                issue_category = self.categorize_issue(finding)
                
                html_content += f"""
                    <div class="finding-item">
                        <div class="finding-content">
                            <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 10px;">
                                <span class="severity-badge severity-{severity}">{severity}</span>
                                <span style="font-size: 0.8em; color: #6c757d; background: #e9ecef; padding: 2px 6px; border-radius: 3px;">{issue_category.title()}</span>
                            </div>
                            <strong>{finding.get('message', 'No message')}</strong><br>
                            <small style="color: #6c757d;">Element: {finding.get('element', 'Unknown')}</small>
                        </div>
                        
                        <div class="finding-media-sidebar">
                """
                
                # Add contextual media based on issue category
                has_media = False
                
                # Screenshot for visual/functional issues
                if issue_category in ['visual', 'functional'] and (finding.get('screenshot') or finding.get('screenshot_base64')):
                    has_media = True
                    html_content += """
                            <div class="media-container">
                                <h5>📸 Visual Evidence</h5>
                    """
                    
                    # Screenshot from file
                    if finding.get('screenshot'):
                        html_content += f"""
                                <img src="file://{finding.get('screenshot')}" class="issue-screenshot" alt="Issue Screenshot">
                        """
                    
                    # Base64 screenshot
                    if finding.get('screenshot_base64'):
                        html_content += f"""
                                <img src="data:image/png;base64,{finding.get('screenshot_base64')}" class="issue-screenshot" alt="Issue Screenshot">
                        """
                    
                    html_content += """
                                <div class="media-caption">Contextual Screenshot</div>
                            </div>
                    """
                
                # Video for performance issues
                if issue_category in ['performance', 'functional'] and finding.get('video'):
                    has_media = True
                    html_content += """
                            <div class="media-container">
                                <h5>🎥 Performance Evidence</h5>
                                <video class="issue-video" controls>
                                    <source src="file://{finding.get('video')}" type="video/webm">
                                    Your browser does not support the video tag.
                                </video>
                                <div class="media-caption">Performance Recording</div>
                            </div>
                    """
                
                # Placeholder if no media available
                if not has_media:
                    html_content += """
                            <div class="media-container">
                                <div class="no-media-placeholder">
                                    📷 No media captured<br>
                                    <small>Media will be captured during analysis</small>
                                </div>
                            </div>
                    """
                
                html_content += """
                        </div>
                    </div>
                """
            
            html_content += """
                </div>
            </div>
            """
        
        # Add screenshots if available
        if enhanced_report['media_attachments']['screenshots']:
            html_content += """
            <div class="screenshot-section">
                <h3>📸 Screenshots</h3>
            """
            for screenshot in enhanced_report['media_attachments']['screenshots']:
                html_content += f"""
                <div>
                    <h4>{screenshot['filename']}</h4>
                    <img src="data:image/png;base64,{screenshot['base64']}" class="screenshot" alt="Analysis Screenshot">
                </div>
                """
            html_content += "</div>"
        
        # Add timeline
        if enhanced_report['issue_timeline']:
            html_content += """
            <div class="timeline">
                <h3>⏱️ Issue Timeline</h3>
            """
            for item in enhanced_report['issue_timeline']:
                timestamp = item.get('timestamp', 'Unknown')
                if timestamp:
                    timestamp = f"{timestamp:.2f}ms"
                html_content += f"""
                <div class="timeline-item">
                    <div class="timeline-time">{timestamp}</div>
                    <div>
                        <strong>{item['type']}</strong> - {item['message']}<br>
                        <small>Module: {item['module']} | Severity: {item['severity']}</small>
                    </div>
                </div>
                """
            html_content += "</div>"
        
        html_content += """
        </div>
    </div>
</body>
</html>
        """
        
        # Save HTML report
        html_filepath = enhanced_report['storage_metadata']['file_path'].replace('.json', '.html')
        with open(html_filepath, 'w') as f:
            f.write(html_content)
        
        logger.info(f"🌐 HTML report generated: {html_filepath}")
        return html_filepath

def main():
    """Test the enhanced report generator"""
    generator = EnhancedReportGenerator()
    
    # Test with a sample analysis
    sample_analysis = {
        "analysis_id": "test_123",
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
                        "element": "input"
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
                        "category": "Craft Bug Category B"
                    }
                ]
            }
        }
    }
    
    enhanced_report = generator.generate_enhanced_report(sample_analysis)
    generator.save_enhanced_report(enhanced_report)
    generator.generate_html_report(enhanced_report)

if __name__ == "__main__":
    main()
