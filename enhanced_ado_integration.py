#!/usr/bin/env python3
"""
Enhanced Azure DevOps Integration
================================

Fetches additional Craft bug examples from Office Visual Studio dashboard
for enhanced prompt engineering of the UX analyzer.
"""

import json
import os
import requests
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import base64

class EnhancedADOIntegration:
    """Enhanced ADO integration for fetching Craft bug examples"""
    
    def __init__(self, personal_access_token: Optional[str] = None):
        self.organization = "office"
        self.project = "OC"
        self.personal_access_token = personal_access_token or os.getenv('AZURE_DEVOPS_PAT')
        self.base_url = f"https://dev.azure.com/{self.organization}/{self.project}"
        self.headers = {}
        
        if self.personal_access_token:
            self.headers = {
                'Authorization': f'Basic {base64.b64encode(f":{self.personal_access_token}".encode()).decode()}',
                'Content-Type': 'application/json'
            }
            print("✅ ADO authentication configured")
        else:
            print("⚠️ No PAT provided - using fallback data")
    
    def fetch_craft_bugs_from_dashboard(self, days_back: int = 30) -> List[Dict]:
        """Fetch Craft bugs from the Office Visual Studio dashboard"""
        if not self.personal_access_token:
            print("❌ PAT required for dashboard access")
            return self._get_fallback_craft_bugs()
        
        try:
            # Query for recent Craft bugs
            date_filter = (datetime.now() - timedelta(days=days_back)).strftime("%Y-%m-%d")
            
            wiql_query = f"""
            SELECT [System.Id], [System.Title], [System.Description], [System.State], 
                   [System.CreatedBy], [System.CreatedDate], [System.Tags],
                   [Microsoft.VSTS.Common.Priority], [Microsoft.VSTS.Common.Severity],
                   [Microsoft.VSTS.TCM.ReproSteps], [System.AreaPath], [System.IterationPath],
                   [Microsoft.VSTS.Common.CustomFields.CraftBug], [Microsoft.VSTS.Common.CustomFields.UXIssue]
            FROM WorkItems 
            WHERE [System.WorkItemType] = 'Bug' 
              AND [System.TeamProject] = '{self.project}'
              AND [System.CreatedDate] >= '{date_filter}'
              AND (
                [System.Title] CONTAINS 'Craft' OR 
                [System.Title] CONTAINS 'UX' OR 
                [System.Title] CONTAINS 'Design' OR
                [System.Tags] CONTAINS 'Craft' OR
                [System.Tags] CONTAINS 'UX' OR
                [System.Tags] CONTAINS 'Design' OR
                [System.Description] CONTAINS 'Craft' OR
                [System.Description] CONTAINS 'UX' OR
                [System.Description] CONTAINS 'Design'
              )
            ORDER BY [System.CreatedDate] DESC
            """
            
            print(f"🔍 Fetching Craft bugs from last {days_back} days...")
            
            execute_url = f"{self.base_url}/_apis/wit/wiql?api-version=6.0"
            payload = {"query": wiql_query}
            
            response = requests.post(execute_url, headers=self.headers, json=payload)
            response.raise_for_status()
            
            work_items = response.json().get('workItems', [])
            print(f"📊 Found {len(work_items)} potential Craft bugs")
            
            # Fetch detailed information for each work item
            craft_bugs = []
            for work_item in work_items[:20]:  # Limit to 20 for performance
                bug_details = self._fetch_work_item_details(work_item['id'])
                if bug_details and self._is_craft_bug(bug_details):
                    craft_bugs.append(bug_details)
            
            print(f"✅ Retrieved {len(craft_bugs)} confirmed Craft bugs")
            return craft_bugs
            
        except Exception as e:
            print(f"❌ Error fetching from dashboard: {e}")
            return self._get_fallback_craft_bugs()
    
    def _fetch_work_item_details(self, work_item_id: int) -> Optional[Dict]:
        """Fetch detailed information for a specific work item"""
        try:
            url = f"{self.base_url}/_apis/wit/workItems/{work_item_id}?api-version=6.0"
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            
            work_item = response.json()
            
            # Extract relevant fields
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
                'iteration_path': fields.get('System.IterationPath', ''),
                'craft_bug_field': fields.get('Microsoft.VSTS.Common.CustomFields.CraftBug', ''),
                'ux_issue_field': fields.get('Microsoft.VSTS.Common.CustomFields.UXIssue', '')
            }
            
        except Exception as e:
            print(f"❌ Error fetching work item {work_item_id}: {e}")
            return None
    
    def _is_craft_bug(self, bug_data: Dict) -> bool:
        """Determine if a bug is a Craft bug based on content analysis"""
        title = bug_data.get('title', '').lower()
        description = bug_data.get('description', '').lower()
        tags = bug_data.get('tags', '').lower()
        
        # Craft bug indicators
        craft_indicators = [
            'craft', 'ux', 'design', 'visual', 'alignment', 'spacing',
            'color', 'typography', 'interaction', 'animation', 'smooth',
            'polish', 'refinement', 'consistency', 'inconsistency',
            'looks off', 'feels wrong', 'user experience', 'usability'
        ]
        
        # Check if any indicators are present
        for indicator in craft_indicators:
            if (indicator in title or 
                indicator in description or 
                indicator in tags):
                return True
        
        return False
    
    def _get_fallback_craft_bugs(self) -> List[Dict]:
        """Fallback Craft bug examples when API access is not available"""
        return [
            {
                'id': 'CRAFT-001',
                'title': 'Excel Ribbon Button Alignment Inconsistency',
                'description': 'The "Save" button in the ribbon appears slightly misaligned compared to other buttons. Visual inconsistency creates a jarring experience.',
                'state': 'Active',
                'severity': 'Medium',
                'tags': 'Craft, Visual, Alignment, Ribbon',
                'craft_bug_type': 'Visual Inconsistency',
                'surface_level': 'L1',
                'user_impact': 'Medium'
            },
            {
                'id': 'CRAFT-002', 
                'title': 'Copilot Dialog Animation Stutter',
                'description': 'When dismissing the Copilot dialog, the animation stutters and doesn\'t feel smooth. Breaks the polished user experience.',
                'state': 'Active',
                'severity': 'Low',
                'tags': 'Craft, Animation, Performance, Copilot',
                'craft_bug_type': 'Performance UX',
                'surface_level': 'L2',
                'user_impact': 'Low'
            },
            {
                'id': 'CRAFT-003',
                'title': 'Cell Selection Color Mismatch',
                'description': 'Selected cell color doesn\'t match the design system color palette. Uses #0078d4 instead of the correct #106ebe.',
                'state': 'Active', 
                'severity': 'Medium',
                'tags': 'Craft, Color, Design System, Cells',
                'craft_bug_type': 'Design System Violation',
                'surface_level': 'L1',
                'user_impact': 'Medium'
            },
            {
                'id': 'CRAFT-004',
                'title': 'Save Dialog Typography Inconsistency',
                'description': 'Font size in save dialog is 16px instead of the standard 14px. Breaks typography hierarchy.',
                'state': 'Active',
                'severity': 'Low', 
                'tags': 'Craft, Typography, Dialog, Save',
                'craft_bug_type': 'Typography Inconsistency',
                'surface_level': 'L2',
                'user_impact': 'Low'
            },
            {
                'id': 'CRAFT-005',
                'title': 'Tooltip Shadow Elevation Wrong',
                'description': 'Tooltip uses L2 shadow instead of L3 shadow. Incorrect surface elevation creates visual confusion.',
                'state': 'Active',
                'severity': 'Low',
                'tags': 'Craft, Shadow, Elevation, Tooltip',
                'craft_bug_type': 'Surface Level Violation', 
                'surface_level': 'L3',
                'user_impact': 'Low'
            },
            {
                'id': 'CRAFT-006',
                'title': 'Icon Spacing Inconsistent in Format Panel',
                'description': 'Icons in format panel have inconsistent spacing - some are 8px apart, others are 12px. Visual rhythm is broken.',
                'state': 'Active',
                'severity': 'Medium',
                'tags': 'Craft, Spacing, Icons, Panel',
                'craft_bug_type': 'Spacing Inconsistency',
                'surface_level': 'L2', 
                'user_impact': 'Medium'
            },
            {
                'id': 'CRAFT-007',
                'title': 'Dropdown Border Radius Mismatch',
                'description': 'Chart type dropdown uses 8px border radius instead of standard 4px. Inconsistent with design system.',
                'state': 'Active',
                'severity': 'Low',
                'tags': 'Craft, Border Radius, Dropdown, Charts',
                'craft_bug_type': 'Design System Violation',
                'surface_level': 'L3',
                'user_impact': 'Low'
            },
            {
                'id': 'CRAFT-008',
                'title': 'Loading State Animation Too Fast',
                'description': 'Loading spinner animation is 200ms instead of standard 400ms. Feels rushed and unpolished.',
                'state': 'Active',
                'severity': 'Low',
                'tags': 'Craft, Animation, Loading, Performance',
                'craft_bug_type': 'Animation Timing Issue',
                'surface_level': 'L2',
                'user_impact': 'Low'
            },
            {
                'id': 'CRAFT-009',
                'title': 'Button Hover State Color Wrong',
                'description': 'Primary button hover state uses #106ebe instead of correct #005a9e. Color transition feels off.',
                'state': 'Active',
                'severity': 'Medium',
                'tags': 'Craft, Color, Button, Hover',
                'craft_bug_type': 'Interaction State Issue',
                'surface_level': 'L1',
                'user_impact': 'Medium'
            },
            {
                'id': 'CRAFT-010',
                'title': 'Panel Padding Inconsistent',
                'description': 'Format panel uses 20px padding while other panels use 16px. Inconsistent spacing creates visual disharmony.',
                'state': 'Active',
                'severity': 'Medium',
                'tags': 'Craft, Padding, Panel, Consistency',
                'craft_bug_type': 'Spacing Inconsistency',
                'surface_level': 'L2',
                'user_impact': 'Medium'
            }
        ]
    
    def analyze_craft_bug_patterns(self, craft_bugs: List[Dict]) -> Dict:
        """Analyze patterns in Craft bugs for prompt engineering insights"""
        analysis = {
            'total_bugs': len(craft_bugs),
            'bug_types': {},
            'surface_levels': {},
            'severity_distribution': {},
            'common_keywords': {},
            'user_impact': {}
        }
        
        for bug in craft_bugs:
            # Bug type analysis
            bug_type = bug.get('craft_bug_type', 'Unknown')
            analysis['bug_types'][bug_type] = analysis['bug_types'].get(bug_type, 0) + 1
            
            # Surface level analysis
            surface_level = bug.get('surface_level', 'Unknown')
            analysis['surface_levels'][surface_level] = analysis['surface_levels'].get(surface_level, 0) + 1
            
            # Severity analysis
            severity = bug.get('severity', 'Unknown')
            analysis['severity_distribution'][severity] = analysis['severity_distribution'].get(severity, 0) + 1
            
            # User impact analysis
            user_impact = bug.get('user_impact', 'Unknown')
            analysis['user_impact'][user_impact] = analysis['user_impact'].get(user_impact, 0) + 1
            
            # Keyword analysis
            title = bug.get('title', '').lower()
            description = bug.get('description', '').lower()
            tags = bug.get('tags', '').lower()
            
            all_text = f"{title} {description} {tags}"
            words = all_text.split()
            for word in words:
                if len(word) > 3:  # Skip short words
                    analysis['common_keywords'][word] = analysis['common_keywords'].get(word, 0) + 1
        
        return analysis
    
    def generate_prompt_engineering_insights(self, analysis: Dict) -> Dict:
        """Generate insights for prompt engineering based on Craft bug analysis"""
        insights = {
            'detection_priorities': [],
            'surface_level_focus': [],
            'common_patterns': [],
            'prompt_enhancements': []
        }
        
        # Detection priorities based on frequency
        bug_types = sorted(analysis['bug_types'].items(), key=lambda x: x[1], reverse=True)
        insights['detection_priorities'] = [bug_type for bug_type, count in bug_types[:5]]
        
        # Surface level focus
        surface_levels = sorted(analysis['surface_levels'].items(), key=lambda x: x[1], reverse=True)
        insights['surface_level_focus'] = [level for level, count in surface_levels]
        
        # Common patterns
        keywords = sorted(analysis['common_keywords'].items(), key=lambda x: x[1], reverse=True)
        insights['common_patterns'] = [keyword for keyword, count in keywords[:10]]
        
        # Prompt enhancements
        insights['prompt_enhancements'] = [
            f"Focus on {', '.join(insights['detection_priorities'])} detection",
            f"Prioritize {', '.join(insights['surface_level_focus'])} surface analysis",
            f"Look for patterns: {', '.join(insights['common_patterns'][:5])}",
            "Check design system compliance for colors, spacing, typography",
            "Validate surface level hierarchy (L1/L2/L3)",
            "Assess animation smoothness and timing",
            "Verify interaction state consistency"
        ]
        
        return insights
    
    def save_craft_bugs_to_file(self, craft_bugs: List[Dict], filename: str = None) -> str:
        """Save Craft bugs to JSON file for analysis"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"craft_bugs_{timestamp}.json"
        
        filepath = f"ado_data/{filename}"
        os.makedirs("ado_data", exist_ok=True)
        
        with open(filepath, 'w') as f:
            json.dump(craft_bugs, f, indent=2, default=str)
        
        print(f"✅ Saved {len(craft_bugs)} Craft bugs to {filepath}")
        return filepath

# Test the enhanced integration
if __name__ == "__main__":
    ado_integration = EnhancedADOIntegration()
    
    # Fetch Craft bugs
    print("🔍 Fetching Craft bugs from ADO...")
    craft_bugs = ado_integration.fetch_craft_bugs_from_dashboard(days_back=30)
    
    # Analyze patterns
    print("📊 Analyzing Craft bug patterns...")
    analysis = ado_integration.analyze_craft_bug_patterns(craft_bugs)
    
    # Generate insights
    print("💡 Generating prompt engineering insights...")
    insights = ado_integration.generate_prompt_engineering_insights(analysis)
    
    # Save results
    filepath = ado_integration.save_craft_bugs_to_file(craft_bugs)
    
    # Print summary
    print(f"\n📋 Summary:")
    print(f"   Total Craft bugs: {analysis['total_bugs']}")
    print(f"   Top bug types: {', '.join(insights['detection_priorities'])}")
    print(f"   Surface focus: {', '.join(insights['surface_level_focus'])}")
    print(f"   Common patterns: {', '.join(insights['common_patterns'][:5])}")
    print(f"   Saved to: {filepath}")
