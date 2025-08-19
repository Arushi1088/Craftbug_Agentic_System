#!/usr/bin/env python3
"""
Authentication Setup Script
==========================

Helps configure Figma and Azure DevOps authentication tokens
for real data integration.
"""

import os
import json
from pathlib import Path

def setup_authentication():
    """Interactive setup for authentication tokens"""
    
    print("🔐 Setting up authentication for real data integration...")
    print("=" * 60)
    
    # Check if tokens already exist
    figma_token = os.getenv('FIGMA_ACCESS_TOKEN')
    ado_token = os.getenv('AZURE_DEVOPS_PAT')
    
    print(f"Current Figma token: {'✅ Set' if figma_token else '❌ Not set'}")
    print(f"Current ADO token: {'✅ Set' if ado_token else '❌ Not set'}")
    print()
    
    # Figma token setup
    if not figma_token:
        print("📋 FIGMA TOKEN SETUP:")
        print("1. Go to https://www.figma.com/settings")
        print("2. Navigate to 'Personal access tokens'")
        print("3. Click 'Create new token'")
        print("4. Name it 'Craft Bug Analyzer'")
        print("5. Copy the token (starts with 'figd_')")
        print()
        
        figma_input = input("Enter your Figma Personal Access Token (or press Enter to skip): ").strip()
        if figma_input:
            os.environ['FIGMA_ACCESS_TOKEN'] = figma_input
            print("✅ Figma token set!")
        else:
            print("⚠️ Skipping Figma token setup")
    else:
        print("✅ Figma token already configured")
    
    print()
    
    # ADO token setup
    if not ado_token:
        print("📋 AZURE DEVOPS TOKEN SETUP:")
        print("1. Go to https://dev.azure.com/office/OC")
        print("2. Click your profile picture → 'Personal access tokens'")
        print("3. Click 'New Token'")
        print("4. Set scope to 'Work Items (Read)' and 'Queries (Read)'")
        print("5. Copy the token")
        print()
        
        ado_input = input("Enter your Azure DevOps Personal Access Token (or press Enter to skip): ").strip()
        if ado_input:
            os.environ['AZURE_DEVOPS_PAT'] = ado_input
            print("✅ ADO token set!")
        else:
            print("⚠️ Skipping ADO token setup")
    else:
        print("✅ ADO token already configured")
    
    print()
    
    # Save to .env file for persistence
    env_file = Path('.env')
    env_content = []
    
    if os.getenv('FIGMA_ACCESS_TOKEN'):
        env_content.append(f"FIGMA_ACCESS_TOKEN={os.getenv('FIGMA_ACCESS_TOKEN')}")
    
    if os.getenv('AZURE_DEVOPS_PAT'):
        env_content.append(f"AZURE_DEVOPS_PAT={os.getenv('AZURE_DEVOPS_PAT')}")
    
    if env_content:
        with open(env_file, 'w') as f:
            f.write('\n'.join(env_content))
        print(f"✅ Tokens saved to {env_file}")
    
    print()
    print("🎯 Next steps:")
    print("1. Test Figma integration: python test_figma_integration.py")
    print("2. Test ADO integration: python test_ado_integration.py")
    print("3. Run enhanced analyzer: python enhanced_fastapi_server.py")

if __name__ == "__main__":
    setup_authentication()
