#!/usr/bin/env python3
"""
Fast Azure DevOps Integration
Uses the initial query results directly without individual API calls
"""

import subprocess
import json
import os
from typing import List, Dict, Optional
from datetime import datetime

class FastADOIntegrator:
    """Fast ADO integration using query results directly"""
    
    def __init__(self, organization: str, project: str):
        self.organization = organization
        self.project = project
    
    def fetch_bugs_fast(self, query_id: str = None, max_results: int = 50) -> List[Dict]:
        """Fetch bugs quickly using the query results directly"""
        try:
            print(f"🚀 Fast bug fetching (max: {max_results})...")
            
            if query_id:
                # Use specific query
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
                
                # Convert to our format directly from the query results
                bugs = []
                for i, work_item in enumerate(work_items[:max_results]):
                    print(f"📋 Processing work item {i+1}/{min(len(work_items), max_results)}...")
                    
                    bug_details = self.extract_bug_details(work_item)
                    if bug_details:
                        bugs.append(bug_details)
                
                return bugs
            else:
                print(f"❌ Failed to fetch work items: {result.stderr}")
                return []
                
        except Exception as e:
            print(f"❌ Error fetching bugs: {e}")
            return []
    
    def extract_bug_details(self, work_item: Dict) -> Optional[Dict]:
        """Extract bug details from work item data"""
        try:
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
            print(f"❌ Error extracting bug details: {e}")
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
    
    def save_analysis_data(self, data: Dict, output_file: str = "ado_bugs_fast_analysis.json"):
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
            },
            'copilot_specific': {
                'description': 'Copilot-specific bug detection prompt',
                'template': f"""Focus on Copilot/AI-related issues based on {len(analysis_data['examples']['copilot_issues'])} historical Copilot bugs.

Common Copilot issues:
- Dialog blocking interactions
- Response quality problems
- Performance issues
- Context awareness problems
- UI/UX inconsistencies

Check for these specific Copilot issues in the current scenario."""
            }
        }
        
        return templates

def main():
    """Main function for fast ADO integration"""
    print("🚀 Fast Azure DevOps Integration")
    print("=" * 50)
    
    # Configuration
    organization = "office"
    project = "OC"
    query_id = "6c1d07cd-a5d6-4483-9627-740d04b7fba8"
    
    integrator = FastADOIntegrator(organization, project)
    
    # Fetch bugs quickly
    print(f"🔍 Fetching bugs from {organization}/{project}...")
    bugs = integrator.fetch_bugs_fast(query_id=query_id, max_results=30)
    
    if bugs:
        print(f"\n✅ Successfully fetched {len(bugs)} bugs!")
        
        # Generate analysis
        analysis_data = integrator.generate_prompt_engineering_data(bugs)
        integrator.save_analysis_data(analysis_data)
        
        # Create prompt templates
        templates = integrator.create_prompt_templates(analysis_data)
        
        # Save templates
        with open("prompt_templates.json", 'w', encoding='utf-8') as f:
            json.dump(templates, f, indent=2, ensure_ascii=False)
        
        print(f"📁 Prompt templates saved to: prompt_templates.json")
        
        # Show summary
        print(f"\n📊 Analysis Summary:")
        print(f"Total bugs: {analysis_data['total_bugs']}")
        print(f"States: {analysis_data['analysis']['states']}")
        print(f"Top keywords: {dict(sorted(analysis_data['analysis']['common_keywords'].items(), key=lambda x: x[1], reverse=True)[:5])}")
        
        print(f"\n📝 Bug Categories:")
        for category, bugs_list in analysis_data['examples'].items():
            print(f"  {category}: {len(bugs_list)} bugs")
        
        print(f"\n🎉 Fast integration successful! You can now use this data for prompt engineering.")
        
    else:
        print("❌ No bugs found or integration failed")

if __name__ == "__main__":
    main()
