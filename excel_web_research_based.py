#!/usr/bin/env python3
"""
Research-based Excel Web interaction using canvas and formula bar approach
Based on Excel Web's actual DOM structure and interaction patterns
"""

import asyncio
import time
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class ExcelWebCanvasInteractor:
    """Handles Excel Web interactions using canvas and formula bar approach"""
    
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 10)
    
    async def focus_excel_canvas(self):
        """Focus the Excel canvas/grid area"""
        print("🎯 Focusing Excel canvas...")
        
        # Try to find and click the main Excel canvas/grid
        canvas_selectors = [
            "canvas",  # Direct canvas element
            "[role='application']",  # Excel application area
            "[class*='grid']",  # Grid container
            "[class*='sheet']",  # Sheet container
            "[class*='workbook']",  # Workbook area
            "[data-testid*='grid']",  # Grid test ID
            "[aria-label*='grid']"  # Grid aria label
        ]
        
        for selector in canvas_selectors:
            try:
                elements = self.driver.find_elements("css selector", selector)
                if elements:
                    print(f"  Found {len(elements)} canvas elements with selector: {selector}")
                    
                    # Click on the first canvas element
                    canvas = elements[0]
                    try:
                        # Use JavaScript click for canvas
                        self.driver.execute_script("arguments[0].click();", canvas)
                        print(f"  ✅ Canvas focused with selector: {selector}")
                        await asyncio.sleep(1)
                        return True
                    except Exception as e:
                        print(f"  ❌ Canvas click failed: {e}")
                        continue
                        
            except Exception as e:
                print(f"  ❌ Error with selector '{selector}': {e}")
                continue
        
        print("  ❌ Could not focus Excel canvas")
        return False
    
    async def navigate_to_cell_a1(self):
        """Navigate to cell A1 using keyboard shortcuts"""
        print("📍 Navigating to cell A1...")
        
        try:
            # Send Ctrl+Home to go to A1
            actions = ActionChains(self.driver)
            actions.key_down(Keys.CONTROL).send_keys(Keys.HOME).key_up(Keys.CONTROL).perform()
            print("  ✅ Sent Ctrl+Home to navigate to A1")
            await asyncio.sleep(1)
            return True
        except Exception as e:
            print(f"  ❌ Failed to navigate to A1: {e}")
            return False
    
    async def find_formula_bar(self):
        """Find the Excel formula bar"""
        print("🔍 Looking for formula bar...")
        
        formula_bar_selectors = [
            "[aria-label*='Formula']",
            "[aria-label*='formula']",
            "[class*='formula']",
            "[class*='Formula']",
            "[role='textbox'][aria-label*='formula']",
            "input[aria-label*='formula']",
            "[data-testid*='formula']",
            "[class*='ewa-formula']"
        ]
        
        for selector in formula_bar_selectors:
            try:
                elements = self.driver.find_elements("css selector", selector)
                if elements:
                    print(f"  Found {len(elements)} formula bar elements with selector: {selector}")
                    return elements[0]
            except Exception as e:
                print(f"  ❌ Error with selector '{selector}': {e}")
                continue
        
        print("  ❌ Could not find formula bar")
        return None
    
    async def enter_data_via_formula_bar(self, data):
        """Enter data using the formula bar"""
        print(f"📝 Entering data via formula bar: {data}")
        
        # First focus the canvas
        if not await self.focus_excel_canvas():
            return False
        
        # Navigate to A1
        if not await self.navigate_to_cell_a1():
            return False
        
        # Find formula bar
        formula_bar = await self.find_formula_bar()
        if not formula_bar:
            print("  ❌ Formula bar not found, trying direct typing...")
            return await self.enter_data_direct(data)
        
        try:
            # Click on formula bar
            self.driver.execute_script("arguments[0].click();", formula_bar)
            print("  ✅ Clicked formula bar")
            await asyncio.sleep(0.5)
            
            # Clear existing content (Ctrl+A)
            actions = ActionChains(self.driver)
            actions.key_down(Keys.CONTROL).send_keys('a').key_up(Keys.CONTROL).perform()
            await asyncio.sleep(0.5)
            
            # Type the data
            formula_bar.send_keys(data)
            print(f"  ✅ Typed data: {data}")
            await asyncio.sleep(0.5)
            
            # Press Enter to commit
            formula_bar.send_keys(Keys.ENTER)
            print("  ✅ Pressed Enter to commit data")
            await asyncio.sleep(1)
            
            return True
            
        except Exception as e:
            print(f"  ❌ Formula bar entry failed: {e}")
            return await self.enter_data_direct(data)
    
    async def enter_data_direct(self, data):
        """Fallback: try direct typing to focused element"""
        print(f"📝 Trying direct data entry: {data}")
        
        try:
            # First, try to find and click on a specific cell
            print("  🔍 Looking for active cell...")
            cell_selectors = [
                "[data-testid*='cell']",
                "[class*='cell']",
                "td",
                "[role='gridcell']",
                "[aria-selected='true']",
                "[class*='selected']"
            ]
            
            cell_found = False
            for selector in cell_selectors:
                try:
                    cells = self.driver.find_elements("css selector", selector)
                    if cells:
                        print(f"    Found {len(cells)} cells with selector: {selector}")
                        # Click on the first cell to make it active
                        cell = cells[0]
                        self.driver.execute_script("arguments[0].click();", cell)
                        print(f"    ✅ Clicked on cell with selector: {selector}")
                        cell_found = True
                        await asyncio.sleep(1)
                        break
                except Exception as e:
                    print(f"    ❌ Error with cell selector '{selector}': {e}")
                    continue
            
            if not cell_found:
                print("    ⚠️  No specific cell found, trying canvas focus...")
                # Fallback to canvas focus
                await self.focus_excel_canvas()
                await self.navigate_to_cell_a1()
            
            # Now try typing with F2 to enter edit mode
            print("  🔧 Trying F2 edit mode...")
            actions = ActionChains(self.driver)
            actions.send_keys(Keys.F2).perform()
            await asyncio.sleep(0.5)
            
            # Clear any existing content
            actions.key_down(Keys.CONTROL).send_keys('a').key_up(Keys.CONTROL).perform()
            await asyncio.sleep(0.5)
            
            # Type the data
            actions.send_keys(data).perform()
            print(f"    ✅ Typed data: {data}")
            await asyncio.sleep(0.5)
            
            # Press Enter to commit
            actions.send_keys(Keys.ENTER).perform()
            print("    ✅ Pressed Enter to commit")
            await asyncio.sleep(1)
            
            return True
            
        except Exception as e:
            print(f"    ❌ F2 edit mode failed: {e}")
            
            # Final fallback: try direct typing without F2
            try:
                print("    🔧 Trying direct typing without F2...")
                actions = ActionChains(self.driver)
                actions.send_keys(data).perform()
                print(f"      ✅ Direct typing successful: {data}")
                await asyncio.sleep(0.5)
                
                actions.send_keys(Keys.ENTER).perform()
                print(f"      ✅ Pressed Enter to commit")
                await asyncio.sleep(1)
                
                return True
            except Exception as e2:
                print(f"      ❌ Direct typing also failed: {e2}")
                return False
    
    async def enter_multiple_cells(self, cell_data):
        """Enter data into multiple cells"""
        print(f"📊 Entering data into multiple cells: {cell_data}")
        
        results = []
        for cell, data in cell_data.items():
            print(f"  📝 Entering '{data}' into {cell}...")
            
            # For now, just enter into A1, A2, A3, etc.
            # In a full implementation, we'd navigate to specific cells
            success = await self.enter_data_via_formula_bar(data)
            results.append((cell, success))
            
            if success:
                # Navigate to next cell (down arrow)
                try:
                    actions = ActionChains(self.driver)
                    actions.send_keys(Keys.ARROW_DOWN).perform()
                    await asyncio.sleep(0.5)
                except Exception as e:
                    print(f"    ❌ Failed to navigate to next cell: {e}")
        
        return results

