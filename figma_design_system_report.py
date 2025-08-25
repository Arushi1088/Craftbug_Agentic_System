#!/usr/bin/env python3
"""
Figma Design System Report Generator
Shows comprehensive design system specifications from Figma files
"""

import json
from datetime import datetime
from figma_design_system_integration import FigmaDesignSystemIntegration

def generate_figma_design_report():
    """Generate comprehensive Figma design system report"""
    
    print("🎨 Generating Figma Design System Report...")
    
    # Initialize Figma integration
    figma_integration = FigmaDesignSystemIntegration()
    
    # Get all design systems
    design_systems = {
        "excel_web_fluent": "Excel Web Fluent 2",
        "office_icons": "Office Icons",
        "excel_copilot": "Excel Copilot UI Kit"
    }
    
    all_data = {}
    
    for system_key, system_name in design_systems.items():
        print(f"📊 Processing {system_name}...")
        
        # Extract design tokens
        tokens = figma_integration.extract_design_tokens(system_key)
        
        # Get component specifications
        components = figma_integration.get_component_specifications(system_key)
        
        # Generate report
        report = figma_integration.generate_design_report(system_key)
        
        all_data[system_key] = {
            "name": system_name,
            "tokens": tokens,
            "components": components,
            "report": report
        }
    
    # Create HTML report
    html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Figma Design System Specifications - {datetime.now().strftime('%Y-%m-%d')}</title>
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
            max-width: 1600px;
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
        
        .system-section {{
            background: white;
            border-radius: 12px;
            overflow: hidden;
            box-shadow: 0 4px 15px rgba(0,0,0,0.08);
            margin-bottom: 30px;
        }}
        
        .system-header {{
            background: #f8f9fa;
            padding: 25px;
            border-bottom: 1px solid #e9ecef;
        }}
        
        .system-title {{
            font-size: 1.8em;
            font-weight: bold;
            color: #333;
            margin-bottom: 10px;
        }}
        
        .system-stats {{
            display: flex;
            gap: 20px;
            color: #666;
            font-size: 0.9em;
        }}
        
        .tokens-section {{
            padding: 25px;
            border-bottom: 1px solid #e9ecef;
        }}
        
        .section-title {{
            font-size: 1.4em;
            font-weight: bold;
            color: #333;
            margin-bottom: 20px;
        }}
        
        .token-categories {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
        }}
        
        .token-category {{
            background: #f8f9fa;
            border-radius: 8px;
            padding: 20px;
        }}
        
        .category-title {{
            font-weight: bold;
            color: #333;
            margin-bottom: 15px;
            text-transform: capitalize;
        }}
        
        .token-list {{
            display: flex;
            flex-direction: column;
            gap: 8px;
        }}
        
        .token-item {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 8px 12px;
            background: white;
            border-radius: 6px;
            border: 1px solid #e9ecef;
        }}
        
        .token-name {{
            font-family: 'Courier New', monospace;
            font-size: 0.9em;
            color: #333;
        }}
        
        .token-value {{
            font-family: 'Courier New', monospace;
            font-size: 0.9em;
            color: #0078d4;
            font-weight: bold;
        }}
        
        .components-section {{
            padding: 25px;
        }}
        
        .component-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
            gap: 20px;
        }}
        
        .component-card {{
            background: #f8f9fa;
            border-radius: 8px;
            padding: 20px;
            border: 1px solid #e9ecef;
        }}
        
        .component-name {{
            font-weight: bold;
            color: #333;
            margin-bottom: 15px;
            font-size: 1.1em;
        }}
        
        .component-properties {{
            display: flex;
            flex-direction: column;
            gap: 8px;
        }}
        
        .property-item {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 6px 10px;
            background: white;
            border-radius: 4px;
            font-size: 0.9em;
        }}
        
        .property-name {{
            color: #666;
        }}
        
        .property-value {{
            font-family: 'Courier New', monospace;
            color: #0078d4;
            font-weight: bold;
        }}
        
        .footer {{
            text-align: center;
            padding: 30px;
            color: #666;
            font-size: 0.9em;
        }}
        
        @media (max-width: 768px) {{
            .summary-stats {{
                grid-template-columns: repeat(2, 1fr);
            }}
            
            .token-categories {{
                grid-template-columns: 1fr;
            }}
            
            .component-grid {{
                grid-template-columns: 1fr;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎨 Figma Design System Specifications</h1>
            <div class="subtitle">Comprehensive Design Tokens & Components from Excel Web Figma Files</div>
            <div style="margin-top: 15px; font-size: 0.9em; opacity: 0.8;">
                Generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}
            </div>
        </div>
        
        <div class="summary-stats">
            <div class="stat-card">
                <div class="stat-number">{len(design_systems)}</div>
                <div class="stat-label">Design Systems</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{sum(len(data['tokens']) for data in all_data.values())}</div>
                <div class="stat-label">Total Design Tokens</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{sum(len(data['components']) for data in all_data.values())}</div>
                <div class="stat-label">Total Components</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">Figma</div>
                <div class="stat-label">Data Source</div>
            </div>
        </div>
"""
    
    # Add each design system
    for system_key, data in all_data.items():
        html_content += f"""
        <div class="system-section">
            <div class="system-header">
                <div class="system-title">🎯 {data['name']}</div>
                <div class="system-stats">
                    <span>📊 {len(data['tokens'])} Design Tokens</span>
                    <span>🔧 {len(data['components'])} Components</span>
                    <span>📁 {len(data['report']['token_categories'])} Token Categories</span>
                </div>
            </div>
"""
        
        # Add design tokens section
        if data['tokens']:
            html_content += """
            <div class="tokens-section">
                <div class="section-title">🎨 Design Tokens</div>
                <div class="token-categories">
"""
            
            # Group tokens by type
            token_categories = {}
            for token in data['tokens']:
                if token.type not in token_categories:
                    token_categories[token.type] = []
                token_categories[token.type].append(token)
            
            for category, tokens in token_categories.items():
                html_content += f"""
                    <div class="token-category">
                        <div class="category-title">{category.replace('_', ' ').title()}</div>
                        <div class="token-list">
"""
                
                for token in tokens:
                    html_content += f"""
                            <div class="token-item">
                                <span class="token-name">{token.name}</span>
                                <span class="token-value">{token.value}</span>
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
        
        # Add components section
        if data['components']:
            html_content += """
            <div class="components-section">
                <div class="section-title">🔧 Component Specifications</div>
                <div class="component-grid">
"""
            
            for component in data['components']:
                html_content += f"""
                    <div class="component-card">
                        <div class="component-name">{component.name}</div>
                        <div class="component-properties">
"""
                
                for prop_name, prop_value in component.properties.items():
                    html_content += f"""
                            <div class="property-item">
                                <span class="property-name">{prop_name}</span>
                                <span class="property-value">{prop_value}</span>
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
        
        html_content += """
        </div>
"""
    
    # Close HTML
    html_content += f"""
        <div class="footer">
            <p><strong>Source:</strong> Figma Design System Files</p>
            <p><strong>Analysis Date:</strong> """ + datetime.now().strftime('%B %d, %Y at %I:%M %p') + """</p>
            <p><strong>Total Design Systems:</strong> {len(design_systems)} | <strong>Total Tokens:</strong> {sum(len(data['tokens']) for data in all_data.values())} | <strong>Total Components:</strong> {sum(len(data['components']) for data in all_data.values())}</p>
        </div>
    </div>
</body>
</html>
"""
    
    # Write to file
    with open('figma_design_system_report.html', 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print("✅ Figma design system report generated: figma_design_system_report.html")
    print("📊 Report includes:")
    print(f"   - {len(design_systems)} design systems analyzed")
    print(f"   - {sum(len(data['tokens']) for data in all_data.values())} total design tokens")
    print(f"   - {sum(len(data['components']) for data in all_data.values())} total components")
    print("   - Complete design token specifications")
    print("   - Component specifications with properties")
    print("   - Organized by design system categories")

if __name__ == "__main__":
    generate_figma_design_report()

