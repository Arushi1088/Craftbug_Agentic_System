#!/usr/bin/env python3
"""
Test Azure DevOps Integration with Real API
==========================================

Tests the ADO integration with real API access using authentication tokens.
"""

import os
import requests
import base64
from enhanced_ado_integration import EnhancedADOIntegration

# Load environment variables
from load_env import load_env_file
load_env_file()

def test_ado_api_access():
    """Test real Azure DevOps API access"""
    
    print("🔍 Testing Azure DevOps API Integration...")
    print("=" * 50)
    
    # Check if token is available
    ado_token = os.getenv('AZURE_DEVOPS_PAT')
    if not ado_token:
        print("❌ No ADO token found. Please run: python setup_authentication.py")
        return False
    
    print(f"✅ ADO token found: {ado_token[:10]}...")
    
    # Test API access
    try:
        organization = "office"
        project = "OC"
        base_url = f"https://dev.azure.com/{organization}/{project}"
        
        headers = {
            'Authorization': f'Basic {base64.b64encode(f":{ado_token}".encode()).decode()}',
            'Content-Type': 'application/json'
        }
        
        # Test project access
        print(f"🔍 Testing API access to project: {project}")
        project_url = f"{base_url}/_apis/project?api-version=6.0"
        response = requests.get(project_url, headers=headers)
        
        if response.status_code == 200:
            project_data = response.json()
            print(f"✅ Successfully accessed ADO project!")
            print(f"   Project name: {project_data.get('name', 'Unknown')}")
            print(f"   Project ID: {project_data.get('id', 'Unknown')}")
            print(f"   State: {project_data.get('state', 'Unknown')}")
            
            # Test work items query
            print(f"\n🔍 Testing work items query...")
            wiql_url = f"{base_url}/_apis/wit/wiql?api-version=6.0"
            payload = {
                "query": f"""SELECT [System.Id], [System.Title], [System.State]
                            FROM WorkItems 
                            WHERE [System.WorkItemType] = 'Bug' 
                              AND [System.TeamProject] = '{project}'
                              AND [System.Title] CONTAINS 'Craft'
                            ORDER BY [System.CreatedDate] DESC
                            TOP 5"""
            }
            
            wiql_response = requests.post(wiql_url, headers=headers, json=payload)
            
            if wiql_response.status_code == 200:
                work_items = wiql_response.json().get('workItems', [])
                print(f"✅ Successfully queried work items!")
                print(f"   Found {len(work_items)} Craft-related bugs")
                
                if work_items:
                    # Test fetching details for first work item
                    first_item = work_items[0]
                    item_url = f"{base_url}/_apis/wit/workItems/{first_item['id']}?api-version=6.0"
                    item_response = requests.get(item_url, headers=headers)
                    
                    if item_response.status_code == 200:
                        item_data = item_response.json()
                        fields = item_data.get('fields', {})
                        print(f"   Sample bug: {fields.get('System.Title', 'Unknown')}")
                        print(f"   State: {fields.get('System.State', 'Unknown')}")
                        print(f"   Created: {fields.get('System.CreatedDate', 'Unknown')}")
                    else:
                        print(f"⚠️ Could not fetch work item details: {item_response.status_code}")
                else:
                    print("   No Craft-related bugs found in recent data")
            else:
                print(f"⚠️ Could not query work items: {wiql_response.status_code}")
            
            return True
            
        else:
            print(f"❌ API access failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing ADO API: {e}")
        return False

def test_ado_integration():
    """Test the ADO integration module with real data"""
    
    print("\n🔧 Testing ADO Integration Module...")
    print("=" * 50)
    
    ado = EnhancedADOIntegration()
    
    # Test Craft bug fetching
    print("🔍 Fetching Craft bugs from ADO...")
    craft_bugs = ado.fetch_craft_bugs_from_dashboard(days_back=30)
    
    print(f"✅ Retrieved {len(craft_bugs)} Craft bugs")
    
    if craft_bugs:
        # Show sample bugs
        print("\n📋 Sample Craft bugs:")
        for i, bug in enumerate(craft_bugs[:3]):
            print(f"   {i+1}. {bug.get('title', 'Unknown')}")
            print(f"      Type: {bug.get('craft_bug_type', 'Unknown')}")
            print(f"      Surface: {bug.get('surface_level', 'Unknown')}")
            print(f"      Severity: {bug.get('severity', 'Unknown')}")
            print()
    
    # Test pattern analysis
    print("📊 Analyzing Craft bug patterns...")
    analysis = ado.analyze_craft_bug_patterns(craft_bugs)
    
    print(f"   Total bugs: {analysis['total_bugs']}")
    print(f"   Bug types: {list(analysis['bug_types'].keys())}")
    print(f"   Surface levels: {list(analysis['surface_levels'].keys())}")
    
    # Test insights generation
    print("\n💡 Generating prompt engineering insights...")
    insights = ado.generate_prompt_engineering_insights(analysis)
    
    print(f"   Detection priorities: {insights['detection_priorities']}")
    print(f"   Surface focus: {insights['surface_level_focus']}")
    print(f"   Common patterns: {insights['common_patterns'][:5]}")
    
    return True

if __name__ == "__main__":
    print("🚀 Starting Azure DevOps Integration Tests...")
    
    # Test API access
    api_success = test_ado_api_access()
    
    # Test integration module
    integration_success = test_ado_integration()
    
    print("\n📊 Test Results:")
    print(f"   API Access: {'✅ PASS' if api_success else '❌ FAIL'}")
    print(f"   Integration: {'✅ PASS' if integration_success else '❌ FAIL'}")
    
    if api_success and integration_success:
        print("\n🎉 All tests passed! ADO integration is working with real data.")
    else:
        print("\n⚠️ Some tests failed. Check your authentication setup.")

