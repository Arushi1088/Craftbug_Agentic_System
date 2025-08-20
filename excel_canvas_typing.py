"""
Excel Canvas Typing Utility
Handles typing into Excel Web canvas elements
"""

import asyncio
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains


class ExcelCanvasTyper:
    """Utility class for typing into Excel Web canvas"""
    
    def __init__(self, driver):
        self.driver = driver
    
    async def focus_canvas(self):
        """Focus the Excel canvas for typing"""
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
                    
                    # Click on the first canvas element using JavaScript
                    canvas = elements[0]
                    try:
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
    
    async def navigate_to_a1(self):
        """Navigate to cell A1 using Ctrl+Home"""
        try:
            actions = ActionChains(self.driver)
            actions.key_down(Keys.CONTROL).send_keys(Keys.HOME).key_up(Keys.CONTROL).perform()
            print("  ✅ Sent Ctrl+Home to navigate to A1")
            await asyncio.sleep(1)
            return True
        except Exception as e:
            print(f"  ❌ Failed to navigate to A1: {e}")
            return False
    
    async def type_data(self, data_list):
        """Type data into Excel cells using canvas approach"""
        success_count = 0
        
        for i, data in enumerate(data_list):
            try:
                print(f"  📝 Entering data {i+1}: {data}")
                
                # Type the data directly
                actions = ActionChains(self.driver)
                actions.send_keys(data).perform()
                print(f"    ✅ Typed: {data}")
                await asyncio.sleep(0.5)
                
                # Press Enter to commit
                actions.send_keys(Keys.ENTER).perform()
                print(f"    ✅ Pressed Enter to commit")
                await asyncio.sleep(1)
                
                success_count += 1
                
                # Navigate to next cell (down arrow) for next iteration
                if i < len(data_list) - 1:
                    actions.send_keys(Keys.ARROW_DOWN).perform()
                    await asyncio.sleep(0.5)
                    
            except Exception as e:
                print(f"    ❌ Failed to enter data {i+1}: {e}")
                continue
        
        print(f"  📊 Successfully entered {success_count}/{len(data_list)} data entries")
        return success_count > 0
    
    async def dismiss_copilot_dialog(self):
        """Dismiss the Copilot dialog if present"""
        print("🤖 Checking for Copilot dialog...")
        
        try:
            dialogs = self.driver.find_elements("css selector", "[class*='ewa-popup-ltr']")
            if dialogs:
                print(f"  ⚠️  Copilot dialog present: {len(dialogs)} dialogs found")
                
                # Try to dismiss the dialog by clicking the X button
                print("  Trying to dismiss Copilot dialog...")
                x_button_selectors = [
                    "[class*='ewaother_ClosePaneGlyph']",
                    "[title='Close']",
                    "img[title='Close']",
                    "[class*='ClosePaneGlyph']"
                ]
                
                for x_selector in x_button_selectors:
                    try:
                        x_buttons = self.driver.find_elements("css selector", x_selector)
                        if x_buttons:
                            print(f"    Found {len(x_buttons)} X buttons with selector: {x_selector}")
                            
                            for x_button in x_buttons:
                                try:
                                    class_name = x_button.get_attribute("class")
                                    title = x_button.get_attribute("title")
                                    print(f"      X Button: class='{class_name}', title='{title}'")
                                    
                                    # Try JavaScript click (this worked in our test)
                                    try:
                                        self.driver.execute_script("arguments[0].click();", x_button)
                                        print(f"      ✅ JavaScript click successful")
                                        await asyncio.sleep(2)
                                        return True
                                    except Exception as e:
                                        print(f"      ❌ JavaScript click failed: {e}")
                                        continue
                                        
                                except Exception as e:
                                    print(f"      ❌ Error with X button: {e}")
                                    continue
                            
                            break
                            
                    except Exception as e:
                        print(f"    ❌ Error with X selector '{x_selector}': {e}")
                        continue
            else:
                print("  ✅ No Copilot dialog found")
                
        except Exception as e:
            print(f"  ❌ Error checking for Copilot dialog: {e}")
        
        return False

