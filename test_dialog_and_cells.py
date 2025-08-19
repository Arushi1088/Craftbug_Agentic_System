#!/usr/bin/env python3
"""
Test to specifically debug Copilot dialog and cell interaction
"""
import asyncio
import time
from excel_web_selenium_only import get_selenium_navigator

async def test_dialog_and_cells():
    """Test Copilot dialog and cell interaction"""
    print("🔍 Testing Copilot dialog and cell interaction...")
    
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
                                    navigator.driver.save_screenshot("initial_state.png")
                                    print(f"  📸 Initial screenshot saved")
                                    
                                    # Look for Copilot dialog first
                                    print("🔍 Looking for Copilot dialog...")
                                    dialog_selectors = [
                                        "[role='dialog']",
                                        "[role='alertdialog']",
                                        "[class*='dialog']",
                                        "[class*='modal']",
                                        "[class*='popup']",
                                        "[class*='overlay']"
                                    ]
                                    
                                    dialog_found = False
                                    for selector in dialog_selectors:
                                        try:
                                            dialogs = navigator.driver.find_elements("css selector", selector)
                                            if dialogs:
                                                print(f"  ✅ Found {len(dialogs)} dialog elements with selector: {selector}")
                                                for j, dialog in enumerate(dialogs):
                                                    try:
                                                        text = dialog.text
                                                        class_name = dialog.get_attribute("class")
                                                        aria_label = dialog.get_attribute("aria-label")
                                                        print(f"    Dialog {j}: text='{text[:100]}...', class='{class_name}', aria-label='{aria_label}'")
                                                        dialog_found = True
                                                    except Exception as e:
                                                        print(f"    Dialog {j}: Error getting attributes: {e}")
                                        except Exception as e:
                                            continue
                                    
                                    if not dialog_found:
                                        print("  ⚠️  No dialog elements found")
                                    
                                    # Now try to interact with cells
                                    print("🔍 Looking for cells...")
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
                                                
                                                # Try different click methods
                                                click_success = False
                                                
                                                # Method 1: Direct click
                                                try:
                                                    cell.click()
                                                    print(f"    ✅ Direct click successful")
                                                    click_success = True
                                                except Exception as e:
                                                    print(f"    ❌ Direct click failed: {e}")
                                                
                                                # Method 2: ActionChains
                                                if not click_success:
                                                    try:
                                                        from selenium.webdriver.common.action_chains import ActionChains
                                                        actions = ActionChains(navigator.driver)
                                                        actions.move_to_element(cell).click().perform()
                                                        print(f"    ✅ ActionChains click successful")
                                                        click_success = True
                                                    except Exception as e:
                                                        print(f"    ❌ ActionChains click failed: {e}")
                                                
                                                # Method 3: JavaScript
                                                if not click_success:
                                                    try:
                                                        navigator.driver.execute_script("arguments[0].click();", cell)
                                                        print(f"    ✅ JavaScript click successful")
                                                        click_success = True
                                                    except Exception as e:
                                                        print(f"    ❌ JavaScript click failed: {e}")
                                                
                                                if click_success:
                                                    await asyncio.sleep(2)
                                                    
                                                    # Take screenshot after click
                                                    navigator.driver.save_screenshot("after_cell_click.png")
                                                    print(f"  📸 Screenshot after click saved")
                                                    
                                                    # Try to type something
                                                    print(f"  📝 Trying to type data...")
                                                    
                                                    # Method 1: Direct typing
                                                    try:
                                                        cell.send_keys("Test Data")
                                                        print(f"    ✅ Direct typing successful")
                                                        await asyncio.sleep(1)
                                                    except Exception as e:
                                                        print(f"    ❌ Direct typing failed: {e}")
                                                        
                                                        # Method 2: F2 then type
                                                        try:
                                                            from selenium.webdriver.common.keys import Keys
                                                            cell.send_keys(Keys.F2)
                                                            await asyncio.sleep(0.5)
                                                            cell.send_keys("Test Data F2")
                                                            await asyncio.sleep(0.5)
                                                            cell.send_keys(Keys.ENTER)
                                                            print(f"    ✅ F2 typing successful")
                                                            await asyncio.sleep(1)
                                                        except Exception as e:
                                                            print(f"    ❌ F2 typing failed: {e}")
                                                    
                                                    # Take final screenshot
                                                    navigator.driver.save_screenshot("after_typing.png")
                                                    print(f"  📸 Screenshot after typing saved")
                                                    
                                                    return True
                                                
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
    asyncio.run(test_dialog_and_cells())
