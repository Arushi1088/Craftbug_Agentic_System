#!/usr/bin/env python3
"""
UX Designer Persona for Craft Bug Detection
Synthetic UX designer that identifies UX/design issues in Excel scenarios
"""

import json
from typing import Dict, List, Optional
from datetime import datetime

class UXDesignerPersona:
    """Synthetic UX Designer for Craft Bug Detection"""
    
    def __init__(self):
        self.persona = {
            "role": "Senior UX Designer",
            "expertise": ["Excel Web UX", "Microsoft Fluent Design", "User Interaction Design"],
            "responsibilities": [
                "Identify UX inconsistencies and design flaws",
                "Evaluate user interaction patterns",
                "Assess visual design compliance",
                "Detect accessibility issues",
                "Analyze user flow disruptions"
            ]
        }
        
        # Craft Bug Categories based on ADO data analysis
        self.craft_bug_categories = {
            "visual_inconsistencies": {
                "name": "Visual Inconsistencies",
                "description": "Issues with visual design, styling, and layout",
                "examples": [
                    "Outdated dialog design not following Fluent Design",
                    "Inconsistent color schemes",
                    "Poor spacing and alignment",
                    "Missing visual feedback",
                    "Inconsistent button styling"
                ],
                "severity_levels": {
                    "low": "Minor visual inconsistencies",
                    "medium": "Noticeable design flaws",
                    "high": "Major visual design issues",
                    "critical": "Severe visual problems affecting usability"
                }
            },
            "interaction_problems": {
                "name": "Interaction Problems",
                "description": "Issues with user interactions and element behavior",
                "examples": [
                    "Elements not interactable",
                    "Unexpected interaction responses",
                    "Missing hover states",
                    "Inconsistent click behaviors",
                    "Poor touch targets"
                ],
                "severity_levels": {
                    "low": "Minor interaction quirks",
                    "medium": "Noticeable interaction issues",
                    "high": "Significant interaction problems",
                    "critical": "Broken interactions affecting core functionality"
                }
            },
            "flow_disruptions": {
                "name": "Flow Disruptions",
                "description": "Issues that disrupt user workflow and task completion",
                "examples": [
                    "Dialog blocking interactions",
                    "Unexpected modal dialogs",
                    "Missing confirmation dialogs",
                    "Inconsistent navigation patterns",
                    "Workflow interruptions"
                ],
                "severity_levels": {
                    "low": "Minor flow inconveniences",
                    "medium": "Noticeable workflow disruptions",
                    "high": "Significant flow problems",
                    "critical": "Complete workflow breakdown"
                }
            },
            "performance_ux": {
                "name": "Performance UX Issues",
                "description": "Performance problems affecting user experience",
                "examples": [
                    "Slow response times",
                    "Unresponsive interfaces",
                    "Loading state issues",
                    "UI freezing during operations",
                    "Poor animation performance"
                ],
                "severity_levels": {
                    "low": "Minor performance delays",
                    "medium": "Noticeable performance issues",
                    "high": "Significant performance problems",
                    "critical": "Severe performance issues affecting usability"
                }
            },
            "accessibility_issues": {
                "name": "Accessibility Issues",
                "description": "Problems with accessibility and usability",
                "examples": [
                    "Missing tooltips",
                    "Poor keyboard navigation",
                    "Insufficient color contrast",
                    "Missing screen reader support",
                    "Unclear call-to-action buttons"
                ],
                "severity_levels": {
                    "low": "Minor accessibility issues",
                    "medium": "Noticeable accessibility problems",
                    "high": "Significant accessibility barriers",
                    "critical": "Severe accessibility violations"
                }
            }
        }
        
        # UX Heuristics for Excel Web
        self.ux_heuristics = {
            "consistency": "Interface elements should be consistent in appearance and behavior",
            "feedback": "Users should receive clear feedback for their actions",
            "efficiency": "Common tasks should be efficient and require minimal steps",
            "error_prevention": "Design should prevent errors and provide clear error recovery",
            "recognition": "Users should recognize interface elements rather than recall them",
            "aesthetic_integrity": "Visual design should be clean, modern, and professional",
            "help_and_documentation": "Help should be easily accessible and contextual"
        }
        
        # Expected vs Actual Behavior Patterns
        self.behavior_patterns = {
            "save_operation": {
                "expected": [
                    "Save button clearly visible and accessible",
                    "Clear visual feedback when save is initiated",
                    "Confirmation dialog appears when needed",
                    "Save completes without unexpected dialogs",
                    "User remains in context after save"
                ],
                "actual_issues": [
                    "Save dialog not appearing",
                    "Save confirmation failures",
                    "Unexpected error dialogs",
                    "Save operation blocks interface",
                    "User loses context after save"
                ]
            },
            "dialog_interaction": {
                "expected": [
                    "Dialog appears with clear purpose",
                    "Close button (X) clearly visible",
                    "Dialog dismisses cleanly",
                    "Background content remains accessible",
                    "Dialog follows Fluent Design principles"
                ],
                "actual_issues": [
                    "Dialog blocks underlying content",
                    "Close button not visible or accessible",
                    "Dialog doesn't dismiss properly",
                    "Unexpected dialog behavior",
                    "Dialog design inconsistent with Fluent Design"
                ]
            },
            "cell_interaction": {
                "expected": [
                    "Cells clearly indicate they are interactive",
                    "Clicking cells provides immediate feedback",
                    "Cell selection is visually clear",
                    "Data entry is straightforward",
                    "Cell interactions are responsive"
                ],
                "actual_issues": [
                    "Cells appear non-interactive",
                    "Clicking cells provides no feedback",
                    "Cell selection not visually clear",
                    "Data entry is confusing or blocked",
                    "Cell interactions are slow or unresponsive"
                ]
            }
        }
    
    def get_ux_analysis_prompt(self, scenario_step: str, current_state: Dict) -> str:
        """Generate UX analysis prompt for a specific scenario step"""
        return f"""You are a Senior UX Designer specializing in Excel Web and Microsoft Fluent Design. 

**Your Role**: Analyze the current Excel Web scenario step for Craft bugs - UX/design issues that affect user experience.

**Current Scenario Step**: {scenario_step}

**Current State**: {json.dumps(current_state, indent=2)}

**Craft Bug Categories to Check**:
1. **Visual Inconsistencies**: Design flaws, styling issues, layout problems
2. **Interaction Problems**: Element behavior, click responses, hover states
3. **Flow Disruptions**: Workflow interruptions, unexpected dialogs
4. **Performance UX**: Slow responses, unresponsive interfaces
5. **Accessibility Issues**: Missing tooltips, poor navigation, unclear CTAs

**UX Heuristics to Evaluate**:
- Consistency: Are elements consistent in appearance and behavior?
- Feedback: Do users receive clear feedback for their actions?
- Efficiency: Are tasks efficient and require minimal steps?
- Error Prevention: Does the design prevent errors and provide recovery?
- Recognition: Can users recognize interface elements easily?
- Aesthetic Integrity: Is the visual design clean and professional?

**Analysis Instructions**:
1. Examine the current state for any Craft bugs
2. Categorize issues by type and severity
3. Provide specific UX improvement recommendations
4. Use UX designer language and terminology
5. Reference Microsoft Fluent Design principles where applicable

**Output Format**:
- Craft Bug Type: [category]
- Severity: [low/medium/high/critical]
- Description: [detailed UX issue description]
- Impact: [how this affects user experience]
- Recommendation: [specific UX improvement suggestion]
- Fluent Design Compliance: [yes/no with explanation]

Analyze the current state and identify any Craft bugs that would affect user experience."""

    def analyze_ux_issue(self, issue_data: Dict) -> Dict:
        """Analyze a specific UX issue and categorize it"""
        analysis = {
            "craft_bug_type": None,
            "severity": "low",
            "description": "",
            "impact": "",
            "recommendation": "",
            "fluent_design_compliant": True,
            "detected_at": datetime.now().isoformat()
        }
        
        # Analyze based on issue characteristics
        issue_text = issue_data.get("description", "").lower()
        
        # Categorize by keywords and patterns
        if any(word in issue_text for word in ["dialog", "modal", "popup"]):
            analysis["craft_bug_type"] = "flow_disruptions"
        elif any(word in issue_text for word in ["button", "click", "interact"]):
            analysis["craft_bug_type"] = "interaction_problems"
        elif any(word in issue_text for word in ["color", "style", "design", "visual"]):
            analysis["craft_bug_type"] = "visual_inconsistencies"
        elif any(word in issue_text for word in ["slow", "freeze", "hang", "performance"]):
            analysis["craft_bug_type"] = "performance_ux"
        elif any(word in issue_text for word in ["tooltip", "accessibility", "keyboard"]):
            analysis["craft_bug_type"] = "accessibility_issues"
        
        # Determine severity based on impact
        if any(word in issue_text for word in ["critical", "broken", "fail", "error"]):
            analysis["severity"] = "critical"
        elif any(word in issue_text for word in ["major", "significant", "block"]):
            analysis["severity"] = "high"
        elif any(word in issue_text for word in ["noticeable", "problem", "issue"]):
            analysis["severity"] = "medium"
        
        return analysis
    
    def generate_craft_bug_report(self, issues: List[Dict]) -> Dict:
        """Generate a comprehensive Craft bug report"""
        report = {
            "report_type": "Craft Bug Analysis",
            "generated_by": "Synthetic UX Designer",
            "generated_at": datetime.now().isoformat(),
            "total_issues": len(issues),
            "summary": {
                "critical": len([i for i in issues if i.get("severity") == "critical"]),
                "high": len([i for i in issues if i.get("severity") == "high"]),
                "medium": len([i for i in issues if i.get("severity") == "medium"]),
                "low": len([i for i in issues if i.get("severity") == "low"])
            },
            "issues_by_category": {},
            "recommendations": [],
            "fluent_design_compliance": True
        }
        
        # Group issues by category
        for issue in issues:
            category = issue.get("craft_bug_type", "unknown")
            if category not in report["issues_by_category"]:
                report["issues_by_category"][category] = []
            report["issues_by_category"][category].append(issue)
        
        # Generate recommendations
        for category, category_issues in report["issues_by_category"].items():
            if category_issues:
                category_name = self.craft_bug_categories.get(category, {}).get("name", category)
                report["recommendations"].append({
                    "category": category_name,
                    "priority": "high" if any(i.get("severity") in ["critical", "high"] for i in category_issues) else "medium",
                    "action": f"Review and address {len(category_issues)} {category_name.lower()} issues"
                })
        
        return report

