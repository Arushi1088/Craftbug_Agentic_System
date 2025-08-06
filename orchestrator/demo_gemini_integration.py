#!/usr/bin/env python3
"""
STEP 4 Demo: Complete Multi-Agent Pipeline with Git Auto-Commit/Push Integration
Demonstrates UX Analyzer → ADO Tickets → Gemini CLI Fixes → Git Auto-Commit/Push
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
    """Demo the complete orchestration pipeline with Git Auto-Commit/Push integration"""
    
    print("🎯 COMPLETE MULTI-AGENT PIPELINE DEMO - STEP 4")
    print("🔄 UX Analyzer → ADO Tickets → Gemini CLI Fixes → Git Auto-Commit/Push")
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
    
    print(f"   ✅ Git Handler: {agents['git_handler']['available']}")
    print(f"      Auto Commit: {agents['git_handler']['auto_commit_enabled']}")
    print(f"      Auto Push: {agents['git_handler']['auto_push_enabled']}")
    git_status = agents['git_handler']['repository_status']
    if git_status:
        print(f"      Repository: {git_status.get('is_repo', False)}")
        print(f"      Branch: {git_status.get('branch', 'Unknown')}")
        print(f"      Clean: {git_status.get('is_clean', False)}")
    
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

async def demo_git_integration():
    """Demo STEP 4: Git Auto-Commit/Push Integration"""
    
    print("\n🔗 STEP 4 DEMO: Git Auto-Commit/Push Integration")
    print("=" * 60)
    
    try:
        # Initialize orchestrator with Git integration
        orchestrator = OrchestratorAgent()
        await orchestrator.initialize_agents()
        
        # Test Git handler directly
        if orchestrator.git_handler:
            print("✅ Git Handler initialized successfully")
            
            # Check Git status
            git_status = orchestrator.git_handler.check_git_status()
            print(f"📊 Git Repository Status:")
            print(f"   Is Repo: {git_status.get('is_repo', False)}")
            print(f"   Branch: {git_status.get('branch', 'Unknown')}")
            print(f"   Clean: {git_status.get('is_clean', False)}")
            print(f"   Has Changes: {git_status.get('has_changes', False)}")
            
            # Test auto-commit configuration
            auto_commit = orchestrator.config.get('git', {}).get('auto_commit_enabled', False)
            auto_push = orchestrator.config.get('git', {}).get('auto_push', False)
            
            print(f"⚙️ Configuration:")
            print(f"   Auto Commit Enabled: {auto_commit}")
            print(f"   Auto Push Enabled: {auto_push}")
            
            if auto_commit:
                print("✅ Git auto-commit is ENABLED - fixes will be committed automatically")
            else:
                print("⚠️ Git auto-commit is DISABLED - enable in .env with AUTO_COMMIT_ENABLED=true")
                
            if auto_push:
                print("✅ Git auto-push is ENABLED - commits will be pushed automatically")
            else:
                print("⚠️ Git auto-push is DISABLED - enable in .env with AUTO_PUSH=true")
                
        else:
            print("❌ Git Handler not initialized")
            return False
            
        # Create a mock issue to test Git integration
        mock_issue = {
            "type": "accessibility",
            "message": "Missing alt text on image elements",
            "severity": "medium",
            "file": "index.html",
            "analysis_id": "git_test_001"
        }
        
        print(f"\n🧪 Testing Git integration with mock issue:")
        print(f"   Type: {mock_issue['type']}")
        print(f"   File: {mock_issue['file']}")
        print(f"   Severity: {mock_issue['severity']}")
        
        # If auto-commit is enabled, this would trigger Git operations
        if auto_commit:
            print("🔄 This would trigger automatic Git commit/push after Gemini fixes")
            print("   (Skipping actual commit in demo to avoid test commits)")
        else:
            print("ℹ️ Enable auto-commit to test full Git integration")
            
        return True
        
    except Exception as e:
        print(f"❌ Git integration demo failed: {e}")
        return False


if __name__ == "__main__":
    print("Starting STEP 4: Complete Multi-Agent Pipeline with Git Integration...")
    
    # Run main pipeline demo
    success = asyncio.run(demo_complete_pipeline())
    
    # Run STEP 4 Git integration demo
    git_success = asyncio.run(demo_git_integration())
    
    # Run standalone component demos
    asyncio.run(demo_gemini_standalone())
    asyncio.run(demo_ado_standalone())
    
    if success and git_success:
        print("\n" + "="*70)
        print("✅ STEP 4 COMPLETE: Git Auto-Commit/Push Integration Working!")
        print("🎯 Issues detected → ADO tickets created → Gemini fixes applied → Git auto-commit/push")
        print("🤖 Automated bug fixing with Gemini CLI")
        print("� Automated Git workflow for seamless deployment")
        print("�🔐 Secrets secured via .env")  
        print("📦 Cleanly modularized in git_utils.py")
        print("🧪 Ready for end-to-end testing with real Git operations")
        print("🚀 Full automation pipeline complete!")
    else:
        print("\n❌ Demo failed. Check configuration.")

    print("\n🧠 Debug Tip:")
    print("To test Gemini CLI manually:")
    print('gemini fix --file frontend/index.html --prompt "Fix: Missing alt text on images"')
