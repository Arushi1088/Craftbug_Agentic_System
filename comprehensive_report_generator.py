#!/usr/bin/env python3
"""
Comprehensive Report Generator - Uses the beautiful HTML format from full_bug_report.html
"""

import os
import base64
from datetime import datetime
from PIL import Image
import io
from typing import List, Dict, Any

def encode_image_to_base64(image_path):
    """Convert image to base64 for HTML embedding"""
    try:
        # Handle None or empty paths
        if not image_path or not isinstance(image_path, str):
            print(f"⚠️ Invalid image path: {image_path}")
            return None
            
        if not os.path.exists(image_path):
            print(f"⚠️ Image file not found: {image_path}")
            return None
            
        with Image.open(image_path) as img:
            # Resize for better display
            max_width = 600
            if img.width > max_width:
                ratio = max_width / img.width
                new_height = int(img.height * ratio)
                img = img.resize((max_width, new_height), Image.Resampling.LANCZOS)
            
            # Convert to base64
            buffer = io.BytesIO()
            img.save(buffer, format='PNG')
            buffer.seek(0)
            return base64.b64encode(buffer.getvalue()).decode('utf-8')
    except Exception as e:
        print(f"❌ Error encoding image {image_path}: {e}")
        return None

def generate_comprehensive_html_report(bugs: List[Dict], telemetry_data: Dict, scenario_name: str = "Excel Web Analysis") -> str:
    """Generate comprehensive HTML report with the beautiful format"""
    
    print(f"🔍 Generating Comprehensive HTML Report with {len(bugs)} bugs...")
    
    # Process bugs to include screenshots
    processed_bugs = []
    for bug in bugs:
        # Get screenshot paths from the bug
        screenshot_paths = []
        
        # Check for screenshot_path (singular) first
        if 'screenshot_path' in bug and bug['screenshot_path']:
            screenshot_paths.append(bug['screenshot_path'])
        
        # Check for screenshot_paths (plural) 
        elif 'screenshot_paths' in bug and bug['screenshot_paths']:
            if isinstance(bug['screenshot_paths'], list):
                screenshot_paths.extend(bug['screenshot_paths'])
            else:
                screenshot_paths.append(bug['screenshot_paths'])
        
        # Fallback: extract from affected_steps
        elif 'affected_steps' in bug:
            import re
            matches = re.findall(r'([^,\s]+\.png)', bug.get('affected_steps', ''))
            screenshot_paths.extend(matches)
        
        # Remove duplicates and None values
        screenshot_paths = list(set([path for path in screenshot_paths if path and isinstance(path, str)]))
        
        print(f"🔍 Bug '{bug.get('title', 'Unknown')}' has {len(screenshot_paths)} screenshot paths: {screenshot_paths}")
        
        processed_bug = {
            'title': bug.get('title', 'Unknown Issue'),
            'type': bug.get('type', 'Visual'),
            'severity': bug.get('severity', 'Yellow'),
            'description': bug.get('description', bug.get('title', 'No description available')),
            'impact': bug.get('impact', 'Affects user experience'),
            'immediate_fix': bug.get('what_to_correct', 'Review and fix the identified issue'),
            'affected_steps': bug.get('affected_steps', 'Multiple steps'),
            'screenshot_paths': screenshot_paths,
            'expected': bug.get('expected', 'Proper implementation'),
            'actual': bug.get('actual', 'Current implementation has issues'),
            'confidence': bug.get('confidence', 'Medium')
        }
        processed_bugs.append(processed_bug)
    
    # Count severity breakdown
    severity_counts = {}
    for bug in processed_bugs:
        severity = bug['severity'].lower()
        severity_counts[severity] = severity_counts.get(severity, 0) + 1
    
    # Generate HTML
    html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🔍 Comprehensive Excel Web UX Analysis</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
        }}
        
        .header {{
            background: white;
            padding: 40px;
            border-radius: 20px;
            text-align: center;
            margin-bottom: 30px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        }}
        
        .header h1 {{
            font-size: 2.5em;
            color: #333;
            margin-bottom: 10px;
            font-weight: bold;
        }}
        
        .subtitle {{
            font-size: 1.2em;
            color: #666;
            margin-bottom: 15px;
        }}
        
        .stats {{
            font-size: 0.9em;
            color: #888;
        }}
        
        .summary-stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 40px;
        }}
        
        .stat-card {{
            background: white;
            padding: 25px;
            border-radius: 12px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.08);
            text-align: center;
            transition: transform 0.2s;
        }}
        
        .stat-card:hover {{
            transform: translateY(-2px);
        }}
        
        .stat-number {{
            font-size: 2.5em;
            font-weight: bold;
            color: #667eea;
            margin-bottom: 5px;
        }}
        
        .stat-label {{
            color: #666;
            font-size: 0.9em;
            font-weight: 500;
        }}
        
        .severity-breakdown {{
            background: white;
            padding: 25px;
            border-radius: 12px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.08);
            margin-bottom: 30px;
        }}
        
        .severity-title {{
            font-size: 1.3em;
            font-weight: bold;
            margin-bottom: 20px;
            color: #333;
        }}
        
        .severity-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 15px;
        }}
        
        .severity-item {{
            padding: 15px;
            border-radius: 8px;
            text-align: center;
            color: white;
            font-weight: bold;
        }}
        
        .severity-red {{
            background: linear-gradient(135deg, #dc3545, #c82333);
        }}
        
        .severity-orange {{
            background: linear-gradient(135deg, #fd7e14, #e55a00);
        }}
        
        .severity-yellow {{
            background: linear-gradient(135deg, #ffc107, #e0a800);
            color: #333;
        }}
        
        .bugs-section {{
            background: white;
            border-radius: 12px;
            overflow: hidden;
            box-shadow: 0 4px 15px rgba(0,0,0,0.08);
            margin-bottom: 30px;
        }}
        
        .bugs-header {{
            background: #f8f9fa;
            padding: 25px;
            border-bottom: 1px solid #e9ecef;
        }}
        
        .bugs-title {{
            font-size: 1.8em;
            font-weight: bold;
            color: #333;
            margin-bottom: 10px;
        }}
        
        .bugs-subtitle {{
            color: #666;
            font-size: 1em;
        }}
        
        .bug-card {{
            border-bottom: 1px solid #e9ecef;
            padding: 30px;
        }}
        
        .bug-card:last-child {{
            border-bottom: none;
        }}
        
        .bug-header {{
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            margin-bottom: 20px;
            flex-wrap: wrap;
            gap: 15px;
        }}
        
        .bug-title {{
            font-size: 1.4em;
            font-weight: bold;
            color: #333;
            flex: 1;
        }}
        
        .bug-meta {{
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
        }}
        
        .bug-type {{
            background: #e3f2fd;
            color: #1976d2;
            padding: 5px 12px;
            border-radius: 20px;
            font-size: 0.8em;
            font-weight: bold;
        }}
        
        .bug-severity {{
            padding: 5px 12px;
            border-radius: 20px;
            font-size: 0.8em;
            font-weight: bold;
            color: white;
        }}
        
        .severity-red-badge {{
            background: #dc3545;
        }}
        
        .severity-orange-badge {{
            background: #fd7e14;
        }}
        
        .severity-yellow-badge {{
            background: #ffc107;
            color: #333;
        }}
        
        .bug-content {{
            display: grid;
            grid-template-columns: 2fr 1fr;
            gap: 30px;
            margin-bottom: 20px;
        }}
        
        .bug-details {{
            display: flex;
            flex-direction: column;
            gap: 15px;
        }}
        
        .detail-item {{
            background: #f8f9fa;
            padding: 15px;
            border-radius: 8px;
        }}
        
        .detail-label {{
            font-weight: bold;
            color: #333;
            margin-bottom: 5px;
            font-size: 0.9em;
        }}
        
        .detail-value {{
            color: #666;
            font-size: 0.95em;
            line-height: 1.5;
        }}
        
        .bug-screenshots {{
            display: flex;
            flex-direction: column;
            gap: 15px;
        }}
        
        .screenshot-item {{
            text-align: center;
        }}
        
        .screenshot-item img {{
            max-width: 100%;
            height: auto;
            border-radius: 8px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
            border: 2px solid #e9ecef;
        }}
        
        .screenshot-caption {{
            margin-top: 8px;
            font-size: 0.8em;
            color: #666;
            font-weight: 500;
        }}
        
        .affected-steps {{
            background: #fff3cd;
            border: 1px solid #ffeaa7;
            color: #856404;
            padding: 12px;
            border-radius: 8px;
            font-size: 0.9em;
            margin-top: 15px;
        }}
        
        .footer {{
            text-align: center;
            padding: 30px;
            color: #666;
            font-size: 0.9em;
        }}
        
        @media (max-width: 768px) {{
            .bug-content {{
                grid-template-columns: 1fr;
            }}
            
            .bug-header {{
                flex-direction: column;
                align-items: flex-start;
            }}
            
            .summary-stats {{
                grid-template-columns: repeat(2, 1fr);
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔍 Comprehensive Excel Web UX Analysis</h1>
            <div class="subtitle">LLM-Powered Craft Bug Detection with Screenshots</div>
            <div class="stats">
                Generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')} | 
                Scenario: {scenario_name} | {len(processed_bugs)} Craft Bugs Detected
            </div>
        </div>
        
        <div class="summary-stats">
            <div class="stat-card">
                <div class="stat-number">{len(processed_bugs)}</div>
                <div class="stat-label">Craft Bugs Found</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{severity_counts.get('red', 0)}</div>
                <div class="stat-label">Critical Issues</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{severity_counts.get('orange', 0)}</div>
                <div class="stat-label">High Priority</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{severity_counts.get('yellow', 0)}</div>
                <div class="stat-label">Medium Priority</div>
            </div>
        </div>
        
        <div class="severity-breakdown">
            <div class="severity-title">Severity Distribution</div>
            <div class="severity-grid">
                {f'<div class="severity-item severity-red">Red: {severity_counts.get("red", 0)}</div>' if severity_counts.get('red', 0) > 0 else ''}
                {f'<div class="severity-item severity-orange">Orange: {severity_counts.get("orange", 0)}</div>' if severity_counts.get('orange', 0) > 0 else ''}
                {f'<div class="severity-item severity-yellow">Yellow: {severity_counts.get("yellow", 0)}</div>' if severity_counts.get('yellow', 0) > 0 else ''}
            </div>
        </div>
        
        <div class="bugs-section">
            <div class="bugs-header">
                <div class="bugs-title">Detailed Bug Analysis</div>
                <div class="bugs-subtitle">Each bug includes screenshots and detailed analysis</div>
            </div>
    """
    
    # Add each bug
    for i, bug in enumerate(processed_bugs, 1):
        # Encode screenshots
        screenshot_html = ""
        print(f"🔍 Processing {len(bug['screenshot_paths'])} screenshots for bug {i}")
        for j, screenshot_path in enumerate(bug['screenshot_paths']):
            print(f"📸 Encoding screenshot {j+1}: {screenshot_path}")
            base64_image = encode_image_to_base64(screenshot_path)
            if base64_image:
                print(f"✅ Successfully encoded screenshot {j+1} ({len(base64_image)} chars)")
                screenshot_html += f"""
                <div class="screenshot-item">
                    <img src="data:image/png;base64,{base64_image}" alt="Screenshot {j+1}">
                    <div class="screenshot-caption">Screenshot {j+1}: {os.path.basename(screenshot_path)}</div>
                </div>
                """
            else:
                print(f"❌ Failed to encode screenshot {j+1}")
        
        # Get severity class
        severity_class = f"severity-{bug['severity'].lower()}-badge"
        
        html_content += f"""
            <div class="bug-card">
                <div class="bug-header">
                    <div class="bug-title">Bug #{i}: {bug['title']}</div>
                    <div class="bug-meta">
                        <div class="bug-type">{bug['type']}</div>
                        <div class="bug-severity {severity_class}">{bug['severity']}</div>
                    </div>
                </div>
                
                <div class="bug-content">
                    <div class="bug-details">
                        <div class="detail-item">
                            <div class="detail-label">Description</div>
                            <div class="detail-value">{bug['description']}</div>
                        </div>
                        
                        <div class="detail-item">
                            <div class="detail-label">Impact</div>
                            <div class="detail-value">{bug['impact']}</div>
                        </div>
                        
                        <div class="detail-item">
                            <div class="detail-label">Expected Behavior</div>
                            <div class="detail-value">{bug['expected']}</div>
                        </div>
                        
                        <div class="detail-item">
                            <div class="detail-label">Actual Behavior</div>
                            <div class="detail-value">{bug['actual']}</div>
                        </div>
                        
                        <div class="detail-item">
                            <div class="detail-label">Immediate Fix</div>
                            <div class="detail-value">{bug['immediate_fix']}</div>
                        </div>
                        
                        <div class="detail-item">
                            <div class="detail-label">Confidence Level</div>
                            <div class="detail-value">{bug['confidence']}</div>
                        </div>
                    </div>
                    
                    <div class="bug-screenshots">
                        {screenshot_html if screenshot_html else '<div class="screenshot-item"><div class="screenshot-caption">No screenshots available</div></div>'}
                    </div>
                </div>
                
                <div class="affected-steps">
                    <strong>Affected Steps:</strong> {bug['affected_steps']}
                </div>
            </div>
        """
    
    # Close HTML
    html_content += """
        </div>
        
        <div class="footer">
            <p>Generated by CraftBug Agentic System | LLM-Powered UX Analysis</p>
            <p>This report contains detailed craft bug analysis with embedded screenshots for visual verification.</p>
        </div>
    </div>
</body>
</html>
    """
    
    return html_content

def save_comprehensive_report(html_content: str, filename: str = None) -> str:
    """Save the comprehensive HTML report to a file"""
    if not filename:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"comprehensive_ux_report_{timestamp}.html"
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"✅ Comprehensive report saved: {filename}")
    return filename
