#!/usr/bin/env python3
"""
Test the JSON-first analyzer with a small batch of screenshots
"""

import asyncio
import json
from pathlib import Path
from final_craft_bug_analyzer import FinalCraftBugAnalyzer

async def test_small_batch():
    """Test with just 2-3 screenshots to verify the fix"""
    
    print("🧪 Testing JSON-First Analyzer with Small Batch...")
    
    # Load existing telemetry data
    telemetry_file = Path("telemetry_output/telemetry_document_creation_20250825_125803.json")
    if not telemetry_file.exists():
        print("❌ Telemetry file not found")
        return
    
    with open(telemetry_file, 'r') as f:
        telemetry_data = json.load(f)
    
    # Get only 2-3 steps with screenshots for testing
    steps_with_screenshots = []
    for step in telemetry_data.get('steps', []):
        if step.get('screenshot_path') and Path(step['screenshot_path']).exists():
            steps_with_screenshots.append(step)
            if len(steps_with_screenshots) >= 3:  # Limit to 3 for testing
                break
    
    print(f"📸 Testing with {len(steps_with_screenshots)} screenshots")
    
    # Show what we're testing with
    for i, step in enumerate(steps_with_screenshots, 1):
        print(f"  Step {i}: {step.get('step_name', 'Unknown')} → {Path(step['screenshot_path']).name}")
    
    # Initialize analyzer
    analyzer = FinalCraftBugAnalyzer()
    
    # Run analysis
    bugs = await analyzer.analyze_screenshots(steps_with_screenshots)
    
    print(f"\n🎯 Analysis Results:")
    print(f"✅ Found {len(bugs)} bugs")
    
    # Check each bug for proper screenshot assignment
    for i, bug in enumerate(bugs, 1):
        print(f"\n--- Bug {i} ---")
        print(f"Title: {bug.get('title', 'Unknown')}")
        print(f"Type: {bug.get('type', 'Unknown')}")
        print(f"Severity: {bug.get('severity', 'Unknown')}")
        
        # Check screenshot assignment
        screenshot_paths = bug.get('screenshot_paths', [])
        print(f"Screenshot Paths: {len(screenshot_paths)} assigned")
        
        for j, path in enumerate(screenshot_paths, 1):
            if path and Path(path).exists():
                print(f"  ✅ Screenshot {j}: {Path(path).name} (exists)")
            else:
                print(f"  ❌ Screenshot {j}: {path} (missing/invalid)")
        
        # Check affected steps
        affected_steps = bug.get('affected_steps', [])
        print(f"Affected Steps: {len(affected_steps)} referenced")
        
        # Check if any paths are None
        if None in screenshot_paths:
            print("  ⚠️ WARNING: Found None in screenshot paths!")
        else:
            print("  ✅ All screenshot paths are valid")
    
    # Summary
    total_screenshots = sum(len(bug.get('screenshot_paths', [])) for bug in bugs)
    valid_screenshots = sum(
        len([p for p in bug.get('screenshot_paths', []) if p and Path(p).exists()])
        for bug in bugs
    )
    
    print(f"\n📊 Summary:")
    print(f"  Total bugs: {len(bugs)}")
    print(f"  Total screenshots assigned: {total_screenshots}")
    print(f"  Valid screenshots: {valid_screenshots}")
    print(f"  Invalid screenshots: {total_screenshots - valid_screenshots}")
    
    if total_screenshots == valid_screenshots and total_screenshots > 0:
        print("✅ SUCCESS: All screenshots are valid and properly assigned!")
        return True
    else:
        print("❌ ISSUES FOUND: Some screenshots are invalid or missing")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_small_batch())
    if success:
        print("\n🎉 Ready for full analysis!")
    else:
        print("\n⚠️ Please fix issues before running full analysis")
