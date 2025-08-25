#!/usr/bin/env python3
"""
Generate Consolidated Bug Report
Creates an HTML report showing the consolidated bugs with screenshots
"""

import os
import base64
from datetime import datetime
from PIL import Image
import io
import asyncio
from consolidation_analyzer import ConsolidationAnalyzer

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

async def generate_consolidated_html_report():
    """Generate comprehensive HTML report with consolidated bugs"""
    
    print("🔍 Generating Consolidated Bug Report...")
    
    # First, run the consolidation to get the actual consolidated bugs
    analyzer = ConsolidationAnalyzer()
    
    # Full set of 36 bugs from our analysis
    full_bugs = [
        # Screenshot 1: excel_initial_state_1756061972.png (10 bugs)
        {
            'title': 'Misaligned spacing in toolbar',
            'type': 'Visual',
            'severity': 'Orange',
            'step_name': 'Navigate to Excel',
            'description': 'Toolbar elements have inconsistent spacing',
            'impact': 'Reduces visual hierarchy and professional appearance',
            'immediate_fix': 'Standardize spacing between toolbar elements'
        },
        {
            'title': 'Low color contrast',
            'type': 'Accessibility',
            'severity': 'Red',
            'step_name': 'Navigate to Excel',
            'description': 'Text elements have insufficient contrast ratios',
            'impact': 'Makes content difficult to read for users with visual impairments',
            'immediate_fix': 'Increase contrast ratio to meet WCAG guidelines'
        },
        {
            'title': 'Small click targets for toolbar icons',
            'type': 'Interaction',
            'severity': 'Yellow',
            'step_name': 'Navigate to Excel',
            'description': 'Toolbar buttons are too small for comfortable clicking',
            'impact': 'Increases user effort and potential for misclicks',
            'immediate_fix': 'Increase button size to minimum 44x44px'
        },
        {
            'title': 'Lack of clear visual feedback for AI suggestions',
            'type': 'AI',
            'severity': 'Yellow',
            'step_name': 'Navigate to Excel',
            'description': 'AI features lack clear visual indicators',
            'impact': 'Users may not understand AI capabilities',
            'immediate_fix': 'Add clear visual indicators for AI-powered features'
        },
        {
            'title': 'Inconsistent alignment of text in cells',
            'type': 'Design',
            'severity': 'Orange',
            'step_name': 'Navigate to Excel',
            'description': 'Cell content alignment varies inconsistently',
            'impact': 'Reduces data readability and professional appearance',
            'immediate_fix': 'Standardize cell alignment based on content type'
        },
        {
            'title': 'Poor visual hierarchy in ribbon',
            'type': 'Visual',
            'severity': 'Orange',
            'step_name': 'Navigate to Excel',
            'description': 'Ribbon sections lack clear visual separation',
            'impact': 'Makes navigation confusing for users',
            'immediate_fix': 'Improve visual separation between ribbon sections'
        },
        {
            'title': 'Missing hover states for interactive elements',
            'type': 'Interaction',
            'severity': 'Yellow',
            'step_name': 'Navigate to Excel',
            'description': 'Buttons lack clear hover feedback',
            'impact': 'Users can\'t tell which elements are interactive',
            'immediate_fix': 'Add consistent hover states for all interactive elements'
        },
        {
            'title': 'Inconsistent icon sizing',
            'type': 'Visual',
            'severity': 'Yellow',
            'step_name': 'Navigate to Excel',
            'description': 'Icons have varying sizes across the interface',
            'impact': 'Reduces visual consistency and professional appearance',
            'immediate_fix': 'Standardize icon sizes across all interface elements'
        },
        {
            'title': 'Poor spacing around form elements',
            'type': 'Layout',
            'severity': 'Orange',
            'step_name': 'Navigate to Excel',
            'description': 'Form elements lack adequate spacing',
            'impact': 'Makes forms difficult to read and interact with',
            'immediate_fix': 'Increase spacing between form elements'
        },
        {
            'title': 'Inconsistent typography scale',
            'type': 'Design',
            'severity': 'Yellow',
            'step_name': 'Navigate to Excel',
            'description': 'Text sizes don\'t follow a consistent scale',
            'impact': 'Reduces readability and visual hierarchy',
            'immediate_fix': 'Implement consistent typography scale'
        },
        
        # Screenshot 2: excel_copilot_dialog_1756061967.png (18 bugs)
        {
            'title': 'Copilot dialog input field visual affordance',
            'type': 'Interaction',
            'severity': 'Orange',
            'step_name': 'Dismiss Copilot Dialog',
            'description': 'Input field lacks clear visual indication of interactivity',
            'impact': 'Users may not realize they can type in the field',
            'immediate_fix': 'Add clear visual affordances for input field'
        },
        {
            'title': 'Dialog positioning blocks content',
            'type': 'Layout',
            'severity': 'Red',
            'step_name': 'Dismiss Copilot Dialog',
            'description': 'Dialog appears in position that obscures important content',
            'impact': 'Users can\'t see underlying spreadsheet data',
            'immediate_fix': 'Reposition dialog to avoid content obstruction'
        },
        {
            'title': 'Insufficient contrast in dialog text',
            'type': 'Accessibility',
            'severity': 'Orange',
            'step_name': 'Dismiss Copilot Dialog',
            'description': 'Dialog text has poor contrast against background',
            'impact': 'Difficult to read for users with visual impairments',
            'immediate_fix': 'Increase text contrast ratio'
        },
        {
            'title': 'Missing close button accessibility',
            'type': 'Accessibility',
            'severity': 'Red',
            'step_name': 'Dismiss Copilot Dialog',
            'description': 'Close button lacks proper accessibility attributes',
            'impact': 'Screen readers can\'t identify the close function',
            'immediate_fix': 'Add proper ARIA labels and keyboard navigation'
        },
        {
            'title': 'Dialog shadow too subtle',
            'type': 'Visual',
            'severity': 'Yellow',
            'step_name': 'Dismiss Copilot Dialog',
            'description': 'Dialog shadow doesn\'t provide enough depth',
            'impact': 'Dialog doesn\'t appear elevated from background',
            'immediate_fix': 'Increase shadow depth for better visual separation'
        },
        {
            'title': 'Inconsistent button styling',
            'type': 'Design',
            'severity': 'Orange',
            'step_name': 'Dismiss Copilot Dialog',
            'description': 'Dialog buttons don\'t match main interface styling',
            'impact': 'Breaks visual consistency across the application',
            'immediate_fix': 'Standardize button styling with main interface'
        },
        {
            'title': 'Poor focus indicators',
            'type': 'Accessibility',
            'severity': 'Orange',
            'step_name': 'Dismiss Copilot Dialog',
            'description': 'Focus indicators are too subtle or missing',
            'impact': 'Keyboard users can\'t see which element is focused',
            'immediate_fix': 'Add clear, visible focus indicators'
        },
        {
            'title': 'Dialog animation too fast',
            'type': 'Interaction',
            'severity': 'Yellow',
            'step_name': 'Dismiss Copilot Dialog',
            'description': 'Dialog appears/disappears too quickly',
            'impact': 'Users may miss the dialog or feel disoriented',
            'immediate_fix': 'Slow down dialog animation for better UX'
        },
        {
            'title': 'Missing loading states',
            'type': 'Interaction',
            'severity': 'Yellow',
            'step_name': 'Dismiss Copilot Dialog',
            'description': 'No visual feedback during AI processing',
            'impact': 'Users don\'t know if their request is being processed',
            'immediate_fix': 'Add loading indicators for AI operations'
        },
        {
            'title': 'Inconsistent spacing in dialog',
            'type': 'Layout',
            'severity': 'Yellow',
            'step_name': 'Dismiss Copilot Dialog',
            'description': 'Dialog elements have inconsistent spacing',
            'impact': 'Reduces visual hierarchy and professional appearance',
            'immediate_fix': 'Standardize spacing throughout dialog'
        },
        {
            'title': 'Poor error handling visualization',
            'type': 'Interaction',
            'severity': 'Orange',
            'step_name': 'Dismiss Copilot Dialog',
            'description': 'Error states lack clear visual indicators',
            'impact': 'Users may not understand when something goes wrong',
            'immediate_fix': 'Add clear error state visualizations'
        },
        {
            'title': 'Missing keyboard shortcuts',
            'type': 'Accessibility',
            'severity': 'Yellow',
            'step_name': 'Dismiss Copilot Dialog',
            'description': 'Dialog lacks keyboard navigation shortcuts',
            'impact': 'Power users can\'t efficiently navigate with keyboard',
            'immediate_fix': 'Add keyboard shortcuts for common actions'
        },
        {
            'title': 'Inconsistent icon usage',
            'type': 'Design',
            'severity': 'Yellow',
            'step_name': 'Dismiss Copilot Dialog',
            'description': 'Icons don\'t follow consistent design language',
            'impact': 'Reduces visual consistency and user understanding',
            'immediate_fix': 'Standardize icon usage across dialog'
        },
        {
            'title': 'Poor responsive behavior',
            'type': 'Layout',
            'severity': 'Orange',
            'step_name': 'Dismiss Copilot Dialog',
            'description': 'Dialog doesn\'t adapt well to different screen sizes',
            'impact': 'Poor experience on different devices',
            'immediate_fix': 'Improve responsive design for dialog'
        },
        {
            'title': 'Missing progress indicators',
            'type': 'Interaction',
            'severity': 'Yellow',
            'step_name': 'Dismiss Copilot Dialog',
            'description': 'No indication of AI processing progress',
            'impact': 'Users don\'t know how long operations will take',
            'immediate_fix': 'Add progress indicators for long operations'
        },
        {
            'title': 'Inconsistent color usage',
            'type': 'Visual',
            'severity': 'Yellow',
            'step_name': 'Dismiss Copilot Dialog',
            'description': 'Colors don\'t match main application palette',
            'impact': 'Breaks visual consistency and brand identity',
            'immediate_fix': 'Use consistent color palette throughout'
        },
        {
            'title': 'Poor text hierarchy',
            'type': 'Design',
            'severity': 'Orange',
            'step_name': 'Dismiss Copilot Dialog',
            'description': 'Text elements lack clear hierarchy',
            'impact': 'Makes content difficult to scan and understand',
            'immediate_fix': 'Improve text hierarchy with proper sizing and weight'
        },
        {
            'title': 'Missing help text',
            'type': 'Interaction',
            'severity': 'Yellow',
            'step_name': 'Dismiss Copilot Dialog',
            'description': 'No contextual help for AI features',
            'impact': 'Users may not understand how to use AI features',
            'immediate_fix': 'Add contextual help and tooltips'
        },
        
        # Screenshot 3: excel_final_state_1755521895.png (8 bugs)
        {
            'title': 'Inconsistent save button styling',
            'type': 'Design',
            'severity': 'Orange',
            'step_name': 'Save Workbook',
            'description': 'Save button doesn\'t match other primary actions',
            'impact': 'Reduces visual consistency and user confidence',
            'immediate_fix': 'Standardize save button styling with other primary actions'
        },
        {
            'title': 'Poor visual feedback for save action',
            'type': 'Interaction',
            'severity': 'Orange',
            'step_name': 'Save Workbook',
            'description': 'No clear indication when save is successful',
            'impact': 'Users may not know if their work was saved',
            'immediate_fix': 'Add clear success indicators for save actions'
        },
        {
            'title': 'Missing auto-save indicators',
            'type': 'Interaction',
            'severity': 'Yellow',
            'step_name': 'Save Workbook',
            'description': 'No visual indication of auto-save status',
            'impact': 'Users may not know if their work is being saved automatically',
            'immediate_fix': 'Add auto-save status indicators'
        },
        {
            'title': 'Inconsistent file naming display',
            'type': 'Visual',
            'severity': 'Yellow',
            'step_name': 'Save Workbook',
            'description': 'File name display doesn\'t follow consistent formatting',
            'impact': 'Makes it difficult to identify files quickly',
            'immediate_fix': 'Standardize file name display formatting'
        },
        {
            'title': 'Poor error handling for save failures',
            'type': 'Interaction',
            'severity': 'Red',
            'step_name': 'Save Workbook',
            'description': 'Save errors lack clear user guidance',
            'impact': 'Users don\'t know how to resolve save issues',
            'immediate_fix': 'Add clear error messages and recovery options'
        },
        {
            'title': 'Missing save confirmation dialog',
            'type': 'Interaction',
            'severity': 'Yellow',
            'step_name': 'Save Workbook',
            'description': 'No confirmation when overwriting existing files',
            'impact': 'Users may accidentally overwrite important files',
            'immediate_fix': 'Add confirmation dialogs for destructive actions'
        },
        {
            'title': 'Inconsistent save location display',
            'type': 'Visual',
            'severity': 'Yellow',
            'step_name': 'Save Workbook',
            'description': 'Save location information is not clearly displayed',
            'impact': 'Users may not know where their files are saved',
            'immediate_fix': 'Add clear save location indicators'
        },
        {
            'title': 'Poor keyboard navigation for save',
            'type': 'Accessibility',
            'severity': 'Orange',
            'step_name': 'Save Workbook',
            'description': 'Save functionality lacks proper keyboard support',
            'impact': 'Keyboard users can\'t efficiently save their work',
            'immediate_fix': 'Add keyboard shortcuts and navigation for save'
        }
    ]
    
    # Steps data
    steps_data = [
        {
            'step_name': 'Navigate to Excel',
            'description': 'User navigates to Excel web app and sees initial interface',
            'screenshot_path': 'screenshots/excel_web/excel_initial_state_1756061972.png',
            'scenario_description': 'Excel Document Creation with Copilot',
            'persona_type': 'Power User'
        },
        {
            'step_name': 'Dismiss Copilot Dialog',
            'description': 'User dismisses the Copilot dialog with suggestions',
            'screenshot_path': 'screenshots/excel_web/excel_copilot_dialog_1756061967.png',
            'scenario_description': 'Excel Document Creation with Copilot',
            'persona_type': 'Power User'
        },
        {
            'step_name': 'Save Workbook',
            'description': 'User saves the workbook',
            'screenshot_path': 'screenshots/excel_web/excel_final_state_1755521895.png',
            'scenario_description': 'Excel Document Creation with Copilot',
            'persona_type': 'Power User'
        }
    ]
    
    # Run consolidation
    consolidated_bugs = await analyzer.consolidate_bugs(full_bugs, steps_data)
    
    # Generate HTML
    html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Consolidated Excel Web UX Analysis Report - {datetime.now().strftime('%Y-%m-%d')}</title>
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
        
        .consolidation-stats {{
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
        
        .before-after {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
            margin-bottom: 30px;
        }}
        
        .before-card, .after-card {{
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        
        .before-card h3 {{
            color: #dc3545;
            margin-bottom: 15px;
        }}
        
        .after-card h3 {{
            color: #28a745;
            margin-bottom: 15px;
        }}
        
        .bug-item {{
            background: #f8f9fa;
            margin-bottom: 10px;
            padding: 10px;
            border-radius: 5px;
            font-size: 0.9em;
        }}
        
        .consolidated-bugs {{
            background: white;
            margin-bottom: 30px;
            border-radius: 10px;
            overflow: hidden;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        
        .consolidated-header {{
            background: #f8f9fa;
            padding: 20px;
            border-bottom: 1px solid #e9ecef;
        }}
        
        .consolidated-title {{
            font-size: 1.5em;
            font-weight: bold;
            color: #333;
            margin-bottom: 10px;
        }}
        
        .consolidated-info {{
            color: #666;
            font-size: 0.9em;
        }}
        
        .bug-detail {{
            padding: 20px;
            border-bottom: 1px solid #e9ecef;
        }}
        
        .bug-detail:last-child {{
            border-bottom: none;
        }}
        
        .bug-title {{
            font-weight: bold;
            font-size: 1.2em;
            margin-bottom: 15px;
            color: #333;
        }}
        
        .bug-meta {{
            display: flex;
            gap: 15px;
            margin-bottom: 15px;
            flex-wrap: wrap;
        }}
        
        .bug-type {{
            background: #e9ecef;
            padding: 4px 12px;
            border-radius: 15px;
            font-size: 0.8em;
        }}
        
        .bug-severity {{
            padding: 4px 12px;
            border-radius: 15px;
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
            margin-bottom: 15px;
            color: #555;
        }}
        
        .bug-impact {{
            margin-bottom: 15px;
            font-style: italic;
            color: #666;
        }}
        
        .bug-fix {{
            background: #e8f5e8;
            padding: 12px;
            border-radius: 8px;
            font-size: 0.9em;
            color: #2d5a2d;
        }}
        
        .affected-screenshots {{
            margin-top: 15px;
            padding: 15px;
            background: #f8f9fa;
            border-radius: 8px;
        }}
        
        .screenshot-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 15px;
            margin-top: 10px;
        }}
        
        .screenshot-item {{
            text-align: center;
        }}
        
        .screenshot-item img {{
            max-width: 100%;
            height: auto;
            border-radius: 5px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        
        .screenshot-caption {{
            margin-top: 8px;
            font-size: 0.8em;
            color: #666;
        }}
        
        .consolidation-note {{
            background: #fff3cd;
            border: 1px solid #ffeaa7;
            color: #856404;
            padding: 10px;
            border-radius: 5px;
            margin-top: 10px;
            font-size: 0.9em;
        }}
        
        @media (max-width: 768px) {{
            .before-after {{
                grid-template-columns: 1fr;
            }}
            
            .consolidation-stats {{
                grid-template-columns: repeat(2, 1fr);
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔍 Consolidated Excel Web UX Analysis Report</h1>
            <div class="subtitle">Multi-Screenshot Analysis with Intelligent Deduplication</div>
            <div style="margin-top: 15px; font-size: 0.9em; opacity: 0.8;">
                Generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}
            </div>
        </div>
        
        <div class="consolidation-stats">
            <div class="stat-card">
                <div class="stat-number">{len(full_bugs)}</div>
                <div class="stat-label">Raw Bugs Found</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{len(consolidated_bugs)}</div>
                <div class="stat-label">Consolidated Bugs</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{len(full_bugs) - len(consolidated_bugs)}</div>
                <div class="stat-label">Duplicates Removed</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{((len(full_bugs) - len(consolidated_bugs)) / len(full_bugs) * 100):.1f}%</div>
                <div class="stat-label">Reduction Rate</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{len(steps_data)}</div>
                <div class="stat-label">Screenshots Analyzed</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">GPT-4o</div>
                <div class="stat-label">Consolidation Model</div>
            </div>
        </div>
        
        <div class="before-after">
            <div class="before-card">
                <h3>📊 Before Consolidation</h3>
                <p><strong>Raw Issues:</strong> {len(full_bugs)} bugs across {len(steps_data)} screenshots</p>
                <div style="margin-top: 15px;">
                    <strong>Sample Raw Bugs:</strong>
                    <div class="bug-item">• Low color contrast in toolbar</div>
                    <div class="bug-item">• Insufficient contrast in dialog text</div>
                    <div class="bug-item">• Missing hover states for interactive elements</div>
                    <div class="bug-item">• Inconsistent button styling</div>
                    <div class="bug-item">• Poor visual feedback for save action</div>
                    <div class="bug-item">• ... and {len(full_bugs) - 5} more</div>
                </div>
            </div>
            <div class="after-card">
                <h3>✅ After Consolidation</h3>
                <p><strong>Unique Issues:</strong> {len(consolidated_bugs)} developer-ready bugs</p>
                <div style="margin-top: 15px;">
                    <strong>Consolidated Categories:</strong>
                    <div class="bug-item">• Accessibility issues (color contrast, ARIA)</div>
                    <div class="bug-item">• Interaction feedback (save actions, loading states)</div>
                    <div class="bug-item">• Layout problems (dialog positioning)</div>
                    <div class="bug-item">• Design system consistency (button styling)</div>
                    <div class="bug-item">• Visual hierarchy and spacing</div>
                </div>
            </div>
        </div>
        
        <div class="consolidated-bugs">
            <div class="consolidated-header">
                <div class="consolidated-title">🎯 Consolidated Developer-Ready Bugs</div>
                <div class="consolidated-info">
                    {len(consolidated_bugs)} unique, actionable issues after intelligent deduplication
                </div>
            </div>
"""
    
    # Add each consolidated bug
    for i, bug in enumerate(consolidated_bugs, 1):
        severity_class = bug.get('severity', 'Yellow').lower()
        
        # Get affected screenshots
        screenshot_paths = bug.get('screenshot_paths', [])
        screenshot_html = ""
        
        if screenshot_paths:
            screenshot_html = '<div class="affected-screenshots">'
            screenshot_html += '<strong>Affected Screenshots:</strong>'
            screenshot_html += '<div class="screenshot-grid">'
            
            for screenshot_path in screenshot_paths:
                screenshot_base64 = encode_image_to_base64(screenshot_path)
                if screenshot_base64:
                    screenshot_name = os.path.basename(screenshot_path)
                    screenshot_html += f'''
                    <div class="screenshot-item">
                        <img src="data:image/png;base64,{screenshot_base64}" alt="Screenshot: {screenshot_name}">
                        <div class="screenshot-caption">{screenshot_name}</div>
                    </div>
                    '''
            
            screenshot_html += '</div></div>'
        
        html_content += f"""
            <div class="bug-detail">
                <div class="bug-title">{bug.get('title', 'Unknown Bug')}</div>
                <div class="bug-meta">
                    <span class="bug-type">{bug.get('type', 'Unknown')}</span>
                    <span class="bug-severity {severity_class}">{bug.get('severity', 'Yellow')}</span>
                </div>
                <div class="bug-description">
                    <strong>Issue:</strong> {bug.get('description', 'No description available')}
                </div>
                <div class="bug-impact">
                    <strong>Impact:</strong> {bug.get('impact', 'No impact specified')}
                </div>
                <div class="bug-fix">
                    <strong>Developer Fix:</strong> {bug.get('immediate_fix', 'No fix specified')}
                </div>
                {screenshot_html}
                <div class="consolidation-note">
                    <strong>Consolidation Note:</strong> {bug.get('consolidation_note', 'This issue was identified through multi-screenshot analysis and deduplication.')}
                </div>
            </div>
"""
    
    # Close HTML
    html_content += """
        </div>
    </div>
</body>
</html>
"""
    
    # Write to file
    with open('consolidated_bug_report.html', 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print("✅ Consolidated bug report generated: consolidated_bug_report.html")
    print("📊 Report includes:")
    print(f"   - {len(consolidated_bugs)} consolidated bugs (reduced from {len(full_bugs)})")
    print("   - Before/after comparison")
    print("   - Screenshots embedded for each bug")
    print("   - Developer-ready fixes and impact analysis")
    print("   - Consolidation notes and deduplication details")

if __name__ == "__main__":
    asyncio.run(generate_consolidated_html_report())

