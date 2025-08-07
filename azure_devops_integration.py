#!/usr/bin/env python3
"""
Azure DevOps Integration Client
Connects UX analysis results with Azure DevOps work items and dashboards
"""

import os
import json
import requests
import base64
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

@dataclass
class UXIssue:
    """Structure for UX issues to be converted to work items"""
    title: str
    description: str
    category: str
    severity: str
    app_type: str
    scenario_id: str
    scenario_title: str
    reproduction_steps: List[str] = None
    acceptance_criteria: List[str] = None

@dataclass
class WorkItemConfig:
    """Configuration for Azure DevOps work item creation"""
    work_item_type: str = "Bug"  # Bug, User Story, Task, etc.
    area_path: str = ""
    iteration_path: str = ""
    assigned_to: str = ""
    priority: int = 2  # 1=High, 2=Medium, 3=Low, 4=Very Low

class AzureDevOpsClient:
    """Azure DevOps API client for work item management"""
    
    def __init__(self, demo_mode: bool = False):
        # Demo mode for testing without ADO connectivity
        self.demo_mode = demo_mode
        
        # Load configuration from environment
        self.organization = os.getenv('ADO_ORGANIZATION', 'your-org')
        self.project = os.getenv('ADO_PROJECT', 'UX-Analysis')
        self.personal_access_token = os.getenv('ADO_PAT', '')
        
        # API configuration
        self.base_url = f"https://dev.azure.com/{self.organization}/{self.project}/_apis"
        self.api_version = "7.0"
        
        # Authentication header
        if self.personal_access_token and not self.demo_mode:
            credentials = base64.b64encode(f":{self.personal_access_token}".encode()).decode()
            self.headers = {
                "Authorization": f"Basic {credentials}",
                "Content-Type": "application/json-patch+json"
            }
            self.authenticated = True
        else:
            self.headers = {"Content-Type": "application/json"}
            self.authenticated = False
    
    def test_connection(self) -> Dict[str, Any]:
        """Test connection to Azure DevOps"""
        if not self.authenticated:
            return {
                "connected": False,
                "error": "No Azure DevOps PAT configured",
                "demo_mode": True
            }
        
        try:
            # Test with a simple project info request
            url = f"{self.base_url}/project?api-version={self.api_version}"
            response = requests.get(url, headers=self.headers, timeout=10)
            
            if response.status_code == 200:
                return {
                    "connected": True,
                    "organization": self.organization,
                    "project": self.project,
                    "demo_mode": False
                }
            else:
                return {
                    "connected": False,
                    "error": f"API error: {response.status_code}",
                    "demo_mode": True
                }
                
        except requests.exceptions.RequestException as e:
            return {
                "connected": False,
                "error": f"Connection error: {str(e)}",
                "demo_mode": True
            }
    
    def create_work_item(self, ux_issue: UXIssue, config: WorkItemConfig = None) -> Dict[str, Any]:
        """Create Azure DevOps work item from UX issue"""
        
        if config is None:
            config = WorkItemConfig()
        
        # If not authenticated, return demo response
        if not self.authenticated:
            return self._create_demo_work_item(ux_issue, config)
        
        try:
            # Prepare work item fields
            work_item_data = self._prepare_work_item_data(ux_issue, config)
            
            # Create work item via API
            url = f"{self.base_url}/wit/workitems/${config.work_item_type}?api-version={self.api_version}"
            response = requests.post(url, headers=self.headers, json=work_item_data, timeout=30)
            
            if response.status_code == 200:
                work_item = response.json()
                return {
                    "success": True,
                    "work_item_id": work_item.get("id"),
                    "work_item_url": work_item.get("_links", {}).get("html", {}).get("href", ""),
                    "title": ux_issue.title
                }
            else:
                return {
                    "success": False,
                    "error": f"Failed to create work item: {response.status_code}",
                    "response": response.text
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"Exception creating work item: {str(e)}"
            }
    
    def create_ux_work_item(self, ux_issue_dict: Dict[str, Any]) -> Dict[str, Any]:
        """Create UX work item from dictionary (convenience method for integration tests)"""
        
        # Convert dictionary to UXIssue object
        ux_issue = UXIssue(
            app_type=ux_issue_dict.get("app_type", "unknown"),
            scenario_id=ux_issue_dict.get("scenario", "unknown"),
            scenario_title=ux_issue_dict.get("scenario", "unknown"),
            title=ux_issue_dict.get("title", "UX Issue"),
            description=ux_issue_dict.get("description", ""),
            category=ux_issue_dict.get("category", "General"),
            severity=ux_issue_dict.get("severity", "medium")
        )
        
        return self.create_work_item(ux_issue)
    
    def _prepare_work_item_data(self, ux_issue: UXIssue, config: WorkItemConfig) -> List[Dict]:
        """Prepare work item data for Azure DevOps API"""
        
        # Build description with rich formatting
        description = self._build_work_item_description(ux_issue)
        
        # Build tags
        tags = f"UX-Analysis; {ux_issue.app_type}; {ux_issue.category}; {ux_issue.severity}"
        
        fields = [
            {"op": "add", "path": "/fields/System.Title", "value": ux_issue.title},
            {"op": "add", "path": "/fields/System.Description", "value": description},
            {"op": "add", "path": "/fields/System.Tags", "value": tags},
            {"op": "add", "path": "/fields/Microsoft.VSTS.Common.Priority", "value": config.priority},
            {"op": "add", "path": "/fields/Microsoft.VSTS.Common.Severity", "value": self._map_severity_to_ado(ux_issue.severity)}
        ]
        
        # Add optional fields if provided
        if config.area_path:
            fields.append({"op": "add", "path": "/fields/System.AreaPath", "value": config.area_path})
        
        if config.iteration_path:
            fields.append({"op": "add", "path": "/fields/System.IterationPath", "value": config.iteration_path})
        
        if config.assigned_to:
            fields.append({"op": "add", "path": "/fields/System.AssignedTo", "value": config.assigned_to})
        
        return fields
    
    def _build_work_item_description(self, ux_issue: UXIssue) -> str:
        """Build rich HTML description for work item"""
        
        description = f"""
<h3>UX Issue Analysis</h3>
<p><strong>Application:</strong> {ux_issue.app_type.title()}</p>
<p><strong>Scenario:</strong> {ux_issue.scenario_title}</p>
<p><strong>Category:</strong> {ux_issue.category}</p>
<p><strong>Severity:</strong> {ux_issue.severity.title()}</p>

<h3>Issue Description</h3>
<p>{ux_issue.description}</p>
"""
        
        if ux_issue.reproduction_steps:
            description += """
<h3>Reproduction Steps</h3>
<ol>
"""
            for step in ux_issue.reproduction_steps:
                description += f"<li>{step}</li>\n"
            description += "</ol>\n"
        
        if ux_issue.acceptance_criteria:
            description += """
<h3>Acceptance Criteria</h3>
<ul>
"""
            for criterion in ux_issue.acceptance_criteria:
                description += f"<li>{criterion}</li>\n"
            description += "</ul>\n"
        
        description += f"""
<h3>Analysis Details</h3>
<p><strong>Generated:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
<p><strong>Scenario ID:</strong> {ux_issue.scenario_id}</p>
<p><strong>Source:</strong> Automated UX Analysis System</p>
"""
        
        return description
    
    def _map_severity_to_ado(self, severity: str) -> str:
        """Map UX severity to Azure DevOps severity levels"""
        severity_map = {
            "high": "1 - Critical",
            "medium": "2 - High", 
            "low": "3 - Medium"
        }
        return severity_map.get(severity.lower(), "3 - Medium")
    
    def _create_demo_work_item(self, ux_issue: UXIssue, config: WorkItemConfig) -> Dict[str, Any]:
        """Create demo work item response when not connected to ADO"""
        
        demo_id = hash(f"{ux_issue.title}{datetime.now()}") % 10000
        
        return {
            "success": True,
            "work_item_id": demo_id,
            "work_item_url": f"https://dev.azure.com/{self.organization}/{self.project}/_workitems/edit/{demo_id}",
            "title": ux_issue.title,
            "demo_mode": True,
            "note": "Demo mode - work item not actually created in Azure DevOps"
        }
    
    def create_bulk_work_items(self, ux_issues: List[UXIssue], config: WorkItemConfig = None) -> Dict[str, Any]:
        """Create multiple work items from UX issues"""
        
        results = {
            "total_issues": len(ux_issues),
            "successful_creations": 0,
            "failed_creations": 0,
            "work_items": [],
            "errors": []
        }
        
        for issue in ux_issues:
            try:
                result = self.create_work_item(issue, config)
                
                if result.get("success"):
                    results["successful_creations"] += 1
                    results["work_items"].append(result)
                else:
                    results["failed_creations"] += 1
                    results["errors"].append({
                        "issue_title": issue.title,
                        "error": result.get("error", "Unknown error")
                    })
                    
            except Exception as e:
                results["failed_creations"] += 1
                results["errors"].append({
                    "issue_title": issue.title,
                    "error": str(e)
                })
        
        return results
    
    def get_project_work_items(self, query_filter: str = None) -> List[Dict[str, Any]]:
        """Retrieve work items from the project"""
        
        if not self.authenticated:
            return self._get_demo_work_items()
        
        try:
            # Build WIQL query
            if query_filter:
                wiql = f"SELECT [System.Id], [System.Title], [System.State] FROM WorkItems WHERE [System.TeamProject] = '{self.project}' AND {query_filter}"
            else:
                wiql = f"SELECT [System.Id], [System.Title], [System.State] FROM WorkItems WHERE [System.TeamProject] = '{self.project}' AND [System.Tags] CONTAINS 'UX-Analysis'"
            
            # Execute query
            url = f"{self.base_url}/wit/wiql?api-version={self.api_version}"
            query_data = {"query": wiql}
            
            response = requests.post(url, headers=self.headers, json=query_data, timeout=30)
            
            if response.status_code == 200:
                return response.json().get("workItems", [])
            else:
                return []
                
        except requests.exceptions.RequestException:
            return []
    
    def _get_demo_work_items(self) -> List[Dict[str, Any]]:
        """Return demo work items for testing"""
        return [
            {"id": 1001, "title": "Excel formula bar usability issue", "state": "New"},
            {"id": 1002, "title": "Word track changes interface complexity", "state": "Active"},
            {"id": 1003, "title": "PowerPoint animation timing controls", "state": "Resolved"}
        ]

