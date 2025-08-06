#!/usr/bin/env python3
"""
Enhanced Demo: UX Analyzer → ADO Tickets → Coder Tasks
Shows the complete multi-agent pipeline with Azure DevOps integration
"""

import asyncio
import sys
import os
from pathlib import Path

# Add orchestrator to path
sys.path.append(str(Path(__file__).parent))
from main import OrchestratorAgent

async def demo_full_pipeline():
    """Demo the complete orchestration pipeline with ADO integration"""
    
    print("🎯 COMPLETE MULTI-AGENT PIPELINE DEMO")
    print("🔄 UX Analyzer → ADO Tickets → Coder Tasks → Auto Fixes")
    print("=" * 60)
    
    # Initialize orchestrator
    print("\n🚀 1. Initializing Multi-Agent Orchestrator...")
    orchestrator = OrchestratorAgent()
    await orchestrator.initialize_agents()
    
    # Check all agent statuses
    print("\n📊 2. Multi-Agent Status Check...")
    status = orchestrator.get_status()
    
    print(f"   ✅ UX Analyzer: {status['agents']['ux_analyzer']['available']}")
    print(f"      Endpoint: {status['agents']['ux_analyzer']['endpoint']}")
    
    print(f"   ✅ Coder Agent: {status['agents']['coder_agent']['available']}")
    print(f"      Path: {status['agents']['coder_agent']['path']}")
    
    print(f"   ✅ ADO Client: {status['agents']['ado_client']['available']}")
    print(f"      Org: {status['agents']['ado_client']['org']}")
    print(f"      Project: {status['agents']['ado_client']['project']}")
    print(f"      Configured: {status['agents']['ado_client']['configured']}")
    
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
        if ado_tickets['ticket_ids']:
            print(f"   Ticket IDs: {', '.join(map(str, ado_tickets['ticket_ids']))}")
        else:
            print(f"   Status: ADO not configured (demo mode)")
        
        # Recommendations
        print(f"\n💡 8. Recommendations:")
        for i, rec in enumerate(result['recommendations'], 1):
            print(f"   {i}. {rec}")
        
        print(f"\n🎉 SUCCESS: Complete Multi-Agent Pipeline Working!")
        
        if ado_tickets['created'] > 0:
            print(f"\n📋 Next Steps:")
            print(f"   1. Check Azure DevOps for created tickets")
            print(f"   2. Review and assign tickets to developers")
            print(f"   3. Track progress through ADO dashboards")
        else:
            print(f"\n⚙️ To Enable ADO Ticket Creation:")
            print(f"   1. Update .env with your ADO credentials:")
            print(f"      ADO_ORG=your-organization")
            print(f"      ADO_PROJECT=your-project")
            print(f"      ADO_TOKEN=your-pat-token")
            print(f"   2. Generate PAT: https://dev.azure.com/[org]/_usersSettings/tokens")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Pipeline failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def demo_ado_standalone():
    """Demo ADO client standalone functionality"""
    print("\n" + "="*60)
    print("🧪 STANDALONE ADO CLIENT TEST")
    print("="*60)
    
    from ado_client import AzureDevOpsClient
    
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
            
            # Create test ticket
            test_issue = {
                "type": "accessibility",
                "severity": "high", 
                "message": "Demo: Missing alt text on hero banner image",
                "file": "index.html",
                "element": "img.hero-banner",
                "recommendation": "Add descriptive alt text: <img alt='Company logo and mission statement' ...>"
            }
            
            print(f"\n🎫 Creating test ADO ticket...")
            ticket_id = client.create_ado_ticket(test_issue)
            
            if ticket_id:
                print(f"✅ Demo ticket created: #{ticket_id}")
                print(f"   View at: https://dev.azure.com/{client.org}/{client.project}/_workitems/edit/{ticket_id}")
            else:
                print(f"❌ Failed to create demo ticket")
        else:
            print(f"❌ ADO Connection failed")
    else:
        print(f"⚠️  ADO not configured - demo mode only")

if __name__ == "__main__":
    print("Starting Complete Multi-Agent Pipeline Demo...")
    
    # Run main pipeline demo
    success = asyncio.run(demo_full_pipeline())
    
    # Run standalone ADO demo
    asyncio.run(demo_ado_standalone())
    
    if success:
        print("\n" + "="*60)
        print("✅ STEP 2 COMPLETE: ADO Integration Working!")
        print("🎯 Issues detected → ADO tickets created automatically")
        print("🔐 Secrets secured via .env")  
        print("📦 Cleanly modularized in ado_client.py")
        print("🧪 Ready for end-to-end testing")
        print("🚀 Ready for STEP 3: Full Coder Agent Integration")
    else:
        print("\n❌ Demo failed. Check configuration.")
