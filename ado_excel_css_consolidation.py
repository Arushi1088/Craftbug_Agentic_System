#!/usr/bin/env python3
"""
ADO Excel CSS Bug Consolidation
Consolidates the ADO reference bugs into CSS-specific categories
"""

import json
import os
from datetime import datetime

def load_ado_bugs():
    """Load ADO bug data"""
    try:
        with open('ado_data/craft_bugs_20250819_150824.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print("ADO bug file not found")
        return []

def consolidate_css_bugs(bugs):
    """Consolidate bugs into CSS categories"""
    
    css_categories = {
        'Color & Contrast': [],
        'Spacing & Layout': [],
        'Typography': [],
        'Border & Radius': [],
        'Shadow & Elevation': [],
        'Animation & Performance': [],
        'Alignment & Positioning': [],
        'Design System Violations': []
    }
    
    for bug in bugs:
        title = bug.get('title', '').lower()
        description = bug.get('description', '').lower()
        tags = bug.get('tags', '').lower()
        
        # Categorize based on content
        if any(word in title or word in description for word in ['color', 'contrast', 'palette', 'hex']):
            css_categories['Color & Contrast'].append(bug)
        elif any(word in title or word in description for word in ['spacing', 'padding', 'margin', 'gap', 'rhythm']):
            css_categories['Spacing & Layout'].append(bug)
        elif any(word in title or word in description for word in ['font', 'typography', 'text', 'size']):
            css_categories['Typography'].append(bug)
        elif any(word in title or word in description for word in ['border', 'radius', 'rounded']):
            css_categories['Border & Radius'].append(bug)
        elif any(word in title or word in description for word in ['shadow', 'elevation', 'surface']):
            css_categories['Shadow & Elevation'].append(bug)
        elif any(word in title or word in description for word in ['animation', 'transition', 'loading', 'smooth']):
            css_categories['Animation & Performance'].append(bug)
        elif any(word in title or word in description for word in ['align', 'position', 'misaligned']):
            css_categories['Alignment & Positioning'].append(bug)
        elif any(word in title or word in description for word in ['design system', 'inconsistent', 'standard']):
            css_categories['Design System Violations'].append(bug)
    
    return css_categories

def generate_css_fixes(bugs):
    """Generate CSS fixes for bugs"""
    fixes = []
    
    for bug in bugs:
        title = bug.get('title', '')
        description = bug.get('description', '')
        
        # Generate CSS fix based on bug type
        if 'color' in title.lower() or 'palette' in description.lower():
            if 'selection' in title.lower():
                fixes.append({
                    'bug': title,
                    'css_fix': '.excel-cell-selected { background-color: #106ebe !important; }',
                    'explanation': 'Fix cell selection color to match design system'
                })
            elif 'hover' in title.lower():
                fixes.append({
                    'bug': title,
                    'css_fix': '.excel-button:hover { background-color: #005a9e !important; }',
                    'explanation': 'Fix button hover state color'
                })
        
        elif 'spacing' in title.lower() or 'padding' in description.lower():
            if 'icon' in title.lower():
                fixes.append({
                    'bug': title,
                    'css_fix': '.format-panel-icon { margin: 0 8px !important; }',
                    'explanation': 'Standardize icon spacing to 8px'
                })
            elif 'panel' in title.lower():
                fixes.append({
                    'bug': title,
                    'css_fix': '.excel-panel { padding: 16px !important; }',
                    'explanation': 'Standardize panel padding to 16px'
                })
        
        elif 'font' in title.lower() or 'typography' in description.lower():
            fixes.append({
                'bug': title,
                'css_fix': '.save-dialog { font-size: 14px !important; }',
                'explanation': 'Fix typography to match design system'
            })
        
        elif 'border' in title.lower() or 'radius' in description.lower():
            fixes.append({
                'bug': title,
                'css_fix': '.chart-dropdown { border-radius: 4px !important; }',
                'explanation': 'Standardize border radius to 4px'
            })
        
        elif 'shadow' in title.lower() or 'elevation' in description.lower():
            fixes.append({
                'bug': title,
                'css_fix': '.excel-tooltip { box-shadow: 0 4px 8px rgba(0,0,0,0.12) !important; }',
                'explanation': 'Fix tooltip shadow to L3 elevation'
            })
        
        elif 'animation' in title.lower():
            fixes.append({
                'bug': title,
                'css_fix': '.loading-spinner { animation-duration: 400ms !important; }',
                'explanation': 'Fix animation timing to standard 400ms'
            })
        
        elif 'align' in title.lower():
            fixes.append({
                'bug': title,
                'css_fix': '.ribbon-button { vertical-align: middle !important; }',
                'explanation': 'Fix button alignment in ribbon'
            })
    
    return fixes

def create_css_consolidation_report():
    """Create comprehensive CSS consolidation report"""
    
    print("🔍 Loading ADO Excel CSS bugs...")
    bugs = load_ado_bugs()
    
    if not bugs:
        print("❌ No bugs found")
        return
    
    print(f"📊 Found {len(bugs)} ADO bugs to consolidate")
    
    # Consolidate by CSS category
    css_categories = consolidate_css_bugs(bugs)
    
    # Generate CSS fixes
    all_fixes = generate_css_fixes(bugs)
    
    # Create HTML report
    html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ADO Excel CSS Bug Consolidation - {datetime.now().strftime('%Y-%m-%d')}</title>
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
            background: #f8f9fa;
        }}
        
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
        }}
        
        .header {{
            background: linear-gradient(135deg, #0078d4 0%, #106ebe 100%);
            color: white;
            padding: 40px 20px;
            text-align: center;
            border-radius: 15px;
            margin-bottom: 30px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.1);
        }}
        
        .header h1 {{
            font-size: 2.8em;
            margin-bottom: 15px;
            font-weight: 700;
        }}
        
        .header .subtitle {{
            font-size: 1.3em;
            opacity: 0.9;
            margin-bottom: 10px;
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
            color: #0078d4;
            margin-bottom: 5px;
        }}
        
        .stat-label {{
            color: #666;
            font-size: 0.9em;
            font-weight: 500;
        }}
        
        .category-section {{
            background: white;
            border-radius: 12px;
            overflow: hidden;
            box-shadow: 0 4px 15px rgba(0,0,0,0.08);
            margin-bottom: 30px;
        }}
        
        .category-header {{
            background: #f8f9fa;
            padding: 25px;
            border-bottom: 1px solid #e9ecef;
        }}
        
        .category-title {{
            font-size: 1.8em;
            font-weight: bold;
            color: #333;
            margin-bottom: 10px;
        }}
        
        .category-count {{
            color: #666;
            font-size: 1em;
        }}
        
        .bug-item {{
            padding: 25px;
            border-bottom: 1px solid #e9ecef;
            transition: background-color 0.2s;
        }}
        
        .bug-item:hover {{
            background-color: #f8f9fa;
        }}
        
        .bug-item:last-child {{
            border-bottom: none;
        }}
        
        .bug-header {{
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            margin-bottom: 15px;
            gap: 20px;
        }}
        
        .bug-title {{
            font-size: 1.2em;
            font-weight: bold;
            color: #333;
            flex: 1;
        }}
        
        .bug-severity {{
            padding: 4px 12px;
            border-radius: 15px;
            font-size: 0.8em;
            font-weight: bold;
            color: white;
        }}
        
        .bug-severity.medium {{
            background: #fd7e14;
        }}
        
        .bug-severity.low {{
            background: #ffc107;
            color: #333;
        }}
        
        .bug-description {{
            color: #666;
            margin-bottom: 15px;
            font-size: 0.95em;
        }}
        
        .css-fix {{
            background: #f8f9fa;
            border: 1px solid #e9ecef;
            border-radius: 8px;
            padding: 15px;
            margin-top: 10px;
        }}
        
        .css-code {{
            background: #2d3748;
            color: #e2e8f0;
            padding: 12px;
            border-radius: 6px;
            font-family: 'Courier New', monospace;
            font-size: 0.9em;
            margin: 10px 0;
            overflow-x: auto;
        }}
        
        .fix-explanation {{
            color: #2d3748;
            font-size: 0.9em;
            font-style: italic;
        }}
        
        .footer {{
            text-align: center;
            padding: 30px;
            color: #666;
            font-size: 0.9em;
        }}
        
        @media (max-width: 768px) {{
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
            <h1>🎨 ADO Excel CSS Bug Consolidation</h1>
            <div class="subtitle">Comprehensive CSS Fixes for Excel Web Craft Bugs</div>
            <div style="margin-top: 15px; font-size: 0.9em; opacity: 0.8;">
                Generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}
            </div>
        </div>
        
        <div class="summary-stats">
            <div class="stat-card">
                <div class="stat-number">{len(bugs)}</div>
                <div class="stat-label">Total ADO Bugs</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{len(css_categories)}</div>
                <div class="stat-label">CSS Categories</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{len(all_fixes)}</div>
                <div class="stat-label">CSS Fixes Generated</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">ADO</div>
                <div class="stat-label">Data Source</div>
            </div>
        </div>
"""
    
    # Add each CSS category
    for category_name, category_bugs in css_categories.items():
        if not category_bugs:
            continue
            
        html_content += f"""
        <div class="category-section">
            <div class="category-header">
                <div class="category-title">🎯 {category_name}</div>
                <div class="category-count">{len(category_bugs)} bugs in this category</div>
            </div>
"""
        
        for bug in category_bugs:
            severity_class = bug.get('severity', 'Low').lower()
            
            # Find corresponding CSS fix
            bug_fix = None
            for fix in all_fixes:
                if fix['bug'] == bug['title']:
                    bug_fix = fix
                    break
            
            html_content += f"""
            <div class="bug-item">
                <div class="bug-header">
                    <div class="bug-title">{bug.get('title', 'Unknown Bug')}</div>
                    <div class="bug-severity {severity_class}">{bug.get('severity', 'Low')}</div>
                </div>
                <div class="bug-description">{bug.get('description', 'No description available')}</div>
"""
            
            if bug_fix:
                html_content += f"""
                <div class="css-fix">
                    <strong>🔧 CSS Fix:</strong>
                    <div class="css-code">{bug_fix['css_fix']}</div>
                    <div class="fix-explanation">{bug_fix['explanation']}</div>
                </div>
"""
            
            html_content += """
            </div>
"""
        
        html_content += """
        </div>
"""
    
    # Add comprehensive CSS fixes section
    html_content += f"""
        <div class="category-section">
            <div class="category-header">
                <div class="category-title">📋 Complete CSS Fixes Summary</div>
                <div class="category-count">All {len(all_fixes)} fixes in one place</div>
            </div>
            <div style="padding: 25px;">
                <div class="css-code">
"""
    
    for fix in all_fixes:
        html_content += f"""
/* {fix['bug']} */
{fix['css_fix']}
/* {fix['explanation']} */

"""
    
    html_content += """
                </div>
            </div>
        </div>
        
        <div class="footer">
            <p><strong>Source:</strong> ADO Craft Bugs Reference Data</p>
            <p><strong>Analysis Date:</strong> """ + datetime.now().strftime('%B %d, %Y at %I:%M %p') + """</p>
            <p><strong>Total Bugs Analyzed:</strong> """ + str(len(bugs)) + """ | <strong>CSS Fixes Generated:</strong> """ + str(len(all_fixes)) + """</p>
        </div>
    </div>
</body>
</html>
"""
    
    # Write to file
    with open('ado_excel_css_consolidation.html', 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print("✅ ADO Excel CSS consolidation report generated: ado_excel_css_consolidation.html")
    print("📊 Report includes:")
    print(f"   - {len(bugs)} ADO bugs categorized by CSS type")
    print(f"   - {len(css_categories)} CSS categories")
    print(f"   - {len(all_fixes)} specific CSS fixes")
    print("   - Complete CSS code block for easy implementation")

if __name__ == "__main__":
    create_css_consolidation_report()

