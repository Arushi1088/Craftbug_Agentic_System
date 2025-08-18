"""
Excel Document Creation Scenario
Tests creating a new workbook, adding data, and saving
"""

import asyncio
import time
from typing import List, Dict, Any
from dataclasses import dataclass
from selenium.webdriver.common.by import By
from excel_web_selenium_only import get_selenium_navigator


@dataclass
class ScenarioStep:
    name: str
    description: str
    action: str  # 'click', 'fill', 'wait', 'screenshot'
    selector: str
    value: str = None
    timeout: int = 10
    required: bool = True


@dataclass
class ScenarioResult:
    scenario_name: str
    success: bool
    steps_completed: int
    total_steps: int
    execution_time: float
    screenshots: List[str]
    errors: List[str]
    performance_metrics: Dict[str, Any]


class ExcelDocumentCreationScenario:
    """Excel Document Creation Scenario Executor"""
    
    def __init__(self):
        self.navigator = None
        self.steps = [
            ScenarioStep(
                name="Navigate to Excel Web",
                description="Ensure we're on Excel Web with authentication",
                action="navigate",
                selector="",
                timeout=30
            ),
            ScenarioStep(
                name="Click New Workbook",
                description="Click the 'Blank workbook' text to create a new workbook",
                action="click",
                selector="span:contains('Blank workbook'), .fui-Text:contains('Blank workbook')",
                timeout=15
            ),
            ScenarioStep(
                name="Wait for Workbook to Load",
                description="Wait for the new workbook to fully load",
                action="wait",
                selector=".excel-app, [data-testid='excel-app'], .workbook-container",
                timeout=20
            ),
            ScenarioStep(
                name="Take Screenshot - Initial State",
                description="Capture initial workbook state",
                action="screenshot",
                selector="",
                value="excel_initial_state"
            ),
            ScenarioStep(
                name="Click First Cell",
                description="Click on cell A1 to start entering data",
                action="click",
                selector="[data-testid='cell-A1'], .cell-A1, td[data-cell='A1']",
                timeout=10
            ),
            ScenarioStep(
                name="Enter Sample Data",
                description="Enter sample data in cell A1",
                action="fill",
                selector="[data-testid='cell-input'], .cell-input, input[type='text']",
                value="Sample Data for Testing",
                timeout=10
            ),
            ScenarioStep(
                name="Press Enter",
                description="Press Enter to confirm data entry",
                action="key",
                selector="",
                value="Enter",
                timeout=5
            ),
            ScenarioStep(
                name="Take Screenshot - Data Entered",
                description="Capture workbook with data entered",
                action="screenshot",
                selector="",
                value="excel_data_entered"
            ),
            ScenarioStep(
                name="Click Save Button",
                description="Click the save button to save the workbook",
                action="click",
                selector="[data-testid='save-button'], .save-button, button:contains('Save'), a:contains('Save')",
                timeout=15
            ),
            ScenarioStep(
                name="Wait for Save Dialog",
                description="Wait for save dialog to appear",
                action="wait",
                selector="[data-testid='save-dialog'], .save-dialog, .modal",
                timeout=10
            ),
            ScenarioStep(
                name="Enter File Name",
                description="Enter a filename for the workbook",
                action="fill",
                selector="[data-testid='filename-input'], .filename-input, input[placeholder*='name']",
                value="TestWorkbook_Automation",
                timeout=10
            ),
            ScenarioStep(
                name="Click Save in Dialog",
                description="Click save in the save dialog",
                action="click",
                selector="[data-testid='save-confirm'], .save-confirm, button:contains('Save')",
                timeout=10
            ),
            ScenarioStep(
                name="Wait for Save Confirmation",
                description="Wait for save confirmation",
                action="wait",
                selector="[data-testid='save-success'], .save-success, .success-message",
                timeout=15
            ),
            ScenarioStep(
                name="Take Screenshot - Final State",
                description="Capture final workbook state after save",
                action="screenshot",
                selector="",
                value="excel_final_state"
            )
        ]
    
    async def execute_scenario(self) -> ScenarioResult:
        """Execute the Excel document creation scenario"""
        start_time = time.time()
        result = ScenarioResult(
            scenario_name="Excel Document Creation",
            success=False,
            steps_completed=0,
            total_steps=len(self.steps),
            execution_time=0,
            screenshots=[],
            errors=[],
            performance_metrics={}
        )
        
        try:
            print("🚀 Starting Excel Document Creation Scenario...")
            
            # Get navigator
            self.navigator = await get_selenium_navigator()
            
            # Initialize and authenticate
            if not await self.navigator.initialize():
                result.errors.append("Failed to initialize navigator")
                return result
            
            if not await self.navigator.ensure_authenticated():
                result.errors.append("Failed to authenticate to Excel Web")
                return result
            
            print("✅ Authentication successful, starting scenario steps...")
            
            # Execute each step
            for i, step in enumerate(self.steps, 1):
                print(f"\n📋 Step {i}/{len(self.steps)}: {step.name}")
                print(f"   Description: {step.description}")
                
                step_success = await self.execute_step(step, result)
                
                if step_success:
                    result.steps_completed += 1
                    print(f"   ✅ Step completed successfully")
                else:
                    result.errors.append(f"Step {i} failed: {step.name}")
                    print(f"   ❌ Step failed")
                    
                    if step.required:
                        print(f"   ⚠️  Required step failed, stopping scenario")
                        break
                    else:
                        print(f"   ⚠️  Non-required step failed, continuing...")
                
                # Small delay between steps
                await asyncio.sleep(1)
            
            # Calculate execution time
            result.execution_time = time.time() - start_time
            
            # Determine success
            if result.steps_completed >= len(self.steps) * 0.8:  # 80% success rate
                result.success = True
                print(f"\n🎉 Scenario completed successfully!")
            else:
                print(f"\n⚠️  Scenario completed with errors")
            
            print(f"📊 Results:")
            print(f"   Steps completed: {result.steps_completed}/{result.total_steps}")
            print(f"   Execution time: {result.execution_time:.2f} seconds")
            print(f"   Screenshots taken: {len(result.screenshots)}")
            print(f"   Errors: {len(result.errors)}")
            
            return result
            
        except Exception as e:
            result.errors.append(f"Scenario execution failed: {str(e)}")
            print(f"❌ Scenario execution failed: {e}")
            return result
        finally:
            # Cleanup
            if self.navigator:
                await self.navigator.close()
    
    async def execute_step(self, step: ScenarioStep, result: ScenarioResult) -> bool:
        """Execute a single scenario step"""
        try:
            if step.action == "navigate":
                return await self.navigator.navigate_to_excel_web()
            
            elif step.action == "click":
                # Try multiple selectors including XPath
                selectors = step.selector.split(", ")
                for selector in selectors:
                    selector = selector.strip()
                    
                    # Try CSS selector first
                    if await self.navigator.click_element(selector, step.timeout):
                        return True
                    
                    # If it's a text-based selector, try XPath
                    if "contains" in selector or "text" in selector:
                        # Convert to XPath
                        if "Blank workbook" in selector:
                            xpath = "//span[contains(text(), 'Blank workbook')]"
                            if await self.navigator.click_element_by_xpath(xpath, step.timeout):
                                return True
                        
                        # Try other common text patterns
                        if "New" in selector:
                            xpath = "//span[contains(text(), 'New')]"
                            if await self.navigator.click_element_by_xpath(xpath, step.timeout):
                                return True
                
                return False
            
            elif step.action == "fill":
                if await self.navigator.fill_input(step.selector, step.value, step.timeout):
                    return True
                return False
            
            elif step.action == "wait":
                if await self.navigator.wait_for_element(step.selector, step.timeout):
                    return True
                return False
            
            elif step.action == "screenshot":
                screenshot_path = await self.navigator.take_screenshot(step.value)
                if screenshot_path:
                    result.screenshots.append(screenshot_path)
                    return True
                return False
            
            elif step.action == "key":
                # Handle keyboard input
                if step.value == "Enter":
                    # Press Enter key
                    from selenium.webdriver.common.keys import Keys
                    self.navigator.driver.find_element(By.TAG_NAME, "body").send_keys(Keys.ENTER)
                    return True
                return False
            
            else:
                print(f"⚠️  Unknown action: {step.action}")
                return False
                
        except Exception as e:
            print(f"❌ Step execution error: {e}")
            return False


async def test_excel_scenario():
    """Test the Excel document creation scenario"""
    scenario = ExcelDocumentCreationScenario()
    result = await scenario.execute_scenario()
    
    print("\n" + "=" * 60)
    print("EXCEL SCENARIO TEST RESULTS")
    print("=" * 60)
    print(f"Scenario: {result.scenario_name}")
    print(f"Success: {'✅ Yes' if result.success else '❌ No'}")
    print(f"Steps Completed: {result.steps_completed}/{result.total_steps}")
    print(f"Execution Time: {result.execution_time:.2f} seconds")
    print(f"Screenshots: {len(result.screenshots)}")
    
    if result.screenshots:
        print("\n📸 Screenshots taken:")
        for screenshot in result.screenshots:
            print(f"   - {screenshot}")
    
    if result.errors:
        print("\n❌ Errors encountered:")
        for error in result.errors:
            print(f"   - {error}")
    
    return result.success


if __name__ == "__main__":
    asyncio.run(test_excel_scenario())
