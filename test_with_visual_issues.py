#!/usr/bin/env python3
"""
Test with Visual Issues
======================

Test the new prompts with a screenshot that has visual issues.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def test_with_visual_issues():
    """Test with a screenshot that has visual issues"""
    
    print("🧪 TESTING WITH VISUAL ISSUES")
    print("=" * 40)
    
    try:
        from llm_enhanced_analyzer import LLMEnhancedAnalyzer
        
        # Look for copilot dialog screenshots which might have visual issues
        screenshots_dir = Path("screenshots/excel_web")
        if not screenshots_dir.exists():
            print("❌ No screenshots directory found")
            return
        
        # Look for copilot dialog screenshots
        screenshot_files = list(screenshots_dir.glob("*copilot*.png"))
        if not screenshot_files:
            # Fallback to any screenshot
            screenshot_files = list(screenshots_dir.glob("*.png"))
        
        if not screenshot_files:
            print("❌ No screenshot files found")
            return
        
        test_screenshot = max(screenshot_files, key=lambda x: x.stat().st_mtime)
        print(f"📸 Using screenshot: {test_screenshot.name}")
        
        # Create test step
        test_step = {
            "step_name": "Test Step (1 of 1)",
            "action_type": "test",
            "duration_ms": 1000,
            "screenshot_path": str(test_screenshot),
            "scenario_description": "Quick Test Scenario",
            "persona_type": "Test User"
        }
        
        # Run analysis
        analyzer = LLMEnhancedAnalyzer()
        print("🤖 Running analysis on screenshot with potential visual issues...")
        
        llm_bugs = await analyzer.analyze_step_with_llm(test_step)
        
        print(f"📊 Found {len(llm_bugs)} bugs")
        
        if llm_bugs:
            print("\n📋 DETECTED BUGS:")
            for i, bug in enumerate(llm_bugs, 1):
                title = bug.get('title', 'N/A')
                bug_type = bug.get('type', 'N/A')
                severity = bug.get('severity', 'N/A')
                
                print(f"\n   {i}. {title}")
                print(f"      Type: {bug_type}")
                print(f"      Severity: {severity}")
                
                # Check for problematic patterns
                title_lower = title.lower()
                problematic_patterns = [
                    "delayed response", "slow response", "unresponsive", 
                    "clicking", "entering", "when user", "after clicking",
                    "takes time", "loading time", "performance issue"
                ]
                
                found_problems = [p for p in problematic_patterns if p in title_lower]
                if found_problems:
                    print(f"      ❌ PROBLEMS: {found_problems}")
                else:
                    print(f"      ✅ NO PROBLEMS")
                
                # Check for valid visual issues
                visual_indicators = [
                    "misaligned", "misalignment", "inconsistent", "color contrast",
                    "font size", "typography", "spacing", "padding", "alignment",
                    "visual", "layout", "design", "overlap", "cramped"
                ]
                
                found_visual = [v for v in visual_indicators if v in title_lower]
                if found_visual:
                    print(f"      ✅ VISUAL ISSUES: {found_visual}")
                
                # Show description if it's not a "no issues" message
                if "no visual issues" not in title_lower and "no issues" not in title_lower:
                    description = bug.get('description', 'N/A')
                    if description and len(description) > 10:
                        print(f"      Description: {description[:100]}...")
        else:
            print("📝 No bugs detected")
            
    except Exception as e:
        print(f"❌ Error during analysis: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    import asyncio
    asyncio.run(test_with_visual_issues())

