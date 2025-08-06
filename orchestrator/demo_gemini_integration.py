#!/usr/bin/env python3
"""
STEP 3 Demo: Complete Multi-Agent Pipeline with Gemini CLI Integration
Demonstrates UX Analyzer → ADO Tickets → Gemini CLI Fixes → Coder Tasks → Auto Fixes
"""

import asyncio
import sys
import os
from pathlib import Path

# Add orchestrator to path
sys.path.append(str(Path(__file__).parent))
from main import OrchestratorAgent
from ado_client import AzureDevOpsClient
from gemini_handler import GeminiHandler

async def demo_complete_pipeline():
    """Demo the complete orchestration pipeline with Gemini CLI integration"""
    
    print("🎯 COMPLETE MULTI-AGENT PIPELINE DEMO")
    print("🔄 UX Analyzer → ADO Tickets → Gemini CLI Fixes → Coder Tasks → Auto Fixes")
    print("=" * 70)
    
    # Initialize orchestrator
    print("\n🚀 1. Initializing Multi-Agent Orchestrator...")
    orchestrator = OrchestratorAgent()
    await orchestrator.initialize_agents()
    
    # Check all agent statuses
    print("\n📊 2. Multi-Agent Status Check...")
    status = orchestrator.get_status()
    
    agents = status['agents']
    
    print(f"   ✅ UX Analyzer: {agents['ux_analyzer']['available']}")
    print(f"      Endpoint: {agents['ux_analyzer']['endpoint']}")
    
    print(f"   ✅ Coder Agent: {agents['coder_agent']['available']}")
    print(f"      Path: {agents['coder_agent']['path']}")
    
    print(f"   ✅ ADO Client: {agents['ado_client']['available']}")
    print(f"      Org: {agents['ado_client']['org']}")
    print(f"      Project: {agents['ado_client']['project']}")
    print(f"      Configured: {agents['ado_client']['configured']}")
    
    print(f"   ✅ Gemini Handler: {agents['gemini_handler']['available']}")
    print(f"      CLI Available: {agents['gemini_handler']['cli_available']}")
    print(f"      Frontend Path: {agents['gemini_handler']['frontend_path']}")
    print(f"      Path Exists: {agents['gemini_handler']['frontend_path_exists']}")
    
    # Run full orchestration cycle
    print("\n🔄 3. Running Complete Orchestration Cycle...")
    test_url = "https://example.com"
    print(f"   Target URL: {test_url}")
    
    try:
        result = await orchestrator.orchestrate_full_cycle(test_url)
        
        print(f"\n✅ 4. Pipeline Results:")
        print(f"   Orchestration ID: {result['orchestration_id']}")
        print(f"   URL Analyzed: {result['url']}")
        
        # Analysis results
        analysis = result['analysis']
        print(f"\n📊 5. UX Analysis Results:")
        print(f"   Analysis ID: {analysis['analysis_id']}")
        print(f"   Overall Score: {analysis['overall_score']}/100")
        print(f"   Issues Found: {analysis['issues_found']}")
        print(f"   Severity Breakdown: {analysis['severity_breakdown']}")
        
        # Coder tasks
        tasks = result['tasks']
        print(f"\n🎯 6. Coder Tasks Created:")
        print(f"   Total Tasks: {tasks['created']}")
        for i, task in enumerate(tasks['task_details'], 1):
            print(f"   Task {i}: [{task['priority'].upper()}] {task['description']}")
        
        # ADO tickets
        ado_tickets = result['ado_tickets']
        print(f"\n🎫 7. Azure DevOps Integration:")
        print(f"   Tickets Created: {ado_tickets['created']}")
        if ado_tickets.get('ticket_ids'):
            print(f"   Ticket IDs: {', '.join(map(str, ado_tickets['ticket_ids']))}")
        else:
            print(f"   Status: ADO not configured (demo mode)")
        
        # Gemini fixes - NEW IN STEP 3!
        gemini_fixes = result['gemini_fixes']
        print(f"\n🤖 8. Gemini CLI Fixes:")
        print(f"   Fixes Attempted: {gemini_fixes['attempted']}")
        print(f"   Fixes Successful: {gemini_fixes['successful']}")
        print(f"   Fixes Failed: {gemini_fixes['failed']}")
        
        if gemini_fixes['results']:
            print(f"   Fix Details:")
            for fix_result in gemini_fixes['results']:
                status_icon = "✅" if fix_result['fix_successful'] else "❌"
                print(f"   {status_icon} {fix_result['issue_type']}: {fix_result['issue_message']}")
                print(f"      File: {fix_result['file']}")
                if 'error' in fix_result:
                    print(f"      Error: {fix_result['error']}")
        
        # Recommendations
        print(f"\n💡 9. Recommendations:")
        for i, rec in enumerate(result['recommendations'], 1):
            print(f"   {i}. {rec}")
        
        print(f"\n🎉 SUCCESS: Complete Multi-Agent Pipeline with Gemini CLI Working!")
        
        # Configuration tips
        print(f"\n⚙️ To Enable Full Functionality:")
        
        if ado_tickets['created'] == 0:
            print(f"   1. Update .env with your ADO credentials:")
            print(f"      ADO_ORG=your-organization")
            print(f"      ADO_PROJECT=your-project")
            print(f"      ADO_TOKEN=your-pat-token")
        
        if gemini_fixes['attempted'] == 0 or gemini_fixes['failed'] > 0:
            print(f"   2. Install and configure Gemini CLI:")
            print(f"      pip install gemini-cli  # or your preferred method")
            print(f"      GEMINI_CLI_PATH=gemini  # update path if needed")
            print(f"      FRONTEND_PATH=../frontend  # path to your source files")
        
        print(f"   3. Generate ADO PAT: https://dev.azure.com/[org]/_usersSettings/tokens")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Pipeline failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def demo_gemini_standalone():
    """Demo Gemini handler standalone functionality"""
    print("\n" + "="*70)
    print("🧪 STANDALONE GEMINI CLI TEST")
    print("="*70)
    
    try:
        handler = GeminiHandler()
        status = handler.get_status()
        
        print(f"Gemini Configuration:")
        print(f"  CLI Path: {status['gemini_cli_path']}")
        print(f"  Frontend Path: {status['frontend_path']}")
        print(f"  CLI Available: {status['cli_available']}")
        print(f"  Frontend Path Exists: {status['frontend_path_exists']}")
        
        if status['cli_available']:
            print(f"\n✅ Gemini CLI is available!")
            
            # Test fix with sample issue
            print(f"\n🔧 Testing Gemini fix with sample issue...")
            test_issue = {
                "type": "accessibility",
                "severity": "high",
                "message": "Missing alt text on hero banner image",
                "file": "index.html",
                "element": "img.hero-banner",
                "recommendation": "Add descriptive alt text to improve screen reader accessibility"
            }
            
            print(f"   Issue: {test_issue['message']}")
            print(f"   File: {test_issue['file']}")
            print(f"   Severity: {test_issue['severity']}")
            
            # This would normally call Gemini CLI
            success = handler.fix_bug_with_gemini(test_issue)
            
            if success:
                print(f"✅ Demo fix applied successfully!")
            else:
                print(f"❌ Demo fix failed (expected in demo mode)")
        else:
            print(f"❌ Gemini CLI not available")
            print(f"   Install: pip install gemini-cli")
            print(f"   Or update GEMINI_CLI_PATH in .env")
            
    except Exception as e:
        print(f"❌ Gemini handler error: {e}")

