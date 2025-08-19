#!/usr/bin/env python3
"""
Test to specifically target and click the X button in the Copilot dialog
"""
import asyncio
import time
from excel_web_selenium_only import get_selenium_navigator

async def test_x_button_click():
    """Test clicking the X button in Copilot dialog"""
    print("🔍 Testing X button click in Copilot dialog...")
    
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
        
        # Get initial window handle
        initial_window = navigator.driver.current_window_handle
        initial_url = navigator.driver.current_url
        print(f"📋 Initial window: {initial_window}")
        print(f"📋 Initial URL: {initial_url}")
        
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
        excel_window_found = False
        
        for attempt in range(max_attempts):
            try:
                await asyncio.sleep(2)
                
                # Check for new windows
                all_windows = navigator.driver.window_handles
                
                if len(all_windows) > 1 and not excel_window_found:
                    print(f"📋 Attempt {attempt + 1}/{max_attempts}: Found {len(all_windows)} windows")
                    
                    # Switch to the new window
                    new_window = [w for w in all_windows if w != initial_window][0]
                    navigator.driver.switch_to.window(new_window)
                    new_url = navigator.driver.current_url
                    print(f"✅ Switched to new window: {new_url}")
                    
                    # Check if this looks like Excel
                    if "sharepoint.com" in new_url and ":x:" in new_url:
                        print(f"✅ This is Excel! URL: {new_url}")
                        excel_window_found = True
                        
                        # Wait for Excel to load
                        await asyncio.sleep(5)
                        
                        # Check iframes in the Excel window
                        print("🔍 Checking iframes in Excel window...")
                        iframes = navigator.driver.find_elements("css selector", "iframe")
                        print(f"📋 Found {len(iframes)} iframes in Excel window")
                        
                        for i, iframe in enumerate(iframes):
                            try:
                                src = iframe.get_attribute("src")
                                print(f"  Iframe {i}: {src}")
                                
                                # Check if this is the Excel iframe
                                if "sharepoint.com" in src and ":x:" in src:
                                    print(f"  ✅ This looks like the Excel iframe!")
                                    
                                    # Switch to this iframe
                                    navigator.driver.switch_to.frame(iframe)
                                    print(f"  ✅ Switched to Excel iframe")
                                    await asyncio.sleep(3)
                                    
                                    # Check elements in iframe
                                    all_elements = navigator.driver.find_elements("css selector", "*")
                                    print(f"  📊 Found {len(all_elements)} elements in Excel iframe")
                                    
                                    # Take initial screenshot
                                    navigator.driver.save_screenshot("before_x_click.png")
                                    print(f"  📸 Screenshot before X click saved")
                                    
                                    # Look for Copilot dialog specifically
                                    print("🔍 Looking for Copilot dialog...")
                                    dialog_selectors = [
                                        "[class*='ewa-popup-ltr']",
                                        "[class*='ewa-new-user-notification']",
                                        "[class*='popup']",
                                        "[role='dialog']"
                                    ]
                                    
                                    dialog_found = False
                                    for selector in dialog_selectors:
                                        try:
                                            dialogs = navigator.driver.find_elements("css selector", selector)
                                            if dialogs:
                                                print(f"  ✅ Found {len(dialogs)} dialog elements with selector: {selector}")
                                                dialog_found = True
                                                
                                                for j, dialog in enumerate(dialogs):
                                                    try:
                                                        class_name = dialog.get_attribute("class")
                                                        text = dialog.text
                                                        print(f"    Dialog {j}: class='{class_name}', text='{text[:100]}...'")
                                                        
                                                        # Try multiple approaches to find and click the X button
                                                        
                                                        # Approach 1: Look for X button by text content
                                                        print(f"      Approach 1: Looking for X button by text...")
                                                        x_elements = dialog.find_elements("css selector", "*")
                                                        for elem in x_elements:
                                                            try:
                                                                elem_text = elem.text.strip()
                                                                if elem_text in ["×", "✕", "X", "x", "Close", "close"]:
                                                                    print(f"        Found X element with text: '{elem_text}'")
                                                                    elem.click()
                                                                    print(f"        ✅ Clicked X element with text: '{elem_text}'")
                                                                    await asyncio.sleep(2)
                                                                    break
                                                            except Exception as e:
                                                                continue
                                                        
                                                        # Approach 2: Look for X button by aria-label
                                                        print(f"      Approach 2: Looking for X button by aria-label...")
                                                        x_buttons = dialog.find_elements("css selector", "[aria-label*='close'], [aria-label*='dismiss'], [aria-label*='Close'], [aria-label*='Dismiss']")
                                                        for button in x_buttons:
                                                            try:
                                                                aria_label = button.get_attribute("aria-label")
                                                                print(f"        Found X button with aria-label: '{aria_label}'")
                                                                button.click()
                                                                print(f"        ✅ Clicked X button with aria-label: '{aria_label}'")
                                                                await asyncio.sleep(2)
                                                                break
                                                            except Exception as e:
                                                                print(f"        ❌ Error clicking X button: {e}")
                                                                continue
                                                        
                                                        # Approach 3: Look for X button by class
                                                        print(f"      Approach 3: Looking for X button by class...")
                                                        x_buttons = dialog.find_elements("css selector", "[class*='close'], [class*='dismiss'], [class*='Close'], [class*='Dismiss']")
                                                        for button in x_buttons:
                                                            try:
                                                                class_name = button.get_attribute("class")
                                                                print(f"        Found X button with class: '{class_name}'")
                                                                button.click()
                                                                print(f"        ✅ Clicked X button with class: '{class_name}'")
                                                                await asyncio.sleep(2)
                                                                break
                                                            except Exception as e:
                                                                print(f"        ❌ Error clicking X button: {e}")
                                                                continue
                                                        
                                                        # Approach 4: Click in top-right corner of dialog
                                                        print(f"      Approach 4: Clicking in top-right corner of dialog...")
                                                        try:
                                                            location = dialog.location
                                                            size = dialog.size
                                                            print(f"        Dialog location: {location}, size: {size}")
                                                            
                                                            # Calculate top-right corner
                                                            x = location['x'] + size['width'] - 30  # 30px from right edge
                                                            y = location['y'] + 30  # 30px from top edge
                                                            
                                                            from selenium.webdriver.common.action_chains import ActionChains
                                                            actions = ActionChains(navigator.driver)
                                                            actions.move_by_offset(x, y).click().perform()
                                                            print(f"        ✅ Clicked at position ({x}, {y})")
                                                            await asyncio.sleep(2)
                                                        except Exception as e:
                                                            print(f"        ❌ Error clicking in corner: {e}")
                                                        
                                                        # Approach 5: Try JavaScript click on dialog
                                                        print(f"      Approach 5: JavaScript click on dialog...")
                                                        try:
                                                            navigator.driver.execute_script("arguments[0].click();", dialog)
                                                            print(f"        ✅ JavaScript click on dialog")
                                                            await asyncio.sleep(2)
                                                        except Exception as e:
                                                            print(f"        ❌ JavaScript click failed: {e}")
                                                        
                                                        break
                                                        
                                                    except Exception as e:
                                                        print(f"    ❌ Error with dialog {j}: {e}")
                                                        continue
                                                
                                                break
                                                
                                        except Exception as e:
                                            print(f"  ❌ Error with selector '{selector}': {e}")
                                            continue
                                    
                                    if not dialog_found:
                                        print("  ⚠️  No dialog elements found")
                                    
                                    # Take screenshot after attempts
                                    navigator.driver.save_screenshot("after_x_click.png")
                                    print(f"  📸 Screenshot after X click attempts saved")
                                    
                                    # Now try to interact with cells
                                    print("🔍 Now trying to interact with cells...")
                                    cell_selectors = [
                                        "[data-row='0'][data-col='0']",  # A1 cell
                                        "[role='gridcell']",  # Any grid cell
                                        "[class*='cell']",  # Any cell-like element
                                        "td"  # Table cells
                                    ]
                                    
                                    for selector in cell_selectors:
                                        try:
                                            cells = navigator.driver.find_elements("css selector", selector)
                                            if cells:
                                                print(f"  ✅ Found {len(cells)} cells with selector: {selector}")
                                                
                                                # Try to click on the first cell
                                                cell = cells[0]
                                                print(f"  🖱️  Trying to click on cell...")
                                                
                                                try:
                                                    cell.click()
                                                    print(f"    ✅ Cell click successful")
                                                    await asyncio.sleep(2)
                                                    
                                                    # Try to type something
                                                    try:
                                                        cell.send_keys("Test Data")
                                                        print(f"    ✅ Typing successful")
                                                        await asyncio.sleep(1)
                                                    except Exception as e:
                                                        print(f"    ❌ Typing failed: {e}")
                                                    
                                                except Exception as e:
                                                    print(f"    ❌ Cell click failed: {e}")
                                                
                                                break
                                                
                                        except Exception as e:
                                            print(f"  ❌ Error with selector '{selector}': {e}")
                                            continue
                                    
                                    break
                                else:
                                    print(f"  ⚠️  This doesn't look like the Excel iframe")
                                    
                            except Exception as e:
                                print(f"  ❌ Error with iframe {i}: {e}")
                        
                        break
                    else:
                        print(f"⚠️  New window doesn't look like Excel: {new_url}")
                        # Switch back to original window and continue waiting
                        navigator.driver.switch_to.window(initial_window)
                
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
    asyncio.run(test_x_button_click())
