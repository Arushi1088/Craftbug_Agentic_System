#!/usr/bin/env python3
"""
Simple Excel UX Analyzer
Demonstrates the Synthetic UX Designer concept for Craft bug detection
"""

import asyncio
import json
from typing import Dict, List, Any
from datetime import datetime
from ux_designer_persona import UXDesignerPersona

class SimpleExcelUXAnalyzer:
    """Simple Excel UX Analyzer for Craft Bug Detection"""
    
    def __init__(self):
        self.ux_designer = UXDesignerPersona()
        self.craft_bugs_detected = []
        self.ux_analysis_results = []
    
    async def analyze_excel_scenario_ux(self, scenario_data: Dict) -> Dict:
        """Analyze Excel scenario UX using synthetic UX designer"""
        print("🎨 Simple Excel UX Analysis with Synthetic UX Designer")
        print("=" * 60)
        
        # Simulate scenario execution with UX analysis
        scenario_steps = [
            {
                "name": "Navigate to Excel Web",
                "action": "navigate",
                "success": True,
                "execution_time": 2.5,
                "elements_found": ["excel_web_interface", "login_button"],
                "ui_state": "authenticated"
            },
            {
                "name": "Click New Workbook",
                "action": "click",
                "success": True,
                "execution_time": 1.2,
                "clicked_element": "new_workbook_button",
                "ui_state": "workbook_creation_initiated"
            },
            {
                "name": "Wait for Excel to Launch",
                "action": "wait_and_switch_iframe",
                "success": True,
                "execution_time": 8.5,
                "elements_found": ["excel_iframe", "excel_canvas"],
                "ui_state": "excel_loaded"
            },
            {
                "name": "Dismiss Copilot Dialog",
                "action": "dismiss_copilot_dialog",
                "success": True,
                "execution_time": 3.1,
                "dialog_detected": True,
                "dialog_elements": ["copilot_dialog", "close_button"],
                "ui_state": "dialog_dismissed"
            },
            {
                "name": "Enter Sample Data",
                "action": "fill_any_input",
                "success": True,
                "execution_time": 4.2,
                "elements_found": ["excel_cells", "formula_bar"],
                "clicked_element": "active_cell",
                "ui_state": "data_entered"
            },
            {
                "name": "Click Save Button",
                "action": "click_save_button",
                "success": True,
                "execution_time": 6.8,
                "clicked_element": "save_button",
                "dialog_detected": True,
                "dialog_elements": ["save_dialog", "filename_input", "save_confirm_button"],
                "ui_state": "save_completed"
            }
        ]
        
        # Analyze each step
        for i, step in enumerate(scenario_steps, 1):
            print(f"\n📋 Step {i}: {step['name']}")
            
            # Create current state for UX analysis
            current_state = {
                "step_name": step["name"],
                "step_data": step,
                "timestamp": datetime.now().isoformat(),
                "ui_elements": step.get("elements_found", []),
                "interaction_state": self.analyze_interaction_state(step),
                "visual_state": self.analyze_visual_state(step)
            }
            
            # Perform UX analysis
            ux_analysis = await self.perform_ux_analysis(step["name"], current_state)
            
            # Store results
            self.ux_analysis_results.append({
                "step": step["name"],
                "state": current_state,
                "analysis": ux_analysis,
                "timestamp": datetime.now().isoformat()
            })
            
            # Check for Craft bugs
            if ux_analysis.get("craft_bugs"):
                self.craft_bugs_detected.extend(ux_analysis["craft_bugs"])
                print(f"🚨 Craft bugs detected in {step['name']}: {len(ux_analysis['craft_bugs'])} issues")
        
        # Generate comprehensive UX report
        ux_report = self.generate_comprehensive_ux_report()
        
        return {
            "scenario_results": {
                "steps_completed": len(scenario_steps),
                "total_steps": len(scenario_steps),
                "execution_time": sum(step["execution_time"] for step in scenario_steps),
                "success": True
            },
            "ux_analysis": ux_report,
            "craft_bugs": self.craft_bugs_detected
        }
    
    def analyze_interaction_state(self, step_data: Dict) -> Dict:
        """Analyze interaction state from step data"""
        interaction_state = {
            "status": "successful" if step_data.get("success", False) else "failed",
            "response_time": step_data.get("execution_time", 0),
            "interaction_successful": step_data.get("success", False),
            "error_occurred": not step_data.get("success", False),
            "blocking_elements": []
        }
        
        # Check for blocking elements (dialogs, etc.)
        if step_data.get("dialog_detected", False):
            interaction_state["blocking_elements"].append("dialog")
        
        return interaction_state
    
    def analyze_visual_state(self, step_data: Dict) -> Dict:
        """Analyze visual state from step data"""
        visual_state = {
            "screenshot_available": False,
            "visual_elements_detected": step_data.get("elements_found", []),
            "layout_issues": [],
            "design_consistency": "unknown"
        }
        
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
        
        # Rule-based UX analysis for Craft bug detection
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
        
        if "data" in step_name.lower() or "input" in step_name.lower():
            craft_bugs.extend(self.analyze_cell_interaction_ux_issues(current_state))
        
        # Check for general UX issues
        craft_bugs.extend(self.analyze_general_ux_issues(current_state))
        
        return craft_bugs
    
    def analyze_save_ux_issues(self, current_state: Dict) -> List[Dict]:
        """Analyze save operation UX issues"""
        issues = []
        interaction_state = current_state.get("interaction_state", {})
        
        # Check for save response time issues
        response_time = interaction_state.get("response_time", 0)
        if response_time > 5.0:  # More than 5 seconds
            issues.append({
                "craft_bug_type": "performance_ux",
                "severity": "high",
                "description": f"Save operation took {response_time:.1f} seconds",
                "impact": "Slow save operation affects user productivity",
                "recommendation": "Optimize save operation performance",
                "fluent_design_compliant": True
            })
        
        # Check for save dialog issues
        if interaction_state.get("blocking_elements"):
            issues.append({
                "craft_bug_type": "flow_disruptions",
                "severity": "medium",
                "description": "Save operation involves dialog interaction",
                "impact": "Additional steps required for save operation",
                "recommendation": "Consider auto-save or streamlined save flow",
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
                "severity": "medium",
                "description": "Dialog appears during workflow",
                "impact": "User workflow interrupted by dialog",
                "recommendation": "Ensure dialogs are dismissible and don't block essential interactions",
                "fluent_design_compliant": True
            })
        
        # Check for dialog response time issues
        response_time = interaction_state.get("response_time", 0)
        if response_time > 3.0:  # More than 3 seconds
            issues.append({
                "craft_bug_type": "performance_ux",
                "severity": "medium",
                "description": f"Dialog interaction took {response_time:.1f} seconds",
                "impact": "Slow dialog interaction affects user experience",
                "recommendation": "Optimize dialog interaction responsiveness",
                "fluent_design_compliant": True
            })
        
        return issues
    
    def analyze_cell_interaction_ux_issues(self, current_state: Dict) -> List[Dict]:
        """Analyze cell interaction UX issues"""
        issues = []
        interaction_state = current_state.get("interaction_state", {})
        
        # Check for cell interaction response time issues
        response_time = interaction_state.get("response_time", 0)
        if response_time > 2.0:  # More than 2 seconds
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

    async def analyze_scenario_with_telemetry(self, telemetry_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze scenario using telemetry data for comprehensive UX analysis with Craft bug detection"""
        print("🎨 Analyzing scenario with telemetry data...")
        
        # Initialize results
        results = {
            "scenario_name": telemetry_data.get("scenario_name", "Unknown"),
            "craft_bugs": [],
            "ux_score": 0,
            "recommendations": [],
            "performance_issues": [],
            "interaction_issues": [],
            "total_steps": len(telemetry_data.get("steps", [])),
            "execution_time": telemetry_data.get("total_duration_ms", 0) / 1000 if telemetry_data.get("total_duration_ms") else 0
        }
        
        # Analyze performance issues
        performance_issues = self._analyze_performance(telemetry_data)
        results["performance_issues"] = performance_issues
        
        # Analyze interaction issues
        interaction_issues = self._analyze_interactions(telemetry_data)
        results["interaction_issues"] = interaction_issues
        
        # Store telemetry data for step analysis
        self._current_telemetry_data = telemetry_data
        
        # Analyze each step with comprehensive Craft bug detection
        for step in telemetry_data.get("steps", []):
            step_bugs = await self._analyze_step_with_telemetry(step)
            results["craft_bugs"].extend(step_bugs)
        
        # Add scenario-level Craft bugs based on overall patterns
        scenario_bugs = self._analyze_scenario_level_issues(telemetry_data)
        results["craft_bugs"].extend(scenario_bugs)
        
        # Calculate overall UX score
        results["ux_score"] = self._calculate_ux_score(results["craft_bugs"])
        
        # Generate comprehensive recommendations
        results["recommendations"] = self._generate_recommendations(results["craft_bugs"])
        
        print(f"🎯 Craft bugs detected: {len(results['craft_bugs'])}")
        print(f"📊 UX Score: {results['ux_score']}/100")
        
        return results

    def _calculate_ux_score(self, craft_bugs: List[Dict[str, Any]]) -> float:
        """Calculate UX score based on craft bugs"""
        if not craft_bugs:
            return 100.0  # Perfect score if no bugs
        
        # Calculate score based on bug severity
        total_penalty = 0
        for bug in craft_bugs:
            severity = bug.get("severity", "low")
            if severity == "high":
                total_penalty += 20
            elif severity == "medium":
                total_penalty += 10
            elif severity == "low":
                total_penalty += 5
        
        # Cap penalty at 100
        total_penalty = min(total_penalty, 100)
        
        return max(0, 100 - total_penalty)

    def _generate_recommendations(self, craft_bugs: List[Dict[str, Any]]) -> List[str]:
        """Generate recommendations based on craft bugs"""
        recommendations = []
        
        for bug in craft_bugs:
            if "recommendation" in bug:
                recommendations.append(bug["recommendation"])
        
        return recommendations

    def _analyze_performance(self, telemetry_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Analyze performance issues from telemetry"""
        issues = []
        
        total_duration = telemetry_data.get("total_duration_ms", 0)
        if total_duration > 30000:  # 30 seconds threshold
            issues.append({
                "type": "performance",
                "title": "Slow Scenario Execution",
                "description": f"Scenario took {total_duration/1000:.1f} seconds to complete",
                "severity": "medium",
                "recommendation": "Optimize scenario steps to reduce execution time"
            })
        
        # Check individual step performance
        for step in telemetry_data.get("steps", []):
            duration = step.get("duration_ms", 0)
            if duration > 5000:  # 5 seconds per step threshold
                issues.append({
                    "type": "performance",
                    "title": f"Slow Step: {step.get('name', 'Unknown')}",
                    "description": f"Step took {duration/1000:.1f} seconds",
                    "severity": "low",
                    "recommendation": "Investigate step performance bottlenecks"
                })
        
        return issues

    def _analyze_interactions(self, telemetry_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Analyze interaction issues from telemetry"""
        issues = []
        
        for step in telemetry_data.get("steps", []):
            # Check for dialog issues
            if step.get("dialog_detected") and not step.get("interaction_successful"):
                issues.append({
                    "type": "interaction",
                    "title": f"Dialog Blocking: {step.get('name', 'Unknown')}",
                    "description": "Dialog detected but interaction failed",
                    "severity": "high",
                    "recommendation": "Ensure dialogs are properly dismissed before proceeding"
                })
            
            # Check for interaction failures
            if step.get("interaction_attempted") and not step.get("interaction_successful"):
                issues.append({
                    "type": "interaction",
                    "title": f"Interaction Failed: {step.get('name', 'Unknown')}",
                    "description": step.get("error_message", "Unknown error"),
                    "severity": "high",
                    "recommendation": "Review element selectors and interaction methods"
                })
        
        return issues

    async def _analyze_step_with_telemetry(self, step: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Analyze a single step with telemetry data using comprehensive Craft bug detection"""
        bugs = []
        step_name = step.get('name', 'Unknown')
        
        # Get screenshot path for this step if available
        screenshot_path = step.get('screenshot_path')
        if screenshot_path and screenshot_path.startswith('screenshots/'):
            screenshot_path = f"/{screenshot_path}"
        
        # 1. FLOW DISRUPTIONS - Based on ADO Craft bug patterns
        if not step.get("success"):
            bugs.append({
                "category": "flow_disruptions",
                "title": f"Workflow Breakdown: {step_name}",
                "description": f"Step '{step_name}' failed, disrupting user workflow. Error: {step.get('error_message', 'Unknown error')}",
                "severity": "high",
                "step_name": step_name,
                "recommendation": "Implement robust error handling and fallback mechanisms for this step"
            })
        
        # 2. INTERACTION PROBLEMS - Based on ADO Craft bug patterns
        if step.get("dialog_detected"):
            dialog_type = step.get('dialog_type', 'unknown')
            
            # For Copilot dialog bugs, try to find the Copilot dialog screenshot
            bug_screenshot_path = None
            if dialog_type.lower() == 'copilot':
                # Look for Copilot dialog screenshot in the step's screenshot or related screenshots
                if screenshot_path and 'copilot_dialog' in screenshot_path:
                    bug_screenshot_path = screenshot_path
                else:
                    # Try to find Copilot dialog screenshot from other steps
                    for other_step in self._get_all_steps():
                        other_screenshot = other_step.get('screenshot_path')
                        if other_screenshot and 'copilot_dialog' in other_screenshot:
                            bug_screenshot_path = f"/{other_screenshot}"
                            break
            
            bugs.append({
                "category": "interaction_problems",
                "title": f"Unexpected Dialog Interruption: {step_name}",
                "description": f"Dialog of type '{dialog_type}' appeared unexpectedly during '{step_name}', blocking user progress",
                "severity": "medium",
                "step_name": step_name,
                "recommendation": "Implement proactive dialog detection and dismissal to prevent workflow interruptions",
                "screenshot_path": bug_screenshot_path
            })
        
        if step.get("interaction_attempted") and not step.get("interaction_successful"):
            bugs.append({
                "category": "interaction_problems",
                "title": f"Element Interaction Failure: {step_name}",
                "description": f"Failed to interact with UI elements in step '{step_name}'. This suggests poor element accessibility or inconsistent interaction patterns.",
                "severity": "high",
                "step_name": step_name,
                "recommendation": "Review element selectors, ensure consistent interaction patterns, and improve element accessibility"
            })
        
        # 3. PERFORMANCE UX ISSUES - Based on ADO Craft bug patterns
        duration = step.get("duration_ms", 0)
        if duration > 5000:  # 5 seconds threshold
            bugs.append({
                "category": "performance_ux",
                "title": f"Slow Response Time: {step_name}",
                "description": f"Step '{step_name}' took {duration/1000:.1f} seconds, exceeding acceptable response time for smooth user experience",
                "severity": "medium",
                "step_name": step_name,
                "recommendation": "Optimize step performance to reduce response time and improve user experience"
            })
        elif duration > 2000:  # 2 seconds threshold
            bugs.append({
                "category": "performance_ux",
                "title": f"Suboptimal Performance: {step_name}",
                "description": f"Step '{step_name}' took {duration/1000:.1f} seconds, which is noticeable to users",
                "severity": "low",
                "step_name": step_name,
                "recommendation": "Consider performance optimizations for this step"
            })
        
        # 4. VISUAL INCONSISTENCIES - Based on ADO Craft bug patterns
        if step.get("ui_signals") and "visual_issues" in step.get("ui_signals", {}):
            bugs.append({
                "category": "visual_inconsistencies",
                "title": f"Visual Design Issue: {step_name}",
                "description": f"Visual inconsistencies detected in step '{step_name}', affecting UI coherence and user trust",
                "severity": "medium",
                "step_name": step_name,
                "recommendation": "Review visual design consistency and ensure adherence to design system guidelines"
            })
        
        # 5. ACCESSIBILITY ISSUES - Based on ADO Craft bug patterns
        if step.get("ui_signals") and "accessibility_issues" in step.get("ui_signals", {}):
            bugs.append({
                "category": "accessibility_issues",
                "title": f"Accessibility Problem: {step_name}",
                "description": f"Accessibility issues detected in step '{step_name}', limiting usability for users with disabilities",
                "severity": "high",
                "step_name": step_name,
                "recommendation": "Implement proper accessibility features including ARIA labels, keyboard navigation, and screen reader support"
            })
        
        # 6. EXCEL-SPECIFIC CRAFT BUGS - Based on our Excel analysis
        if "copilot" in step_name.lower() or step.get("dialog_type") == "copilot":
            # For Copilot dialog bugs, try to find the Copilot dialog screenshot
            bug_screenshot_path = None
            if screenshot_path and 'copilot_dialog' in screenshot_path:
                bug_screenshot_path = screenshot_path
            else:
                # Try to find Copilot dialog screenshot from other steps
                for other_step in self._get_all_steps():
                    other_screenshot = other_step.get('screenshot_path')
                    if other_screenshot and 'copilot_dialog' in other_screenshot:
                        bug_screenshot_path = f"/{other_screenshot}"
                        break
            
            bugs.append({
                "category": "interaction_problems",
                "title": f"Copilot Dialog UX Issue: {step_name}",
                "description": f"Copilot dialog appeared in step '{step_name}', which can disrupt user workflow and create confusion",
                "severity": "medium",
                "step_name": step_name,
                "recommendation": "Consider making Copilot opt-in rather than automatic, or provide clear dismissal options",
                "screenshot_path": bug_screenshot_path
            })
        
        if "save" in step_name.lower() and step.get("dialog_detected"):
            bugs.append({
                "category": "flow_disruptions",
                "title": f"Save Dialog UX Issue: {step_name}",
                "description": f"Save dialog appeared unexpectedly in step '{step_name}', potentially confusing users about save status",
                "severity": "low",
                "step_name": step_name,
                "recommendation": "Implement auto-save functionality or provide clearer save status indicators"
            })
        
        if "cell" in step_name.lower() or "data" in step_name.lower():
            if not step.get("interaction_successful"):
                bugs.append({
                    "category": "interaction_problems",
                    "title": f"Cell Interaction Issue: {step_name}",
                    "description": f"Failed to interact with Excel cells in step '{step_name}', indicating poor cell accessibility",
                    "severity": "medium",
                    "step_name": step_name,
                    "recommendation": "Improve cell interaction patterns and ensure consistent cell selection behavior"
                })
        
        return bugs

    def _analyze_scenario_level_issues(self, telemetry_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Analyze scenario-level issues based on overall patterns"""
        bugs = []
        
        # Check overall execution time
        total_duration = telemetry_data.get("total_duration_ms", 0)
        if total_duration > 60000:  # 1 minute threshold
            bugs.append({
                "category": "performance_ux",
                "title": "Overall Slow Performance",
                "description": f"Complete scenario took {total_duration/1000:.1f} seconds, which is too slow for good user experience",
                "severity": "high",
                "recommendation": "Optimize overall scenario performance to reduce total execution time"
            })
        
        # Check for multiple dialog interruptions
        dialog_count = sum(1 for step in telemetry_data.get("steps", []) if step.get("dialog_detected"))
        if dialog_count > 1:
            bugs.append({
                "category": "flow_disruptions",
                "title": "Multiple Dialog Interruptions",
                "description": f"Scenario was interrupted by {dialog_count} dialogs, creating a fragmented user experience",
                "severity": "medium",
                "recommendation": "Minimize dialog interruptions and implement smoother workflow transitions"
            })
        
        # Check for interaction failures
        failed_interactions = sum(1 for step in telemetry_data.get("steps", []) 
                                if step.get("interaction_attempted") and not step.get("interaction_successful"))
        if failed_interactions > 0:
            bugs.append({
                "category": "interaction_problems",
                "title": "Multiple Interaction Failures",
                "description": f"Found {failed_interactions} interaction failures across the scenario, indicating UI accessibility issues",
                "severity": "high",
                "recommendation": "Review and fix element interaction patterns throughout the application"
            })
        
        # Check for step failures
        failed_steps = sum(1 for step in telemetry_data.get("steps", []) if not step.get("success"))
        if failed_steps > 0:
            bugs.append({
                "category": "flow_disruptions",
                "title": "Scenario Reliability Issues",
                "description": f"{failed_steps} steps failed during execution, indicating workflow reliability problems",
                "severity": "high",
                "recommendation": "Improve scenario reliability through better error handling and robust step implementation"
            })
        
        return bugs
    
    def _get_all_steps(self) -> List[Dict[str, Any]]:
        """Get all steps from the current telemetry data"""
        if hasattr(self, '_current_telemetry_data'):
            return self._current_telemetry_data.get("steps", [])
        return []

async def main():
    """Test the Simple Excel UX Analyzer"""
    print("🎨 Simple Excel UX Analyzer Test")
    print("=" * 50)
    
    analyzer = SimpleExcelUXAnalyzer()
    
    # Analyze Excel scenario UX
    results = await analyzer.analyze_excel_scenario_ux({})
    
    print(f"\n📊 Analysis Results:")
    print(f"Steps analyzed: {results['scenario_results']['steps_completed']}")
    print(f"Total Craft bugs detected: {len(results['craft_bugs'])}")
    print(f"Overall UX score: {results['ux_analysis']['overall_ux_score']:.1f}/100")
    
    print(f"\n🚨 Craft Bug Summary:")
    for bug_type, count in results['ux_analysis']['craft_bug_summary'].items():
        print(f"  {bug_type}: {count} bugs")
    
    print(f"\n📝 Top Recommendations:")
    for i, rec in enumerate(results['ux_analysis']['recommendations'][:3], 1):
        print(f"  {i}. {rec}")
    
    # Save detailed report
    with open("simple_ux_analysis_report.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"\n📁 Detailed report saved to: simple_ux_analysis_report.json")
    print(f"✅ Simple Excel UX Analyzer test completed!")

if __name__ == "__main__":
    asyncio.run(main())
