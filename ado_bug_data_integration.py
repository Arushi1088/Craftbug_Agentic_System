#!/usr/bin/env python3
"""
Azure DevOps Bug Data Integration Module
For prompt engineering with historical Excel bug data
"""

import json
import csv
import os
import requests
from datetime import datetime
from typing import List, Dict, Optional
import base64

class ADOBugDataIntegrator:
    """Handles integration with Azure DevOps for Excel bug data"""
    
    def __init__(self, organization: str, project: str, personal_access_token: Optional[str] = None):
        self.organization = organization
        self.project = project
        self.personal_access_token = personal_access_token
        self.base_url = f"https://dev.azure.com/{organization}/{project}"
        self.headers = {}
        
        if personal_access_token:
            self.headers = {
                'Authorization': f'Basic {base64.b64encode(f":{personal_access_token}".encode()).decode()}',
                'Content-Type': 'application/json'
            }
    
    def load_csv_bug_data(self, csv_file_path: str) -> List[Dict]:
        """Load bug data from CSV export"""
        bugs = []
        
        try:
            with open(csv_file_path, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    bugs.append(row)
            
            print(f"✅ Loaded {len(bugs)} bugs from CSV: {csv_file_path}")
            return bugs
            
        except Exception as e:
            print(f"❌ Error loading CSV bug data: {e}")
            return []
    
    def fetch_bugs_via_api(self, query_id: str = None, wiql: str = None) -> List[Dict]:
        """Fetch bugs via ADO REST API"""
        if not self.personal_access_token:
            print("❌ Personal Access Token required for API access")
            return []
        
        try:
            # Option 1: Use specific query ID (recommended)
            if query_id:
                print(f"🔍 Fetching bugs using query ID: {query_id}")
                url = f"{self.base_url}/_apis/wit/queries/{query_id}?api-version=6.0"
                
                # First, get the query definition
                response = requests.get(url, headers=self.headers)
                response.raise_for_status()
                query_info = response.json()
                
                # Then execute the query
                execute_url = f"{self.base_url}/_apis/wit/wiql?api-version=6.0"
                payload = {"query": query_info.get('wiql', '')}
                
                print(f"📋 Executing query: {query_info.get('name', 'Unknown Query')}")
            
            # Option 2: Use custom WIQL
            elif wiql:
                print(f"🔍 Fetching bugs using custom WIQL")
                execute_url = f"{self.base_url}/_apis/wit/wiql?api-version=6.0"
                payload = {"query": wiql}
            
            else:
                # Option 3: Default Excel-related bugs query
                print(f"🔍 Fetching Excel-related bugs using default query")
                execute_url = f"{self.base_url}/_apis/wit/wiql?api-version=6.0"
                payload = {
                    "query": f"""SELECT [System.Id], [System.Title], [System.Description], [System.State], 
                                       [System.CreatedBy], [System.CreatedDate], [System.Tags],
                                       [Microsoft.VSTS.Common.Priority], [Microsoft.VSTS.Common.Severity],
                                       [Microsoft.VSTS.TCM.ReproSteps], [System.AreaPath], [System.IterationPath]
                                FROM WorkItems 
                                WHERE [System.WorkItemType] = 'Bug' 
                                  AND [System.TeamProject] = '{self.project}'
                                  AND ([System.Title] CONTAINS 'Excel' OR [System.Description] CONTAINS 'Excel' OR [System.Tags] CONTAINS 'Excel')
                                ORDER BY [System.CreatedDate] DESC"""
                }
            
            response = requests.post(execute_url, headers=self.headers, json=payload)
            response.raise_for_status()
            
            work_items = response.json().get('workItems', [])
            bugs = []
            
            # Fetch detailed information for each work item
            for work_item in work_items[:50]:  # Limit to 50 for performance
                bug_details = self.fetch_work_item_details(work_item['id'])
                if bug_details:
                    bugs.append(bug_details)
            
            print(f"✅ Fetched {len(bugs)} bugs via API")
            return bugs
            
        except Exception as e:
            print(f"❌ Error fetching bugs via API: {e}")
            return []
    
    def fetch_work_item_details(self, work_item_id: int) -> Optional[Dict]:
        """Fetch detailed information for a specific work item"""
        try:
            url = f"{self.base_url}/_apis/wit/workItems/{work_item_id}?api-version=6.0"
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            
            work_item = response.json()
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
            
        except Exception as e:
            print(f"❌ Error fetching work item {work_item_id}: {e}")
            return None
    
    def analyze_bug_patterns(self, bugs: List[Dict]) -> Dict:
        """Analyze bug patterns for prompt engineering"""
        analysis = {
            'total_bugs': len(bugs),
            'states': {},
            'priorities': {},
            'severities': {},
            'common_keywords': {},
            'excel_features': {},
            'bug_categories': {}
        }
        
        for bug in bugs:
            # State analysis
            state = bug.get('state', 'Unknown')
            analysis['states'][state] = analysis['states'].get(state, 0) + 1
            
            # Priority analysis
            priority = bug.get('priority', 'Unknown')
            analysis['priorities'][priority] = analysis['priorities'].get(priority, 0) + 1
            
            # Severity analysis
            severity = bug.get('severity', 'Unknown')
            analysis['severities'][severity] = analysis['severities'].get(severity, 0) + 1
            
            # Keyword analysis
            title = bug.get('title', '').lower()
            description = bug.get('description', '').lower()
            combined_text = f"{title} {description}"
            
            # Common Excel-related keywords
            excel_keywords = [
                'save', 'save as', 'workbook', 'worksheet', 'cell', 'formula', 'function',
                'chart', 'pivot', 'filter', 'sort', 'format', 'style', 'copilot', 'dialog',
                'crash', 'freeze', 'hang', 'slow', 'performance', 'error', 'exception',
                'ui', 'interface', 'button', 'menu', 'ribbon', 'toolbar', 'shortcut'
            ]
            
            for keyword in excel_keywords:
                if keyword in combined_text:
                    analysis['common_keywords'][keyword] = analysis['common_keywords'].get(keyword, 0) + 1
            
            # Excel feature analysis
            excel_features = [
                'formulas', 'charts', 'pivot tables', 'conditional formatting', 'data validation',
                'macros', 'vba', 'add-ins', 'templates', 'themes', 'styles', 'copilot', 'ai'
            ]
            
            for feature in excel_features:
                if feature in combined_text:
                    analysis['excel_features'][feature] = analysis['excel_features'].get(feature, 0) + 1
        
        return analysis
    
    def generate_prompt_engineering_data(self, bugs: List[Dict]) -> Dict:
        """Generate data for prompt engineering"""
        analysis = self.analyze_bug_patterns(bugs)
        
        # Create categorized examples
        examples = {
            'save_issues': [],
            'ui_issues': [],
            'performance_issues': [],
            'copilot_issues': [],
            'data_entry_issues': [],
            'other_issues': []
        }
        
        for bug in bugs:
            title = bug.get('title', '').lower()
            description = bug.get('description', '').lower()
            combined_text = f"{title} {description}"
            
            if any(word in combined_text for word in ['save', 'save as', 'workbook']):
                examples['save_issues'].append(bug)
            elif any(word in combined_text for word in ['ui', 'interface', 'button', 'menu', 'dialog']):
                examples['ui_issues'].append(bug)
            elif any(word in combined_text for word in ['slow', 'performance', 'freeze', 'hang']):
                examples['performance_issues'].append(bug)
            elif any(word in combined_text for word in ['copilot', 'ai', 'assistant']):
                examples['copilot_issues'].append(bug)
            elif any(word in combined_text for word in ['cell', 'data', 'entry', 'input']):
                examples['data_entry_issues'].append(bug)
            else:
                examples['other_issues'].append(bug)
        
        return {
            'analysis': analysis,
            'examples': examples,
            'total_bugs': len(bugs),
            'generated_at': datetime.now().isoformat()
        }
    
    def save_analysis_data(self, data: Dict, output_file: str = "ado_bug_analysis.json"):
        """Save analysis data to JSON file"""
        try:
            with open(output_file, 'w', encoding='utf-8') as file:
                json.dump(data, file, indent=2, ensure_ascii=False)
            print(f"✅ Analysis data saved to: {output_file}")
        except Exception as e:
            print(f"❌ Error saving analysis data: {e}")
    
    def create_prompt_templates(self, analysis_data: Dict) -> Dict:
        """Create prompt templates based on bug analysis"""
        templates = {
            'general_bug_detection': {
                'description': 'General bug detection prompt for Excel scenarios',
                'template': f"""Based on analysis of {analysis_data['total_bugs']} historical Excel bugs, detect potential issues in the current scenario.

Common bug patterns to watch for:
- Save issues: {analysis_data['analysis']['common_keywords'].get('save', 0)} occurrences
- UI issues: {analysis_data['analysis']['common_keywords'].get('ui', 0)} occurrences  
- Performance issues: {analysis_data['analysis']['common_keywords'].get('performance', 0)} occurrences
- Copilot issues: {analysis_data['analysis']['common_keywords'].get('copilot', 0)} occurrences

Analyze the current Excel scenario and identify potential bugs based on these patterns."""
            },
            'save_specific': {
                'description': 'Save-specific bug detection prompt',
                'template': f"""Focus on save-related issues based on {len(analysis_data['examples']['save_issues'])} historical save bugs.

Common save issues:
- Save dialog not appearing
- Save confirmation failures
- File naming conflicts
- Auto-save issues
- Save location problems

Check for these specific issues in the current save operation."""
            },
            'ui_specific': {
                'description': 'UI-specific bug detection prompt', 
                'template': f"""Focus on UI-related issues based on {len(analysis_data['examples']['ui_issues'])} historical UI bugs.

Common UI issues:
- Dialog dismissal problems
- Button click failures
- Element not interactable
- Layout issues
- Responsiveness problems

Check for these specific UI issues in the current scenario."""
            }
        }
        
        return templates

def main():
    """Main function for testing ADO integration"""
    print("🔍 ADO Bug Data Integration Test")
    
    # Configuration - UPDATE THESE VALUES
    organization = "office"  # Your ADO organization
    project = "OC"          # Your ADO project
    personal_access_token = None  # Your Personal Access Token
    query_id = "6c1d07cd-a5d6-4483-9627-740d04b7fba8"  # Your query ID from ADO
    
    integrator = ADOBugDataIntegrator(organization, project, personal_access_token)
    
    # Option 1: Load from CSV (if you export from dashboard)
    csv_file = "excel_bugs_export.csv"
    if os.path.exists(csv_file):
        print("📁 Found CSV file, loading bug data...")
        bugs = integrator.load_csv_bug_data(csv_file)
        if bugs:
            analysis_data = integrator.generate_prompt_engineering_data(bugs)
            integrator.save_analysis_data(analysis_data)
            templates = integrator.create_prompt_templates(analysis_data)
            print("✅ Prompt engineering data generated successfully from CSV!")
    
    # Option 2: Fetch via API using query ID (recommended)
    elif personal_access_token:
        print("🔗 Fetching bug data via ADO API...")
        bugs = integrator.fetch_bugs_via_api(query_id=query_id)
        if bugs:
            analysis_data = integrator.generate_prompt_engineering_data(bugs)
            integrator.save_analysis_data(analysis_data)
            templates = integrator.create_prompt_templates(analysis_data)
            print("✅ Prompt engineering data generated successfully from API!")
        else:
            print("❌ No bugs found via API")
    
    # Option 3: Fetch via API using default Excel query
    elif personal_access_token:
        print("🔗 Fetching Excel bugs via default query...")
        bugs = integrator.fetch_bugs_via_api()
        if bugs:
            analysis_data = integrator.generate_prompt_engineering_data(bugs)
            integrator.save_analysis_data(analysis_data)
            templates = integrator.create_prompt_templates(analysis_data)
            print("✅ Prompt engineering data generated successfully from default query!")
        else:
            print("❌ No bugs found via default query")
    
    else:
        print("📋 To use this module:")
        print("1. Update the configuration values at the top of main():")
        print("   - organization = 'office'")
        print("   - project = 'OC'")
        print("   - personal_access_token = 'your_pat_here'")
        print("   - query_id = '6c1d07cd-a5d6-4483-9627-740d04b7fba8'")
        print("2. Or export bug data as CSV from your ADO dashboard")
        print("3. Save as 'excel_bugs_export.csv' in this directory")
        print("4. Run: python ado_bug_data_integration.py")

if __name__ == "__main__":
    main()
