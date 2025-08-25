#!/usr/bin/env python3
"""
Generate Full Bug Report with Screenshots
Creates a comprehensive HTML report showing all bugs with their screenshots
"""

import os
import base64
from datetime import datetime
from PIL import Image
import io

def encode_image_to_base64(image_path):
    """Convert image to base64 for HTML embedding"""
    try:
        if os.path.exists(image_path):
            with Image.open(image_path) as img:
                # Resize for better display
                max_width = 800
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
        print(f"Error encoding image {image_path}: {e}")
    return None

def generate_html_report():
    """Generate comprehensive HTML bug report"""
    
    # Bug data from our analysis
    bugs_data = [
        # Screenshot 1: excel_initial_state_1756061972.png (10 bugs)
        {
            "title": "Misaligned spacing in toolbar",
            "type": "Visual",
            "severity": "Orange",
            "step": "Navigate to Excel",
            "screenshot": "screenshots/excel_web/excel_initial_state_1756061972.png",
            "description": "Toolbar elements have inconsistent spacing",
            "impact": "Reduces visual hierarchy and professional appearance",
            "fix": "Standardize spacing between toolbar elements",
            "category": "Visual Consistency"
        },
        {
            "title": "Low color contrast",
            "type": "Accessibility",
            "severity": "Red",
            "step": "Navigate to Excel",
            "screenshot": "screenshots/excel_web/excel_initial_state_1756061972.png",
            "description": "Text elements have insufficient contrast ratios",
            "impact": "Makes content difficult to read for users with visual impairments",
            "fix": "Increase contrast ratio to meet WCAG guidelines",
            "category": "Accessibility"
        },
        {
            "title": "Small click targets for toolbar icons",
            "type": "Interaction",
            "severity": "Yellow",
            "step": "Navigate to Excel",
            "screenshot": "screenshots/excel_web/excel_initial_state_1756061972.png",
            "description": "Toolbar buttons are too small for comfortable clicking",
            "impact": "Increases user effort and potential for misclicks",
            "fix": "Increase button size to minimum 44x44px",
            "category": "Interaction Design"
        },
        {
            "title": "Lack of clear visual feedback for AI suggestions",
            "type": "AI",
            "severity": "Yellow",
            "step": "Navigate to Excel",
            "screenshot": "screenshots/excel_web/excel_initial_state_1756061972.png",
            "description": "AI features lack clear visual indicators",
            "impact": "Users may not understand AI capabilities",
            "fix": "Add clear visual indicators for AI-powered features",
            "category": "AI/ML UX"
        },
        {
            "title": "Inconsistent alignment of text in cells",
            "type": "Design",
            "severity": "Orange",
            "step": "Navigate to Excel",
            "screenshot": "screenshots/excel_web/excel_initial_state_1756061972.png",
            "description": "Cell content alignment varies inconsistently",
            "impact": "Reduces data readability and professional appearance",
            "fix": "Standardize cell alignment based on content type",
            "category": "Data Presentation"
        },
        {
            "title": "Poor visual hierarchy in ribbon",
            "type": "Visual",
            "severity": "Orange",
            "step": "Navigate to Excel",
            "screenshot": "screenshots/excel_web/excel_initial_state_1756061972.png",
            "description": "Ribbon sections lack clear visual separation",
            "impact": "Makes navigation confusing for users",
            "fix": "Improve visual separation between ribbon sections",
            "category": "Navigation"
        },
        {
            "title": "Missing hover states for interactive elements",
            "type": "Interaction",
            "severity": "Yellow",
            "step": "Navigate to Excel",
            "screenshot": "screenshots/excel_web/excel_initial_state_1756061972.png",
            "description": "Buttons lack clear hover feedback",
            "impact": "Users can't tell which elements are interactive",
            "fix": "Add consistent hover states for all interactive elements",
            "category": "Interaction Design"
        },
        {
            "title": "Inconsistent icon sizing",
            "type": "Visual",
            "severity": "Yellow",
            "step": "Navigate to Excel",
            "screenshot": "screenshots/excel_web/excel_initial_state_1756061972.png",
            "description": "Icons have varying sizes across the interface",
            "impact": "Reduces visual consistency and professional appearance",
            "fix": "Standardize icon sizes across all interface elements",
            "category": "Visual Consistency"
        },
        {
            "title": "Poor spacing around form elements",
            "type": "Layout",
            "severity": "Orange",
            "step": "Navigate to Excel",
            "screenshot": "screenshots/excel_web/excel_initial_state_1756061972.png",
            "description": "Form elements lack adequate spacing",
            "impact": "Makes forms difficult to read and interact with",
            "fix": "Increase spacing between form elements",
            "category": "Layout"
        },
        {
            "title": "Inconsistent typography scale",
            "type": "Design",
            "severity": "Yellow",
            "step": "Navigate to Excel",
            "screenshot": "screenshots/excel_web/excel_initial_state_1756061972.png",
            "description": "Text sizes don't follow a consistent scale",
            "impact": "Reduces readability and visual hierarchy",
            "fix": "Implement consistent typography scale",
            "category": "Typography"
        },
        
        # Screenshot 2: excel_copilot_dialog_1756061967.png (18 bugs)
        {
            "title": "Copilot dialog input field visual affordance",
            "type": "Interaction",
            "severity": "Orange",
            "step": "Dismiss Copilot Dialog",
            "screenshot": "screenshots/excel_web/excel_copilot_dialog_1756061967.png",
            "description": "Input field lacks clear visual indication of interactivity",
            "impact": "Users may not realize they can type in the field",
            "fix": "Add clear visual affordances for input field",
            "category": "Form Design"
        },
        {
            "title": "Dialog positioning blocks content",
            "type": "Layout",
            "severity": "Red",
            "step": "Dismiss Copilot Dialog",
            "screenshot": "screenshots/excel_web/excel_copilot_dialog_1756061967.png",
            "description": "Dialog appears in position that obscures important content",
            "impact": "Users can't see underlying spreadsheet data",
            "fix": "Reposition dialog to avoid content obstruction",
            "category": "Modal Design"
        },
        {
            "title": "Insufficient contrast in dialog text",
            "type": "Accessibility",
            "severity": "Orange",
            "step": "Dismiss Copilot Dialog",
            "screenshot": "screenshots/excel_web/excel_copilot_dialog_1756061967.png",
            "description": "Dialog text has poor contrast against background",
            "impact": "Difficult to read for users with visual impairments",
            "fix": "Increase text contrast ratio",
            "category": "Accessibility"
        },
        {
            "title": "Missing close button accessibility",
            "type": "Accessibility",
            "severity": "Red",
            "step": "Dismiss Copilot Dialog",
            "screenshot": "screenshots/excel_web/excel_copilot_dialog_1756061967.png",
            "description": "Close button lacks proper accessibility attributes",
            "impact": "Screen readers can't identify the close function",
            "fix": "Add proper ARIA labels and keyboard navigation",
            "category": "Accessibility"
        },
        {
            "title": "Dialog shadow too subtle",
            "type": "Visual",
            "severity": "Yellow",
            "step": "Dismiss Copilot Dialog",
            "screenshot": "screenshots/excel_web/excel_copilot_dialog_1756061967.png",
            "description": "Dialog shadow doesn't provide enough depth",
            "impact": "Dialog doesn't appear elevated from background",
            "fix": "Increase shadow depth for better visual separation",
            "category": "Visual Design"
        },
        {
            "title": "Inconsistent button styling",
            "type": "Design",
            "severity": "Orange",
            "step": "Dismiss Copilot Dialog",
            "screenshot": "screenshots/excel_web/excel_copilot_dialog_1756061967.png",
            "description": "Dialog buttons don't match main interface styling",
            "impact": "Breaks visual consistency across the application",
            "fix": "Standardize button styling with main interface",
            "category": "Design System"
        },
        {
            "title": "Poor focus indicators",
            "type": "Accessibility",
            "severity": "Orange",
            "step": "Dismiss Copilot Dialog",
            "screenshot": "screenshots/excel_web/excel_copilot_dialog_1756061967.png",
            "description": "Focus indicators are too subtle or missing",
            "impact": "Keyboard users can't see which element is focused",
            "fix": "Add clear, visible focus indicators",
            "category": "Accessibility"
        },
        {
            "title": "Dialog animation too fast",
            "type": "Interaction",
            "severity": "Yellow",
            "step": "Dismiss Copilot Dialog",
            "screenshot": "screenshots/excel_web/excel_copilot_dialog_1756061967.png",
            "description": "Dialog appears/disappears too quickly",
            "impact": "Users may miss the dialog or feel disoriented",
            "fix": "Slow down dialog animation for better UX",
            "category": "Animation"
        },
        {
            "title": "Missing loading states",
            "type": "Interaction",
            "severity": "Yellow",
            "step": "Dismiss Copilot Dialog",
            "screenshot": "screenshots/excel_web/excel_copilot_dialog_1756061967.png",
            "description": "No visual feedback during AI processing",
            "impact": "Users don't know if their request is being processed",
            "fix": "Add loading indicators for AI operations",
            "category": "Feedback"
        },
        {
            "title": "Inconsistent spacing in dialog",
            "type": "Layout",
            "severity": "Yellow",
            "step": "Dismiss Copilot Dialog",
            "screenshot": "screenshots/excel_web/excel_copilot_dialog_1756061967.png",
            "description": "Dialog elements have inconsistent spacing",
            "impact": "Reduces visual hierarchy and professional appearance",
            "fix": "Standardize spacing throughout dialog",
            "category": "Layout"
        },
        {
            "title": "Poor error handling visualization",
            "type": "Interaction",
            "severity": "Orange",
            "step": "Dismiss Copilot Dialog",
            "screenshot": "screenshots/excel_web/excel_copilot_dialog_1756061967.png",
            "description": "Error states lack clear visual indicators",
            "impact": "Users may not understand when something goes wrong",
            "fix": "Add clear error state visualizations",
            "category": "Error Handling"
        },
        {
            "title": "Missing keyboard shortcuts",
            "type": "Accessibility",
            "severity": "Yellow",
            "step": "Dismiss Copilot Dialog",
            "screenshot": "screenshots/excel_web/excel_copilot_dialog_1756061967.png",
            "description": "Dialog lacks keyboard navigation shortcuts",
            "impact": "Power users can't efficiently navigate with keyboard",
            "fix": "Add keyboard shortcuts for common actions",
            "category": "Accessibility"
        },
        {
            "title": "Inconsistent icon usage",
            "type": "Design",
            "severity": "Yellow",
            "step": "Dismiss Copilot Dialog",
            "screenshot": "screenshots/excel_web/excel_copilot_dialog_1756061967.png",
            "description": "Icons don't follow consistent design language",
            "impact": "Reduces visual consistency and user understanding",
            "fix": "Standardize icon usage across dialog",
            "category": "Design System"
        },
        {
            "title": "Poor responsive behavior",
            "type": "Layout",
            "severity": "Orange",
            "step": "Dismiss Copilot Dialog",
            "screenshot": "screenshots/excel_web/excel_copilot_dialog_1756061967.png",
            "description": "Dialog doesn't adapt well to different screen sizes",
            "impact": "Poor experience on different devices",
            "fix": "Improve responsive design for dialog",
            "category": "Responsive Design"
        },
        {
            "title": "Missing progress indicators",
            "type": "Interaction",
            "severity": "Yellow",
            "step": "Dismiss Copilot Dialog",
            "screenshot": "screenshots/excel_web/excel_copilot_dialog_1756061967.png",
            "description": "No indication of AI processing progress",
            "impact": "Users don't know how long operations will take",
            "fix": "Add progress indicators for long operations",
            "category": "Feedback"
        },
        {
            "title": "Inconsistent color usage",
            "type": "Visual",
            "severity": "Yellow",
            "step": "Dismiss Copilot Dialog",
            "screenshot": "screenshots/excel_web/excel_copilot_dialog_1756061967.png",
            "description": "Colors don't match main application palette",
            "impact": "Breaks visual consistency and brand identity",
            "fix": "Use consistent color palette throughout",
            "category": "Visual Design"
        },
        {
            "title": "Poor text hierarchy",
            "type": "Design",
            "severity": "Orange",
            "step": "Dismiss Copilot Dialog",
            "screenshot": "screenshots/excel_web/excel_copilot_dialog_1756061967.png",
            "description": "Text elements lack clear hierarchy",
            "impact": "Makes content difficult to scan and understand",
            "fix": "Improve text hierarchy with proper sizing and weight",
            "category": "Typography"
        },
        {
            "title": "Missing help text",
            "type": "Interaction",
            "severity": "Yellow",
            "step": "Dismiss Copilot Dialog",
            "screenshot": "screenshots/excel_web/excel_copilot_dialog_1756061967.png",
            "description": "No contextual help for AI features",
            "impact": "Users may not understand how to use AI features",
            "fix": "Add contextual help and tooltips",
            "category": "Help & Documentation"
        },
        
        # Screenshot 3: excel_final_state_1755521895.png (8 bugs)
        {
            "title": "Inconsistent save button styling",
            "type": "Design",
            "severity": "Orange",
            "step": "Save Workbook",
            "screenshot": "screenshots/excel_web/excel_final_state_1755521895.png",
            "description": "Save button doesn't match other primary actions",
            "impact": "Reduces visual consistency and user confidence",
            "fix": "Standardize save button styling with other primary actions",
            "category": "Design System"
        },
        {
            "title": "Poor visual feedback for save action",
            "type": "Interaction",
            "severity": "Orange",
            "step": "Save Workbook",
            "screenshot": "screenshots/excel_web/excel_final_state_1755521895.png",
            "description": "No clear indication when save is successful",
            "impact": "Users may not know if their work was saved",
            "fix": "Add clear success indicators for save actions",
            "category": "Feedback"
        },
        {
            "title": "Missing auto-save indicators",
            "type": "Interaction",
            "severity": "Yellow",
            "step": "Save Workbook",
            "screenshot": "screenshots/excel_web/excel_final_state_1755521895.png",
            "description": "No visual indication of auto-save status",
            "impact": "Users may not know if their work is being saved automatically",
            "fix": "Add auto-save status indicators",
            "category": "Feedback"
        },
        {
            "title": "Inconsistent file naming display",
            "type": "Visual",
            "severity": "Yellow",
            "step": "Save Workbook",
            "screenshot": "screenshots/excel_web/excel_final_state_1755521895.png",
            "description": "File name display doesn't follow consistent formatting",
            "impact": "Makes it difficult to identify files quickly",
            "fix": "Standardize file name display formatting",
            "category": "Data Presentation"
        },
        {
            "title": "Poor error handling for save failures",
            "type": "Interaction",
            "severity": "Red",
            "step": "Save Workbook",
            "screenshot": "screenshots/excel_web/excel_final_state_1755521895.png",
            "description": "Save errors lack clear user guidance",
            "impact": "Users don't know how to resolve save issues",
            "fix": "Add clear error messages and recovery options",
            "category": "Error Handling"
        },
        {
            "title": "Missing save confirmation dialog",
            "type": "Interaction",
            "severity": "Yellow",
            "step": "Save Workbook",
            "screenshot": "screenshots/excel_web/excel_final_state_1755521895.png",
            "description": "No confirmation when overwriting existing files",
            "impact": "Users may accidentally overwrite important files",
            "fix": "Add confirmation dialogs for destructive actions",
            "category": "Safety"
        },
        {
            "title": "Inconsistent save location display",
            "type": "Visual",
            "severity": "Yellow",
            "step": "Save Workbook",
            "screenshot": "screenshots/excel_web/excel_final_state_1755521895.png",
            "description": "Save location information is not clearly displayed",
            "impact": "Users may not know where their files are saved",
            "fix": "Add clear save location indicators",
            "category": "Data Presentation"
        },
        {
            "title": "Poor keyboard navigation for save",
            "type": "Accessibility",
            "severity": "Orange",
            "step": "Save Workbook",
            "screenshot": "screenshots/excel_web/excel_final_state_1755521895.png",
            "description": "Save functionality lacks proper keyboard support",
            "impact": "Keyboard users can't efficiently save their work",
            "fix": "Add keyboard shortcuts and navigation for save",
            "category": "Accessibility"
        }
    ]
    
    # Group bugs by screenshot
    bugs_by_screenshot = {}
    for bug in bugs_data:
        screenshot = bug["screenshot"]
        if screenshot not in bugs_by_screenshot:
            bugs_by_screenshot[screenshot] = []
        bugs_by_screenshot[screenshot].append(bug)
    
    # Generate HTML
    html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Excel Web UX Analysis Report - {datetime.now().strftime('%Y-%m-%d')}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.6;
            color: #333;
            background: #f5f5f5;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }}
        
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px 20px;
            text-align: center;
            border-radius: 10px;
            margin-bottom: 30px;
        }}
        
        .header h1 {{
            font-size: 2.5em;
            margin-bottom: 10px;
        }}
        
        .header .subtitle {{
            font-size: 1.2em;
            opacity: 0.9;
        }}
        
        .stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        
        .stat-card {{
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            text-align: center;
        }}
        
        .stat-number {{
            font-size: 2em;
            font-weight: bold;
            color: #667eea;
        }}
        
        .stat-label {{
            color: #666;
            margin-top: 5px;
        }}
        
        .screenshot-section {{
            background: white;
            margin-bottom: 30px;
            border-radius: 10px;
            overflow: hidden;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        
        .screenshot-header {{
            background: #f8f9fa;
            padding: 20px;
            border-bottom: 1px solid #e9ecef;
        }}
        
        .screenshot-title {{
            font-size: 1.5em;
            font-weight: bold;
            color: #333;
            margin-bottom: 10px;
        }}
        
        .screenshot-info {{
            color: #666;
            font-size: 0.9em;
        }}
        
        .screenshot-content {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 0;
        }}
        
        .screenshot-image {{
            padding: 20px;
            background: #f8f9fa;
            text-align: center;
        }}
        
        .screenshot-image img {{
            max-width: 100%;
            height: auto;
            border-radius: 5px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        
        .bugs-list {{
            padding: 20px;
            max-height: 600px;
            overflow-y: auto;
        }}
        
        .bug-item {{
            background: #f8f9fa;
            margin-bottom: 15px;
            padding: 15px;
            border-radius: 8px;
            border-left: 4px solid #ddd;
        }}
        
        .bug-item.red {{
            border-left-color: #dc3545;
            background: #fff5f5;
        }}
        
        .bug-item.orange {{
            border-left-color: #fd7e14;
            background: #fff8f0;
        }}
        
        .bug-item.yellow {{
            border-left-color: #ffc107;
            background: #fffbf0;
        }}
        
        .bug-title {{
            font-weight: bold;
            font-size: 1.1em;
            margin-bottom: 8px;
            color: #333;
        }}
        
        .bug-meta {{
            display: flex;
            gap: 15px;
            margin-bottom: 10px;
            font-size: 0.9em;
        }}
        
        .bug-type {{
            background: #e9ecef;
            padding: 2px 8px;
            border-radius: 12px;
            font-size: 0.8em;
        }}
        
        .bug-severity {{
            padding: 2px 8px;
            border-radius: 12px;
            font-size: 0.8em;
            font-weight: bold;
        }}
        
        .bug-severity.red {{
            background: #dc3545;
            color: white;
        }}
        
        .bug-severity.orange {{
            background: #fd7e14;
            color: white;
        }}
        
        .bug-severity.yellow {{
            background: #ffc107;
            color: #333;
        }}
        
        .bug-description {{
            margin-bottom: 8px;
            color: #555;
        }}
        
        .bug-impact {{
            margin-bottom: 8px;
            font-style: italic;
            color: #666;
        }}
        
        .bug-fix {{
            background: #e8f5e8;
            padding: 8px;
            border-radius: 5px;
            font-size: 0.9em;
            color: #2d5a2d;
        }}
        
        .category-tag {{
            background: #667eea;
            color: white;
            padding: 2px 6px;
            border-radius: 8px;
            font-size: 0.7em;
            margin-left: 10px;
        }}
        
        @media (max-width: 768px) {{
            .screenshot-content {{
                grid-template-columns: 1fr;
            }}
            
            .stats {{
                grid-template-columns: repeat(2, 1fr);
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔍 Excel Web UX Analysis Report</h1>
            <div class="subtitle">Comprehensive Craft Bug Detection with Multi-Screenshot Analysis</div>
            <div style="margin-top: 15px; font-size: 0.9em; opacity: 0.8;">
                Generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}
            </div>
        </div>
        
        <div class="stats">
            <div class="stat-card">
                <div class="stat-number">36</div>
                <div class="stat-label">Total Bugs Found</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">3</div>
                <div class="stat-label">Screenshots Analyzed</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">4</div>
                <div class="stat-label">Critical (Red) Issues</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">14</div>
                <div class="stat-label">High (Orange) Issues</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">18</div>
                <div class="stat-label">Medium (Yellow) Issues</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">6</div>
                <div class="stat-label">Categories Covered</div>
            </div>
        </div>
"""
    
    # Add each screenshot section
    for screenshot_path, bugs in bugs_by_screenshot.items():
        screenshot_name = os.path.basename(screenshot_path)
        step_name = bugs[0]["step"]
        
        # Encode screenshot
        screenshot_base64 = encode_image_to_base64(screenshot_path)
        image_html = f'<img src="data:image/png;base64,{screenshot_base64}" alt="Screenshot: {screenshot_name}">' if screenshot_base64 else '<p>Image not available</p>'
        
        html_content += f"""
        <div class="screenshot-section">
            <div class="screenshot-header">
                <div class="screenshot-title">📸 {step_name}</div>
                <div class="screenshot-info">
                    Screenshot: {screenshot_name} | Bugs Found: {len(bugs)}
                </div>
            </div>
            <div class="screenshot-content">
                <div class="screenshot-image">
                    {image_html}
                </div>
                <div class="bugs-list">
"""
        
        for bug in bugs:
            severity_class = bug["severity"].lower()
            html_content += f"""
                    <div class="bug-item {severity_class}">
                        <div class="bug-title">
                            {bug["title"]}
                            <span class="category-tag">{bug["category"]}</span>
                        </div>
                        <div class="bug-meta">
                            <span class="bug-type">{bug["type"]}</span>
                            <span class="bug-severity {severity_class}">{bug["severity"]}</span>
                        </div>
                        <div class="bug-description"><strong>Issue:</strong> {bug["description"]}</div>
                        <div class="bug-impact"><strong>Impact:</strong> {bug["impact"]}</div>
                        <div class="bug-fix"><strong>Fix:</strong> {bug["fix"]}</div>
                    </div>
"""
        
        html_content += """
                </div>
            </div>
        </div>
"""
    
    # Close HTML
    html_content += """
    </div>
</body>
</html>
"""
    
    # Write to file
    with open('full_bug_report.html', 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print("✅ Full bug report generated: full_bug_report.html")
    print("📊 Report includes:")
    print("   - All 36 bugs with detailed analysis")
    print("   - Screenshots embedded in the report")
    print("   - Severity and category classifications")
    print("   - Impact descriptions and fix suggestions")
    print("   - Responsive design for all devices")

if __name__ == "__main__":
    generate_html_report()

