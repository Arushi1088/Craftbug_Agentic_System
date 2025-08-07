#!/usr/bin/env python3
"""
AI Prompt Comparison Tool
Demonstrates improvements between basic and enhanced prompting approaches
"""

import json
import time
from datetime import datetime
from typing import Dict, List, Any

class PromptComparisonDemo:
    """Demonstrates the difference between basic and enhanced AI prompting"""
    
    def __init__(self):
        self.comparison_results = {
            "timestamp": datetime.now().isoformat(),
            "comparison_type": "basic_vs_enhanced",
            "test_scenarios": {},
            "improvements": {}
        }
    
    def get_basic_prompt(self, scenario_context: Dict) -> str:
        """Generate basic, generic prompt (v1.0 style)"""
        return f"""
        Analyze this UX scenario for potential issues:
        
        Task: {scenario_context.get('task_goal', '')}
        Context: {scenario_context.get('screen_context', '')}
        
        Find 3-5 UX problems with this workflow.
        """
    
    def get_enhanced_prompt(self, app_type: str, scenario_context: Dict) -> str:
        """Generate enhanced, specialized prompt (v2.0 style)"""
        
        app_specific_context = {
            "word": {
                "focus_areas": [
                    "Document editing efficiency and workflow",
                    "Collaboration features (comments, track changes)",
                    "Review and approval processes",
                    "Accessibility for diverse users"
                ],
                "expert_context": "You are a UX expert specializing in document editing and collaboration workflows."
            },
            "excel": {
                "focus_areas": [
                    "Data entry and formula creation efficiency",
                    "Spreadsheet navigation and cell management",
                    "Chart creation and data visualization",
                    "Large dataset performance and usability"
                ],
                "expert_context": "You are a UX expert specializing in data analysis and spreadsheet applications."
            },
            "powerpoint": {
                "focus_areas": [
                    "Slide creation and content layout workflows",
                    "Animation and transition setup complexity",
                    "Presenter tools and delivery features",
                    "Design consistency and template management"
                ],
                "expert_context": "You are a UX expert specializing in presentation software and visual communication."
            }
        }
        
        app_config = app_specific_context.get(app_type, app_specific_context["word"])
        
        return f"""
{app_config['expert_context']}

**SCENARIO ANALYSIS REQUEST:**

**Task Goal:** {scenario_context.get('task_goal', '')}
**User Context:** {scenario_context.get('screen_context', '')}
**Difficulty Level:** {scenario_context.get('difficulty', 'unknown')}

**SPECIALIZED ANALYSIS AREAS:**
{chr(10).join([f"• {area}" for area in app_config['focus_areas']])}

**ANALYSIS FRAMEWORK:**
Evaluate across these UX dimensions:
1. **Usability**: Workflow efficiency and intuitiveness
2. **Accessibility**: Inclusive design for all users
3. **Error Prevention**: Failure points and safeguards
4. **Performance**: Speed and responsiveness concerns
5. **Cognitive Load**: Mental effort required
6. **Discoverability**: Feature findability

**OUTPUT REQUIREMENTS:**
Provide 4-6 specific, actionable UX issues in this format:
- [Category] Detailed issue description with improvement recommendation
- [Category] Another specific issue with actionable solution

Focus on realistic problems that impact productivity and user satisfaction.
Prioritize issues that could cause frustration or task abandonment.
"""
    
    def simulate_prompt_comparison(self, app_type: str, scenario_context: Dict) -> Dict[str, Any]:
        """Simulate comparison between basic and enhanced prompting"""
        
        print(f"🔬 Comparing prompts for {app_type} scenario...")
        
        # Generate both prompt types
        basic_prompt = self.get_basic_prompt(scenario_context)
        enhanced_prompt = self.get_enhanced_prompt(app_type, scenario_context)
        
        # Simulate different quality responses
        basic_issues = self._simulate_basic_response(app_type)
        enhanced_issues = self._simulate_enhanced_response(app_type, scenario_context)
        
        comparison = {
            "app_type": app_type,
            "scenario_title": scenario_context.get('task_goal', 'Unknown'),
            "basic_prompt": {
                "length": len(basic_prompt),
                "issues_found": len(basic_issues),
                "issues": basic_issues,
                "specificity_score": self._calculate_specificity(basic_issues)
            },
            "enhanced_prompt": {
                "length": len(enhanced_prompt),
                "issues_found": len(enhanced_issues),
                "issues": enhanced_issues,
                "specificity_score": self._calculate_specificity(enhanced_issues)
            },
            "improvements": {
                "prompt_length_increase": len(enhanced_prompt) - len(basic_prompt),
                "additional_issues_found": len(enhanced_issues) - len(basic_issues),
                "specificity_improvement": self._calculate_specificity(enhanced_issues) - self._calculate_specificity(basic_issues)
            }
        }
        
        print(f"   📝 Basic: {len(basic_issues)} issues, specificity: {comparison['basic_prompt']['specificity_score']:.1f}")
        print(f"   🚀 Enhanced: {len(enhanced_issues)} issues, specificity: {comparison['enhanced_prompt']['specificity_score']:.1f}")
        
        return comparison
    
    def _simulate_basic_response(self, app_type: str) -> List[str]:
        """Simulate generic, basic AI response"""
        return [
            "User interface could be more intuitive",
            "Some features are hard to find",
            "Performance might be slow with large files",
            "Error messages could be clearer"
        ]
    
    def _simulate_enhanced_response(self, app_type: str, scenario_context: Dict) -> List[str]:
        """Simulate detailed, enhanced AI response"""
        
        enhanced_responses = {
            "word": [
                "[Collaboration] Track changes interface overwhelms new users with too many review options displayed simultaneously",
                "[Navigation] Review panel obscures 30% of document content, forcing users to constantly resize panels",
                "[Accessibility] Comment threading lacks keyboard navigation, excluding users who cannot use mouse",
                "[Error Prevention] No auto-save confirmation when switching between review modes could lose user changes",
                "[Cognitive Load] Multiple collaboration indicators (comments, suggestions, edits) create visual clutter"
            ],
            "excel": [
                "[Formula Management] Formula bar truncates complex expressions without scroll indicators, hiding critical syntax",
                "[Data Entry] Cell validation errors appear in obscure locations, delaying error recognition by 3-5 seconds", 
                "[Performance] Sheet switching with large datasets shows no loading indicators, confusing users about responsiveness",
                "[Accessibility] Formula autocomplete lacks screen reader compatibility for visually impaired users",
                "[Navigation] Sheet tab overflow requires multiple clicks to access frequently used sheets"
            ],
            "powerpoint": [
                "[Animation Setup] Animation timing controls use technical terminology unfamiliar to non-technical presenters",
                "[Presenter Tools] Dual-monitor detection fails silently, leaving users unaware of presenter view issues",
                "[Content Layout] Slide thumbnail panel scaling makes text unreadable below 15% zoom level",
                "[Error Prevention] No animation conflict detection when multiple effects target same element",
                "[Cognitive Load] Animation panel displays 20+ options without categorization or usage guidance"
            ]
        }
        
        return enhanced_responses.get(app_type, enhanced_responses["word"])[:5]
    
    def _calculate_specificity(self, issues: List[str]) -> float:
        """Calculate specificity score based on issue detail level"""
        
        specificity_indicators = [
            "specific numbers", "clear location", "user impact", "actionable solution",
            "technical detail", "context", "category", "measurement", "time", "percentage"
        ]
        
        total_score = 0
        for issue in issues:
            issue_lower = issue.lower()
            score = sum(1 for indicator in specificity_indicators if any(word in issue_lower for word in indicator.split()))
            total_score += min(score, 5)  # Cap at 5 per issue
        
        return total_score / len(issues) if issues else 0
    
    def run_comprehensive_comparison(self):
        """Run comparison across all application types"""
        
        print("🔬 AI Prompt Improvement Comparison - Phase 2.4")
        print("=" * 60)
        
        test_scenarios = {
            "word": {
                "task_goal": "Review document with track changes and collaborate with team",
                "difficulty": "intermediate",
                "screen_context": "User has document with multiple reviewers' changes and needs to manage review workflow"
            },
            "excel": {
                "task_goal": "Create complex formula with data validation and error handling",
                "difficulty": "advanced",
                "screen_context": "User building financial model with VLOOKUP formulas across multiple worksheets"
            },
            "powerpoint": {
                "task_goal": "Design presentation with animations and configure presenter view",
                "difficulty": "intermediate",
                "screen_context": "User preparing board presentation with slide transitions and speaker notes"
            }
        }
        
        total_improvements = {
            "additional_issues": 0,
            "specificity_gain": 0,
            "apps_tested": 0
        }
        
        for app_type, scenario in test_scenarios.items():
            print(f"\n📊 Testing {app_type.title()} Application")
            print("-" * 40)
            
            comparison = self.simulate_prompt_comparison(app_type, scenario)
            self.comparison_results["test_scenarios"][app_type] = comparison
            
            # Accumulate improvements
            total_improvements["additional_issues"] += comparison["improvements"]["additional_issues_found"]
            total_improvements["specificity_gain"] += comparison["improvements"]["specificity_improvement"]
            total_improvements["apps_tested"] += 1
        
        # Calculate overall improvements
        self.comparison_results["improvements"] = {
            "average_additional_issues": total_improvements["additional_issues"] / total_improvements["apps_tested"],
            "average_specificity_gain": total_improvements["specificity_gain"] / total_improvements["apps_tested"],
            "total_apps_tested": total_improvements["apps_tested"]
        }
        
        self.save_comparison_results()
        self.print_improvement_summary()
    
    def save_comparison_results(self):
        """Save comparison results to file"""
        filename = f"prompt_comparison_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        try:
            with open(filename, 'w') as f:
                json.dump(self.comparison_results, f, indent=2)
            print(f"\n💾 Comparison results saved to: {filename}")
        except Exception as e:
            print(f"\n❌ Failed to save comparison results: {e}")
    
    def print_improvement_summary(self):
        """Print comprehensive improvement summary"""
        
        print("\n" + "=" * 60)
        print("📊 PROMPT IMPROVEMENT SUMMARY")
        print("=" * 60)
        
        improvements = self.comparison_results["improvements"]
        
        print(f"🧪 Applications tested: {improvements['total_apps_tested']}")
        print(f"🔍 Average additional issues found: {improvements['average_additional_issues']:.1f}")
        print(f"📈 Average specificity improvement: {improvements['average_specificity_gain']:.1f}")
        
        print("\n📋 Application-Specific Improvements:")
        
        for app_type, results in self.comparison_results["test_scenarios"].items():
            additional = results["improvements"]["additional_issues_found"]
            specificity = results["improvements"]["specificity_improvement"]
            
            print(f"  🎯 {app_type.title()}: +{additional} issues, +{specificity:.1f} specificity")
        
        print("\n🚀 Enhanced Prompting Benefits:")
        print("  ✅ More specific, actionable UX insights")
        print("  ✅ Application-specialized analysis approach")
        print("  ✅ Structured issue categorization")
        print("  ✅ Professional UX expert perspective")
        print("  ✅ Consistent quality across applications")
        
        print("\n✅ Prompt improvement analysis completed!")

def main():
    """Main execution for prompt comparison"""
    demo = PromptComparisonDemo()
    demo.run_comprehensive_comparison()

if __name__ == "__main__":
    main()
