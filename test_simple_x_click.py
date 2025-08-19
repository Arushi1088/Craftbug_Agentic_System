#!/usr/bin/env python3
"""
Simple test to click the X button in the Copilot dialog
"""
import asyncio
import time
from excel_web_selenium_only import get_selenium_navigator

async def test_simple_x_click():
    """Simple test to click the X button"""
    print("🔍 Simple test to click X button...")
    
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
                                    
                                    # Look for Copilot dialog
                                    print("🔍 Looking for Copilot dialog...")
                                    dialogs = navigator.driver.find_elements("css selector", "[class*='ewa-popup-ltr']")
                                    
                                    if dialogs:
                                        print(f"  ✅ Found {len(dialogs)} Copilot dialogs")
                                        
                                        for dialog in dialogs:
                                            try:
                                                class_name = dialog.get_attribute("class")
                                                print(f"    Dialog class: {class_name}")
                                                
                                                # Look for X button by text content
                                                print(f"    Looking for X button...")
                                                all_elements = dialog.find_elements("css selector", "*")
                                                print(f"    Found {len(all_elements)} elements in dialog")
                                                
                                                for elem in all_elements:
                                                    try:
                                                        elem_text = elem.text.strip()
                                                        if elem_text in ["×", "✕", "X", "x"]:
                                                            print(f"      Found X element with text: '{elem_text}'")
                                                            elem.click()
                                                            print(f"      ✅ Clicked X element")
                                                            await asyncio.sleep(2)
                                                            break
                                                    except Exception as e:
                                                        continue
                                                
                                                # If no X found by text, try by aria-label
                                                print(f"    Looking for X button by aria-label...")
                                                x_buttons = dialog.find_elements("css selector", "[aria-label*='close'], [aria-label*='dismiss']")
                                                for button in x_buttons:
                                                    try:
                                                        aria_label = button.get_attribute("aria-label")
                                                        print(f"      Found X button with aria-label: '{aria_label}'")
                                                        button.click()
                                                        print(f"      ✅ Clicked X button")
                                                        await asyncio.sleep(2)
                                                        break
                                                    except Exception as e:
                                                        print(f"      ❌ Error clicking X button: {e}")
                                                        continue
                                                
                                                break
                                                
                                            except Exception as e:
                                                print(f"    ❌ Error with dialog: {e}")
                                                continue
                                    else:
                                        print(f"  ⚠️  No Copilot dialog found")
                                    
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
    asyncio.run(test_simple_x_click())
