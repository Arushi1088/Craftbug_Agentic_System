"""
Excel Web Scenarios Module
Defines and executes Excel Web scenarios for testing
"""

import asyncio
import time
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from excel_web_navigator import ExcelWebNavigator


@dataclass
class ScenarioStep:
    """Represents a single step in a scenario"""
    name: str
    description: str
    action: str  # 'click', 'fill', 'wait', 'screenshot', 'verify'
    selector: str
    value: Optional[str] = None
    timeout: int = 10
    required: bool = True
    success_criteria: Optional[str] = None


@dataclass
class ScenarioResult:
    """Results of scenario execution"""
    scenario_name: str
    success: bool
    steps_completed: int
    total_steps: int
    execution_time: float
    screenshots: List[str]
    errors: List[str]
    performance_metrics: Dict[str, Any]


class ExcelScenarioExecutor:
    """Executes Excel Web scenarios"""
    
    def __init__(self, navigator: ExcelWebNavigator):
        self.navigator = navigator
        self.current_scenario: Optional[str] = None
        self.execution_start_time: Optional[float] = None
    
    async def execute_document_creation_scenario(self) -> ScenarioResult:
        """Execute the document creation scenario"""
        scenario_name = "Document Creation: Create new workbook, add data, save"
        
        steps = [
            ScenarioStep(
                name="Navigate to Excel Web",
                description="Ensure we're on Excel Web homepage",
                action="verify",
                selector="text=Excel",
                timeout=15
            ),
            ScenarioStep(
                name="Click New Blank Workbook",
                description="Click the new blank workbook button",
                action="click",
                selector="text=Blank workbook",
                timeout=10
            ),
            ScenarioStep(
                name="Wait for Workbook to Load",
                description="Wait for the new workbook to fully load",
                action="wait",
                selector="[data-testid='excel-worksheet']",
                timeout=30
            ),
            ScenarioStep(
                name="Add Header Row",
                description="Add headers to the first row",
                action="fill",
                selector="[data-testid='cell-A1']",
                value="Name",
                timeout=10
            ),
            ScenarioStep(
                name="Add Second Header",
                description="Add second header to B1",
                action="fill",
                selector="[data-testid='cell-B1']",
                value="Age",
                timeout=10
            ),
            ScenarioStep(
                name="Add Third Header",
                description="Add third header to C1",
                action="fill",
                selector="[data-testid='cell-C1']",
                value="Email",
                timeout=10
            ),
            ScenarioStep(
                name="Add Sample Data Row 1",
                description="Add sample data to row 2",
                action="fill",
                selector="[data-testid='cell-A2']",
                value="John Doe",
                timeout=10
            ),
            ScenarioStep(
                name="Add Age Data",
                description="Add age data to B2",
                action="fill",
                selector="[data-testid='cell-B2']",
                value="30",
                timeout=10
            ),
            ScenarioStep(
                name="Add Email Data",
                description="Add email data to C2",
                action="fill",
                selector="[data-testid='cell-C2']",
                value="john@example.com",
                timeout=10
            ),
            ScenarioStep(
                name="Add Second Data Row",
                description="Add second row of sample data",
                action="fill",
                selector="[data-testid='cell-A3']",
                value="Jane Smith",
                timeout=10
            ),
            ScenarioStep(
                name="Add Second Age",
                description="Add age for second person",
                action="fill",
                selector="[data-testid='cell-B3']",
                value="25",
                timeout=10
            ),
            ScenarioStep(
                name="Add Second Email",
                description="Add email for second person",
                action="fill",
                selector="[data-testid='cell-C3']",
                value="jane@example.com",
                timeout=10
            ),
            ScenarioStep(
                name="Take Screenshot Before Save",
                description="Capture the workbook before saving",
                action="screenshot",
                selector="",
                value="workbook_before_save"
            ),
            ScenarioStep(
                name="Click Save Button",
                description="Click the save button",
                action="click",
                selector="text=Save",
                timeout=10
            ),
            ScenarioStep(
                name="Wait for Save Dialog",
                description="Wait for save dialog to appear",
                action="wait",
                selector="text=Save As",
                timeout=15
            ),
            ScenarioStep(
                name="Enter File Name",
                description="Enter a filename for the workbook",
                action="fill",
                selector="input[placeholder*='name']",
                value="TestWorkbook",
                timeout=10
            ),
            ScenarioStep(
                name="Click Save",
                description="Click save to save the file",
                action="click",
                selector="button:has-text('Save')",
                timeout=10
            ),
            ScenarioStep(
                name="Verify Save Success",
                description="Verify the file was saved successfully",
                action="verify",
                selector="text=saved",
                timeout=15
            ),
            ScenarioStep(
                name="Take Final Screenshot",
                description="Capture the final state after save",
                action="screenshot",
                selector="",
                value="workbook_after_save"
            )
        ]
        
        return await self.execute_scenario(scenario_name, steps)
    
    async def execute_scenario(self, scenario_name: str, steps: List[ScenarioStep]) -> ScenarioResult:
        """Execute a scenario with the given steps"""
        self.current_scenario = scenario_name
        self.execution_start_time = time.time()
        
        result = ScenarioResult(
            scenario_name=scenario_name,
            success=False,
            steps_completed=0,
            total_steps=len(steps),
            execution_time=0.0,
            screenshots=[],
            errors=[],
            performance_metrics={}
        )
        
        print(f"\n📋 Executing Scenario: {scenario_name}")
        print(f"📊 Total Steps: {len(steps)}")
        print("=" * 60)
        
        try:
            # Ensure we're authenticated
            if not await self.navigator.ensure_authenticated():
                result.errors.append("Failed to authenticate")
                return result
            
            # Execute each step
            for i, step in enumerate(steps, 1):
                step_start_time = time.time()
                
                print(f"\n🔹 Step {i}/{len(steps)}: {step.name}")
                print(f"   📝 {step.description}")
                
                step_success = await self.execute_step(step, result)
                
                step_time = time.time() - step_start_time
                print(f"   ⏱️  Step time: {step_time:.2f}s")
                
                if step_success:
                    result.steps_completed += 1
                    print(f"   ✅ Step completed successfully")
                else:
                    result.errors.append(f"Step {i} failed: {step.name}")
                    print(f"   ❌ Step failed")
                    
                    if step.required:
                        print(f"   🛑 Stopping execution (required step failed)")
                        break
                    else:
                        print(f"   ⚠️  Continuing (step not required)")
                
                # Add performance metric
                result.performance_metrics[f"step_{i}_time"] = step_time
                
                # Small delay between steps
                await asyncio.sleep(1)
            
            # Calculate overall success
            result.success = result.steps_completed == result.total_steps
            result.execution_time = time.time() - self.execution_start_time
            
            print("\n" + "=" * 60)
            print(f"📊 Scenario Results:")
            print(f"   ✅ Success: {result.success}")
            print(f"   📈 Steps Completed: {result.steps_completed}/{result.total_steps}")
            print(f"   ⏱️  Total Time: {result.execution_time:.2f}s")
            print(f"   📸 Screenshots: {len(result.screenshots)}")
            print(f"   ❌ Errors: {len(result.errors)}")
            
            if result.errors:
                print(f"\n❌ Errors encountered:")
                for error in result.errors:
                    print(f"   - {error}")
            
            return result
            
        except Exception as e:
            result.errors.append(f"Scenario execution failed: {str(e)}")
            print(f"❌ Scenario execution failed: {e}")
            return result
    
    async def execute_step(self, step: ScenarioStep, result: ScenarioResult) -> bool:
        """Execute a single scenario step"""
        try:
            if step.action == "click":
                return await self.navigator.click_element(step.selector, step.timeout)
            
            elif step.action == "fill":
                if step.value is None:
                    result.errors.append(f"No value provided for fill action in step: {step.name}")
                    return False
                return await self.navigator.fill_input(step.selector, step.value, step.timeout)
            
            elif step.action == "wait":
                return await self.navigator.wait_for_element(step.selector, step.timeout)
            
            elif step.action == "verify":
                return await self.navigator.wait_for_element(step.selector, step.timeout)
            
            elif step.action == "screenshot":
                screenshot_path = await self.navigator.take_screenshot(step.value or "step_screenshot")
                if screenshot_path:
                    result.screenshots.append(screenshot_path)
                    return True
                else:
                    return False
            
            else:
                result.errors.append(f"Unknown action: {step.action}")
                return False
                
        except Exception as e:
            result.errors.append(f"Step execution error: {str(e)}")
            return False


# Scenario definitions
DOCUMENT_CREATION_SCENARIO = {
    "name": "Document Creation: Create new workbook, add data, save",
    "description": "Create a new Excel workbook, add sample data, and save it",
    "steps": [
        "Navigate to Excel Web",
        "Click New Blank Workbook", 
        "Wait for Workbook to Load",
        "Add Header Row",
        "Add Sample Data",
        "Take Screenshot Before Save",
        "Click Save Button",
        "Enter File Name",
        "Click Save",
        "Verify Save Success",
        "Take Final Screenshot"
    ]
}


async def get_excel_scenario_executor(navigator: ExcelWebNavigator) -> ExcelScenarioExecutor:
    """Get an Excel scenario executor"""
    return ExcelScenarioExecutor(navigator)
