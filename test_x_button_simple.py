#!/usr/bin/env python3
"""
Simple test to verify X button targeting logic
"""
import asyncio
import time
from excel_web_selenium_only import get_selenium_navigator

async def test_x_button_simple():
    """Simple test to verify X button targeting"""
    print("🔍 Simple X button test...")
    
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
                                    
                                    # Test the X button targeting logic
                                    print("🔍 Testing X button targeting logic...")
                                    
                                    # Strategy 1: Look for the X button directly first
                                    print("  Looking for X button directly...")
                                    x_button_selectors = [
                                        "[class*='ewaother_ClosePaneGlyph']",
                                        "[title='Close']",
                                        "img[title='Close']",
                                        "[class*='ClosePaneGlyph']"
                                    ]
                                    
                                    for x_selector in x_button_selectors:
                                        try:
                                            x_buttons = navigator.driver.find_elements("css selector", x_selector)
                                            if x_buttons:
                                                print(f"    Found {len(x_buttons)} X buttons with selector: {x_selector}")
                                                
                                                for x_button in x_buttons:
                                                    try:
                                                        class_name = x_button.get_attribute("class")
                                                        title = x_button.get_attribute("title")
                                                        print(f"      X Button: class='{class_name}', title='{title}'")
                                                        
                                                        # Try different click methods
                                                        try:
                                                            x_button.click()
                                                            print(f"      ✅ Direct click successful")
                                                            await asyncio.sleep(2)
                                                            return True
                                                        except Exception as e:
                                                            print(f"      ❌ Direct click failed: {e}")
                                                            
                                                            # Try ActionChains
                                                            try:
                                                                from selenium.webdriver.common.action_chains import ActionChains
                                                                actions = ActionChains(navigator.driver)
                                                                actions.move_to_element(x_button).click().perform()
                                                                print(f"      ✅ ActionChains click successful")
                                                                await asyncio.sleep(2)
                                                                return True
                                                            except Exception as e2:
                                                                print(f"      ❌ ActionChains click failed: {e2}")
                                                                
                                                                # Try JavaScript click
                                                                try:
                                                                    navigator.driver.execute_script("arguments[0].click();", x_button)
                                                                    print(f"      ✅ JavaScript click successful")
                                                                    await asyncio.sleep(2)
                                                                    return True
                                                                except Exception as e3:
                                                                    print(f"      ❌ JavaScript click failed: {e3}")
                                                                    
                                                                    # Try clicking the parent element
                                                                    try:
                                                                        parent = x_button.find_element("xpath", "..")
                                                                        parent.click()
                                                                        print(f"      ✅ Parent click successful")
                                                                        await asyncio.sleep(2)
                                                                        return True
                                                                    except Exception as e4:
                                                                        print(f"      ❌ Parent click failed: {e4}")
                                                                        continue
                                                        
                                                    except Exception as e:
                                                        print(f"      ❌ Error with X button: {e}")
                                                        continue
                                                
                                                break
                                                
                                        except Exception as e:
                                            print(f"    ❌ Error with X selector '{x_selector}': {e}")
                                            continue
                                    
                                    print("  ❌ No X button found or clicked")
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
    asyncio.run(test_x_button_simple())