class UXAnalysisToADOConverter:
    """Converts UX analysis results to Azure DevOps work items"""
    
    def __init__(self, ado_client: AzureDevOpsClient = None):
        self.ado_client = ado_client if ado_client else AzureDevOpsClient()
    
    def convert_analysis_results(self, analysis_file: str) -> List[UXIssue]:
        """Convert analysis results file to UX issues"""
        
        try:
            with open(analysis_file, 'r') as f:
                data = json.load(f)
            
            ux_issues = []
            
            # Handle different result file formats
            if "scenarios" in data:
                # Single app results format
                app_type = data.get("app_type", "unknown")
                for scenario_id, scenario_data in data["scenarios"].items():
                    if isinstance(scenario_data, dict) and "issues" in scenario_data:
                        issues = self._convert_scenario_issues(scenario_data, app_type, scenario_id)
                        ux_issues.extend(issues)
            
            elif "app_results" in data:
                # Integrated results format
                for app_type, app_data in data["app_results"].items():
                    for scenario_id, scenario_data in app_data.get("scenarios", {}).items():
                        if isinstance(scenario_data, dict) and "issues" in scenario_data:
                            issues = self._convert_scenario_issues(scenario_data, app_type, scenario_id)
                            ux_issues.extend(issues)
            
            return ux_issues
            
        except Exception as e:
            print(f"Error converting analysis results: {e}")
            return []
    
    def _convert_scenario_issues(self, scenario_data: Dict, app_type: str, scenario_id: str) -> List[UXIssue]:
        """Convert scenario issues to UX issues"""
        
        ux_issues = []
        issues = scenario_data.get("issues", [])
        scenario_title = scenario_data.get("title", f"Scenario {scenario_id}")
        
        for i, issue in enumerate(issues):
            if isinstance(issue, dict):
                # Structured issue format
                ux_issue = UXIssue(
                    title=f"{app_type.title()} UX Issue: {issue.get('category', 'General')} - {scenario_title}",
                    description=issue.get("description", str(issue)),
                    category=issue.get("category", "General"),
                    severity=issue.get("severity", "medium"),
                    app_type=app_type,
                    scenario_id=scenario_id,
                    scenario_title=scenario_title
                )
            else:
                # Simple string issue format
                ux_issue = UXIssue(
                    title=f"{app_type.title()} UX Issue: {scenario_title} #{i+1}",
                    description=str(issue),
                    category="General",
                    severity="medium",
                    app_type=app_type,
                    scenario_id=scenario_id,
                    scenario_title=scenario_title
                )
            
            # Add reproduction steps if available
            if "steps" in scenario_data:
                ux_issue.reproduction_steps = [
                    step.get("description", str(step)) 
                    for step in scenario_data["steps"] 
                    if isinstance(step, dict)
                ]
            
            ux_issues.append(ux_issue)
        
        return ux_issues
    
    def sync_results_to_ado(self, analysis_file: str, config: WorkItemConfig = None) -> Dict[str, Any]:
        """Sync UX analysis results to Azure DevOps"""
        
        print(f"🔄 Syncing UX analysis results to Azure DevOps...")
        
        # Convert analysis to UX issues
        ux_issues = self.convert_analysis_results(analysis_file)
        
        if not ux_issues:
            return {
                "success": False,
                "error": "No UX issues found in analysis file"
            }
        
        print(f"📋 Found {len(ux_issues)} UX issues to sync")
        
        # Create work items in bulk
        sync_results = self.ado_client.create_bulk_work_items(ux_issues, config)
        
        print(f"✅ Successfully created {sync_results['successful_creations']} work items")
        if sync_results['failed_creations'] > 0:
            print(f"❌ Failed to create {sync_results['failed_creations']} work items")
        
        return sync_results

