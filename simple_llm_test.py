#!/usr/bin/env python3
"""
Simple LLM Test
==============

Quick test to verify if the LLM analyzer is working with new prompts.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_llm_analyzer_import():
    """Test if we can import the LLM analyzer"""
    
    print("🧪 SIMPLE LLM ANALYZER TEST")
    print("=" * 40)
    
    try:
        # Try to import the analyzer
        from llm_enhanced_analyzer import LLMEnhancedAnalyzer
        print("✅ Successfully imported LLMEnhancedAnalyzer")
        
        # Check if the prompts are loaded
        analyzer = LLMEnhancedAnalyzer()
        print("✅ Successfully created analyzer instance")
        
        # Check the prompts
        if hasattr(analyzer, 'analysis_prompts'):
            print(f"✅ Analysis prompts loaded: {len(analyzer.analysis_prompts)} prompts")
            
            # Check if the new static visual prompts are there
            craft_prompt = analyzer.analysis_prompts.get('craft_bug_detection', '')
            if 'STATIC VISUAL UX ANALYSIS' in craft_prompt:
                print("✅ New static visual analysis prompt found!")
            else:
                print("❌ Old prompt still being used!")
                
            # Check for problematic phrases in the prompt
            problematic_phrases = ['interaction', 'performance', 'timing', 'delay', 'response']
            found_problems = [phrase for phrase in problematic_phrases if phrase in craft_prompt.lower()]
            
            if found_problems:
                print(f"❌ Prompt still contains problematic phrases: {found_problems}")
            else:
                print("✅ Prompt appears to be clean of problematic phrases")
                
        else:
            print("❌ No analysis prompts found")
            
    except ImportError as e:
        print(f"❌ Failed to import LLMEnhancedAnalyzer: {e}")
        return False
    except Exception as e:
        print(f"❌ Error creating analyzer: {e}")
        return False
    
    return True

def test_simple_analysis():
    """Test a simple analysis with one screenshot"""
    
    print("\n🔍 TESTING SIMPLE ANALYSIS")
    print("=" * 30)
    
    try:
        from llm_enhanced_analyzer import LLMEnhancedAnalyzer
        
        # Find a screenshot
        screenshots_dir = Path("screenshots/excel_web")
        if not screenshots_dir.exists():
            print("❌ No screenshots directory found")
            return
        
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
        print("🤖 Running simple analysis...")
        
        llm_bugs = analyzer.analyze_step_with_llm(test_step)
        
        print(f"📊 Found {len(llm_bugs)} bugs")
        
        if llm_bugs:
            print("\n📋 SAMPLE BUGS:")
            for i, bug in enumerate(llm_bugs[:3], 1):  # Show first 3 bugs
                title = bug.get('title', 'N/A')
                print(f"   {i}. {title}")
                
                # Check for problematic patterns
                title_lower = title.lower()
                problematic_patterns = [
                    "delayed response", "slow response", "unresponsive", 
                    "clicking", "entering", "when user", "after clicking"
                ]
                
                found_problems = [p for p in problematic_patterns if p in title_lower]
                if found_problems:
                    print(f"      ❌ PROBLEMS: {found_problems}")
                else:
                    print(f"      ✅ NO PROBLEMS")
        else:
            print("📝 No bugs detected")
            
    except Exception as e:
        print(f"❌ Error during analysis: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # Test import first
    if test_llm_analyzer_import():
        # If import works, test analysis
        test_simple_analysis()
    else:
        print("\n❌ Cannot proceed with analysis test due to import issues")

