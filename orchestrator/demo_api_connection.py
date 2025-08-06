#!/usr/bin/env python3
"""
Demo script showing orchestrator connected to UX Analyzer API
Run this to see the live multi-agent connection in action
"""

import asyncio
import sys
import os
from pathlib import Path

# Add orchestrator to path
sys.path.append(str(Path(__file__).parent))
from main import OrchestratorAgent

async def demo_orchestrator_api_connection():
    """Demo the orchestrator connecting to live UX Analyzer API"""
    
    print("🎯 ORCHESTRATOR + UX ANALYZER API DEMO")
    print("=" * 50)
    
    # Initialize orchestrator
    print("\n🚀 1. Initializing Orchestrator Agent...")
    orchestrator = OrchestratorAgent()
    await orchestrator.initialize_agents()
    
    # Check status
    print("\n📊 2. Checking Agent Status...")
    status = orchestrator.get_status()
    ux_status = status["agents"]["ux_analyzer"]
    
    print(f"   UX Analyzer Available: {ux_status['available']}")
    print(f"   Endpoint: {ux_status['endpoint']}")
    print(f"   Health Status: {ux_status['status']}")
    
    if not ux_status['available']:
        print("\n❌ UX Analyzer API not available!")
        print("   Please start: uvicorn fastapi_server:app --reload --port 8000")
        return
    
    # Run analysis
    print("\n🔄 3. Running Website Analysis...")
    test_url = "https://example.com"
    print(f"   Analyzing: {test_url}")
    
    try:
        result = await orchestrator.analyze_website(test_url)
        
        print(f"\n✅ 4. Analysis Results:")
        print(f"   Analysis ID: {result.analysis_id}")
        print(f"   Overall Score: {result.overall_score}/100")
        print(f"   Issues Found: {len(result.issues)}")
        print(f"   Severity Breakdown: {result.severity_counts}")
        
        # Show issues
        if result.issues:
            print(f"\n📋 5. Top Issues Detected:")
            for i, issue in enumerate(result.issues[:3], 1):
                print(f"   {i}. [{issue['severity'].upper()}] {issue['type']}")
                print(f"      {issue['message']}")
                if issue.get('file'):
                    print(f"      File: {issue['file']}")
                print()
        
        # Create coder tasks
        print(f"🎯 6. Creating Coder Tasks...")
        tasks = await orchestrator.create_coder_tasks(result)
        print(f"   Created {len(tasks)} actionable tasks")
        
        for i, task in enumerate(tasks, 1):
            print(f"   Task {i}: {task.description}")
            print(f"           Files to fix: {', '.join(task.files_to_fix)}")
            print(f"           Priority: {task.priority}")
            print()
        
        print("🎉 SUCCESS: Orchestrator → UX Analyzer API connection working!")
        print("\nNext Step: Connect to Coder Agent for automated fixes")
        
    except Exception as e:
        print(f"\n❌ Analysis failed: {e}")
        return False
    
    return True

if __name__ == "__main__":
    print("Starting Orchestrator API Demo...")
    success = asyncio.run(demo_orchestrator_api_connection())
    
    if success:
        print("\n" + "="*50)
        print("✅ STEP 1 COMPLETE: UX Analyzer API Connected!")
        print("🎯 Ready for STEP 2: Coder Agent Integration")
    else:
        print("\n❌ Demo failed. Check API connection.")
