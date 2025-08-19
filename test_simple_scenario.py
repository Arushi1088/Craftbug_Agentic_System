#!/usr/bin/env python3
"""
Simple test to verify basic scenario functionality
"""
import asyncio
import time
from excel_web_selenium_only import get_selenium_navigator

async def test_simple_scenario():
    """Simple test to verify basic scenario functionality"""
    print("🔍 Testing simple scenario...")
    
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
                
                # Check for new windows
                all_windows = navigator.driver.window_handles
                
                if len(all_windows) > 1:
                    print(f"✅ New window detected! Switching to it...")
                    
                    # Switch to the new window
                    new_window = all_windows[-1]  # Get the last window
                    navigator.driver.switch_to.window(new_window)
                    new_url = navigator.driver.current_url
                    print(f"✅ Switched to new window: {new_url}")
                    
                    # Check if this looks like Excel
                    if "sharepoint.com" in new_url and ":x:" in new_url:
                        print(f"✅ This is Excel! URL: {new_url}")
                        
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
                                    
                                    # Wait a bit more for interface to be ready
                                    await asyncio.sleep(5)
                                    
                                    # Check for Copilot dialog
                                    print("🔍 Checking for Copilot dialog...")
                                    dialogs = navigator.driver.find_elements("css selector", "[class*='ewa-popup-ltr']")
                                    if dialogs:
                                        print(f"  ⚠️  Copilot dialog present: {len(dialogs)} dialogs found")
                                        
                                        # Try to dismiss it with JavaScript click on X button
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
                                    
                                    # Now try to interact with cells
                                    print("🔍 Testing cell interaction...")
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
                                                print(f"  Found {len(cells)} cells with selector: {selector}")
                                                
                                                # Click on the first cell using JavaScript
                                                cell = cells[0]
                                                try:
                                                    navigator.driver.execute_script("arguments[0].click();", cell)
                                                    print(f"  ✅ JavaScript click on cell successful")
                                                    await asyncio.sleep(2)
                                                    
                                                    # Try to type something
                                                    print(f"  📝 Trying to type data...")
                                                    try:
                                                        cell.send_keys("Test Data")
                                                        print(f"    ✅ Direct typing successful")
                                                        await asyncio.sleep(1)
                                                        print(f"  ✅ Cell interaction successful!")
                                                        return True
                                                    except Exception as e:
                                                        print(f"    ❌ Direct typing failed: {e}")
                                                        
                                                        # Try F2 then type
                                                        try:
                                                            from selenium.webdriver.common.keys import Keys
                                                            cell.send_keys(Keys.F2)
                                                            await asyncio.sleep(0.5)
                                                            cell.send_keys("Test Data F2")
                                                            await asyncio.sleep(0.5)
                                                            cell.send_keys(Keys.ENTER)
                                                            print(f"    ✅ F2 typing successful")
                                                            await asyncio.sleep(1)
                                                            print(f"  ✅ Cell interaction successful!")
                                                            return True
                                                        except Exception as e2:
                                                            print(f"    ❌ F2 typing failed: {e2}")
                                                    
                                                except Exception as e:
                                                    print(f"  ❌ JavaScript click failed: {e}")
                                                    continue
                                                
                                                break
                                                
                                        except Exception as e:
                                            print(f"  ❌ Error with selector '{selector}': {e}")
                                            continue
                                    
                                    print("  ❌ Could not interact with any cells")
                                    break
                                else:
                                    print(f"  ⚠️  This doesn't look like the Excel iframe")
                                    
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
    asyncio.run(test_simple_scenario())
