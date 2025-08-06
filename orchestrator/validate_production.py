#!/usr/bin/env python3
"""
Production Credential Validator
Tests all production credentials and system components
"""

import os
import sys
import asyncio
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_ado_credentials():
    """Test Azure DevOps credentials"""
    print("🎫 Testing Azure DevOps credentials...")
    
    ado_org = os.getenv('ADO_ORG')
    ado_project = os.getenv('ADO_PROJECT')
    ado_token = os.getenv('ADO_TOKEN')
    
    if not all([ado_org, ado_project, ado_token]):
        print("❌ Missing ADO credentials in .env")
        print(f"   ADO_ORG: {'✅' if ado_org else '❌'}")
        print(f"   ADO_PROJECT: {'✅' if ado_project else '❌'}")
        print(f"   ADO_TOKEN: {'✅' if ado_token else '❌'}")
        return False
    
    if any(x.startswith('demo-') or x.startswith('your-') for x in [ado_org, ado_project, ado_token]):
        print("❌ ADO credentials still contain demo/template values")
        return False
    
    try:
        from ado_client import AzureDevOpsClient
        client = AzureDevOpsClient()
        
        if client.test_connection():
            print("✅ ADO connection successful!")
            return True
        else:
            print("❌ ADO connection failed - check credentials")
            return False
            
    except Exception as e:
        print(f"❌ ADO test error: {e}")
        return False

def test_gemini_credentials():
    """Test Gemini AI credentials"""
    print("\n🤖 Testing Gemini AI credentials...")
    
    gemini_key = os.getenv('GEMINI_API_KEY')
    
    if not gemini_key:
        print("❌ GEMINI_API_KEY not set in .env")
        return False
    
    if gemini_key.startswith('demo-') or gemini_key.startswith('your-'):
        print("❌ GEMINI_API_KEY still contains demo/template value")
        return False
    
    try:
        import google.generativeai as genai
        genai.configure(api_key=gemini_key)
        
        # Test API connection
        model = genai.GenerativeModel('gemini-pro')
        response = model.generate_content("Hello")
        
        print("✅ Gemini API connection successful!")
        return True
        
    except Exception as e:
        print(f"❌ Gemini API test error: {e}")
        return False

