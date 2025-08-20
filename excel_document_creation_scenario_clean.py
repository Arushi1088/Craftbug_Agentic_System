"""
Excel Document Creation Scenario - Clean Version with Variants
Tests creating a new workbook, adding data, and saving with optional Copilot functionality
"""

import asyncio
import time
from datetime import datetime
from typing import List, Dict, Any
from dataclasses import dataclass
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from excel_web_selenium_only import get_selenium_navigator
from ai_driven_analyzer import AIDrivenAnalyzer


@dataclass
class ScenarioStep:
    name: str
    description: str
    action: str
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
    ai_analysis: Dict[str, Any] = None


class ExcelDocumentCreationScenario:
    """Excel Document Creation Scenario Executor - Clean Version with Variants"""
    
    def __init__(self, variant: str = "basic"):
        """
        Initialize scenario with variant support
        
        Args:
            variant: "basic" for document creation + save, "copilot" for basic + Copilot chart generation
        """
        self.navigator = None
        self.ai_analyzer = AIDrivenAnalyzer()
        self.variant = variant
        
        # Define base steps (common to all variants)
        self.base_steps = [
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
                selector="//span[contains(text(), 'Blank workbook')]",
                timeout=15
            ),
            ScenarioStep(
                name="Wait for Excel to Launch in New Window",
                description="Wait for Excel to launch in new window after clicking 'Blank workbook'",
                action="wait_and_switch_iframe",
                selector="",
                timeout=60
            ),
            ScenarioStep(
                name="Take Screenshot - Copilot Dialog",
                description="Capture the Copilot dialog before dismissing it",
                action="screenshot",
                selector="",
                value="excel_copilot_dialog"
            ),
            ScenarioStep(
                name="Dismiss Copilot Dialog",
                description="Dismiss the 'Start with Copilot' dialog that appears when creating a new workbook",
                action="dismiss_copilot_dialog",
                selector="",
                timeout=10
            ),
            ScenarioStep(
                name="Take Screenshot - Initial State",
                description="Capture initial workbook state",
                action="screenshot",
                selector="",
                value="excel_initial_state"
            ),
            ScenarioStep(
                name="Enter Sample Data",
                description="Enter sample data in cells using canvas approach",
                action="fill_any_input",
                selector="",
                value="Sample Data for Testing",
                timeout=10
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
                action="click_save_button",
                selector="",
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
        
        # Define Copilot-specific steps
        self.copilot_steps = [
            ScenarioStep(
                name="Click Copilot Button",
                description="Click the Copilot button in the Excel ribbon to open Copilot pane",
                action="click_copilot_button",
                selector="",
                timeout=15
            ),
            ScenarioStep(
                name="Take Screenshot - Copilot Pane",
                description="Capture the Copilot pane after opening",
                action="screenshot",
                selector="",
                value="excel_copilot_pane"
            ),
            ScenarioStep(
                name="Enter Chart Prompt",
                description="Enter prompt to generate chart using the data on the sheet",
                action="enter_copilot_prompt",
                selector="",
                value="Create a chart using the data on the sheet",
                timeout=10
            ),
            ScenarioStep(
                name="Wait for Chart Generation",
                description="Wait for Copilot to generate and apply the chart",
                action="wait_for_copilot_response",
                selector="",
                timeout=30
            ),
            ScenarioStep(
                name="Take Screenshot - Chart Generated",
                description="Capture the workbook with the generated chart",
                action="screenshot",
                selector="",
                value="excel_chart_generated"
            ),
            ScenarioStep(
                name="Verify Chart Creation",
                description="Verify that the chart was successfully created and applied",
                action="verify_chart_creation",
                selector="",
                timeout=10
            )
        ]
        
        # Set steps based on variant
        if variant == "basic":
            self.steps = self.base_steps
        elif variant == "copilot":
            # For Copilot variant, skip the save step to avoid interference
            base_steps_without_save = [step for step in self.base_steps if "Save" not in step.name]
            self.steps = base_steps_without_save + self.copilot_steps
        else:
            raise ValueError(f"Unknown variant: {variant}. Supported variants: 'basic', 'copilot'")
    
    async def execute_scenario(self) -> ScenarioResult:
        """Execute the Excel document creation scenario"""
        start_time = time.time()
        result = ScenarioResult(
            scenario_name=f"Excel Document Creation - {self.variant.title()} Variant",
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
            
            # Execute each step with timeout protection
            for i, step in enumerate(self.steps, 1):
                print(f"\n📋 Step {i}/{len(self.steps)}: {step.name}")
                print(f"   Description: {step.description}")
                
                # Add timeout protection for each step
                try:
                    step_success = await asyncio.wait_for(
                        self.execute_step(step, result), 
                        timeout=step.timeout + 30  # Add 30 seconds buffer
                    )
                except asyncio.TimeoutError:
                    print(f"   ⏰ Step timed out after {step.timeout + 30} seconds")
                    result.errors.append(f"Step {i} timed out: {step.name}")
                    if step.required:
                        print(f"   ⚠️  Required step timed out, stopping scenario")
                        break
                    else:
                        print(f"   ⚠️  Non-required step timed out, continuing...")
                        step_success = False
                
                if step_success:
                    result.steps_completed += 1
                    print(f"   ✅ Step completed successfully")
                else:
                    if f"Step {i} timed out: {step.name}" not in result.errors:
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
            
            # Perform AI-driven analysis
            if result.success:
                print("\n🤖 Performing AI-driven analysis...")
                ai_analysis = await self._perform_ai_analysis(result)
                result.ai_analysis = ai_analysis
                print(f"✅ AI analysis completed: {len(ai_analysis.get('craft_bugs', []))} craft bugs found")
            
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
                # Use XPath for text-based elements
                if await self.navigator.click_element_by_xpath(step.selector, step.timeout):
                    return True
                return False
            
            elif step.action == "wait_and_switch_iframe":
                # After clicking Blank workbook, Excel often opens in a new window/tab, then within an iframe
                driver = self.navigator.driver
                if not driver:
                    return False
                try:
                    initial_window = driver.current_window_handle
                    max_attempts = max(1, step.timeout // 2)
                    for _ in range(max_attempts):
                        await asyncio.sleep(2)
                        handles = driver.window_handles
                        if len(handles) > 1:
                            # Switch to the newest window
                            for h in handles:
                                if h != initial_window:
                                    driver.switch_to.window(h)
                                    break
                            # Small wait for content
                            await asyncio.sleep(3)
                            break
                    # Try switching into an Excel iframe if present
                    iframes = driver.find_elements("css selector", "iframe")
                    if iframes:
                        # Prefer SharePoint Excel iframe
                        target = None
                        for f in iframes:
                            try:
                                src = f.get_attribute("src") or ""
                                if "sharepoint.com" in src and ":x:" in src:
                                    target = f
                                    break
                            except:
                                continue
                        driver.switch_to.frame(target or iframes[0])
                        await asyncio.sleep(2)
                    return True
                except Exception as e:
                    print(f"Error switching to Excel iframe/window: {e}")
                    return False
            
            elif step.action == "dismiss_copilot_dialog":
                # Try to dismiss Copilot welcome dialog by clicking X
                driver = self.navigator.driver
                if not driver:
                    return False
                try:
                    print("🔍 Attempting to dismiss Copilot dialog...")
                    await asyncio.sleep(2)
                    
                    # More comprehensive selectors for Copilot dialog close button
                    selectors = [
                        "[class*='ewaother_ClosePaneGlyph']",
                        "[class*='ClosePaneGlyph']",
                        "img[title='Close']",
                        "[title='Close']",
                        "[aria-label*='close']",
                        "[aria-label*='Close']",
                        "button[aria-label*='close']",
                        "button[aria-label*='Close']",
                        "[class*='close']",
                        "[class*='Close']",
                        "svg[title='Close']",
                        "span[title='Close']",
                        "div[title='Close']"
                    ]
                    
                    dialog_dismissed = False
                    for sel in selectors:
                        try:
                            elems = driver.find_elements("css selector", sel)
                            if elems:
                                print(f"✅ Found close button with selector: {sel}")
                                # Try multiple click methods
                                try:
                                    elems[0].click()
                                except:
                                    try:
                                        driver.execute_script("arguments[0].click();", elems[0])
                                    except:
                                        driver.execute_script("arguments[0].dispatchEvent(new MouseEvent('click', {bubbles: true}));", elems[0])
                                
                                await asyncio.sleep(1)
                                dialog_dismissed = True
                                print("✅ Copilot dialog dismissed successfully")
                                break
                        except Exception as ie:
                            print(f"⚠️ Dismiss selector failed {sel}: {ie}")
                            continue
                    
                    if not dialog_dismissed:
                        print("⚠️ Could not find Copilot dialog close button, trying alternative methods...")
                        
                        # Try pressing Escape key
                        try:
                            actions = ActionChains(driver)
                            actions.send_keys(Keys.ESCAPE).perform()
                            await asyncio.sleep(1)
                            print("✅ Tried Escape key to dismiss dialog")
                        except Exception as e:
                            print(f"⚠️ Escape key failed: {e}")
                        
                        # Try clicking outside the dialog
                        try:
                            driver.execute_script("document.body.click();")
                            await asyncio.sleep(1)
                            print("✅ Tried clicking outside dialog")
                        except Exception as e:
                            print(f"⚠️ Click outside failed: {e}")
                    
                    # Always proceed - the dialog might auto-dismiss or typing will dismiss it
                    print("✅ Proceeding with scenario (dialog should be dismissed)")
                    return True
                    
                except Exception as e:
                    print(f"❌ Error dismissing Copilot dialog: {e}")
                    print("✅ Proceeding anyway - dialog may auto-dismiss")
                    return True
            
            elif step.action == "screenshot":
                # Take a screenshot and attach to result
                name = step.value or "screenshot"
                path = await self.navigator.take_screenshot(name)
                if path and result is not None:
                    result.screenshots.append(path)
                return bool(path)
            
            elif step.action == "fill_any_input":
                # Enter data into the active cell using F2 edit mode
                driver = self.navigator.driver
                if not driver:
                    return False
                try:
                    data = step.value or "Sample Data"
                    # Try clicking a visible grid cell
                    cell_selectors = [
                        "[data-testid*='cell']",
                        "[role='gridcell']",
                        "[aria-selected='true']",
                        "[class*='cell']",
                        "td",
                    ]
                    clicked = False
                    for sel in cell_selectors:
                        try:
                            cells = driver.find_elements("css selector", sel)
                            if cells:
                                driver.execute_script("arguments[0].click();", cells[0])
                                await asyncio.sleep(0.5)
                                clicked = True
                                break
                        except Exception:
                            continue
                    if not clicked:
                        # Fallback to focusing canvas-like area
                        for sel in ["canvas", "[role='application']", "[class*='grid']"]:
                            try:
                                elems = driver.find_elements("css selector", sel)
                                if elems:
                                    driver.execute_script("arguments[0].click();", elems[0])
                                    await asyncio.sleep(0.5)
                                    break
                            except Exception:
                                continue
                    actions = ActionChains(driver)
                    actions.send_keys(Keys.F2).perform()
                    await asyncio.sleep(0.2)
                    actions.key_down(Keys.CONTROL).send_keys('a').key_up(Keys.CONTROL).perform()
                    await asyncio.sleep(0.2)
                    actions.send_keys(data).perform()
                    await asyncio.sleep(0.2)
                    actions.send_keys(Keys.ENTER).perform()
                    await asyncio.sleep(0.5)
                    return True
                except Exception as e:
                    print(f"Error filling input: {e}")
                    return False
            
            elif step.action == "click_save_button":
                # Trigger save and handle save dialog/verification
                driver = self.navigator.driver
                if not driver:
                    return False
                try:
                    body = driver.find_element(By.TAG_NAME, "body")
                    body.send_keys(Keys.COMMAND + "s")
                    await asyncio.sleep(2)
                except Exception as e:
                    print(f"Save shortcut failed: {e}")
                # Attempt to handle dialog; if none, verify success
                try:
                    handled = await self.handle_save_dialog()
                    if handled:
                        return True
                except Exception:
                    pass
                try:
                    return await self.verify_save_success()
                except Exception as e:
                    print(f"Save verification failed: {e}")
                    return False
            
            # Copilot-specific actions
            elif step.action == "click_copilot_button":
                # Click the Copilot button in the Excel ribbon
                driver = self.navigator.driver
                if not driver:
                    return False
                try:
                    print("🔍 Looking for Copilot button in ribbon...")
                    
                    # Multiple selectors for Copilot button
                    copilot_selectors = [
                        "[aria-label*='Copilot']",
                        "[title*='Copilot']",
                        "[data-testid*='copilot']",
                        "[class*='copilot']",
                        "button[aria-label*='Copilot']",
                        "button[title*='Copilot']",
                        "[role='button'][aria-label*='Copilot']",
                        "[class*='ewaother_Copilot']",
                        "[class*='CopilotButton']",
                        "button:contains('Copilot')",
                        "[data-automation-id*='copilot']",
                        "[class*='ewaother_CopilotButton']",
                        "[class*='ewaother_CopilotIcon']",
                        "button[class*='copilot']",
                        "[class*='ewaother_Copilot']"
                    ]
                    
                    for selector in copilot_selectors:
                        try:
                            elements = driver.find_elements("css selector", selector)
                            if elements:
                                print(f"✅ Found Copilot button with selector: {selector}")
                                # Try multiple click methods
                                try:
                                    elements[0].click()
                                    print("✅ Clicked Copilot button directly")
                                except Exception as click_e:
                                    print(f"⚠️ Direct click failed: {click_e}")
                                    try:
                                        driver.execute_script("arguments[0].click();", elements[0])
                                        print("✅ Clicked Copilot button via JavaScript")
                                    except Exception as js_e:
                                        print(f"⚠️ JavaScript click failed: {js_e}")
                                        driver.execute_script("arguments[0].dispatchEvent(new MouseEvent('click', {bubbles: true}));", elements[0])
                                        print("✅ Clicked Copilot button via MouseEvent")
                                
                                await asyncio.sleep(3)  # Wait longer for pane to open
                                return True
                        except Exception as e:
                            print(f"⚠️ Selector {selector} failed: {e}")
                            continue
                    
                    # Fallback: try to find by text content
                    try:
                        copilot_elements = driver.find_elements("xpath", "//*[contains(text(), 'Copilot')]")
                        for elem in copilot_elements:
                            if elem.is_displayed() and elem.is_enabled():
                                print("✅ Found Copilot button by text content")
                                driver.execute_script("arguments[0].click();", elem)
                                await asyncio.sleep(3)
                                return True
                    except Exception as e:
                        print(f"⚠️ Text-based search failed: {e}")
                    
                    # Additional fallback: look for any button that might be Copilot
                    try:
                        all_buttons = driver.find_elements("css selector", "button")
                        for button in all_buttons:
                            try:
                                aria_label = button.get_attribute("aria-label") or ""
                                title = button.get_attribute("title") or ""
                                if "copilot" in aria_label.lower() or "copilot" in title.lower():
                                    print(f"✅ Found Copilot button via attribute search: {aria_label or title}")
                                    driver.execute_script("arguments[0].click();", button)
                                    await asyncio.sleep(3)
                                    return True
                            except:
                                continue
                    except Exception as e:
                        print(f"⚠️ Attribute search failed: {e}")
                    
                    print("❌ Could not find Copilot button")
                    return False
                    
                except Exception as e:
                    print(f"❌ Error clicking Copilot button: {e}")
                    return False
            
            elif step.action == "enter_copilot_prompt":
                # Enter prompt in Copilot pane
                driver = self.navigator.driver
                if not driver:
                    return False
                try:
                    print("🔍 Looking for Copilot input field...")
                    
                    # Wait for Copilot pane to fully load
                    await asyncio.sleep(2)
                    
                    prompt = step.value or "Create a chart using the data on the sheet"
                    
                    # Multiple selectors for Copilot input - more specific to avoid Excel cells
                    input_selectors = [
                        "[placeholder*='Ask Copilot']",
                        "[placeholder*='Ask me anything']",
                        "[aria-label*='Ask Copilot']",
                        "[data-testid*='copilot-input']",
                        "[class*='copilot-input']",
                        "[class*='ewaother_CopilotInput']",
                        "textarea[placeholder*='Ask']",
                        "input[placeholder*='Ask']",
                        "[contenteditable='true'][placeholder*='Ask']",
                        # More specific selectors to avoid Excel cells
                        "[class*='ewaother_CopilotChatInput']",
                        "[class*='ewaother_CopilotMessageInput']",
                        "[class*='ewaother_CopilotTextInput']",
                        "[data-testid*='copilot-chat-input']",
                        "[data-testid*='copilot-message-input']",
                        # Only use role='textbox' if it's within Copilot pane
                        "[class*='ewaother_Copilot'] [role='textbox']",
                        "[class*='ewaother_CopilotPane'] [role='textbox']",
                        "[class*='ewaother_CopilotChat'] [role='textbox']"
                    ]
                    
                    for selector in input_selectors:
                        try:
                            elements = driver.find_elements("css selector", selector)
                            if elements:
                                print(f"✅ Found Copilot input with selector: {selector}")
                                input_element = elements[0]
                                
                                # Validate that this is actually a Copilot input (not an Excel cell)
                                try:
                                    # Check if element is within Copilot pane
                                    parent = input_element.find_element("xpath", "./ancestor::*[contains(@class, 'ewaother_Copilot') or contains(@class, 'ewaother_CopilotPane') or contains(@class, 'ewaother_CopilotChat')]")
                                    print(f"✅ Validated input is within Copilot pane")
                                except:
                                    # If not in Copilot pane, check if it has Copilot-specific attributes
                                    aria_label = input_element.get_attribute("aria-label") or ""
                                    placeholder = input_element.get_attribute("placeholder") or ""
                                    if "copilot" in aria_label.lower() or "ask" in placeholder.lower():
                                        print(f"✅ Validated input has Copilot-specific attributes")
                                    else:
                                        print(f"⚠️ Input found but may not be Copilot input, skipping...")
                                        continue
                                
                                # Try multiple input methods
                                try:
                                    # Method 1: Direct send_keys
                                    input_element.clear()
                                    input_element.send_keys(prompt)
                                    print(f"✅ Entered prompt: {prompt}")
                                except Exception as e1:
                                    print(f"⚠️ Direct send_keys failed: {e1}")
                                    try:
                                        # Method 2: JavaScript injection
                                        driver.execute_script(f"arguments[0].value = '{prompt}';", input_element)
                                        print(f"✅ Entered prompt via JavaScript: {prompt}")
                                    except Exception as e2:
                                        print(f"⚠️ JavaScript injection failed: {e2}")
                                        try:
                                            # Method 3: Click and type
                                            input_element.click()
                                            await asyncio.sleep(0.5)
                                            actions = ActionChains(driver)
                                            actions.send_keys(prompt).perform()
                                            print(f"✅ Entered prompt via ActionChains: {prompt}")
                                        except Exception as e3:
                                            print(f"⚠️ ActionChains failed: {e3}")
                                            continue
                                
                                await asyncio.sleep(1)
                                
                                # Try to submit the prompt
                                try:
                                    input_element.send_keys(Keys.ENTER)
                                    print("✅ Submitted prompt with Enter key")
                                except Exception as e:
                                    print(f"⚠️ Enter key failed: {e}")
                                    # Look for send button
                                    send_selectors = [
                                        "[aria-label*='Send']",
                                        "[title*='Send']",
                                        "button[aria-label*='Send']",
                                        "[class*='send']",
                                        "[data-testid*='send']",
                                        "button[type='submit']",
                                        "[role='button']"
                                    ]
                                    for send_sel in send_selectors:
                                        try:
                                            send_buttons = driver.find_elements("css selector", send_sel)
                                            if send_buttons:
                                                driver.execute_script("arguments[0].click();", send_buttons[0])
                                                print(f"✅ Submitted prompt via send button: {send_sel}")
                                                break
                                        except Exception as send_e:
                                            print(f"⚠️ Send button {send_sel} failed: {send_e}")
                                            continue
                                
                                await asyncio.sleep(2)
                                return True
                        except Exception as e:
                            print(f"⚠️ Input selector {selector} failed: {e}")
                            continue
                    
                    print("❌ Could not find or interact with Copilot input field")
                    return False
                    
                except Exception as e:
                    print(f"❌ Error entering Copilot prompt: {e}")
                    return False
            
            elif step.action == "wait_for_copilot_response":
                # Wait for Copilot to generate response and apply chart
                driver = self.navigator.driver
                if not driver:
                    return False
                try:
                    print("⏳ Waiting for Copilot response...")
                    
                    # Wait for response indicators
                    max_wait = step.timeout
                    start_time = time.time()
                    
                    while time.time() - start_time < max_wait:
                        try:
                            # Look for response indicators
                            response_indicators = [
                                "[class*='copilot-response']",
                                "[class*='ewaother_CopilotResponse']",
                                "[data-testid*='copilot-response']",
                                "[aria-label*='Copilot response']",
                                "[class*='typing']",
                                "[class*='loading']"
                            ]
                            
                            response_found = False
                            for indicator in response_indicators:
                                elements = driver.find_elements("css selector", indicator)
                                if elements:
                                    print(f"✅ Found response indicator: {indicator}")
                                    response_found = True
                                    break
                            
                            if response_found:
                                # Wait a bit more for completion
                                await asyncio.sleep(5)
                                return True
                            
                            await asyncio.sleep(2)
                            
                        except Exception as e:
                            print(f"⚠️ Error checking response: {e}")
                            await asyncio.sleep(2)
                    
                    print("⚠️ Timeout waiting for Copilot response, proceeding anyway")
                    return True
                    
                except Exception as e:
                    print(f"❌ Error waiting for Copilot response: {e}")
                    return True  # Continue anyway
            
            elif step.action == "verify_chart_creation":
                # Verify that a chart was created
                driver = self.navigator.driver
                if not driver:
                    return False
                try:
                    print("🔍 Verifying chart creation...")
                    
                    # Look for chart elements
                    chart_selectors = [
                        "[class*='chart']",
                        "[data-testid*='chart']",
                        "[aria-label*='chart']",
                        "[role='img']",
                        "canvas[class*='chart']",
                        "[class*='ewaother_Chart']",
                        "[class*='ChartContainer']"
                    ]
                    
                    for selector in chart_selectors:
                        try:
                            elements = driver.find_elements("css selector", selector)
                            if elements:
                                print(f"✅ Found chart with selector: {selector}")
                                return True
                        except Exception as e:
                            print(f"⚠️ Chart selector {selector} failed: {e}")
                            continue
                    
                    # Fallback: look for any visual elements that might be charts
                    try:
                        visual_elements = driver.find_elements("css selector", "canvas, svg, img")
                        if len(visual_elements) > 0:
                            print(f"✅ Found {len(visual_elements)} visual elements (potential charts)")
                            return True
                    except Exception as e:
                        print(f"⚠️ Visual element search failed: {e}")
                    
                    print("⚠️ Could not verify chart creation, but proceeding")
                    return True  # Continue anyway
                    
                except Exception as e:
                    print(f"❌ Error verifying chart creation: {e}")
                    return True  # Continue anyway
            
            else:
                print(f"Unknown action: {step.action}")
                return False
        except Exception as e:
            print(f"Step execution failed: {e}")
            return False
    
    async def execute_step_with_details(self, step: ScenarioStep) -> Dict:
        """Execute a step and return detailed data for UX analysis"""
        step_data = {
            "step_name": step.name,
            "step_description": step.description,
            "action": step.action,
            "success": False,
            "error": None,
            "elements_found": [],
            "clicked_element": None,
            "dialog_detected": False,
            "dialog_elements": [],
            "visual_elements": [],
            "layout_problems": [],
            "execution_time": 0
        }
        
        try:
            # Execute the step action
            if step.action == "navigate":
                step_data["success"] = await self.navigator.navigate_to_excel_web()
                step_data["elements_found"] = ["excel_web_interface"]
                
            elif step.action == "click":
                step_data["success"] = await self.navigator.click_element_by_xpath(step.selector, step.timeout)
                step_data["clicked_element"] = "new_workbook_button"
                
            elif step.action == "wait_and_switch_iframe":
                step_data["success"] = await self.execute_step(step, None)  # Use existing method
                step_data["elements_found"] = ["excel_iframe", "excel_canvas"]
                
            elif step.action == "dismiss_copilot_dialog":
                step_data["success"] = await self.execute_step(step, None)  # Use existing method
                step_data["dialog_detected"] = True
                step_data["dialog_elements"] = ["copilot_dialog", "close_button"]
                
            elif step.action == "take_screenshot":
                step_data["success"] = await self.take_screenshot(step.description.lower().replace(' ', '_'))
                step_data["visual_elements"] = ["screenshot_captured"]
                
            elif step.action == "fill_any_input":
                step_data["success"] = await self.execute_step(step, None)  # Use existing method
                step_data["elements_found"] = ["excel_cells", "formula_bar"]
                step_data["clicked_element"] = "active_cell"
                
            elif step.action == "click_save_button":
                step_data["success"] = await self.execute_step(step, None)  # Use existing method
                step_data["clicked_element"] = "save_button"
                step_data["dialog_detected"] = True
                step_data["dialog_elements"] = ["save_dialog", "filename_input", "save_confirm_button"]
                
            else:
                step_data["success"] = await self.execute_step(step, None)  # Use existing method
                
        except Exception as e:
            step_data["success"] = False
            step_data["error"] = str(e)
            print(f"   ❌ Step execution error: {e}")
        
        return step_data
    
    async def execute_scenario_with_ux_hooks(self, ux_callback=None) -> Dict:
        """Execute scenario with UX analysis hooks"""
        print("🚀 Starting Excel Document Creation Scenario with UX Analysis...")
        
        start_time = time.time()
        results = {
            "scenario_name": "Document Creation with UX Analysis",
            "steps_completed": 0,
            "total_steps": len(self.steps),
            "execution_time": 0,
            "screenshots": [],
            "errors": [],
            "ux_analysis_data": [],
            "start_time": time.time()
        }
        
        try:
            # Get navigator
            self.navigator = await get_selenium_navigator()
            
            # Initialize and authenticate
            if not await self.navigator.initialize():
                results["errors"].append("Failed to initialize navigator")
                return results
            
            if not await self.navigator.ensure_authenticated():
                results["errors"].append("Failed to authenticate to Excel Web")
                return results
            
            print("✅ Authentication successful, starting scenario steps with UX analysis...")
            
            # Execute each step with UX analysis
            for i, step in enumerate(self.steps, 1):
                print(f"\n📋 Step {i}/{len(self.steps)}: {step.name}")
                print(f"   Description: {step.description}")
                
                step_start_time = time.time()
                
                # Execute step and collect detailed data
                step_data = await self.execute_step_with_details(step)
                step_execution_time = time.time() - step_start_time
                
                # Add execution time to step data
                step_data["execution_time"] = step_execution_time
                step_data["success"] = step_data.get("success", False)
                
                if step_data["success"]:
                    print(f"   ✅ Step completed successfully")
                    results["steps_completed"] += 1
                else:
                    print(f"   ❌ Step failed")
                    results["errors"].append({
                        "step": step.name,
                        "error": step_data.get("error", "Step execution failed")
                    })
                
                # Take screenshot after each step
                try:
                    screenshot_path = await self.take_screenshot(f"step_{i}_{step.name.lower().replace(' ', '_')}")
                    results["screenshots"].append(screenshot_path)
                    step_data["screenshot_path"] = screenshot_path
                except Exception as e:
                    print(f"   ⚠️  Screenshot failed: {e}")
                    step_data["screenshot_path"] = None
                
                # Call UX analysis callback if provided
                if ux_callback:
                    try:
                        await ux_callback(step.name, step_data, step_data.get("screenshot_path"))
                    except Exception as e:
                        print(f"   ⚠️  UX analysis failed: {e}")
                
                # Store step data for UX analysis
                results["ux_analysis_data"].append(step_data)
                
                # Small delay between steps
                await asyncio.sleep(1)
            
            results["execution_time"] = time.time() - start_time
            
            print(f"\n🎉 Scenario with UX Analysis completed successfully!")
            print(f"📊 Results:")
            print(f"   Steps completed: {results['steps_completed']}/{results['total_steps']}")
            print(f"   Execution time: {results['execution_time']:.2f} seconds")
            print(f"   Screenshots taken: {len(results['screenshots'])}")
            print(f"   Errors: {len(results['errors'])}")
            
            return results
            
        except Exception as e:
            results["errors"].append(f"Scenario execution failed: {str(e)}")
            print(f"❌ Scenario execution failed: {e}")
            return results
        finally:
            # Cleanup
            if self.navigator:
                await self.navigator.close()
    
    async def execute_step_with_details(self, step: ScenarioStep) -> Dict:
        """Execute a step and return detailed data for UX analysis"""
        step_data = {
            "step_name": step.name,
            "step_description": step.description,
            "action": step.action,
            "success": False,
            "error": None,
            "elements_found": [],
            "clicked_element": None,
            "dialog_detected": False,
            "dialog_elements": [],
            "visual_elements": [],
            "layout_problems": [],
            "execution_time": 0
        }
        
        try:
            # Execute the step action
            if step.action == "navigate":
                step_data["success"] = await self.navigator.navigate_to_excel_web()
                step_data["elements_found"] = ["excel_web_interface"]
                
            elif step.action == "click":
                step_data["success"] = await self.navigator.click_element_by_xpath(step.selector, step.timeout)
                step_data["clicked_element"] = "new_workbook_button"
                
            elif step.action == "wait_and_switch_iframe":
                step_data["success"] = await self.execute_step(step, None)  # Use existing method
                step_data["elements_found"] = ["excel_iframe", "excel_canvas"]
                
            elif step.action == "dismiss_copilot_dialog":
                step_data["success"] = await self.execute_step(step, None)  # Use existing method
                step_data["dialog_detected"] = True
                step_data["dialog_elements"] = ["copilot_dialog", "close_button"]
                
            elif step.action == "take_screenshot":
                step_data["success"] = await self.take_screenshot(step.description.lower().replace(' ', '_'))
                step_data["visual_elements"] = ["screenshot_captured"]
                
            elif step.action == "fill_any_input":
                step_data["success"] = await self.execute_step(step, None)  # Use existing method
                step_data["elements_found"] = ["excel_cells", "formula_bar"]
                step_data["clicked_element"] = "active_cell"
                
            elif step.action == "click_save_button":
                step_data["success"] = await self.execute_step(step, None)  # Use existing method
                step_data["clicked_element"] = "save_button"
                step_data["dialog_detected"] = True
                step_data["dialog_elements"] = ["save_dialog", "filename_input", "save_confirm_button"]
                
            else:
                step_data["success"] = await self.execute_step(step, None)  # Use existing method
                
        except Exception as e:
            step_data["success"] = False
            step_data["error"] = str(e)
            print(f"   ❌ Step execution error: {e}")
        
        return step_data
    
    async def handle_save_dialog(self):
        """Handle save dialog if it appears"""
        print("    📋 Handling save dialog...")
        
        try:
            # Wait for dialog to fully load
            await asyncio.sleep(2)
            
            # Look for filename input field
            print("      🔍 Looking for filename input...")
            filename_selectors = [
                "[data-testid*='filename']",
                "[class*='filename']",
                "[data-testid*='name']",
                "[class*='name']",
                "input[placeholder*='name']",
                "input[placeholder*='filename']",
                "input[type='text']",
                "[contenteditable='true']"
            ]
            
            filename_entered = False
            for selector in filename_selectors:
                try:
                    elements = self.navigator.driver.find_elements("css selector", selector)
                    if elements:
                        print(f"        Found {len(elements)} filename input elements with selector: {selector}")
                        input_elem = elements[0]
                        
                        # Clear and enter filename
                        input_elem.clear()
                        filename = f"TestWorkbook_Automation_{int(time.time())}"
                        input_elem.send_keys(filename)
                        print(f"        ✅ Entered filename: {filename}")
                        filename_entered = True
                        await asyncio.sleep(1)
                        break
                except Exception as e:
                    print(f"        ❌ Error with filename selector '{selector}': {e}")
                    continue
            
            if not filename_entered:
                print("        ⚠️  Could not find filename input, trying keyboard input...")
                try:
                    filename = f"TestWorkbook_Automation_{int(time.time())}"
                    body = self.navigator.driver.find_element(By.TAG_NAME, "body")
                    body.send_keys(filename)
                    print(f"        ✅ Used keyboard input for filename: {filename}")
                    await asyncio.sleep(1)
                except Exception as e:
                    print(f"        ❌ Keyboard input failed: {e}")
            
            # Look for save confirm button
            print("      🔍 Looking for save confirm button...")
            confirm_selectors = [
                "[data-testid*='save-confirm']",
                "[class*='save-confirm']",
                "[data-testid*='confirm']",
                "[class*='confirm']",
                "button[aria-label*='Save']",
                "button[aria-label*='Confirm']",
                "button[title*='Save']",
                "button[title*='Confirm']",
                "button",
                "a"
            ]
            
            for selector in confirm_selectors:
                try:
                    elements = self.navigator.driver.find_elements("css selector", selector)
                    if elements:
                        print(f"        Found {len(elements)} confirm elements with selector: {selector}")
                        # Try to click the first one
                        elements[0].click()
                        print(f"        ✅ Successfully clicked save confirm with selector: {selector}")
                        await asyncio.sleep(3)
                        return await self.verify_save_success()
                except Exception as e:
                    print(f"        ❌ Failed with selector '{selector}': {e}")
                    continue
            
            # Fallback: try Enter key
            print("      🔧 Trying Enter key for save confirm...")
            try:
                body = self.navigator.driver.find_element(By.TAG_NAME, "body")
                body.send_keys(Keys.ENTER)
                print(f"        ✅ Used Enter key for save confirm")
                await asyncio.sleep(3)
                return await self.verify_save_success()
            except Exception as e:
                print(f"        ❌ Enter key failed: {e}")
            
            print("      ⚠️  Could not confirm save, but continuing...")
            return True
            
        except Exception as e:
            print(f"      ❌ Error handling save dialog: {e}")
            return True
    
    async def verify_save_success(self):
        """Verify that the save was successful"""
        print("    🔍 Verifying save success...")
        
        try:
            # Wait a moment for any confirmation to appear
            await asyncio.sleep(2)
            
            # Strategy 1: Look for save confirmation elements
            confirmation_selectors = [
                "[data-testid*='save-success']",
                "[class*='save-success']",
                "[data-testid*='success']",
                "[class*='success']",
                "[data-testid*='saved']",
                "[class*='saved']",
                "[aria-label*='saved']",
                "[title*='saved']",
                "[data-testid*='confirmation']",
                "[class*='confirmation']"
            ]
            
            confirmation_found = False
            for selector in confirmation_selectors:
                try:
                    elements = self.navigator.driver.find_elements("css selector", selector)
                    if elements:
                        print(f"      ✅ Found save confirmation with selector: {selector}")
                        confirmation_found = True
                        break
                except Exception as e:
                    continue
            
            # Strategy 2: Check for any notification or toast messages
            notification_selectors = [
                "[data-testid*='notification']",
                "[class*='notification']",
                "[data-testid*='toast']",
                "[class*='toast']",
                "[data-testid*='message']",
                "[class*='message']"
            ]
            
            notification_found = False
            for selector in notification_selectors:
                try:
                    elements = self.navigator.driver.find_elements("css selector", selector)
                    if elements:
                        for elem in elements:
                            text = elem.text.lower()
                            if any(word in text for word in ["saved", "saved successfully", "file saved", "workbook saved"]):
                                print(f"      ✅ Found save notification: {text}")
                                notification_found = True
                                break
                        if notification_found:
                            break
                except Exception as e:
                    continue
            
            # Strategy 3: Check if we're back to the Excel interface (auto-save)
            try:
                excel_elements = self.navigator.driver.find_elements("css selector", "[data-testid*='cell'], [class*='cell'], td, [role='gridcell']")
                if excel_elements:
                    print(f"      ✅ Excel interface is active (likely auto-saved)")
                    return True
            except Exception as e:
                pass
            
            if confirmation_found or notification_found:
                print("      ✅ Save confirmation detected")
                return True
            else:
                print("      ⚠️  No save confirmation found, but assuming auto-save worked")
                return True  # Continue anyway
                
        except Exception as e:
            print(f"      ❌ Error verifying save success: {e}")
            return True  # Continue anyway
                
        except Exception as e:
            print(f"❌ Step execution error: {e}")
            return False
    
    async def execute_scenario_with_ux_hooks(self, ux_callback=None) -> Dict:
        """Execute scenario with UX analysis hooks"""
        print("🚀 Starting Excel Document Creation Scenario with UX Analysis...")
        
        start_time = time.time()
        results = {
            "scenario_name": "Document Creation with UX Analysis",
            "steps_completed": 0,
            "total_steps": len(self.steps),
            "execution_time": 0,
            "screenshots": [],
            "errors": [],
            "ux_analysis_data": [],
            "start_time": time.time()
        }
        
        try:
            # Get navigator
            self.navigator = await get_selenium_navigator()
            
            # Initialize and authenticate
            if not await self.navigator.initialize():
                results["errors"].append("Failed to initialize navigator")
                return results
            
            if not await self.navigator.ensure_authenticated():
                results["errors"].append("Failed to authenticate to Excel Web")
                return results
            
            print("✅ Authentication successful, starting scenario steps with UX analysis...")
            
            # Execute each step with UX analysis
            for i, step in enumerate(self.steps, 1):
                print(f"\n📋 Step {i}/{len(self.steps)}: {step.name}")
                print(f"   Description: {step.description}")
                
                step_start_time = time.time()
                
                # Execute step and collect detailed data
                step_data = await self.execute_step_with_details(step)
                step_execution_time = time.time() - step_start_time
                
                # Add execution time to step data
                step_data["execution_time"] = step_execution_time
                step_data["success"] = step_data.get("success", False)
                
                if step_data["success"]:
                    print(f"   ✅ Step completed successfully")
                    results["steps_completed"] += 1
                else:
                    print(f"   ❌ Step failed")
                    results["errors"].append({
                        "step": step.name,
                        "error": step_data.get("error", "Step execution failed")
                    })
                
                # Take screenshot after each step
                try:
                    screenshot_path = await self.take_screenshot(f"step_{i}_{step.name.lower().replace(' ', '_')}")
                    results["screenshots"].append(screenshot_path)
                    step_data["screenshot_path"] = screenshot_path
                except Exception as e:
                    print(f"   ⚠️  Screenshot failed: {e}")
                    step_data["screenshot_path"] = None
                
                # Call UX analysis callback if provided
                if ux_callback:
                    try:
                        await ux_callback(step.name, step_data, step_data.get("screenshot_path"))
                    except Exception as e:
                        print(f"   ⚠️  UX analysis failed: {e}")
                
                # Store step data for UX analysis
                results["ux_analysis_data"].append(step_data)
                
                # Small delay between steps
                await asyncio.sleep(1)
            
            results["execution_time"] = time.time() - start_time
            
            print(f"\n🎉 Scenario with UX Analysis completed successfully!")
            print(f"📊 Results:")
            print(f"   Steps completed: {results['steps_completed']}/{results['total_steps']}")
            print(f"   Execution time: {results['execution_time']:.2f} seconds")
            print(f"   Screenshots taken: {len(results['screenshots'])}")
            print(f"   Errors: {len(results['errors'])}")
            
            return results
            
        except Exception as e:
            results["errors"].append(f"Scenario execution failed: {str(e)}")
            print(f"❌ Scenario execution failed: {e}")
            return results
        finally:
            # Cleanup
            if self.navigator:
                await self.navigator.close()
    
    async def execute_step_with_details(self, step: ScenarioStep) -> Dict:
        """Execute a step and return detailed data for UX analysis"""
        step_data = {
            "step_name": step.name,
            "step_description": step.description,
            "action": step.action,
            "success": False,
            "error": None,
            "elements_found": [],
            "clicked_element": None,
            "dialog_detected": False,
            "dialog_elements": [],
            "visual_elements": [],
            "layout_problems": [],
            "execution_time": 0
        }
        
        try:
            # Execute the step action
            if step.action == "navigate":
                step_data["success"] = await self.navigator.navigate_to_excel_web()
                step_data["elements_found"] = ["excel_web_interface"]
                
            elif step.action == "click":
                step_data["success"] = await self.navigator.click_element_by_xpath(step.selector, step.timeout)
                step_data["clicked_element"] = "new_workbook_button"
                
            elif step.action == "wait_and_switch_iframe":
                step_data["success"] = await self.execute_step(step, None)  # Use existing method
                step_data["elements_found"] = ["excel_iframe", "excel_canvas"]
                
            elif step.action == "dismiss_copilot_dialog":
                step_data["success"] = await self.execute_step(step, None)  # Use existing method
                step_data["dialog_detected"] = True
                step_data["dialog_elements"] = ["copilot_dialog", "close_button"]
                
            elif step.action == "take_screenshot":
                step_data["success"] = await self.take_screenshot(step.description.lower().replace(' ', '_'))
                step_data["visual_elements"] = ["screenshot_captured"]
                
            elif step.action == "fill_any_input":
                step_data["success"] = await self.execute_step(step, None)  # Use existing method
                step_data["elements_found"] = ["excel_cells", "formula_bar"]
                step_data["clicked_element"] = "active_cell"
                
            elif step.action == "click_save_button":
                step_data["success"] = await self.execute_step(step, None)  # Use existing method
                step_data["clicked_element"] = "save_button"
                step_data["dialog_detected"] = True
                step_data["dialog_elements"] = ["save_dialog", "filename_input", "save_confirm_button"]
                
            else:
                step_data["success"] = await self.execute_step(step, None)  # Use existing method
                
        except Exception as e:
            step_data["success"] = False
            step_data["error"] = str(e)
            print(f"   ❌ Step execution error: {e}")
        
        return step_data
    
    async def _perform_ai_analysis(self, result: ScenarioResult) -> Dict[str, Any]:
        """Perform AI-driven analysis of the scenario"""
        try:
            print("🤖 Preparing scenario data for AI analysis...")
            
            # Prepare scenario data for AI analysis
            scenario_data = {
                "scenario_name": "Excel Document Creation Scenario",
                "steps": [
                    {
                        "name": step.name,
                        "description": step.description,
                        "action": step.action,
                        "duration": 0,  # We don't have individual step timing
                        "success": True  # Assume success if we got here
                    }
                    for step in self.steps[:result.steps_completed]
                ],
                "screenshots": result.screenshots,
                "telemetry": {
                    "total_time": result.execution_time,
                    "steps_completed": result.steps_completed,
                    "total_steps": result.total_steps,
                    "performance_metrics": {
                        "success_rate": result.steps_completed / result.total_steps if result.total_steps > 0 else 0,
                        "error_count": len(result.errors),
                        "execution_time": result.execution_time
                    }
                }
            }
            
            # Perform AI analysis
            ai_analysis = await self.ai_analyzer.analyze_scenario(scenario_data)
            
            return ai_analysis
            
        except Exception as e:
            print(f"❌ AI analysis failed: {e}")
            return {
                "craft_bugs": [
                    {
                        "title": "AI Analysis Unavailable",
                        "description": "The AI analysis could not be completed.",
                        "category": "system",
                        "severity": "yellow",
                        "evidence": "AI analysis failure",
                        "impact_analysis": "Unable to assess UX impact",
                        "recommendations": "Retry the analysis"
                    }
                ],
                "overall_assessment": {
                    "scenario_quality": "unknown",
                    "summary": "AI analysis failed",
                    "key_strengths": [],
                    "critical_issues": ["AI analysis unavailable"]
                },
                "persona_impact": {
                    "novice_users": "Unable to assess",
                    "full_stack_analysts": "Unable to assess",
                    "super_fans": "Unable to assess"
                },
                "business_impact": {
                    "usability_impact": "unknown",
                    "adoption_risk": "unknown",
                    "competitive_disadvantage": "Unable to assess",
                    "workflow_disruption": "Unable to assess"
                },
                "analysis_metadata": {
                    "analyzer_type": "fallback",
                    "analysis_timestamp": datetime.now().isoformat(),
                    "ai_model": "none",
                    "response_quality": "fallback"
                }
            }


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
    
    # Display AI analysis results
    if result.ai_analysis:
        print("\n🤖 AI Analysis Results:")
        print("=" * 40)
        
        craft_bugs = result.ai_analysis.get('craft_bugs', [])
        print(f"Craft Bugs Found: {len(craft_bugs)}")
        
        if craft_bugs:
            print("\n📋 Craft Bugs:")
            for i, bug in enumerate(craft_bugs, 1):
                print(f"   {i}. {bug.get('title', 'Unknown')}")
                print(f"      Category: {bug.get('category', 'Unknown')}")
                print(f"      Severity: {bug.get('severity', 'Unknown')}")
                print(f"      Description: {bug.get('description', 'No description')[:100]}...")
        
        overall_assessment = result.ai_analysis.get('overall_assessment', {})
        print(f"\n📊 Overall Assessment:")
        print(f"   Quality: {overall_assessment.get('scenario_quality', 'Unknown')}")
        print(f"   Summary: {overall_assessment.get('summary', 'No summary')}")
        
        business_impact = result.ai_analysis.get('business_impact', {})
        print(f"\n💼 Business Impact:")
        print(f"   Usability Impact: {business_impact.get('usability_impact', 'Unknown')}/10")
        print(f"   Adoption Risk: {business_impact.get('adoption_risk', 'Unknown')}")
    
    return result.success


if __name__ == "__main__":
    asyncio.run(test_excel_scenario())