# Test function
async def test_canvas_interaction():
    """Test the canvas-based interaction approach"""
    from excel_web_selenium_only import get_selenium_navigator
    
    print("🧪 Testing canvas-based Excel interaction...")
    
    navigator = await get_selenium_navigator()
    try:
        if not await navigator.initialize():
            print("❌ Failed to initialize navigator")
            return
        
        if not await navigator.ensure_authenticated():
            print("❌ Failed to authenticate")
            return
        
        print("✅ Authenticated, navigating to Excel...")
        await navigator.navigate_to_excel_web()
        await asyncio.sleep(5)
        
        # Click "Blank workbook"
        print("🖱️  Clicking 'Blank workbook'...")
        try:
            blank_workbook = navigator.driver.find_element("xpath", "//span[contains(text(), 'Blank workbook')]")
            blank_workbook.click()
            print("✅ Clicked 'Blank workbook'")
        except Exception as e:
            print(f"❌ Failed to click 'Blank workbook': {e}")
            return
        
        # Wait for new window and switch to it
        print("⏳ Waiting for new window...")
        max_attempts = 30
        
        for attempt in range(max_attempts):
            try:
                await asyncio.sleep(2)
                all_windows = navigator.driver.window_handles
                
                if len(all_windows) > 1:
                    print(f"✅ New window detected! Switching to it...")
                    new_window = all_windows[-1]
                    navigator.driver.switch_to.window(new_window)
                    new_url = navigator.driver.current_url
                    print(f"✅ Switched to new window: {new_url}")
                    
                    if "sharepoint.com" in new_url and ":x:" in new_url:
                        print(f"✅ This is Excel! URL: {new_url}")
                        await asyncio.sleep(5)
                        
                        # Check iframes in the Excel window
                        print("🔍 Checking iframes in Excel window...")
                        iframes = navigator.driver.find_elements("css selector", "iframe")
                        print(f"📋 Found {len(iframes)} iframes in Excel window")
                        
                        for i, iframe in enumerate(iframes):
                            try:
                                src = iframe.get_attribute("src")
                                print(f"  Iframe {i}: {src}")
                                
                                if "sharepoint.com" in src and ":x:" in src:
                                    print(f"  ✅ This looks like the Excel iframe!")
                                    navigator.driver.switch_to.frame(iframe)
                                    print(f"  ✅ Switched to Excel iframe")
                                    await asyncio.sleep(3)
                                    
                                    # Wait for interface to be ready
                                    await asyncio.sleep(5)
                                    
                                    # Handle Copilot dialog
                                    print("🔍 Checking for Copilot dialog...")
                                    dialogs = navigator.driver.find_elements("css selector", "[class*='ewa-popup-ltr']")
                                    if dialogs:
                                        print(f"  ⚠️  Copilot dialog present: {len(dialogs)} dialogs found")
                                        
                                        # Dismiss with JavaScript click on X button
                                        print("  Trying to dismiss Copilot dialog...")
                                        x_buttons = navigator.driver.find_elements("css selector", "[class*='ewaother_ClosePaneGlyph']")
                                        if x_buttons:
                                            print(f"    Found {len(x_buttons)} X buttons")
                                            for x_button in x_buttons:
                                                try:
                                                    navigator.driver.execute_script("arguments[0].click();", x_button)
                                                    print(f"    ✅ JavaScript click on X button successful")
                                                    await asyncio.sleep(2)
                                                    break
                                                except Exception as e:
                                                    print(f"    ❌ JavaScript click failed: {e}")
                                                    continue
                                    else:
                                        print(f"  ✅ No Copilot dialog found")
                                    
                                    # Test canvas interaction
                                    print("🔍 Testing canvas interaction...")
                                    interactor = ExcelWebCanvasInteractor(navigator.driver)
                                    
                                    # Test data entry
                                    test_data = {
                                        "A1": "Test Data 1",
                                        "A2": "Test Data 2", 
                                        "A3": "Test Data 3"
                                    }
                                    
                                    results = await interactor.enter_multiple_cells(test_data)
                                    
                                    print("📊 Canvas interaction results:")
                                    for cell, success in results:
                                        status = "✅" if success else "❌"
                                        print(f"  {status} {cell}: {success}")
                                    
                                    # Take a screenshot to visually confirm
                                    try:
                                        import os
                                        ts = int(time.time())
                                        screenshot_dir = os.path.join(os.getcwd(), "enhanced_reports_backup", "screenshots")
                                        os.makedirs(screenshot_dir, exist_ok=True)
                                        screenshot_path = os.path.join(screenshot_dir, f"excel_canvas_result_{ts}.png")
                                        navigator.driver.save_screenshot(screenshot_path)
                                        print(f"📸 Saved screenshot: {screenshot_path}")
                                    except Exception as e:
                                        print(f"❌ Failed to save screenshot: {e}")
                                    
                                    return True
                                    
                            except Exception as e:
                                print(f"  ❌ Error with iframe {i}: {e}")
                        
                        break
                    else:
                        print(f"⚠️  New window doesn't look like Excel: {new_url}")
                        
            except Exception as e:
                print(f"⚠️  Error in check {attempt + 1}: {e}")
                await asyncio.sleep(2)
        
        print("\n🔍 Test complete!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
    finally:
        try:
            await navigator.close()
            print("✅ Browser closed")
        except:
            pass

if __name__ == "__main__":
    asyncio.run(test_canvas_interaction())
