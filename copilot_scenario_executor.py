#!/usr/bin/env python3
"""
Copilot Scenario Executor
Executes complex Copilot scenarios with enhanced AI-specific UX detection
"""

import asyncio
import json
import time
from datetime import datetime
from dataclasses import dataclass
from typing import Dict, Any, Optional, List
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import logging

from excel_scenario_telemetry import ExcelScenarioTelemetry
from ai_driven_analyzer import AIDrivenAnalyzer

@dataclass
class CopilotStep:
    """Represents a Copilot-specific step"""
    name: str
    description: str
    action: str  # 'activate_copilot', 'type_prompt', 'wait_response', 'apply_suggestion', 'verify_result'
    prompt: Optional[str] = None
    expected_ai_behavior: Optional[str] = None
    timeout: int = 30
    screenshot_label: Optional[str] = None

class CopilotScenarioExecutor:
    """Executes Copilot scenarios with enhanced AI-specific UX detection"""
    
    def __init__(self):
        self.telemetry = ExcelScenarioTelemetry()
        self.ai_analyzer = AIDrivenAnalyzer()
        self.driver = None
        self.ai_interaction_log = []
        self.trust_score = 0
        self.frustration_score = 0
        
    async def execute_copilot_chart_generation(self) -> Dict[str, Any]:
        """Execute the Copilot chart generation scenario"""
        print("🤖 Starting Copilot Chart Generation Scenario")
        print("=" * 60)
        
        try:
            # Initialize browser
            self.driver = webdriver.Chrome()
            self.driver.maximize_window()
            
            # Step 1: Navigate to Excel Web
            await self._execute_copilot_step(CopilotStep(
                name="Navigate to Excel Web",
                description="Navigate to Excel Web and create new workbook",
                action="navigate",
                timeout=15
            ))
            
            # Step 2: Dismiss Copilot dialog
            await self._execute_copilot_step(CopilotStep(
                name="Dismiss Copilot Dialog",
                description="Dismiss initial Copilot dialog if present",
                action="dismiss_copilot",
                timeout=5
            ))
            
            # Step 3: Enter sales data
            await self._execute_copilot_step(CopilotStep(
                name="Enter Sales Data",
                description="Enter sample sales data for FY 2024-2025",
                action="enter_data",
                timeout=30
            ))
            
            # Step 4: Click Copilot icon
            await self._execute_copilot_step(CopilotStep(
                name="Activate Copilot",
                description="Click Copilot icon in top ribbon to open chat pane",
                action="activate_copilot",
                timeout=10
            ))
            
            # Step 5: Wait for Copilot pane
            await self._execute_copilot_step(CopilotStep(
                name="Wait for Copilot Pane",
                description="Wait for Copilot chat pane to fully load",
                action="wait_pane",
                timeout=8
            ))
            
            # Step 6: Type Copilot prompt
            await self._execute_copilot_step(CopilotStep(
                name="Type Copilot Prompt",
                description="Enter prompt to create chart from data",
                action="type_prompt",
                prompt="Create a chart using the sales data on this sheet",
                timeout=15
            ))
            
            # Step 7: Wait for Copilot response
            await self._execute_copilot_step(CopilotStep(
                name="Wait for Copilot Response",
                description="Wait for Copilot to process and respond",
                action="wait_response",
                timeout=30
            ))
            
            # Step 8: Verify chart generation
            await self._execute_copilot_step(CopilotStep(
                name="Verify Chart Generation",
                description="Verify chart was generated and displayed",
                action="verify_result",
                timeout=15
            ))
            
            # Step 9: Take final screenshot
            await self._execute_copilot_step(CopilotStep(
                name="Take Final Screenshot",
                description="Capture final state with generated chart",
                action="screenshot",
                timeout=5
            ))
            
            # Analyze the Copilot scenario
            # Perform AI-driven analysis
            ai_analysis_result = await self._perform_ai_analysis()
            
            return {
                "success": True,
                "ai_analysis": ai_analysis_result,
                "ai_interaction_log": self.ai_interaction_log,
                "trust_score": self.trust_score,
                "frustration_score": self.frustration_score
            }
            
        except Exception as e:
            logging.error(f"Copilot scenario failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "ai_interaction_log": self.ai_interaction_log
            }
        finally:
            if self.driver:
                self.driver.quit()

    async def _execute_copilot_step(self, step: CopilotStep) -> Dict[str, Any]:
        """Execute a single Copilot step with AI-specific monitoring"""
        result = {
            "success": False,
            "ai_interaction_quality": "unknown",
            "trust_impact": 0,
            "frustration_level": 0,
            "screenshot_path": None,
            "error_message": None,
            "ai_specific_issues": []
        }
        
        start_time = time.time()
        
        try:
            print(f"🤖 {step.name}")
            print(f"   📝 {step.description}")
            
            if step.action == "navigate":
                result = await self._navigate_to_excel()
                
            elif step.action == "dismiss_copilot":
                result = await self._dismiss_copilot_dialog()
                
            elif step.action == "enter_data":
                result = await self._enter_sales_data()
                
            elif step.action == "activate_copilot":
                result = await self._activate_copilot()
                
            elif step.action == "wait_pane":
                result = await self._wait_for_copilot_pane()
                
            elif step.action == "type_prompt":
                result = await self._type_copilot_prompt(step.prompt)
                
            elif step.action == "wait_response":
                result = await self._wait_for_copilot_response()
                
            elif step.action == "verify_result":
                result = await self._verify_chart_generation()
                
            elif step.action == "screenshot":
                result = await self._take_screenshot(step.screenshot_label or step.name.lower().replace(" ", "_"))
            
            # Update AI interaction log
            self.ai_interaction_log.append({
                "step": step.name,
                "action": step.action,
                "duration": time.time() - start_time,
                "success": result["success"],
                "ai_interaction_quality": result["ai_interaction_quality"],
                "trust_impact": result["trust_impact"],
                "frustration_level": result["frustration_level"],
                "ai_specific_issues": result["ai_specific_issues"]
            })
            
            # Update cumulative scores
            self.trust_score += result["trust_impact"]
            self.frustration_score += result["frustration_level"]
            
            print(f"   ✅ Completed in {time.time() - start_time:.2f}s")
            if result["ai_specific_issues"]:
                print(f"   ⚠️  AI Issues: {', '.join(result['ai_specific_issues'])}")
            
        except Exception as e:
            result["error_message"] = str(e)
            result["frustration_level"] = 2  # High frustration on errors
            print(f"   ❌ Failed: {e}")
            
        return result

    async def _navigate_to_excel(self) -> Dict[str, Any]:
        """Navigate to Excel Web and create new workbook"""
        try:
            # Navigate directly to Excel Web
            self.driver.get("https://www.office.com/launch/excel")
            
            # Wait for Excel to load and look for the interface
            WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "[data-testid='excel-worksheet'], .excel-interface, [data-testid='excel-app'], .excel-app, .excel-worksheet"))
            )
            
            print("   ✅ Excel Web loaded successfully")
            
            # Look for "New" or "Blank workbook" button to create new workbook
            new_workbook_selectors = [
                "[data-testid='new-workbook']",
                "[aria-label*='New']",
                "[aria-label*='Blank']",
                ".new-workbook-button",
                "button[title*='New']",
                "button[title*='Blank']",
                "[data-testid='create-new-workbook']",
                ".create-new-workbook"
            ]
            
            new_workbook_created = False
            for selector in new_workbook_selectors:
                try:
                    new_btn = WebDriverWait(self.driver, 5).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                    )
                    new_btn.click()
                    print(f"   ✅ Clicked new workbook button with selector: {selector}")
                    new_workbook_created = True
                    break
                except TimeoutException:
                    continue
            
            if not new_workbook_created:
                print("   ⚠️  New workbook button not found, trying to find existing workbook...")
            
            # Wait for the workbook to be created and loaded
            WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "[data-testid='excel-worksheet'], .excel-worksheet, .excel-grid, .worksheet, [data-testid='worksheet']"))
            )
            
            print("   ✅ New workbook loaded successfully")
            
            return {
                "success": True,
                "ai_interaction_quality": "good",
                "trust_impact": 0,
                "frustration_level": 0,
                "ai_specific_issues": []
            }
            
        except Exception as e:
            return {
                "success": False,
                "ai_interaction_quality": "poor",
                "trust_impact": 0,
                "frustration_level": 2,
                "ai_specific_issues": ["excel_navigation_failed"],
                "error_message": str(e)
            }

    async def _dismiss_copilot_dialog(self) -> Dict[str, Any]:
        """Dismiss Copilot dialog if present (same approach as basic scenario)"""
        try:
            print("   🔍 Attempting to dismiss Copilot dialog...")
            await asyncio.sleep(2)
            
            # More comprehensive selectors for Copilot dialog close button (same as basic scenario)
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
                "div[title='Close']",
                "[aria-label*='Dismiss']",
                ".copilot-dialog-close",
                "[data-testid*='close']"
            ]
            
            dialog_dismissed = False
            for sel in selectors:
                try:
                    elems = self.driver.find_elements("css selector", sel)
                    if elems:
                        print(f"   ✅ Found close button with selector: {sel}")
                        # Try multiple click methods
                        try:
                            elems[0].click()
                        except:
                            try:
                                self.driver.execute_script("arguments[0].click();", elems[0])
                            except:
                                self.driver.execute_script("arguments[0].dispatchEvent(new MouseEvent('click', {bubbles: true}));", elems[0])
                        
                        await asyncio.sleep(1)
                        dialog_dismissed = True
                        print("   ✅ Copilot dialog dismissed successfully")
                        break
                except Exception as ie:
                    print(f"   ⚠️ Dismiss selector failed {sel}: {ie}")
                    continue
            
            if not dialog_dismissed:
                print("   ⚠️ Could not find Copilot dialog close button, trying alternative methods...")
                
                # Try pressing Escape key
                try:
                    actions = ActionChains(self.driver)
                    actions.send_keys(Keys.ESCAPE).perform()
                    await asyncio.sleep(1)
                    print("   ✅ Tried Escape key to dismiss dialog")
                except Exception as e:
                    print(f"   ⚠️ Escape key failed: {e}")
                
                # Try clicking outside the dialog
                try:
                    self.driver.execute_script("document.body.click();")
                    await asyncio.sleep(1)
                    print("   ✅ Tried clicking outside dialog")
                except Exception as e:
                    print(f"   ⚠️ Click outside failed: {e}")
            
            # Always proceed - the dialog might auto-dismiss or typing will dismiss it
            print("   ✅ Proceeding with scenario (dialog should be dismissed)")
            return {
                "success": True,
                "ai_interaction_quality": "good",
                "trust_impact": 0,
                "frustration_level": 0,
                "ai_specific_issues": []
            }
            
        except Exception as e:
            print(f"   ❌ Error dismissing Copilot dialog: {e}")
            print("   ✅ Proceeding anyway - dialog may auto-dismiss")
            return {
                "success": True,
                "ai_interaction_quality": "good",
                "trust_impact": 0,
                "frustration_level": 0,
                "ai_specific_issues": []
            }

    async def _enter_sales_data(self) -> Dict[str, Any]:
        """Enter sales data for FY 2024-2025"""
        try:
            # Sales data for FY 2024-2025
            data = [
                ["Month", "Sales", "Revenue", "Growth %"],
                ["Apr 2024", "1250", "$125,000", "12.5%"],
                ["May 2024", "1380", "$138,000", "10.4%"],
                ["Jun 2024", "1520", "$152,000", "10.1%"],
                ["Jul 2024", "1680", "$168,000", "10.5%"],
                ["Aug 2024", "1850", "$185,000", "10.1%"],
                ["Sep 2024", "2030", "$203,000", "9.7%"],
                ["Oct 2024", "2230", "$223,000", "9.8%"],
                ["Nov 2024", "2450", "$245,000", "9.9%"],
                ["Dec 2024", "2700", "$270,000", "10.2%"],
                ["Jan 2025", "2970", "$297,000", "10.0%"],
                ["Feb 2025", "3270", "$327,000", "10.1%"],
                ["Mar 2025", "3600", "$360,000", "10.1%"]
            ]
            
            print("   📊 Entering sales data into Excel grid...")
            
            # Try to find the Excel grid/worksheet
            grid_selectors = [
                "[data-testid='excel-worksheet']",
                ".excel-worksheet",
                ".excel-grid",
                "[data-testid='excel-grid']",
                ".worksheet"
            ]
            
            grid_found = False
            for selector in grid_selectors:
                try:
                    grid = self.driver.find_element(By.CSS_SELECTOR, selector)
                    grid_found = True
                    print(f"   ✅ Found Excel grid with selector: {selector}")
                    break
                except NoSuchElementException:
                    continue
            
            if not grid_found:
                print("   ⚠️  Excel grid not found, trying alternative approach...")
            
            # Enter data using keyboard navigation (more reliable)
            try:
                # Start from cell A1 (top-left)
                actions = ActionChains(self.driver)
                
                # Click on the first cell to activate the grid
                first_cell_selectors = [
                    "[data-testid='cell-A1']",
                    "[data-testid='cell-0-0']",
                    ".cell-A1",
                    ".cell-0-0",
                    "[data-testid='excel-cell']",
                    ".excel-cell",
                    "[data-testid='worksheet-cell']",
                    ".worksheet-cell"
                ]
                
                cell_clicked = False
                for selector in first_cell_selectors:
                    try:
                        first_cell = self.driver.find_element(By.CSS_SELECTOR, selector)
                        first_cell.click()
                        cell_clicked = True
                        print(f"   ✅ Clicked first cell with selector: {selector}")
                        break
                    except NoSuchElementException:
                        continue
                
                if not cell_clicked:
                    # Try clicking anywhere in the grid area
                    try:
                        # Look for the worksheet/grid area
                        grid_selectors = [
                            "[data-testid='excel-worksheet']",
                            ".excel-worksheet",
                            ".excel-grid",
                            "[data-testid='worksheet']",
                            ".worksheet"
                        ]
                        
                        for grid_selector in grid_selectors:
                            try:
                                grid_area = self.driver.find_element(By.CSS_SELECTOR, grid_selector)
                                grid_area.click()
                                print(f"   ✅ Clicked in grid area with selector: {grid_selector}")
                                cell_clicked = True
                                break
                            except NoSuchElementException:
                                continue
                        
                        if not cell_clicked:
                            # Last resort: click in body
                            grid_area = self.driver.find_element(By.CSS_SELECTOR, "body")
                            grid_area.click()
                            print("   ✅ Clicked in body area")
                    except:
                        pass
                
                # Enter data row by row using F2 edit mode (same as basic scenario)
                for row_idx, row_data in enumerate(data):
                    for col_idx, cell_value in enumerate(row_data):
                        # Navigate to cell using arrow keys
                        if row_idx > 0 or col_idx > 0:
                            if col_idx == 0:  # First column, go down
                                actions.send_keys(Keys.ARROW_DOWN).perform()
                            else:  # Other columns, go right
                                actions.send_keys(Keys.ARROW_RIGHT).perform()
                            await asyncio.sleep(0.1)
                        
                        # Enter data using F2 edit mode (exactly like the basic scenario)
                        actions.send_keys(Keys.F2).perform()
                        await asyncio.sleep(0.2)
                        actions.key_down(Keys.CONTROL).send_keys('a').key_up(Keys.CONTROL).perform()
                        await asyncio.sleep(0.2)
                        actions.send_keys(cell_value).perform()
                        await asyncio.sleep(0.2)
                        actions.send_keys(Keys.ENTER).perform()
                        await asyncio.sleep(0.5)
                        
                        print(f"   📝 Entered: {cell_value}")
                
                print("   ✅ Sales data entry completed")
                
                return {
                    "success": True,
                    "ai_interaction_quality": "good",
                    "trust_impact": 0,
                    "frustration_level": 0,
                    "ai_specific_issues": []
                }
                
            except Exception as e:
                print(f"   ❌ Data entry failed: {e}")
                return {
                    "success": False,
                    "ai_interaction_quality": "poor",
                    "trust_impact": 0,
                    "frustration_level": 1,
                    "ai_specific_issues": ["data_entry_failed"],
                    "error_message": str(e)
                }
            
        except Exception as e:
            return {
                "success": False,
                "ai_interaction_quality": "poor",
                "trust_impact": 0,
                "frustration_level": 1,
                "ai_specific_issues": ["data_entry_failed"],
                "error_message": str(e)
            }

    async def _activate_copilot(self) -> Dict[str, Any]:
        """Click Copilot icon to open chat pane within Excel"""
        try:
            # Look for Copilot button in Excel ribbon/toolbar
            copilot_selectors = [
                # Excel-specific Copilot selectors
                "[data-testid='excel-copilot-button']",
                "[data-testid='ribbon-copilot']",
                "[data-testid='copilot-button']",
                "[aria-label*='Copilot'][aria-label*='Excel']",
                "[title*='Copilot'][title*='Excel']",
                # General Copilot selectors within Excel context
                ".excel-copilot-button",
                ".ribbon-copilot",
                ".copilot-button",
                "[data-testid*='copilot']",
                "[aria-label*='Copilot']",
                "[title*='Copilot']",
                # Alternative selectors
                "button[aria-label*='AI']",
                "button[title*='AI']",
                "[data-testid='ai-assistant']",
                ".ai-assistant-button",
                # More specific Excel Copilot selectors
                "[data-testid='excel-ai-button']",
                ".excel-ai-button",
                "[data-testid='worksheet-copilot']",
                ".worksheet-copilot"
            ]
            
            for selector in copilot_selectors:
                try:
                    copilot_btn = WebDriverWait(self.driver, 5).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                    )
                    print(f"   ✅ Found Copilot button with selector: {selector}")
                    copilot_btn.click()
                    
                    return {
                        "success": True,
                        "ai_interaction_quality": "good",
                        "trust_impact": 1,  # Positive trust impact
                        "frustration_level": 0,
                        "ai_specific_issues": []
                    }
                except TimeoutException:
                    continue
            
            # If no Copilot button found, try looking for it in the ribbon
            print("   🔍 Copilot button not found in primary selectors, checking ribbon...")
            
            # Look for ribbon elements that might contain Copilot
            ribbon_selectors = [
                ".ribbon",
                "[data-testid='ribbon']",
                ".toolbar",
                "[data-testid='toolbar']"
            ]
            
            for ribbon_selector in ribbon_selectors:
                try:
                    ribbon = self.driver.find_element(By.CSS_SELECTOR, ribbon_selector)
                    # Look for any button that might be Copilot within the ribbon
                    copilot_buttons = ribbon.find_elements(By.CSS_SELECTOR, "button, [role='button']")
                    
                    for btn in copilot_buttons:
                        try:
                            aria_label = btn.get_attribute("aria-label") or ""
                            title = btn.get_attribute("title") or ""
                            text = btn.text or ""
                            
                            if any(keyword in (aria_label + title + text).lower() for keyword in ["copilot", "ai", "assistant"]):
                                print(f"   ✅ Found potential Copilot button: {aria_label} {title} {text}")
                                btn.click()
                                return {
                                    "success": True,
                                    "ai_interaction_quality": "good",
                                    "trust_impact": 1,
                                    "frustration_level": 0,
                                    "ai_specific_issues": []
                                }
                        except:
                            continue
                            
                except NoSuchElementException:
                    continue
            
            return {
                "success": False,
                "ai_interaction_quality": "poor",
                "trust_impact": -1,
                "frustration_level": 2,
                "ai_specific_issues": ["copilot_button_not_found"]
            }
            
        except Exception as e:
            return {
                "success": False,
                "ai_interaction_quality": "poor",
                "trust_impact": -1,
                "frustration_level": 2,
                "ai_specific_issues": ["copilot_activation_failed"],
                "error_message": str(e)
            }

    async def _wait_for_copilot_pane(self) -> Dict[str, Any]:
        """Wait for Copilot chat pane to load"""
        try:
            # Wait for Copilot pane to appear
            pane_selectors = [
                "[data-testid='copilot-pane']",
                ".copilot-pane",
                "[aria-label*='Copilot chat']",
                ".copilot-chat-pane"
            ]
            
            for selector in pane_selectors:
                try:
                    WebDriverWait(self.driver, 8).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                    )
                    return {
                        "success": True,
                        "ai_interaction_quality": "good",
                        "trust_impact": 0,
                        "frustration_level": 0,
                        "ai_specific_issues": []
                    }
                except TimeoutException:
                    continue
            
            return {
                "success": False,
                "ai_interaction_quality": "poor",
                "trust_impact": -1,
                "frustration_level": 2,
                "ai_specific_issues": ["copilot_pane_not_loaded"]
            }
            
        except Exception as e:
            return {
                "success": False,
                "ai_interaction_quality": "poor",
                "trust_impact": -1,
                "frustration_level": 2,
                "ai_specific_issues": ["pane_loading_failed"],
                "error_message": str(e)
            }

    async def _type_copilot_prompt(self, prompt: str) -> Dict[str, Any]:
        """Type prompt in Copilot chat within Excel"""
        try:
            # Find prompt input field within Excel Copilot pane
            input_selectors = [
                # Excel Copilot specific selectors
                "[data-testid='excel-copilot-input']",
                "[data-testid='copilot-input']",
                "[data-testid='ai-input']",
                "[data-testid='chat-input']",
                # General selectors
                ".copilot-input",
                ".ai-input",
                ".chat-input",
                "[aria-label*='Type your message']",
                "[aria-label*='prompt']",
                "[aria-label*='message']",
                "[placeholder*='Ask']",
                "[placeholder*='Type']",
                "[placeholder*='Message']",
                # Input elements
                "textarea[placeholder*='Ask']",
                "textarea[placeholder*='Type']",
                "input[type='text']",
                "textarea",
                "[contenteditable='true']"
            ]
            
            for selector in input_selectors:
                try:
                    input_field = WebDriverWait(self.driver, 5).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                    )
                    input_field.clear()
                    input_field.send_keys(prompt)
                    print(f"   ✅ Typed prompt with selector: {selector}")
                    
                    # Try to send the prompt
                    try:
                        input_field.send_keys(Keys.ENTER)
                        print("   ✅ Sent prompt with Enter key")
                    except:
                        # Try clicking send button
                        send_selectors = [
                            "[data-testid='send-button']",
                            "[aria-label*='Send']",
                            "[title*='Send']",
                            ".send-button",
                            "button[type='submit']"
                        ]
                        
                        for send_selector in send_selectors:
                            try:
                                send_btn = self.driver.find_element(By.CSS_SELECTOR, send_selector)
                                send_btn.click()
                                print(f"   ✅ Clicked send button with selector: {send_selector}")
                                break
                            except NoSuchElementException:
                                continue
                    
                    return {
                        "success": True,
                        "ai_interaction_quality": "good",
                        "trust_impact": 0,
                        "frustration_level": 0,
                        "ai_specific_issues": []
                    }
                except TimeoutException:
                    continue
            
            return {
                "success": False,
                "ai_interaction_quality": "poor",
                "trust_impact": -1,
                "frustration_level": 2,
                "ai_specific_issues": ["prompt_input_not_found"]
            }
            
        except Exception as e:
            return {
                "success": False,
                "ai_interaction_quality": "poor",
                "trust_impact": -1,
                "frustration_level": 2,
                "ai_specific_issues": ["prompt_typing_failed"],
                "error_message": str(e)
            }

    async def _wait_for_copilot_response(self) -> Dict[str, Any]:
        """Wait for Copilot to respond"""
        try:
            # Wait for response indicators
            response_selectors = [
                "[data-testid='copilot-response']",
                ".copilot-response",
                "[aria-label*='Copilot response']"
            ]
            
            for selector in response_selectors:
                try:
                    WebDriverWait(self.driver, 30).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                    )
                    return {
                        "success": True,
                        "ai_interaction_quality": "good",
                        "trust_impact": 1,  # Positive trust impact
                        "frustration_level": 0,
                        "ai_specific_issues": []
                    }
                except TimeoutException:
                    continue
            
            return {
                "success": False,
                "ai_interaction_quality": "poor",
                "trust_impact": -2,  # High negative trust impact
                "frustration_level": 3,  # High frustration
                "ai_specific_issues": ["copilot_no_response"]
            }
            
        except Exception as e:
            return {
                "success": False,
                "ai_interaction_quality": "poor",
                "trust_impact": -2,
                "frustration_level": 3,
                "ai_specific_issues": ["response_wait_failed"],
                "error_message": str(e)
            }

    async def _verify_chart_generation(self) -> Dict[str, Any]:
        """Verify chart was generated"""
        try:
            # Look for chart elements
            chart_selectors = [
                "[data-testid*='chart']",
                ".chart-container",
                "[aria-label*='chart']",
                "canvas",  # Chart.js charts
                "svg"  # SVG charts
            ]
            
            for selector in chart_selectors:
                try:
                    chart_element = WebDriverWait(self.driver, 5).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                    )
                    return {
                        "success": True,
                        "ai_interaction_quality": "excellent",
                        "trust_impact": 2,  # High positive trust impact
                        "frustration_level": 0,
                        "ai_specific_issues": []
                    }
                except TimeoutException:
                    continue
            
            return {
                "success": False,
                "ai_interaction_quality": "poor",
                "trust_impact": -2,
                "frustration_level": 3,
                "ai_specific_issues": ["chart_not_generated"]
            }
            
        except Exception as e:
            return {
                "success": False,
                "ai_interaction_quality": "poor",
                "trust_impact": -2,
                "frustration_level": 3,
                "ai_specific_issues": ["chart_verification_failed"],
                "error_message": str(e)
            }

    async def _take_screenshot(self, label: str) -> Dict[str, Any]:
        """Take screenshot of current state"""
        try:
            screenshot_path = f"screenshots/excel_web/copilot_{label}_{int(time.time())}.png"
            self.driver.save_screenshot(screenshot_path)
            
            return {
                "success": True,
                "ai_interaction_quality": "good",
                "trust_impact": 0,
                "frustration_level": 0,
                "screenshot_path": screenshot_path,
                "ai_specific_issues": []
            }
            
        except Exception as e:
            return {
                "success": False,
                "ai_interaction_quality": "poor",
                "trust_impact": 0,
                "frustration_level": 1,
                "ai_specific_issues": ["screenshot_failed"],
                "error_message": str(e)
            }

    async def _analyze_copilot_scenario(self, scenario_results: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze Copilot scenario with enhanced AI detection"""
        analysis = {
            "ai_trust_score": 0,
            "ai_frustration_score": 0,
            "copilot_effectiveness": 0,
            "ai_specific_craft_bugs": [],
            "trust_building_moments": [],
            "trust_breaking_moments": [],
            "recommendations": []
        }
        
        # Calculate AI trust and frustration scores
        analysis["ai_trust_score"] = max(0, min(10, 5 + scenario_results["trust_score"]))
        analysis["ai_frustration_score"] = max(0, min(10, scenario_results["frustration_score"]))
        
        # Analyze Copilot effectiveness
        successful_steps = sum(1 for step in scenario_results["steps"] if step["success"])
        total_steps = len(scenario_results["steps"])
        analysis["copilot_effectiveness"] = (successful_steps / total_steps) * 100 if total_steps > 0 else 0
        
        # Identify AI-specific craft bugs
        for step in scenario_results["steps"]:
            if step["ai_specific_issues"]:
                analysis["ai_specific_craft_bugs"].extend(step["ai_specific_issues"])
            
            if step["trust_impact"] > 0:
                analysis["trust_building_moments"].append({
                    "step": step["step"],
                    "impact": step["trust_impact"],
                    "quality": step["ai_interaction_quality"]
                })
            
            if step["trust_impact"] < 0:
                analysis["trust_breaking_moments"].append({
                    "step": step["step"],
                    "impact": step["trust_impact"],
                    "frustration": step["frustration_level"],
                    "issues": step["ai_specific_issues"]
                })
        
        # Generate recommendations
        if analysis["ai_frustration_score"] > 5:
            analysis["recommendations"].append("Reduce AI interaction friction to improve user experience")
        
        if analysis["ai_trust_score"] < 5:
            analysis["recommendations"].append("Improve AI reliability and response quality to build trust")
        
        if analysis["copilot_effectiveness"] < 70:
            analysis["recommendations"].append("Enhance Copilot functionality and error handling")
        
        return analysis
    
    async def _perform_ai_analysis(self) -> Dict[str, Any]:
        """Perform AI-driven analysis of the Copilot scenario"""
        try:
            print("🤖 Performing AI-driven analysis of Copilot scenario...")
            
            # Prepare scenario data for AI analysis
            scenario_data = {
                "scenario_name": "Copilot Chart Generation Scenario",
                "steps": self.ai_interaction_log,
                "screenshots": self.telemetry.get_screenshot_paths(),
                "telemetry": {
                    "total_time": sum(step.get("duration", 0) for step in self.ai_interaction_log),
                    "steps_completed": len(self.ai_interaction_log),
                    "total_steps": 8,
                    "performance_metrics": {
                        "trust_score": self.trust_score,
                        "frustration_score": self.frustration_score,
                        "ai_interaction_quality": "mixed" if self.ai_interaction_log else "unknown"
                    }
                }
            }
            
            # Perform AI analysis
            ai_analysis = await self.ai_analyzer.analyze_scenario(scenario_data)
            
            print(f"✅ AI analysis completed: {len(ai_analysis.get('craft_bugs', []))} craft bugs found")
            
            return ai_analysis
            
        except Exception as e:
            print(f"❌ AI analysis failed: {e}")
            return {
                "craft_bugs": [],
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

async def main():
    """Test the Copilot scenario executor"""
    executor = CopilotScenarioExecutor()
    results = await executor.execute_copilot_chart_generation()
    
    print("\n🤖 Copilot Scenario Results")
    print("=" * 60)
    print(f"Success: {results['success']}")
    print(f"AI Trust Score: {results.get('analysis', {}).get('ai_trust_score', 0)}/10")
    print(f"AI Frustration Score: {results.get('analysis', {}).get('ai_frustration_score', 0)}/10")
    print(f"Copilot Effectiveness: {results.get('analysis', {}).get('copilot_effectiveness', 0):.1f}%")
    
    if results.get('analysis', {}).get('ai_specific_craft_bugs'):
        print(f"AI-Specific Issues: {', '.join(results['analysis']['ai_specific_craft_bugs'])}")
    
    if results.get('analysis', {}).get('recommendations'):
        print("Recommendations:")
        for rec in results['analysis']['recommendations']:
            print(f"  - {rec}")

if __name__ == "__main__":
    asyncio.run(main())