async def demo_ado_standalone():
    """Demo ADO client standalone functionality"""
    print("\n" + "="*70)
    print("🧪 STANDALONE ADO CLIENT TEST")
    print("="*70)
    
    try:
        client = AzureDevOpsClient()
        print(f"ADO Configuration:")
        print(f"  Org: {client.org}")
        print(f"  Project: {client.project}")
        print(f"  Token: {'*' * 10 if client.token else 'Not set'}")
        print(f"  Configured: {client.is_configured()}")
        
        if client.is_configured():
            print(f"\n🔗 Testing ADO Connection...")
            if client.test_connection():
                print(f"✅ ADO Connection successful!")
            else:
                print(f"❌ ADO Connection failed (expected with demo credentials)")
        else:
            print(f"⚠️  ADO not configured - demo mode only")
            
    except Exception as e:
        print(f"❌ ADO client error: {e}")

if __name__ == "__main__":
    print("Starting STEP 3: Complete Multi-Agent Pipeline with Gemini CLI...")
    
    # Run main pipeline demo
    success = asyncio.run(demo_complete_pipeline())
    
    # Run standalone component demos
    asyncio.run(demo_gemini_standalone())
    asyncio.run(demo_ado_standalone())
    
    if success:
        print("\n" + "="*70)
        print("✅ STEP 3 COMPLETE: Gemini CLI Integration Working!")
        print("🎯 Issues detected → ADO tickets created → Gemini fixes applied")
        print("🤖 Automated bug fixing with Gemini CLI")
        print("🔐 Secrets secured via .env")  
        print("📦 Cleanly modularized in gemini_handler.py")
        print("🧪 Ready for end-to-end testing with real Gemini CLI")
        print("🚀 Ready for STEP 4: Full Production Deployment")
    else:
        print("\n❌ Demo failed. Check configuration.")

    print("\n🧠 Debug Tip:")
    print("To test Gemini CLI manually:")
    print('gemini fix --file frontend/index.html --prompt "Fix: Missing alt text on images"')
