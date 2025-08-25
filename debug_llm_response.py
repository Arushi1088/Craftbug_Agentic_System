#!/usr/bin/env python3
"""
Debug script to see what the LLM is returning in affected_steps
"""

import asyncio
import json
from pathlib import Path
from final_craft_bug_analyzer import FinalCraftBugAnalyzer

async def debug_llm_response():
    """Debug what the LLM is returning"""
    
    print("🔍 Debugging LLM Response...")
    
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
    
    # Run analysis
    bugs = await analyzer.analyze_screenshots(steps_with_screenshots)
    
    print(f"\n🎯 Found {len(bugs)} bugs")
    
    # Debug each bug's affected_steps
    for i, bug in enumerate(bugs, 1):
        print(f"\n--- Bug {i} ---")
        print(f"Title: {bug.get('title', 'Unknown')}")
        print(f"Affected Steps: '{bug.get('affected_steps', 'None')}'")
        print(f"Screenshot Paths: {bug.get('screenshot_paths', [])}")
        print(f"Step Name: '{bug.get('step_name', 'None')}'")

if __name__ == "__main__":
    asyncio.run(debug_llm_response())
