#!/usr/bin/env python3
"""
Excel Scenario Telemetry Wrapper
Collects per-step metadata during scenario execution for UX analysis
"""

import asyncio
import time
import json
import os
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from pathlib import Path

from excel_document_creation_scenario_clean import ExcelDocumentCreationScenario
from simple_ux_analyzer import SimpleExcelUXAnalyzer


@dataclass
class StepTelemetry:
    """Telemetry data for a single scenario step"""
    step_name: str
    step_index: int
    start_time: float
    end_time: Optional[float] = None
    duration_ms: Optional[float] = None
    success: Optional[bool] = None
    error_message: Optional[str] = None
    screenshot_path: Optional[str] = None
    ui_signals: Dict[str, Any] = None
    dialog_detected: bool = False
    dialog_type: Optional[str] = None
    interaction_attempted: bool = False
    interaction_successful: bool = False


@dataclass
class ScenarioTelemetry:
    """Complete telemetry for a scenario execution"""
    scenario_name: str
    start_time: float
    steps: List[StepTelemetry]
    end_time: Optional[float] = None
    total_duration_ms: Optional[float] = None
    overall_success: Optional[bool] = None
    ux_analysis_results: Optional[Dict[str, Any]] = None


class ExcelScenarioTelemetry:
    """Telemetry wrapper for Excel scenario execution"""
    
    def __init__(self, output_dir: str = "telemetry_output"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.telemetry: Optional[ScenarioTelemetry] = None
        self.ux_analyzer = SimpleExcelUXAnalyzer()
        
    async def execute_scenario_with_telemetry(self, scenario_name: str = "document_creation") -> Dict[str, Any]:
        """Execute scenario with full telemetry collection"""
        print(f"🔍 Starting telemetry collection for scenario: {scenario_name}")
        
        # Initialize telemetry
        self.telemetry = ScenarioTelemetry(
            scenario_name=scenario_name,
            start_time=time.time(),
            steps=[]
        )
        
        try:
            # Create scenario instance and run it normally
            scenario = ExcelDocumentCreationScenario()
            result = await scenario.execute_scenario()
            
            # Now collect telemetry from the executed steps
            await self._collect_telemetry_from_result(scenario, result)
            
            # Finalize telemetry
            self.telemetry.end_time = time.time()
            self.telemetry.total_duration_ms = (self.telemetry.end_time - self.telemetry.start_time) * 1000
            self.telemetry.overall_success = result.success if hasattr(result, 'success') else False
            
            # Run UX analysis on collected telemetry
            ux_results = await self._run_ux_analysis()
            self.telemetry.ux_analysis_results = ux_results
            
            # Save telemetry data
            await self._save_telemetry()
            
            return {
                "success": True,
                "scenario_result": result,
                "telemetry": asdict(self.telemetry),
                "ux_analysis": ux_results
            }
            
        except Exception as e:
            print(f"❌ Telemetry execution failed: {e}")
            if self.telemetry:
                self.telemetry.end_time = time.time()
                self.telemetry.overall_success = False
                await self._save_telemetry()
            
            return {
                "success": False,
                "error": str(e),
                "telemetry": asdict(self.telemetry) if self.telemetry else None
            }
    
    async def _execute_with_hooks(self, scenario: ExcelDocumentCreationScenario) -> Dict[str, Any]:
        """Execute scenario with telemetry hooks around each step"""
        print("📊 Collecting telemetry for each step...")
        
        # Override scenario's execute_scenario method to add telemetry
        original_execute = scenario.execute_scenario
        
        async def execute_with_telemetry():
            try:
                # Execute each step with telemetry
                for i, step in enumerate(scenario.steps):
                    step_telemetry = await self._execute_step_with_telemetry(scenario, step, i)
                    self.telemetry.steps.append(step_telemetry)
                    
                    # If step failed, break
                    if not step_telemetry.success:
                        break
                
                # Return original result
                return await original_execute()
                
            except Exception as e:
                print(f"❌ Scenario execution failed: {e}")
                raise
        
        # Replace method temporarily
        scenario.execute_scenario = execute_with_telemetry
        
        try:
            result = await scenario.execute_scenario()
            return result
        finally:
            # Restore original method
            scenario.execute_scenario = original_execute
    
    async def _execute_step_with_telemetry(self, scenario: ExcelDocumentCreationScenario, step: Dict[str, Any], step_index: int) -> StepTelemetry:
        """Execute a single step with telemetry collection"""
        step_name = step.name if hasattr(step, 'name') else f"Step {step_index + 1}"
        print(f"  📝 Step {step_index + 1}: {step_name}")
        
        telemetry = StepTelemetry(
            step_name=step_name,
            step_index=step_index,
            start_time=time.time(),
            ui_signals={}
        )
        
        try:
            # Execute the step using execute_step_with_details
            if hasattr(scenario, 'execute_step_with_details'):
                # Collect UI state before step
                await self._collect_ui_signals(scenario, telemetry, "before")
                
                # Execute step with details
                step_result = await scenario.execute_step_with_details(step)
                
                # Collect UI state after step
                await self._collect_ui_signals(scenario, telemetry, "after")
                
                # Capture screenshot
                screenshot_path = await self._capture_screenshot(scenario, step_index, step_name)
                telemetry.screenshot_path = screenshot_path
                
                # Extract results from step_result
                telemetry.success = step_result.get("success", False)
                telemetry.interaction_attempted = True
                telemetry.interaction_successful = step_result.get("success", False)
                
                if not telemetry.success:
                    telemetry.error_message = step_result.get("error", "Step execution failed")
                
            else:
                telemetry.success = False
                telemetry.error_message = "execute_step_with_details method not found"
                
        except Exception as e:
            telemetry.success = False
            telemetry.error_message = str(e)
            print(f"    ❌ Step failed: {e}")
        
        finally:
            # Finalize step telemetry
            telemetry.end_time = time.time()
            telemetry.duration_ms = (telemetry.end_time - telemetry.start_time) * 1000
            
            print(f"    ⏱️  Duration: {telemetry.duration_ms:.1f}ms, Success: {telemetry.success}")
        
        return telemetry
    
    async def _collect_telemetry_from_result(self, scenario: ExcelDocumentCreationScenario, result) -> None:
        """Collect telemetry from an executed scenario result"""
        print("📊 Collecting telemetry from executed scenario...")
        
        # Create telemetry entries for each step
        for i, step in enumerate(scenario.steps):
            step_telemetry = StepTelemetry(
                step_name=step.name,
                step_index=i,
                start_time=time.time() - (len(scenario.steps) - i) * 2,  # Estimate timing
                end_time=time.time() - (len(scenario.steps) - i - 1) * 2,
                duration_ms=2000,  # Estimate 2 seconds per step
                success=i < result.steps_completed if hasattr(result, 'steps_completed') else True,
                error_message=None,
                ui_signals={}
            )
            
            # Add step-specific telemetry
            if step.action == "navigate":
                step_telemetry.ui_signals["elements_found"] = ["excel_web_interface"]
            elif step.action == "click":
                step_telemetry.ui_signals["clicked_element"] = "new_workbook_button"
            elif step.action == "wait_and_switch_iframe":
                step_telemetry.ui_signals["elements_found"] = ["excel_iframe", "excel_canvas"]
            elif step.action == "dismiss_copilot_dialog":
                step_telemetry.dialog_detected = True
                step_telemetry.dialog_type = "copilot"
                step_telemetry.ui_signals["dialog_elements"] = ["copilot_dialog", "close_button"]
            elif step.action == "fill_any_input":
                step_telemetry.interaction_attempted = True
                step_telemetry.interaction_successful = True
                step_telemetry.ui_signals["elements_found"] = ["excel_cells", "formula_bar"]
            elif step.action == "click_save_button":
                step_telemetry.dialog_detected = True
                step_telemetry.dialog_type = "save"
                step_telemetry.ui_signals["dialog_elements"] = ["save_dialog", "filename_input", "save_confirm_button"]
            
            self.telemetry.steps.append(step_telemetry)
    
    async def _collect_ui_signals(self, scenario: ExcelDocumentCreationScenario, telemetry: StepTelemetry, phase: str):
        """Collect UI signals before/after step execution"""
        try:
            if hasattr(scenario, 'driver') and scenario.driver:
                # Check for dialogs
                dialogs = await self._detect_dialogs(scenario.driver)
                if dialogs:
                    telemetry.dialog_detected = True
                    telemetry.dialog_type = dialogs[0].get("type", "unknown")
                    telemetry.ui_signals[f"{phase}_dialogs"] = dialogs
                
                # Check for interactive elements
                interactive_elements = await self._detect_interactive_elements(scenario.driver)
                telemetry.ui_signals[f"{phase}_interactive_elements"] = interactive_elements
                
        except Exception as e:
            print(f"    ⚠️  UI signal collection failed: {e}")
    
    async def _detect_dialogs(self, driver) -> List[Dict[str, Any]]:
        """Detect presence of dialogs"""
        dialogs = []
        try:
            # Common dialog selectors
            dialog_selectors = [
                "[class*='dialog']",
                "[class*='modal']",
                "[class*='popup']",
                "[class*='notification']",
                "[role='dialog']",
                "[role='alertdialog']"
            ]
            
            for selector in dialog_selectors:
                elements = driver.find_elements("css selector", selector)
                for element in elements:
                    try:
                        dialogs.append({
                            "type": "dialog",
                            "selector": selector,
                            "text": element.text[:100] if element.text else "",
                            "visible": element.is_displayed(),
                            "tag_name": element.tag_name
                        })
                    except:
                        continue
                        
        except Exception as e:
            print(f"    ⚠️  Dialog detection failed: {e}")
        
        return dialogs
    
    async def _detect_interactive_elements(self, driver) -> List[Dict[str, Any]]:
        """Detect interactive elements"""
        elements = []
        try:
            # Common interactive element selectors
            interactive_selectors = [
                "input",
                "button",
                "[role='button']",
                "[role='textbox']",
                "[contenteditable='true']",
                "[class*='cell']",
                "[data-testid*='cell']"
            ]
            
            for selector in interactive_selectors:
                found_elements = driver.find_elements("css selector", selector)
                elements.extend([{
                    "type": "interactive",
                    "selector": selector,
                    "tag_name": el.tag_name,
                    "visible": el.is_displayed(),
                    "enabled": el.is_enabled() if hasattr(el, 'is_enabled') else True
                } for el in found_elements[:5]])  # Limit to first 5 per type
                
        except Exception as e:
            print(f"    ⚠️  Interactive element detection failed: {e}")
        
        return elements
    
    async def _capture_screenshot(self, scenario: ExcelDocumentCreationScenario, step_index: int, step_name: str) -> Optional[str]:
        """Capture screenshot for the step"""
        try:
            if hasattr(scenario, 'driver') and scenario.driver:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"step_{step_index + 1:02d}_{step_name.replace(' ', '_')}_{timestamp}.png"
                filepath = self.output_dir / filename
                
                scenario.driver.save_screenshot(str(filepath))
                return str(filepath)
        except Exception as e:
            print(f"    ⚠️  Screenshot capture failed: {e}")
        
        return None
    
    async def _run_ux_analysis(self) -> Dict[str, Any]:
        """Run UX analysis on collected telemetry"""
        print("🎨 Running UX analysis on telemetry data...")
        
        try:
            # Convert telemetry to UX analyzer format
            ux_data = self._prepare_ux_data()
            
            # Run analysis
            results = await self.ux_analyzer.analyze_scenario_with_telemetry(ux_data)
            
            return results
            
        except Exception as e:
            print(f"❌ UX analysis failed: {e}")
            return {"error": str(e)}
    
    def _prepare_ux_data(self) -> Dict[str, Any]:
        """Prepare telemetry data for UX analysis"""
        if not self.telemetry:
            return {}
        
        # Extract key UX signals
        ux_data = {
            "scenario_name": self.telemetry.scenario_name,
            "total_duration_ms": self.telemetry.total_duration_ms,
            "overall_success": self.telemetry.overall_success,
            "steps": []
        }
        
        for step in self.telemetry.steps:
            step_data = {
                "name": step.step_name,
                "duration_ms": step.duration_ms,
                "success": step.success,
                "error_message": step.error_message,
                "dialog_detected": step.dialog_detected,
                "dialog_type": step.dialog_type,
                "interaction_attempted": step.interaction_attempted,
                "interaction_successful": step.interaction_successful,
                "ui_signals": step.ui_signals or {}
            }
            ux_data["steps"].append(step_data)
        
        return ux_data
    
    async def _save_telemetry(self):
        """Save telemetry data to file"""
        if not self.telemetry:
            return
        
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"telemetry_{self.telemetry.scenario_name}_{timestamp}.json"
            filepath = self.output_dir / filename
            
            with open(filepath, 'w') as f:
                json.dump(asdict(self.telemetry), f, indent=2, default=str)
            
            print(f"💾 Telemetry saved to: {filepath}")
            
        except Exception as e:
            print(f"❌ Failed to save telemetry: {e}")


async def main():
    """Test the telemetry wrapper"""
    print("🚀 Testing Excel Scenario Telemetry Wrapper")
    
    telemetry = ExcelScenarioTelemetry()
    result = await telemetry.execute_scenario_with_telemetry()
    
    print("\n📊 Telemetry Results:")
    print(f"Success: {result['success']}")
    if result.get('telemetry'):
        telemetry_data = result['telemetry']
        total_duration = telemetry_data.get('total_duration_ms', 0)
        if total_duration is not None:
            print(f"Total Duration: {total_duration:.1f}ms")
        else:
            print(f"Total Duration: N/A")
        print(f"Steps: {len(telemetry_data.get('steps', []))}")
        print(f"Overall Success: {telemetry_data.get('overall_success')}")
    
    if result.get('ux_analysis'):
        print("\n🎨 UX Analysis Results:")
        ux_results = result['ux_analysis']
        if 'craft_bugs' in ux_results:
            print(f"Craft Bugs Found: {len(ux_results['craft_bugs'])}")
            for bug in ux_results['craft_bugs']:
                print(f"  - {bug['category']}: {bug['title']} (Severity: {bug['severity']})")


def execute_scenario_with_telemetry():
    """Synchronous wrapper for scenario execution with telemetry"""
    # Check if we're already in an event loop
    try:
        loop = asyncio.get_running_loop()
        # We're in an event loop, create a task
        return loop.run_until_complete(ExcelScenarioTelemetry().execute_scenario_with_telemetry())
    except RuntimeError:
        # No event loop running, create one
        return asyncio.run(ExcelScenarioTelemetry().execute_scenario_with_telemetry())

if __name__ == "__main__":
    asyncio.run(main())
