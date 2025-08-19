#!/usr/bin/env python3
"""
Test to check which tabs are available and switch to the correct Excel tab
"""
import asyncio
import time
from excel_web_selenium_only import get_selenium_navigator

async def test_tab_check():
    """Test to check tabs and switch to correct Excel tab"""
    print("🔍 Testing tab check and switching...")
    
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
        
        # Check current page content
        print("🔍 Checking current page content...")
        try:
            page_source = navigator.driver.page_source
            if "Blank workbook" in page_source:
                print("✅ 'Blank workbook' found in current page")
            else:
                print("❌ 'Blank workbook' NOT found in current page")
            
            if "Excel" in page_source:
                print("✅ 'Excel' found in current page")
            else:
                print("❌ 'Excel' NOT found in current page")
                
        except Exception as e:
            print(f"❌ Error checking page content: {e}")
        
        # Try to find "Blank workbook" with different selectors
        print("🔍 Looking for 'Blank workbook' with different selectors...")
        selectors = [
            "//span[contains(text(), 'Blank workbook')]",
            "//div[contains(text(), 'Blank workbook')]",
            "//button[contains(text(), 'Blank workbook')]",
            "//a[contains(text(), 'Blank workbook')]",
            "[data-testid*='blank-workbook']",
            "[class*='blank-workbook']",
            "[aria-label*='Blank workbook']",
            "[title*='Blank workbook']"
        ]
        
        blank_workbook_found = False
        for selector in selectors:
            try:
                if selector.startswith("//"):
                    # XPath selector
                    elements = navigator.driver.find_elements("xpath", selector)
                else:
                    # CSS selector
                    elements = navigator.driver.find_elements("css selector", selector)
                
                if elements:
                    print(f"✅ Found {len(elements)} elements with selector: {selector}")
                    blank_workbook_found = True
                    
                    # Try to click the first element
                    try:
                        elements[0].click()
                        print(f"✅ Successfully clicked 'Blank workbook' with selector: {selector}")
                        break
                    except Exception as e:
                        print(f"❌ Failed to click with selector {selector}: {e}")
                        continue
                else:
                    print(f"❌ No elements found with selector: {selector}")
                    
            except Exception as e:
                print(f"❌ Error with selector {selector}: {e}")
                continue
        
        if not blank_workbook_found:
            print("❌ Could not find 'Blank workbook' with any selector")
            
            # Check if we need to wait for page to load
            print("⏳ Waiting for page to load and trying again...")
            await asyncio.sleep(10)
            
            # Try again after waiting
            for selector in selectors:
                try:
                    if selector.startswith("//"):
                        elements = navigator.driver.find_elements("xpath", selector)
                    else:
                        elements = navigator.driver.find_elements("css selector", selector)
                    
                    if elements:
                        print(f"✅ Found {len(elements)} elements with selector: {selector} (after waiting)")
                        try:
                            elements[0].click()
                            print(f"✅ Successfully clicked 'Blank workbook' with selector: {selector}")
                            break
                        except Exception as e:
                            print(f"❌ Failed to click with selector {selector}: {e}")
                            continue
                        
                except Exception as e:
                    print(f"❌ Error with selector {selector}: {e}")
                    continue
        
        # Wait for new window/tab to appear
        print("⏳ Waiting for new window/tab to appear...")
        max_attempts = 30
        excel_window_found = False
        
        for attempt in range(max_attempts):
            try:
                await asyncio.sleep(2)
                
                # Check for new windows
                all_windows = navigator.driver.window_handles
                print(f"📋 Attempt {attempt + 1}/{max_attempts}: Found {len(all_windows)} windows")
                
                if len(all_windows) > 1:
                    print(f"✅ New window detected! Switching to it...")
                    
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
                                    
                                    # Look for Copilot dialog
                                    print("🔍 Looking for Copilot dialog...")
                                    dialog_selectors = [
                                        "[class*='ewa-popup-ltr']",
                                        "[class*='ewa-new-user-notification']",
                                        "[class*='popup']",
                                        "[role='dialog']"
                                    ]
                                    
                                    for selector in dialog_selectors:
                                        try:
                                            dialogs = navigator.driver.find_elements("css selector", selector)
                                            if dialogs:
                                                print(f"  ✅ Found {len(dialogs)} dialog elements with selector: {selector}")
                                                
                                                for dialog in dialogs:
                                                    class_name = dialog.get_attribute("class")
                                                    text = dialog.text
                                                    print(f"    Dialog: class='{class_name}', text='{text[:100]}...'")
                                                    
                                                    # Look for X button
                                                    x_buttons = dialog.find_elements("css selector", "[aria-label*='close'], [aria-label*='dismiss'], [class*='close'], [class*='dismiss']")
                                                    for button in x_buttons:
                                                        try:
                                                            aria_label = button.get_attribute("aria-label")
                                                            class_name = button.get_attribute("class")
                                                            print(f"      X Button: aria-label='{aria_label}', class='{class_name}'")
                                                            
                                                            button.click()
                                                            print(f"      ✅ Clicked X button")
                                                            await asyncio.sleep(2)
                                                            break
                                                        except Exception as e:
                                                            print(f"      ❌ Error clicking X button: {e}")
                                                            continue
                                                    
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
    asyncio.run(test_tab_check())
