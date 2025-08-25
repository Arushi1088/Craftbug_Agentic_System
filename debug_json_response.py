#!/usr/bin/env python3
"""
Debug script to see what the LLM is returning and why JSON parsing is failing
"""

import asyncio
import json
from pathlib import Path
from final_craft_bug_analyzer import FinalCraftBugAnalyzer

async def debug_json_response():
    """Debug what the LLM is returning"""
    
    print("🔍 Debugging JSON Response...")
    
    # Load existing telemetry data
    telemetry_file = Path("telemetry_output/telemetry_document_creation_20250825_125803.json")
    if not telemetry_file.exists():
        print("❌ Telemetry file not found")
        return
    
    with open(telemetry_file, 'r') as f:
        telemetry_data = json.load(f)
    
    # Get steps with screenshots
    steps_with_screenshots = []
    for step in telemetry_data.get('steps', []):
        if step.get('screenshot_path') and Path(step['screenshot_path']).exists():
            steps_with_screenshots.append(step)
    
    print(f"📸 Found {len(steps_with_screenshots)} steps with screenshots")
    
    # Initialize analyzer
    analyzer = FinalCraftBugAnalyzer()
    
    # Get unique steps
    unique_steps = analyzer._deduplicate_and_validate_steps(steps_with_screenshots)
    print(f"📸 Using {len(unique_steps)} unique screenshots for analysis")
    
    # Prepare context
    context = analyzer._prepare_context(unique_steps)
    
    # Prepare images
    ordered_steps = await analyzer._prepare_images_with_data(unique_steps)
    print(f"📸 Prepared {len(ordered_steps)} ordered steps")
    
    # Run analysis
    analysis_text = await analyzer._run_analysis_with_images(context, ordered_steps)
    
    if not analysis_text:
        print("❌ Analysis failed")
        return
    
    print(f"\n📄 Raw LLM Response ({len(analysis_text)} chars):")
    print("=" * 50)
    print(analysis_text)  # Full response
    print("=" * 50)
    
    # Try JSON parsing
    data = analyzer._try_parse_json(analysis_text)
    if data:
        print(f"✅ JSON parsing successful!")
        print(f"📊 Found {len(data.get('bugs', []))} bugs in JSON")
        
        # Show first bug structure
        if data.get('bugs'):
            first_bug = data['bugs'][0]
            print(f"\n🐛 First bug structure:")
            print(json.dumps(first_bug, indent=2))
    else:
        print("❌ JSON parsing failed")
        
        # Try to find JSON-like content
        if '{"bugs"' in analysis_text:
            start = analysis_text.find('{"bugs"')
            end = analysis_text.rfind('}') + 1
            json_part = analysis_text[start:end]
            print(f"\n🔍 Found JSON-like content:")
            print(json_part)
            
            try:
                parsed = json.loads(json_part)
                print("✅ Extracted JSON is valid!")
            except Exception as e:
                print(f"❌ Extracted JSON is invalid: {e}")

if __name__ == "__main__":
    asyncio.run(debug_json_response())
