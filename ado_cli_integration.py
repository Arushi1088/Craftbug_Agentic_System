#!/usr/bin/env python3
"""
Azure DevOps CLI Integration
Uses Azure CLI to fetch bug data from ADO
"""

import subprocess
import json
import os
from typing import List, Dict, Optional

class ADOCLIIntegrator:
    """Handles ADO integration via Azure CLI"""
    
    def __init__(self, organization: str, project: str):
        self.organization = organization
        self.project = project
        
    def check_azure_cli_installed(self) -> bool:
        """Check if Azure CLI is installed"""
        try:
            result = subprocess.run(['az', '--version'], capture_output=True, text=True)
            return result.returncode == 0
        except FileNotFoundError:
            return False
    
    def check_ado_extension(self) -> bool:
        """Check if Azure DevOps extension is installed"""
        try:
            result = subprocess.run(['az', 'extension', 'show', '--name', 'azure-devops'], 
                                  capture_output=True, text=True)
            return result.returncode == 0
        except:
            return False
    
    def install_ado_extension(self) -> bool:
        """Install Azure DevOps extension"""
        try:
            print("📦 Installing Azure DevOps extension...")
            result = subprocess.run(['az', 'extension', 'add', '--name', 'azure-devops'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                print("✅ Azure DevOps extension installed successfully")
                return True
            else:
                print(f"❌ Failed to install extension: {result.stderr}")
                return False
        except Exception as e:
            print(f"❌ Error installing extension: {e}")
            return False
    
    def login_to_azure(self) -> bool:
        """Login to Azure and Azure DevOps"""
        try:
            print("🔐 Logging into Azure...")
            result = subprocess.run(['az', 'login'], capture_output=True, text=True)
            if result.returncode == 0:
                print("✅ Successfully logged into Azure")
                
                # Also login to Azure DevOps
                print("🔐 Logging into Azure DevOps...")
                result = subprocess.run(['az', 'devops', 'login'], capture_output=True, text=True)
                if result.returncode == 0:
                    print("✅ Successfully logged into Azure DevOps")
                    return True
                else:
                    print(f"⚠️  Azure DevOps login failed: {result.stderr}")
                    print("This might be okay if you're using AAD authentication")
                    return True  # Continue anyway
            else:
                print(f"❌ Azure login failed: {result.stderr}")
                return False
        except Exception as e:
            print(f"❌ Error during login: {e}")
            return False
    
    def configure_ado_defaults(self) -> bool:
        """Configure ADO defaults"""
        try:
            print(f"⚙️  Configuring ADO defaults for {self.organization}/{self.project}...")
            
            # Set organization
            result = subprocess.run([
                'az', 'devops', 'configure', '--defaults', 
                f'organization=https://dev.azure.com/{self.organization}'
            ], capture_output=True, text=True)
            
            if result.returncode != 0:
                print(f"❌ Failed to set organization: {result.stderr}")
                return False
            
            # Set project
            result = subprocess.run([
                'az', 'devops', 'configure', '--defaults', 
                f'project={self.project}'
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                print("✅ ADO defaults configured successfully")
                return True
            else:
                print(f"❌ Failed to set project: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"❌ Error configuring defaults: {e}")
            return False
    
    def fetch_bugs_via_cli(self, query_id: str = None, max_results: int = 50) -> List[Dict]:
        """Fetch bugs using Azure CLI"""
        try:
            print(f"🔍 Fetching bugs via CLI (max: {max_results})...")
            
            if query_id:
                # Use specific query with organization and project
                cmd = [
                    'az', 'boards', 'query', 
                    '--id', query_id,
                    '--org', f'https://dev.azure.com/{self.organization}',
                    '--project', self.project,
                    '--output', 'json'
                ]
            else:
                # Use WIQL query for Excel bugs
                wiql_query = f"""
                SELECT [System.Id], [System.Title], [System.Description], [System.State], 
                       [System.CreatedBy], [System.CreatedDate], [System.Tags],
                       [Microsoft.VSTS.Common.Priority], [Microsoft.VSTS.Common.Severity],
                       [Microsoft.VSTS.TCM.ReproSteps], [System.AreaPath], [System.IterationPath]
                FROM WorkItems 
                WHERE [System.WorkItemType] = 'Bug' 
                  AND [System.TeamProject] = '{self.project}'
                  AND ([System.Title] CONTAINS 'Excel' OR [System.Description] CONTAINS 'Excel' OR [System.Tags] CONTAINS 'Excel')
                ORDER BY [System.CreatedDate] DESC
                """
                
                cmd = [
                    'az', 'boards', 'query', 
                    '--wiql', wiql_query,
                    '--org', f'https://dev.azure.com/{self.organization}',
                    '--project', self.project,
                    '--output', 'json'
                ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                data = json.loads(result.stdout)
                
                # Handle different response formats
                if isinstance(data, list):
                    work_items = data
                else:
                    work_items = data.get('workItems', [])
                
                print(f"✅ Found {len(work_items)} work items")
                
                # Fetch detailed information for each work item
                bugs = []
                for i, work_item in enumerate(work_items[:max_results]):
                    print(f"📋 Fetching details for work item {i+1}/{min(len(work_items), max_results)}...")
                    
                    # Extract work item ID
                    if isinstance(work_item, dict):
                        work_item_id = work_item.get('id') or work_item.get('fields', {}).get('System.Id')
                    else:
                        work_item_id = work_item
                    
                    if work_item_id:
                        bug_details = self.fetch_work_item_details_cli(work_item_id)
                        if bug_details:
                            bugs.append(bug_details)
                
                return bugs
            else:
                print(f"❌ Failed to fetch work items: {result.stderr}")
                return []
                
        except Exception as e:
            print(f"❌ Error fetching bugs via CLI: {e}")
            return []
    
    def fetch_work_item_details_cli(self, work_item_id: int) -> Optional[Dict]:
        """Fetch detailed work item information via CLI"""
        try:
            cmd = [
                'az', 'boards', 'work-item', 'show',
                '--id', str(work_item_id),
                '--org', f'https://dev.azure.com/{self.organization}',
                '--project', self.project,
                '--output', 'json'
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                work_item = json.loads(result.stdout)
                fields = work_item.get('fields', {})
                
                return {
                    'id': work_item.get('id'),
                    'title': fields.get('System.Title', ''),
                    'description': fields.get('System.Description', ''),
                    'state': fields.get('System.State', ''),
                    'created_by': fields.get('System.CreatedBy', {}).get('displayName', ''),
                    'created_date': fields.get('System.CreatedDate', ''),
                    'tags': fields.get('System.Tags', ''),
                    'priority': fields.get('Microsoft.VSTS.Common.Priority', ''),
                    'severity': fields.get('Microsoft.VSTS.Common.Severity', ''),
                    'repro_steps': fields.get('Microsoft.VSTS.TCM.ReproSteps', ''),
                    'area_path': fields.get('System.AreaPath', ''),
                    'iteration_path': fields.get('System.IterationPath', '')
                }
            else:
                print(f"❌ Failed to fetch work item {work_item_id}: {result.stderr}")
                return None
                
        except Exception as e:
            print(f"❌ Error fetching work item {work_item_id}: {e}")
            return None
    
    def setup_cli_environment(self) -> bool:
        """Setup CLI environment"""
        print("🔧 Setting up Azure CLI environment...")
        
        # Check if Azure CLI is installed
        if not self.check_azure_cli_installed():
            print("❌ Azure CLI not found. Please install it first:")
            print("   macOS: brew install azure-cli")
            print("   Windows: https://docs.microsoft.com/en-us/cli/azure/install-azure-cli-windows")
            print("   Linux: https://docs.microsoft.com/en-us/cli/azure/install-azure-cli-linux")
            return False
        
        # Check/install ADO extension
        if not self.check_ado_extension():
            if not self.install_ado_extension():
                return False
        
        # Login to Azure
        if not self.login_to_azure():
            return False
        
        # Configure ADO defaults
        if not self.configure_ado_defaults():
            return False
        
        print("✅ CLI environment setup complete!")
        return True

def main():
    """Main function for CLI integration"""
    print("🚀 Azure DevOps CLI Integration")
    print("=" * 50)
    
    # Configuration
    organization = "office"
    project = "OC"
    query_id = "6c1d07cd-a5d6-4483-9627-740d04b7fba8"
    
    integrator = ADOCLIIntegrator(organization, project)
    
    # Setup CLI environment
    if not integrator.setup_cli_environment():
        print("❌ CLI setup failed. Please check the requirements above.")
        return
    
    # Fetch bugs
    print(f"\n🔍 Fetching bugs from {organization}/{project}...")
    bugs = integrator.fetch_bugs_via_cli(query_id=query_id, max_results=30)
    
    if bugs:
        print(f"\n✅ Successfully fetched {len(bugs)} bugs!")
        
        # Save to JSON
        output_file = "ado_bugs_cli.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(bugs, f, indent=2, ensure_ascii=False)
        
        print(f"📁 Bug data saved to: {output_file}")
        
        # Show sample
        print(f"\n📋 Sample bug data:")
        for i, bug in enumerate(bugs[:3]):
            print(f"\nBug {i+1}:")
            print(f"  Title: {bug.get('title', 'N/A')}")
            print(f"  State: {bug.get('state', 'N/A')}")
            print(f"  Priority: {bug.get('priority', 'N/A')}")
            print(f"  Tags: {bug.get('tags', 'N/A')}")
        
        print(f"\n🎉 CLI integration successful! You can now use this data for prompt engineering.")
        
    else:
        print("❌ No bugs found or CLI integration failed")

if __name__ == "__main__":
    main()