def main():
    """Test the UX Designer Persona"""
    print("🎨 UX Designer Persona Test")
    print("=" * 50)
    
    ux_designer = UXDesignerPersona()
    
    print(f"Role: {ux_designer.persona['role']}")
    print(f"Expertise: {', '.join(ux_designer.persona['expertise'])}")
    
    print(f"\n📋 Craft Bug Categories:")
    for category, details in ux_designer.craft_bug_categories.items():
        print(f"  {details['name']}: {details['description']}")
    
    print(f"\n🔍 UX Heuristics:")
    for heuristic, description in ux_designer.ux_heuristics.items():
        print(f"  {heuristic.replace('_', ' ').title()}: {description}")
    
    # Test UX analysis prompt
    test_scenario = "Click Save Button"
    test_state = {
        "current_action": "save_operation",
        "ui_elements": ["save_button", "dialog"],
        "visual_state": "dialog_visible",
        "interaction_state": "waiting_for_user_input"
    }
    
    prompt = ux_designer.get_ux_analysis_prompt(test_scenario, test_state)
    print(f"\n📝 Sample UX Analysis Prompt:")
    print(prompt[:200] + "...")
    
    print(f"\n✅ UX Designer Persona ready for Craft bug detection!")

if __name__ == "__main__":
    main()
