#!/usr/bin/env python3
"""
Azure DevOps Client for Orchestrator Agent
Creates bug work items in Azure DevOps from UX Analyzer issues
"""

import os
import requests
import logging
from typing import Dict, Any, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Azure DevOps configuration
ADO_ORG = os.getenv("ADO_ORG")
ADO_PROJECT = os.getenv("ADO_PROJECT") 
ADO_TOKEN = os.getenv("ADO_TOKEN")

# Setup logging
logger = logging.getLogger('ado_client')

class AzureDevOpsClient:
    """Client for creating and managing Azure DevOps work items"""
    
    def __init__(self, org: Optional[str] = None, project: Optional[str] = None, token: Optional[str] = None):
        self.org = org or ADO_ORG
        self.project = project or ADO_PROJECT
        self.token = token or ADO_TOKEN
        
        # Validate configuration
        if not all([self.org, self.project, self.token]):
            logger.warning("Azure DevOps not fully configured. Missing: " + 
                         ", ".join([k for k, v in {
                             "ADO_ORG": self.org,
                             "ADO_PROJECT": self.project, 
                             "ADO_TOKEN": self.token
                         }.items() if not v]))
    
    def is_configured(self) -> bool:
        """Check if ADO client is properly configured"""
        return all([self.org, self.project, self.token])
    
    def create_ado_ticket(self, issue: Dict[str, Any]) -> Optional[int]:
        """
        Creates a bug work item in Azure DevOps.
        
        Args:
            issue: Dictionary containing issue details with keys:
                - type: Issue type (e.g., 'accessibility', 'performance')
                - severity: Issue severity ('high', 'medium', 'low')
                - message: Issue description
                - file: File where issue was found
                - element: DOM element (optional)
                - recommendation: Fix recommendation
        
        Returns:
            Work item ID if successful, None otherwise
        """
        if not self.is_configured():
            logger.error("Azure DevOps not configured. Please set ADO_ORG, ADO_PROJECT, and ADO_TOKEN")
            return None
        
        try:
            url = f"https://dev.azure.com/{self.org}/{self.project}/_apis/wit/workitems/$Bug?api-version=6.0"
            
            headers = {
                'Content-Type': 'application/json-patch+json',
            }
            
            # Map severity to ADO severity values
            severity_mapping = {
                "high": "1 - Critical",
                "medium": "2 - High", 
                "low": "3 - Medium"
            }
            ado_severity = severity_mapping.get(issue.get("severity", "medium"), "2 - High")
            
            # Create detailed description
            description_parts = [
                f"<b>Issue Type:</b> {issue.get('type', 'Unknown')}<br>",
                f"<b>File:</b> {issue.get('file', 'Not specified')}<br>",
                f"<b>Message:</b> {issue.get('message', 'No description')}<br>"
            ]
            
            if issue.get('element'):
                description_parts.append(f"<b>Element:</b> {issue['element']}<br>")
            
            if issue.get('recommendation'):
                description_parts.append(f"<br><b>Recommended Fix:</b><br>{issue['recommendation']}")
            
            description = "".join(description_parts)
            
            # Create title
            issue_message = issue.get('message', 'UX Issue')
            title = f"UX Bug: {issue_message[:80]}{'...' if len(issue_message) > 80 else ''}"
            
            payload = [
                {
                    "op": "add",
                    "path": "/fields/System.Title",
                    "value": title
                },
                {
                    "op": "add", 
                    "path": "/fields/System.Description",
                    "value": description
                },
                {
                    "op": "add",
                    "path": "/fields/Microsoft.VSTS.Common.Severity",
                    "value": ado_severity
                },
                {
                    "op": "add",
                    "path": "/fields/System.Tags",
                    "value": f"UX-Analyzer; {issue.get('type', 'unknown-type')}; automated"
                }
            ]
            
            logger.info(f"Creating ADO ticket for {issue.get('type')} issue: {issue.get('message', '')[:50]}")
            
            response = requests.post(
                url,
                auth=('', self.token),
                headers=headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code in [200, 201]:
                work_item = response.json()
                work_item_id = work_item['id']
                logger.info(f"✅ Created ADO Bug #{work_item_id}: {title}")
                return work_item_id
            else:
                logger.error(f"❌ Failed to create ADO bug: {response.status_code} - {response.text}")
                return None
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Network error creating ADO ticket: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error creating ADO ticket: {e}")
            return None
    
    def get_work_item(self, work_item_id: int) -> Optional[Dict[str, Any]]:
        """Get details of a work item by ID"""
        if not self.is_configured():
            return None
        
        try:
            url = f"https://dev.azure.com/{self.org}/{self.project}/_apis/wit/workitems/{work_item_id}?api-version=6.0"
            
            response = requests.get(
                url,
                auth=('', self.token),
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Failed to get work item {work_item_id}: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Error getting work item {work_item_id}: {e}")
            return None
    
    def test_connection(self) -> bool:
        """Test the Azure DevOps connection"""
        if not self.is_configured():
            return False
        
        try:
            # Test with a simple query to projects
            url = f"https://dev.azure.com/{self.org}/_apis/projects/{self.project}?api-version=6.0"
            
            response = requests.get(
                url,
                auth=('', self.token),
                timeout=10
            )
            
            if response.status_code == 200:
                logger.info("✅ Azure DevOps connection successful")
                return True
            else:
                logger.error(f"ADO connection failed: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"ADO connection test failed: {e}")
            return False

# Convenience function for backward compatibility
def create_ado_ticket(issue: Dict[str, Any]) -> Optional[int]:
    """
    Creates a bug work item in Azure DevOps.
    Convenience function that uses the default ADO client.
    """
    client = AzureDevOpsClient()
    return client.create_ado_ticket(issue)

# Default client instance
default_client = AzureDevOpsClient()

if __name__ == "__main__":
    # Test the ADO client
    client = AzureDevOpsClient()
    
    print("🧪 Testing Azure DevOps Client...")
    print(f"Configuration: Org={client.org}, Project={client.project}, Token={'*'*10 if client.token else 'None'}")
    
    if client.is_configured():
        print("✅ Configuration complete")
        
        # Test connection
        if client.test_connection():
            print("✅ Connection successful")
            
            # Test ticket creation
            test_issue = {
                "type": "accessibility",
                "severity": "high",
                "message": "Test issue from orchestrator",
                "file": "test.html",
                "element": "img.test",
                "recommendation": "This is a test ticket created by the orchestrator"
            }
            
            ticket_id = client.create_ado_ticket(test_issue)
            if ticket_id:
                print(f"✅ Test ticket created: #{ticket_id}")
            else:
                print("❌ Failed to create test ticket")
        else:
            print("❌ Connection failed")
    else:
        print("❌ ADO not configured. Please set ADO_ORG, ADO_PROJECT, and ADO_TOKEN in .env file")
