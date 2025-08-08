"""
Azure DevOps Work Item Sync Service
Integrates UX Analyzer reports with Azure DevOps as native Work Items
"""

import os
import json
import base64
import requests
from typing import Dict, List, Optional, Any
from datetime import datetime
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ADOSyncService:
    """Service for syncing UX issues to Azure DevOps Work Items"""
    
    def __init__(self):
        """Initialize ADO sync service with configuration"""
        self.organization = os.getenv('ADO_ORGANIZATION')
        self.project = os.getenv('ADO_PROJECT')
        self.personal_access_token = os.getenv('ADO_PAT')
        
        if not all([self.organization, self.project, self.personal_access_token]):
            logger.warning("ADO credentials not fully configured. Set ADO_ORGANIZATION, ADO_PROJECT, ADO_PAT in .env")
            
        # API Configuration
        self.base_url = f"https://dev.azure.com/{self.organization}/{self.project}/_apis"
        self.api_version = "7.0"
        
        # Authentication header
        token_bytes = f":{self.personal_access_token}".encode('ascii')
        token_b64 = base64.b64encode(token_bytes).decode('ascii')
        self.headers = {
            'Authorization': f'Basic {token_b64}',
            'Content-Type': 'application/json-patch+json',
            'Accept': 'application/json'
        }
    
    def validate_credentials(self) -> bool:
        """Validate ADO credentials and connectivity"""
        try:
            if not all([self.organization, self.project, self.personal_access_token]):
                return False
                
            # Test API connection with a simple query
            url = f"{self.base_url}/wit/workitems/$UX-Test?api-version={self.api_version}"
            response = requests.get(url, headers=self.headers, timeout=10)
            
            # We expect 404 for non-existent work item, which means API is accessible
            return response.status_code in [200, 404]
            
        except Exception as e:
            logger.error(f"ADO credential validation failed: {e}")
            return False
    
    def create_work_item(self, issue_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Create a Work Item in Azure DevOps for a UX issue
        
        Args:
            issue_data: Dictionary containing issue information
            
        Returns:
            Created work item data or None if failed
        """
        try:
            # Prepare work item fields
            title = issue_data.get('title', 'UX Issue Detected')
            description = self._format_description(issue_data)
            tags = self._generate_tags(issue_data)
            
            # Work item payload using JSON Patch format
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
                    "path": "/fields/System.Tags",
                    "value": "; ".join(tags)
                },
                {
                    "op": "add",
                    "path": "/fields/System.WorkItemType",
                    "value": "Bug"  # or "Task" depending on your ADO configuration
                },
                {
                    "op": "add",
                    "path": "/fields/System.State",
                    "value": "New"
                },
                {
                    "op": "add",
                    "path": "/fields/Microsoft.VSTS.Common.Priority",
                    "value": self._map_severity_to_priority(issue_data.get('severity', 'medium'))
                },
                {
                    "op": "add",
                    "path": "/fields/Microsoft.VSTS.Common.Severity",
                    "value": self._map_severity(issue_data.get('severity', 'medium'))
                }
            ]
            
            # Add custom fields if available
            if issue_data.get('module'):
                payload.append({
                    "op": "add",
                    "path": "/fields/System.AreaPath",
                    "value": f"{self.project}\\UX\\{issue_data['module'].title()}"
                })
            
            # Create work item
            url = f"{self.base_url}/wit/workitems/$Bug?api-version={self.api_version}"
            response = requests.post(url, headers=self.headers, json=payload, timeout=30)
            
            if response.status_code == 200:
                work_item = response.json()
                logger.info(f"Created ADO Work Item {work_item['id']} for issue: {title}")
                
                # Attach screenshot if available
                if issue_data.get('screenshot_path'):
                    self._attach_screenshot(work_item['id'], issue_data['screenshot_path'])
                
                # Add fix history as comments
                if issue_data.get('fix_history'):
                    self._add_fix_history_comments(work_item['id'], issue_data['fix_history'])
                
                return work_item
            else:
                logger.error(f"Failed to create work item: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Error creating work item: {e}")
            return None
    
    def _format_description(self, issue_data: Dict[str, Any]) -> str:
        """Format issue description for ADO Work Item"""
        description_parts = []
        
        # Basic issue information
        description_parts.append(f"<h3>UX Issue Report</h3>")
        description_parts.append(f"<p><strong>Module:</strong> {issue_data.get('module', 'Unknown')}</p>")
        description_parts.append(f"<p><strong>Element:</strong> <code>{issue_data.get('element', 'N/A')}</code></p>")
        description_parts.append(f"<p><strong>Severity:</strong> {issue_data.get('severity', 'medium').title()}</p>")
        description_parts.append(f"<p><strong>Detected:</strong> {issue_data.get('timestamp', datetime.now().isoformat())}</p>")
        
        # Issue details
        if issue_data.get('description'):
            description_parts.append(f"<h4>Description</h4>")
            description_parts.append(f"<p>{issue_data['description']}</p>")
        
        # Recommendation
        if issue_data.get('recommendation'):
            description_parts.append(f"<h4>Recommended Fix</h4>")
            description_parts.append(f"<p>{issue_data['recommendation']}</p>")
        
        # Report context
        if issue_data.get('report_id'):
            description_parts.append(f"<h4>Source Report</h4>")
            description_parts.append(f"<p><strong>Report ID:</strong> {issue_data['report_id']}</p>")
            
        description_parts.append(f"<hr><p><em>Generated by UX Analyzer on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</em></p>")
        
        return "\n".join(description_parts)
    
    def _generate_tags(self, issue_data: Dict[str, Any]) -> List[str]:
        """Generate tags for work item categorization"""
        tags = ['UX-Analyzer', 'Automated-Detection']
        
        # Add module tag
        if issue_data.get('module'):
            tags.append(f"Module-{issue_data['module'].title()}")
        
        # Add severity tag
        if issue_data.get('severity'):
            tags.append(f"Severity-{issue_data['severity'].title()}")
        
        # Add category tags based on module type
        module = issue_data.get('module', '').lower()
        if 'accessibility' in module or 'a11y' in module:
            tags.append('Accessibility')
        elif 'performance' in module:
            tags.append('Performance')
        elif 'usability' in module:
            tags.append('Usability')
        elif 'visual' in module or 'ui' in module:
            tags.append('Visual-Design')
        else:
            tags.append('UX-General')
        
        return tags
    
    def _map_severity_to_priority(self, severity: str) -> int:
        """Map issue severity to ADO priority"""
        severity_map = {
            'critical': 1,
            'high': 2, 
            'medium': 3,
            'low': 4
        }
        return severity_map.get(severity.lower(), 3)
    
    def _map_severity(self, severity: str) -> str:
        """Map issue severity to ADO severity"""
        severity_map = {
            'critical': '1 - Critical',
            'high': '2 - High',
            'medium': '3 - Medium', 
            'low': '4 - Low'
        }
        return severity_map.get(severity.lower(), '3 - Medium')
    
    def _attach_screenshot(self, work_item_id: int, screenshot_path: str) -> bool:
        """Attach screenshot to work item"""
        try:
            # Check if screenshot file exists
            full_path = Path(f"reports/screenshots/{screenshot_path}")
            if not full_path.exists():
                logger.warning(f"Screenshot not found: {full_path}")
                return False
            
            # Upload attachment
            with open(full_path, 'rb') as file:
                file_content = file.read()
            
            # Upload file to ADO
            upload_url = f"https://dev.azure.com/{self.organization}/{self.project}/_apis/wit/attachments?fileName={screenshot_path}&api-version={self.api_version}"
            upload_headers = {
                'Authorization': self.headers['Authorization'],
                'Content-Type': 'application/octet-stream'
            }
            
            upload_response = requests.post(upload_url, headers=upload_headers, data=file_content, timeout=30)
            
            if upload_response.status_code == 200:
                attachment_ref = upload_response.json()
                
                # Attach to work item
                attach_payload = [{
                    "op": "add",
                    "path": "/relations/-",
                    "value": {
                        "rel": "AttachedFile",
                        "url": attachment_ref['url'],
                        "attributes": {
                            "comment": "UX Issue Screenshot"
                        }
                    }
                }]
                
                attach_url = f"{self.base_url}/wit/workitems/{work_item_id}?api-version={self.api_version}"
                attach_response = requests.patch(attach_url, headers=self.headers, json=attach_payload, timeout=30)
                
                if attach_response.status_code == 200:
                    logger.info(f"Screenshot attached to work item {work_item_id}")
                    return True
                else:
                    logger.error(f"Failed to attach screenshot: {attach_response.status_code}")
                    return False
            else:
                logger.error(f"Failed to upload screenshot: {upload_response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Error attaching screenshot: {e}")
            return False
    
    def _add_fix_history_comments(self, work_item_id: int, fix_history: List[Dict[str, Any]]) -> bool:
        """Add fix history as comments to work item"""
        try:
            for entry in fix_history:
                comment_text = f"Fix History Entry:\n"
                comment_text += f"Date: {entry.get('timestamp', 'Unknown')}\n"
                comment_text += f"Note: {entry.get('note', 'No details')}\n"
                if entry.get('developer'):
                    comment_text += f"Developer: {entry['developer']}\n"
                
                # Add comment
                comment_payload = [{
                    "op": "add",
                    "path": "/fields/System.History",
                    "value": comment_text
                }]
                
                comment_url = f"{self.base_url}/wit/workitems/{work_item_id}?api-version={self.api_version}"
                comment_response = requests.patch(comment_url, headers=self.headers, json=comment_payload, timeout=30)
                
                if comment_response.status_code != 200:
                    logger.warning(f"Failed to add comment: {comment_response.status_code}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error adding fix history comments: {e}")
            return False
    
    def sync_report_to_ado(self, report_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Sync entire report to ADO as multiple work items
        
        Args:
            report_data: Full report data dictionary
            
        Returns:
            Sync status and created work item IDs
        """
        result = {
            'success': True,
            'work_items_created': [],
            'errors': [],
            'total_issues': 0,
            'synced_issues': 0
        }
        
        try:
            # Extract issues from report based on structure
            issues = self._extract_issues_from_report(report_data)
            result['total_issues'] = len(issues)
            
            if not issues:
                result['errors'].append("No issues found in report")
                result['success'] = False
                return result
            
            # Create work item for each issue
            for issue in issues:
                work_item = self.create_work_item(issue)
                if work_item:
                    result['work_items_created'].append({
                        'id': work_item['id'],
                        'title': work_item['fields']['System.Title'],
                        'url': work_item['_links']['html']['href']
                    })
                    result['synced_issues'] += 1
                else:
                    result['errors'].append(f"Failed to create work item for: {issue.get('title', 'Unknown issue')}")
            
            # Mark as success if at least one work item was created
            result['success'] = result['synced_issues'] > 0
            
            logger.info(f"ADO Sync completed: {result['synced_issues']}/{result['total_issues']} issues synced")
            
        except Exception as e:
            logger.error(f"Error syncing report to ADO: {e}")
            result['success'] = False
            result['errors'].append(str(e))
        
        return result
    
    def _extract_issues_from_report(self, report_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract individual issues from report data"""
        issues = []
        
        try:
            # Try to get issues from module_results (newer format)
            module_results = report_data.get('module_results', {})
            
            for module_name, module_data in module_results.items():
                findings = module_data.get('findings', [])
                
                for finding in findings:
                    issue = {
                        'title': finding.get('title', f"{module_name.title()} Issue"),
                        'description': finding.get('description', ''),
                        'module': module_name,
                        'severity': finding.get('severity', 'medium'),
                        'element': finding.get('element', ''),
                        'recommendation': finding.get('recommendation', ''),
                        'timestamp': report_data.get('timestamp', datetime.now().isoformat()),
                        'report_id': report_data.get('analysis_id', 'unknown'),
                        'screenshot_path': finding.get('screenshot_path'),
                        'fix_history': finding.get('fix_history', [])
                    }
                    issues.append(issue)
            
            # Fallback: try legacy ux_issues format
            if not issues and 'ux_issues' in report_data:
                for ux_issue in report_data['ux_issues']:
                    issue = {
                        'title': ux_issue.get('description', 'UX Issue'),
                        'description': ux_issue.get('details', ''),
                        'module': ux_issue.get('category', 'general'),
                        'severity': ux_issue.get('severity', 'medium'),
                        'element': ux_issue.get('element', ''),
                        'recommendation': ux_issue.get('recommendation', ''),
                        'timestamp': report_data.get('timestamp', datetime.now().isoformat()),
                        'report_id': report_data.get('analysis_id', 'unknown'),
                        'screenshot_path': ux_issue.get('screenshot_path'),
                        'fix_history': []
                    }
                    issues.append(issue)
        
        except Exception as e:
            logger.error(f"Error extracting issues from report: {e}")
        
        return issues

# Global service instance
ado_service = ADOSyncService()
