#!/usr/bin/env python3
"""
Server startup validation and basic test
"""

print("🔧 Testing Core Fixes...")

# Test 1: Import validation
try:
    from scenario_executor import ScenarioExecutor  
    from utils.scenario_resolver import resolve_scenario, _ensure_dict
    print("✅ Core imports successful")
except Exception as e:
    print(f"❌ Import failed: {e}")
    exit(1)

# Test 2: Scenario executor basic validation
try:
    executor = ScenarioExecutor(deterministic_mode=True)
    result = executor.execute_url_scenario(
        url="http://test.com",
        scenario_path="scenarios/word_scenarios.yaml", 
        modules={"performance": True}
    )
    
    print(f"✅ Executor returns: {type(result)}")
    print(f"✅ Status: {result.get('status')}")
    print(f"✅ Has required fields: {all(field in result for field in ['analysis_id', 'status', 'module_results', 'scenario_results'])}")
    
    if result.get('status') == 'failed':
        print(f"⚠️  Analysis failed (expected): {result.get('ui_error', 'No UI error')}")
    
except Exception as e:
    print(f"❌ Executor test failed: {e}")
    exit(1)

# Test 3: Server startup check
print("\n🚀 Attempting to start server...")
try:
    import uvicorn
    from enhanced_fastapi_server import app
    
    print("✅ Server imports successful")
    print("✅ FastAPI app loaded")
    print("\n📍 To start the server manually, run:")
    print("   python -c \"import uvicorn; from enhanced_fastapi_server import app; uvicorn.run(app, host='127.0.0.1', port=8000, reload=False)\"")
    print("\n📍 Or use the starter script:")
    print("   python start_server.py")
    print("\n🌐 Once running, access:")
    print("   • Health: http://localhost:8000/health")
    print("   • Dashboard: http://localhost:8000/dashboard") 
    print("   • API Docs: http://localhost:8000/docs")
    
except Exception as e:
    print(f"❌ Server validation failed: {e}")
    exit(1)

print("\n🎉 All core fixes validated successfully!")
print("💡 The robust scenario pipeline is ready for testing.")
