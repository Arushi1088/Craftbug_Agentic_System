#!/usr/bin/env python3
"""
Show the current prompts being used
"""

import sys
from pathlib import Path

# Add the project root to the path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from llm_enhanced_analyzer import LLMEnhancedAnalyzer

def show_prompts():
    """Show all current prompts"""
    
    print("🔍 CURRENT PROMPTS BEING USED")
    print("="*80)
    
    # Initialize analyzer to get prompts
    analyzer = LLMEnhancedAnalyzer()
    
    # Show each prompt
    for prompt_name, prompt_content in analyzer.analysis_prompts.items():
        print(f"\n📋 PROMPT: {prompt_name.upper()}")
        print("-" * 60)
        print(prompt_content)
        print("-" * 60)
        print(f"📏 Length: {len(prompt_content)} characters")
        print(f"📄 Lines: {prompt_content.count(chr(10)) + 1}")
        print()

if __name__ == "__main__":
    show_prompts()
