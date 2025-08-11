#!/usr/bin/env python3
"""
Comprehensive test of the fixed pipeline
"""
import sys
import os

print("🎯 COMPREHENSIVE PIPELINE TEST")
print("="*50)

def test_imports():
    print("1️⃣ Testing imports...")
    try:
        from utils.scenario_resolver import resolve_scenario, _ensure_dict
        print("   ✅ scenario_resolver imports OK")
        
        from scenario_executor import ScenarioExecutor
        print("   ✅ scenario_executor imports OK")
        
        import enhanced_fastapi_server
        print("   ✅ enhanced_fastapi_server imports OK")
        
        return True
    except Exception as e:
        print(f"   ❌ Import failed: {e}")
        return False

def test_scenario_resolution():
    print("\n2️⃣ Testing scenario resolution...")
    try:
        from utils.scenario_resolver import resolve_scenario
        
        # Test Word scenario 1.1
        result = resolve_scenario('scenarios/word_scenarios.yaml', '1.1')
        print(f"   ✅ Word scenario resolved: {result.get('name', 'No name')}")
        print(f"   📊 Steps: {len(result.get('steps', []))}")
        
        # Validate structure
        assert isinstance(result, dict), "Result must be dict"
        assert 'steps' in result, "Result must have steps"
        assert isinstance(result['steps'], list), "Steps must be list"
        
        return True
    except Exception as e:
        print(f"   ❌ Resolution failed: {e}")
        return False

def test_executor_calls():
    print("\n3️⃣ Testing executor calls...")
    try:
        from scenario_executor import ScenarioExecutor
        
        executor = ScenarioExecutor()
        print("   ✅ Executor created")
        
        # Test with correct parameters
        modules = {
            "performance": True,
            "accessibility": True, 
            "keyboard": True,
            "ux_heuristics": True,
            "best_practices": True,
            "health_alerts": True,
            "functional": False
        }
        
        # Test mock scenario execution
        mock_result = executor.execute_mock_scenario(
            'http://localhost:3001/mocks/word/basic-doc.html',  # mock_app_path
            'scenarios/word_scenarios.yaml',                    # scenario_path  
            modules                                             # modules
        )
        
        print(f"   ✅ Mock execution completed: {type(mock_result)}")
        print(f"   📊 Has analysis: {'analysis' in mock_result}")
        print(f"   📊 Status: {mock_result.get('status', 'unknown')}")
        
        # Validate structure
        assert isinstance(mock_result, dict), "Result must be dict"
        assert mock_result is not None, "Result must not be None"
        
        return True
    except Exception as e:
        print(f"   ❌ Executor test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_server_health():
    print("\n4️⃣ Testing server health...")
    try:
        import requests
        response = requests.get("http://127.0.0.1:8000/api/health", timeout=5)
        if response.status_code == 200:
            print("   ✅ Server responding")
            return True
        else:
            print(f"   ⚠️ Server returned {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("   ⚠️ Server not running (expected if not started)")
        return False
    except Exception as e:
        print(f"   ❌ Health check failed: {e}")
        return False

def main():
    all_passed = True
    
    all_passed &= test_imports()
    all_passed &= test_scenario_resolution()
    all_passed &= test_executor_calls()
    all_passed &= test_server_health()
    
    print("\n" + "="*50)
    if all_passed:
        print("🎉 ALL CORE TESTS PASSED!")
        print("✅ Pipeline fixes working correctly")
        print("✅ No NoneType errors")
        print("✅ Structured responses guaranteed")
    else:
        print("❌ Some tests failed")
        
    print("\n📋 NEXT STEPS:")
    print("1. Start server: python3 -m uvicorn enhanced_fastapi_server:app --host 127.0.0.1 --port 8000")
    print("2. Test known-good scenario with curl command provided")
    print("3. Fix custom scenario formats if needed")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
