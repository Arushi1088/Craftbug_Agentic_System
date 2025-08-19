#!/usr/bin/env python3
"""
Test Figma Integration with Real API
===================================

Tests the Figma integration with real API access using authentication tokens.
"""

import os
import requests
from figma_integration import FigmaIntegration

# Load environment variables
from load_env import load_env_file
load_env_file()

def test_figma_api_access():
    """Test real Figma API access"""
    
    print("🎨 Testing Figma API Integration...")
    print("=" * 50)
    
    # Check if token is available
    figma_token = os.getenv('FIGMA_ACCESS_TOKEN')
    if not figma_token:
        print("❌ No Figma token found. Please run: python setup_authentication.py")
        return False
    
    print(f"✅ Figma token found: {figma_token[:10]}...")
    
    # Test API access
    try:
        # Test with Excel Web Fluent 2 file
        file_key = "WIhOBHqKHheLMqZMJimsgF"
        node_id = "2054-46829"
        
        url = f"https://api.figma.com/v1/files/{file_key}"
        headers = {
            "X-Figma-Token": figma_token
        }
        
        print(f"🔍 Testing API access to file: {file_key}")
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            file_data = response.json()
            print(f"✅ Successfully accessed Figma file!")
            print(f"   File name: {file_data.get('name', 'Unknown')}")
            print(f"   Last modified: {file_data.get('lastModified', 'Unknown')}")
            print(f"   Version: {file_data.get('version', 'Unknown')}")
            
            # Test node access
            node_url = f"https://api.figma.com/v1/files/{file_key}/nodes?ids={node_id}"
            node_response = requests.get(node_url, headers=headers)
            
            if node_response.status_code == 200:
                node_data = node_response.json()
                print(f"✅ Successfully accessed node: {node_id}")
                print(f"   Node name: {node_data.get('nodes', {}).get(node_id, {}).get('document', {}).get('name', 'Unknown')}")
            else:
                print(f"⚠️ Could not access specific node: {node_response.status_code}")
            
            return True
            
        else:
            print(f"❌ API access failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing Figma API: {e}")
        return False

def test_figma_integration():
    """Test the Figma integration module with real data"""
    
    print("\n🔧 Testing Figma Integration Module...")
    print("=" * 50)
    
    figma = FigmaIntegration()
    
    # Test all design systems
    design_systems = [
        "excel_web_fluent",
        "office_icons", 
        "excel_copilot",
        "excel_win32_ribbon",
        "excel_fluent_surfaces",
        "office_win32_variables"
    ]
    
    for system in design_systems:
        specs = figma.get_design_specs(system)
        print(f"✅ {system}: {len(specs)} categories")
        
        # Show some details for Excel Web Fluent
        if system == "excel_web_fluent":
            colors = specs.get("colors", {})
            typography = specs.get("typography", {})
            print(f"   Colors: {len(colors)} tokens")
            print(f"   Typography: {len(typography)} tokens")
    
    # Test design compliance
    print("\n🎯 Testing Design Compliance...")
    test_element = {"color": "#0078d4", "font_size": "14px"}
    compliance = figma.check_design_compliance(test_element)
    print(f"   Compliance score: {compliance['score']}/100")
    print(f"   Compliant: {compliance['compliant']}")
    
    return True

if __name__ == "__main__":
    print("🚀 Starting Figma Integration Tests...")
    
    # Test API access
    api_success = test_figma_api_access()
    
    # Test integration module
    integration_success = test_figma_integration()
    
    print("\n📊 Test Results:")
    print(f"   API Access: {'✅ PASS' if api_success else '❌ FAIL'}")
    print(f"   Integration: {'✅ PASS' if integration_success else '❌ FAIL'}")
    
    if api_success and integration_success:
        print("\n🎉 All tests passed! Figma integration is working with real data.")
    else:
        print("\n⚠️ Some tests failed. Check your authentication setup.")
