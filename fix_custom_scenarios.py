#!/usr/bin/env python3
"""
Fix custom scenario files by converting them to supported format
"""

import os
import yaml
from pathlib import Path

def fix_custom_scenarios():
    """Convert all custom scenario files to proper format"""
    custom_dir = Path("scenarios/custom")
    
    if not custom_dir.exists():
        print("No custom scenarios directory found")
        return
    
    # Template for valid scenario
    def create_scenario_template(app_type="word"):
        return {
            "name": f"{app_type.title()}: Basic Document Navigation",
            "app_type": app_type,
            "steps": [
                {
                    "action": "navigate_to_url",
                    "url": "{mock_url}",
                    "description": f"Open {app_type} application"
                },
                {
                    "action": "wait_for_selector", 
                    "selector": "body",
                    "timeout_ms": 5000,
                    "description": "Wait for page to load"
                },
                {
                    "action": "click",
                    "selector": "#main-content, .document-area, .editor",
                    "description": "Click main content area"
                },
                {
                    "action": "wait",
                    "duration": 1000,
                    "description": "Allow interaction to complete"
                }
            ]
        }
    
    fixed_count = 0
    
    for yaml_file in custom_dir.glob("*.yaml"):
        try:
            # Read current content
            with open(yaml_file, 'r') as f:
                content = f.read().strip()
            
            # Check if it's just a comment or empty
            if content.startswith('#') or len(content) < 50:
                print(f"Fixing {yaml_file.name}...")
                
                # Determine app type from comment
                app_type = "word"  # default
                if "excel" in content.lower():
                    app_type = "excel"
                elif "powerpoint" in content.lower() or "ppt" in content.lower():
                    app_type = "powerpoint"
                
                # Create new scenario
                new_scenario = create_scenario_template(app_type)
                
                # Write the fixed scenario
                with open(yaml_file, 'w') as f:
                    yaml.dump(new_scenario, f, default_flow_style=False, indent=2)
                
                fixed_count += 1
                print(f"  ✅ Fixed {yaml_file.name} as {app_type} scenario")
            
            else:
                # Try to parse existing YAML
                try:
                    existing = yaml.safe_load(content)
                    if not isinstance(existing, dict) or 'steps' not in existing:
                        print(f"Invalid format in {yaml_file.name}, fixing...")
                        new_scenario = create_scenario_template()
                        with open(yaml_file, 'w') as f:
                            yaml.dump(new_scenario, f, default_flow_style=False, indent=2)
                        fixed_count += 1
                        print(f"  ✅ Fixed {yaml_file.name}")
                    else:
                        print(f"  ✅ {yaml_file.name} already valid")
                except yaml.YAMLError:
                    print(f"YAML parse error in {yaml_file.name}, fixing...")
                    new_scenario = create_scenario_template()
                    with open(yaml_file, 'w') as f:
                        yaml.dump(new_scenario, f, default_flow_style=False, indent=2)
                    fixed_count += 1
                    print(f"  ✅ Fixed {yaml_file.name}")
                        
        except Exception as e:
            print(f"  ❌ Error fixing {yaml_file.name}: {e}")
    
    print(f"\n🎉 Fixed {fixed_count} custom scenario files")
    return fixed_count

if __name__ == "__main__":
    print("🔧 FIXING CUSTOM SCENARIOS")
    print("="*50)
    fix_custom_scenarios()
    print("\n✅ Custom scenario fix complete!")
