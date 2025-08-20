#!/usr/bin/env python3
"""
Excel UX Analyzer with Synthetic UX Designer
Integrates UX analysis with Excel scenario execution for Craft bug detection
"""

import asyncio
import json
import time
from typing import Dict, List, Optional
from datetime import datetime
from ux_designer_persona import UXDesignerPersona
from excel_document_creation_scenario_clean import ExcelDocumentCreationScenario

class ExcelUXAnalyzer:
    """Excel UX Analyzer with Synthetic UX Designer Integration"""
    
    def __init__(self):
        self.ux_designer = UXDesignerPersona()
        self.scenario_executor = ExcelDocumentCreationScenario()
        self.ux_analysis_results = []
        self.craft_bugs_detected = []
        
    async def execute_scenario_with_ux_analysis(self) -> Dict:
        """Execute Excel scenario with real-time UX analysis"""
        print("🎨 Starting Excel UX Analysis with Synthetic UX Designer")
        print("=" * 60)
        
        # Initialize scenario
        await self.scenario_executor.initialize()
        
        # Execute scenario with UX analysis hooks
        results = await self.scenario_executor.execute_scenario_with_ux_hooks(self.ux_analysis_callback)
        
        # Generate comprehensive UX report
        ux_report = self.generate_comprehensive_ux_report()
        
        return {
            "scenario_results": results,
            "ux_analysis": ux_report,
            "craft_bugs": self.craft_bugs_detected
        }
    
    async def ux_analysis_callback(self, step_name: str, step_data: Dict, screenshot_path: str = None) -> None:
        """UX analysis callback for each scenario step"""
        print(f"\n🎨 UX Analysis: {step_name}")
        
        # Create current state for UX analysis
        current_state = {
            "step_name": step_name,
            "step_data": step_data,
            "screenshot_path": screenshot_path,
            "timestamp": datetime.now().isoformat(),
            "ui_elements": self.extract_ui_elements(step_data),
            "interaction_state": self.analyze_interaction_state(step_data),
            "visual_state": self.analyze_visual_state(step_data, screenshot_path)
        }
        
        # Perform UX analysis
        ux_analysis = await self.perform_ux_analysis(step_name, current_state)
        
        # Store results
        self.ux_analysis_results.append({
            "step": step_name,
            "state": current_state,
            "analysis": ux_analysis,
            "timestamp": datetime.now().isoformat()
        })
        
        # Check for Craft bugs
        if ux_analysis.get("craft_bugs"):
            self.craft_bugs_detected.extend(ux_analysis["craft_bugs"])
            print(f"🚨 Craft bugs detected in {step_name}: {len(ux_analysis['craft_bugs'])} issues")
    
    def extract_ui_elements(self, step_data: Dict) -> List[str]:
        """Extract UI elements from step data"""
        ui_elements = []
        
        # Extract from step data
        if "elements_found" in step_data:
            ui_elements.extend(step_data["elements_found"])
        
        if "clicked_element" in step_data:
            ui_elements.append(step_data["clicked_element"])
        
        if "dialog_elements" in step_data:
            ui_elements.extend(step_data["dialog_elements"])
        
        return list(set(ui_elements))  # Remove duplicates
    
    def analyze_interaction_state(self, step_data: Dict) -> Dict:
        """Analyze interaction state from step data"""
        interaction_state = {
            "status": "unknown",
            "response_time": None,
            "interaction_successful": False,
            "error_occurred": False,
            "blocking_elements": []
        }
        
        # Analyze step success/failure
        if step_data.get("success", False):
            interaction_state["status"] = "successful"
            interaction_state["interaction_successful"] = True
        else:
            interaction_state["status"] = "failed"
            interaction_state["error_occurred"] = True
        
        # Check for blocking elements (dialogs, etc.)
        if "dialog_detected" in step_data and step_data["dialog_detected"]:
            interaction_state["blocking_elements"].append("dialog")
        
        # Check response time
        if "execution_time" in step_data:
            interaction_state["response_time"] = step_data["execution_time"]
        
        return interaction_state
    
    def analyze_visual_state(self, step_data: Dict, screenshot_path: str = None) -> Dict:
        """Analyze visual state from step data and screenshot"""
        visual_state = {
            "screenshot_available": screenshot_path is not None,
            "screenshot_path": screenshot_path,
            "visual_elements_detected": [],
            "layout_issues": [],
            "design_consistency": "unknown"
        }
        
        # Extract visual elements from step data
        if "visual_elements" in step_data:
            visual_state["visual_elements_detected"] = step_data["visual_elements"]
        
        # Check for layout issues
        if "layout_problems" in step_data:
            visual_state["layout_issues"] = step_data["layout_problems"]
        
        return visual_state
    
    async def perform_ux_analysis(self, step_name: str, current_state: Dict) -> Dict:
        """Perform UX analysis for a specific step"""
        analysis = {
            "step_name": step_name,
            "craft_bugs": [],
            "ux_score": 0,
            "recommendations": [],
            "fluent_design_compliance": True
        }
        
        # Generate UX analysis prompt
        prompt = self.ux_designer.get_ux_analysis_prompt(step_name, current_state)
        
        # For now, use rule-based analysis (can be enhanced with AI later)
        craft_bugs = self.rule_based_ux_analysis(step_name, current_state)
        analysis["craft_bugs"] = craft_bugs
        
        # Calculate UX score
        analysis["ux_score"] = self.calculate_ux_score(current_state, craft_bugs)
        
        # Generate recommendations
        analysis["recommendations"] = self.generate_ux_recommendations(craft_bugs)
        
        # Check Fluent Design compliance
        analysis["fluent_design_compliance"] = self.check_fluent_design_compliance(current_state)
        
        return analysis
    
    def rule_based_ux_analysis(self, step_name: str, current_state: Dict) -> List[Dict]:
        """Rule-based UX analysis for Craft bug detection"""
        craft_bugs = []
        
        # Check for common UX issues based on step type
        if "save" in step_name.lower():
            craft_bugs.extend(self.analyze_save_ux_issues(current_state))
        
        if "dialog" in step_name.lower() or "copilot" in step_name.lower():
            craft_bugs.extend(self.analyze_dialog_ux_issues(current_state))
        
        if "cell" in step_name.lower() or "data" in step_name.lower():
            craft_bugs.extend(self.analyze_cell_interaction_ux_issues(current_state))
        
        # Check for general UX issues
        craft_bugs.extend(self.analyze_general_ux_issues(current_state))
        
        return craft_bugs
    
    def analyze_save_ux_issues(self, current_state: Dict) -> List[Dict]:
        """Analyze save operation UX issues"""
        issues = []
        interaction_state = current_state.get("interaction_state", {})
        
        # Check for save dialog issues
        if interaction_state.get("blocking_elements"):
            issues.append({
                "craft_bug_type": "flow_disruptions",
                "severity": "medium",
                "description": "Save operation blocked by unexpected dialog",
                "impact": "User workflow interrupted during save operation",
                "recommendation": "Ensure save operations complete without unexpected dialogs",
                "fluent_design_compliant": False
            })
        
        # Check for save response time issues
        response_time = interaction_state.get("response_time")
        if response_time and response_time > 5.0:  # More than 5 seconds
            issues.append({
                "craft_bug_type": "performance_ux",
                "severity": "high",
                "description": f"Save operation took {response_time:.1f} seconds",
                "impact": "Slow save operation affects user productivity",
                "recommendation": "Optimize save operation performance",
                "fluent_design_compliant": True
            })
        
        return issues
    
    def analyze_dialog_ux_issues(self, current_state: Dict) -> List[Dict]:
        """Analyze dialog UX issues"""
        issues = []
        interaction_state = current_state.get("interaction_state", {})
        
        # Check for dialog blocking issues
        if interaction_state.get("blocking_elements"):
            issues.append({
                "craft_bug_type": "flow_disruptions",
                "severity": "high",
                "description": "Dialog blocking user interaction",
                "impact": "User cannot proceed with workflow due to blocking dialog",
                "recommendation": "Ensure dialogs can be dismissed and don't block essential interactions",
                "fluent_design_compliant": False
            })
        
        # Check for dialog interaction issues
        if not interaction_state.get("interaction_successful", False):
            issues.append({
                "craft_bug_type": "interaction_problems",
                "severity": "critical",
                "description": "Dialog interaction failed",
                "impact": "User cannot interact with dialog elements",
                "recommendation": "Fix dialog interaction issues and ensure proper element accessibility",
                "fluent_design_compliant": False
            })
        
        return issues
    
    def analyze_cell_interaction_ux_issues(self, current_state: Dict) -> List[Dict]:
        """Analyze cell interaction UX issues"""
        issues = []
        interaction_state = current_state.get("interaction_state", {})
        
        # Check for cell interaction issues
        if not interaction_state.get("interaction_successful", False):
            issues.append({
                "craft_bug_type": "interaction_problems",
                "severity": "high",
                "description": "Cell interaction failed",
                "impact": "User cannot interact with cells for data entry",
                "recommendation": "Ensure cells are properly interactive and provide clear feedback",
                "fluent_design_compliant": False
            })
        
        # Check for cell response time issues
        response_time = interaction_state.get("response_time")
        if response_time and response_time > 2.0:  # More than 2 seconds
            issues.append({
                "craft_bug_type": "performance_ux",
                "severity": "medium",
                "description": f"Cell interaction took {response_time:.1f} seconds",
                "impact": "Slow cell interaction affects data entry efficiency",
                "recommendation": "Optimize cell interaction responsiveness",
                "fluent_design_compliant": True
            })
        
        return issues
    
    def analyze_general_ux_issues(self, current_state: Dict) -> List[Dict]:
        """Analyze general UX issues"""
        issues = []
        interaction_state = current_state.get("interaction_state", {})
        
        # Check for general interaction failures
        if interaction_state.get("error_occurred", False):
            issues.append({
                "craft_bug_type": "interaction_problems",
                "severity": "high",
                "description": "General interaction error occurred",
                "impact": "User cannot complete intended action",
                "recommendation": "Investigate and fix interaction error",
                "fluent_design_compliant": False
            })
        
        return issues
    
    def calculate_ux_score(self, current_state: Dict, craft_bugs: List[Dict]) -> int:
        """Calculate UX score (0-100) based on current state and Craft bugs"""
        base_score = 100
        
        # Deduct points for Craft bugs
        for bug in craft_bugs:
            severity = bug.get("severity", "low")
            if severity == "critical":
                base_score -= 25
            elif severity == "high":
                base_score -= 15
            elif severity == "medium":
                base_score -= 10
            elif severity == "low":
                base_score -= 5
        
        # Deduct points for interaction failures
        interaction_state = current_state.get("interaction_state", {})
        if interaction_state.get("error_occurred", False):
            base_score -= 20
        
        if interaction_state.get("blocking_elements"):
            base_score -= 15
        
        # Ensure score doesn't go below 0
        return max(0, base_score)
    
    def generate_ux_recommendations(self, craft_bugs: List[Dict]) -> List[str]:
        """Generate UX recommendations based on Craft bugs"""
        recommendations = []
        
        for bug in craft_bugs:
            recommendations.append(bug.get("recommendation", ""))
        
        return recommendations
    
    def check_fluent_design_compliance(self, current_state: Dict) -> bool:
        """Check if current state complies with Fluent Design principles"""
        # For now, assume compliance unless Craft bugs indicate otherwise
        return True
    
    def generate_comprehensive_ux_report(self) -> Dict:
        """Generate comprehensive UX analysis report"""
        report = {
            "report_type": "Excel UX Analysis Report",
            "generated_by": "Synthetic UX Designer",
            "generated_at": datetime.now().isoformat(),
            "total_steps_analyzed": len(self.ux_analysis_results),
            "total_craft_bugs": len(self.craft_bugs_detected),
            "overall_ux_score": 0,
            "craft_bug_summary": {},
            "step_by_step_analysis": self.ux_analysis_results,
            "recommendations": []
        }
        
        # Calculate overall UX score
        if self.ux_analysis_results:
            total_score = sum(analysis.get("ux_score", 0) for analysis in self.ux_analysis_results)
            report["overall_ux_score"] = total_score / len(self.ux_analysis_results)
        
        # Generate Craft bug summary
        for bug in self.craft_bugs_detected:
            bug_type = bug.get("craft_bug_type", "unknown")
            if bug_type not in report["craft_bug_summary"]:
                report["craft_bug_summary"][bug_type] = 0
            report["craft_bug_summary"][bug_type] += 1
        
        # Generate overall recommendations
        report["recommendations"] = self.generate_overall_recommendations()
        
        return report
    
    def generate_overall_recommendations(self) -> List[str]:
        """Generate overall UX recommendations"""
        recommendations = []
        
        # Count Craft bugs by type
        bug_counts = {}
        for bug in self.craft_bugs_detected:
            bug_type = bug.get("craft_bug_type", "unknown")
            bug_counts[bug_type] = bug_counts.get(bug_type, 0) + 1
        
        # Generate recommendations based on bug patterns
        if bug_counts.get("flow_disruptions", 0) > 0:
            recommendations.append("Review and optimize user workflow to reduce flow disruptions")
        
        if bug_counts.get("interaction_problems", 0) > 0:
            recommendations.append("Improve element interactivity and user feedback mechanisms")
        
        if bug_counts.get("performance_ux", 0) > 0:
            recommendations.append("Optimize performance to improve user experience")
        
        if bug_counts.get("visual_inconsistencies", 0) > 0:
            recommendations.append("Ensure consistent visual design following Fluent Design principles")
        
        return recommendations

def main():
    """Test the Excel UX Analyzer"""
    print("🎨 Excel UX Analyzer Test")
    print("=" * 50)
    
    analyzer = ExcelUXAnalyzer()
    
    print("✅ Excel UX Analyzer initialized")
    print(f"📋 UX Designer Persona: {analyzer.ux_designer.persona['role']}")
    print(f"🔍 Craft Bug Categories: {len(analyzer.ux_designer.craft_bug_categories)}")
    
    print("\n🎯 Ready to execute Excel scenario with UX analysis!")
    print("Run: await analyzer.execute_scenario_with_ux_analysis()")

if __name__ == "__main__":
    main()
