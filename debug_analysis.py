#!/usr/bin/env python3
"""
Debug script to reproduce the NoneType error
"""

import asyncio
import traceback
import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.abspath('.'))

async def test_simple_analysis():
    """Test a simple analysis to see where it fails"""
    try:
        print("🔍 Testing simple scenario execution...")
        
        # Try importing the necessary modules
        from enhanced_scenario_runner import execute_realistic_scenario
        print("✅ Enhanced scenario runner imported successfully")
        
        # Test with a simple URL and scenario
        result = await execute_realistic_scenario(
            url="https://www.google.com",
            scenario_path="scenarios/basic_navigation.yaml",
            headless=True
        )
        
        print("✅ Analysis completed successfully!")
        print(f"Result keys: {list(result.keys())}")
        print(f"Status: {result.get('status', 'unknown')}")
        
        return result
        
    except Exception as e:
        print(f"❌ Error during analysis: {e}")
        print("\n🔍 Full traceback:")
        traceback.print_exc()
        return {"error": str(e), "status": "failed"}

if __name__ == "__main__":
    print("🚀 Starting debug analysis...")
    result = asyncio.run(test_simple_analysis())
    print(f"\n📊 Final result: {result}")
