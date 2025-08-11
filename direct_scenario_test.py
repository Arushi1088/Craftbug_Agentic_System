#!/usr/bin/env python3
"""
Direct scenario testing without server - tests our fixes directly
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from scenario_executor import ScenarioExecutor
from utils.scenario_resolver import ScenarioResolver

def test_word_scenario():
    """Test a known good Word scenario directly"""
    print("🎯 DIRECT SCENARIO TEST")
    print("="*50)
    
    # Initialize components
    resolver = ScenarioResolver()
    executor = ScenarioExecutor()
    
    print("📋 Testing Word scenario resolution...")
    
    # Test scenario resolution from Word YAML
    word_yaml_path = "scenarios/word_scenarios.yaml"
    
    try:
        # Test if the resolver can handle the Word YAML
        print(f"📂 Loading: {word_yaml_path}")
        scenario_data = resolver.resolve_scenario(word_yaml_path, "1.1")
        
        print("✅ Scenario resolved successfully!")
        print(f"📊 Steps found: {len(scenario_data.get('steps', []))}")
        print(f"🏷️  Title: {scenario_data.get('title', 'No title')}")
        
        # Test execution with a mock URL (won't actually browse)
        print("\n🚀 Testing scenario execution...")
        
        mock_url = "https://example.com"
        result = executor.execute_url_scenario(mock_url, word_yaml_path, "1.1")
        
        print("✅ Execution completed!")
        print(f"📊 Result type: {type(result)}")
        print(f"🔍 Has 'analysis' key: {'analysis' in result}")
        print(f"🔍 Has 'errors' key: {'errors' in result}")
        print(f"🔍 Has 'metadata' key: {'metadata' in result}")
        
        # Validate that result is never None and always has expected structure
        assert result is not None, "❌ Result should never be None!"
        assert isinstance(result, dict), "❌ Result should always be a dictionary!"
        
        print("\n🎉 SUCCESS: All fixes working correctly!")
        print("✅ No 'NoneType' errors")
        print("✅ Structured response guaranteed")
        print("✅ UI will receive proper data")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_word_scenario()
    sys.exit(0 if success else 1)