def main():
    """Main execution for Azure DevOps integration testing"""
    
    print("🚀 Azure DevOps Integration - Phase 2.5")
    print("=" * 50)
    
    # Test connection
    ado_client = AzureDevOpsClient()
    connection_test = ado_client.test_connection()
    
    print(f"🔌 Azure DevOps Connection:")
    if connection_test["connected"]:
        print(f"   ✅ Connected to {connection_test['organization']}/{connection_test['project']}")
    else:
        print(f"   ⚠️  {connection_test['error']}")
        if connection_test.get("demo_mode"):
            print("   🎭 Running in demo mode")
    
    # Demo UX issue creation
    print(f"\n📝 Creating demo UX issue...")
    
    demo_issue = UXIssue(
        title="Excel Formula Bar Usability Issue",
        description="Formula bar truncates complex expressions without scroll indicators, making it difficult for users to review and edit long formulas",
        category="Formula Management", 
        severity="medium",
        app_type="excel",
        scenario_id="2.1",
        scenario_title="Enter formula in cell and validate result",
        reproduction_steps=[
            "Open Excel with financial model",
            "Enter complex VLOOKUP formula in cell",
            "Observe formula bar truncation",
            "Attempt to edit formula"
        ],
        acceptance_criteria=[
            "Formula bar should show scroll indicators for long formulas",
            "Users should be able to expand formula bar height",
            "Syntax highlighting should remain visible during editing"
        ]
    )
    
    # Create work item
    work_item_result = ado_client.create_work_item(demo_issue)
    
    if work_item_result["success"]:
        print(f"   ✅ Work item created: ID {work_item_result['work_item_id']}")
        if work_item_result.get("demo_mode"):
            print(f"   🎭 Demo mode - URL: {work_item_result['work_item_url']}")
    else:
        print(f"   ❌ Failed to create work item: {work_item_result['error']}")
    
    print("\n✅ Azure DevOps integration test completed!")

if __name__ == "__main__":
    main()