def test_gemini_cli():
    """Test Gemini CLI installation"""
    print("\n🔧 Testing Gemini CLI installation...")
    
    import subprocess
    
    gemini_path = os.getenv('GEMINI_CLI_PATH', 'gemini')
    
    try:
        result = subprocess.run([gemini_path, '--help'], 
                               capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            print("✅ Gemini CLI available and working!")
            return True
        else:
            print(f"❌ Gemini CLI error (exit code {result.returncode})")
            print(f"   Error: {result.stderr}")
            return False
            
    except FileNotFoundError:
        print(f"❌ Gemini CLI not found at path: {gemini_path}")
        print("   Install with: pip install gemini-cli")
        return False
    except Exception as e:
        print(f"❌ Gemini CLI test error: {e}")
        return False

def test_github_credentials():
    """Test GitHub credentials (optional)"""
    print("\n🐙 Testing GitHub credentials...")
    
    github_token = os.getenv('GITHUB_TOKEN')
    github_owner = os.getenv('GITHUB_REPO_OWNER')
    github_repo = os.getenv('GITHUB_REPO_NAME')
    
    if not all([github_token, github_owner, github_repo]):
        print("⚠️  GitHub credentials not configured (optional)")
        return True  # Optional, so return True
    
    if any(x.startswith('your-') for x in [github_token, github_owner, github_repo]):
        print("⚠️  GitHub credentials contain template values (optional)")
        return True
    
    try:
        from github import Github
        g = Github(github_token)
        
        # Test API connection
        user = g.get_user()
        repo = g.get_repo(f"{github_owner}/{github_repo}")
        
        print(f"✅ GitHub connection successful! User: {user.login}")
        return True
        
    except Exception as e:
        print(f"⚠️  GitHub test error: {e} (optional)")
        return True

def test_ux_analyzer():
    """Test UX Analyzer API connection"""
    print("\n📊 Testing UX Analyzer connection...")
    
    import httpx
    
    endpoint = os.getenv('UX_ANALYZER_API_ENDPOINT', 'http://localhost:8002')
    
    try:
        response = httpx.get(f"{endpoint}/health", timeout=5)
        
        if response.status_code == 200:
            print(f"✅ UX Analyzer available at {endpoint}")
            return True
        else:
            print(f"❌ UX Analyzer returned status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ UX Analyzer not reachable: {e}")
        print("   Start with: uvicorn fastapi_server:app --reload --port 8002")
        return False

def test_git_setup():
    """Test Git repository setup"""
    print("\n📦 Testing Git repository setup...")
    
    import subprocess
    
    try:
        # Check if we're in a git repo
        result = subprocess.run(['git', 'status'], 
                               capture_output=True, text=True)
        
        if result.returncode != 0:
            print("❌ Not in a Git repository")
            print("   Initialize with: git init")
            return False
        
        # Check if remote exists
        result = subprocess.run(['git', 'remote', '-v'], 
                               capture_output=True, text=True)
        
        if not result.stdout.strip():
            print("⚠️  No Git remote configured")
            print("   Add with: git remote add origin <url>")
            return True  # Still functional without remote
        
        print("✅ Git repository properly configured!")
        return True
        
    except Exception as e:
        print(f"❌ Git test error: {e}")
        return False

async def test_full_pipeline():
    """Test the complete orchestration pipeline"""
    print("\n🔄 Testing complete pipeline integration...")
    
    try:
        sys.path.append(str(Path(__file__).parent))
        from main import OrchestratorAgent
        
        orchestrator = OrchestratorAgent()
        await orchestrator.initialize_agents()
        
        status = orchestrator.get_status()
        
        all_agents_ready = all(
            status['agents'][agent]['available'] 
            for agent in ['ux_analyzer', 'coder_agent', 'ado_client', 
                         'gemini_handler', 'git_handler']
        )
        
        if all_agents_ready:
            print("✅ All agents initialized successfully!")
            print("✅ Complete pipeline ready for production!")
            return True
        else:
            print("❌ Some agents failed to initialize")
            for agent, info in status['agents'].items():
                status_icon = "✅" if info['available'] else "❌"
                print(f"   {status_icon} {agent}")
            return False
            
    except Exception as e:
        print(f"❌ Pipeline test error: {e}")
        return False

def main():
    """Run all production readiness tests"""
    print("🚀 PRODUCTION READINESS VALIDATOR")
    print("=" * 50)
    
    tests = [
        ("ADO Credentials", test_ado_credentials),
        ("Gemini API", test_gemini_credentials),
        ("Gemini CLI", test_gemini_cli),
        ("GitHub (Optional)", test_github_credentials),
        ("UX Analyzer", test_ux_analyzer),
        ("Git Setup", test_git_setup),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            results.append((test_name, False))
    
    # Test full pipeline
    try:
        pipeline_result = asyncio.run(test_full_pipeline())
        results.append(("Full Pipeline", pipeline_result))
    except Exception as e:
        print(f"❌ Pipeline test crashed: {e}")
        results.append(("Full Pipeline", False))
    
    # Summary
    print("\n" + "=" * 50)
    print("📋 PRODUCTION READINESS SUMMARY")
    print("=" * 50)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status_icon = "✅" if result else "❌"
        print(f"{status_icon} {test_name}")
    
    print(f"\n📊 Overall Score: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 READY FOR PRODUCTION!")
        print("🚀 Run 'python main.py' to start the AI-powered CI system")
    else:
        print(f"\n⚠️  {total - passed} issues need to be resolved")
        print("📖 See PRODUCTION_SETUP_GUIDE.md for help")
    
    return passed == total

if __name__ == "__main__":
    main()
