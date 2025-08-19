#!/usr/bin/env python3
"""
Test script to check when Copilot dialog appears and how to handle it
"""
import asyncio
import time
from excel_web_selenium_only import get_selenium_navigator

async def test_copilot_timing():
    """Test when Copilot dialog appears and how to handle it"""
    print("🧪 Testing Copilot dialog timing...")
    
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
        
        # Wait for new window and monitor for Copilot dialog
        print("⏳ Waiting for new window and monitoring for Copilot dialog...")
        max_attempts = 60  # Monitor for 2 minutes
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
                        
                        # Check iframes
                        iframes = navigator.driver.find_elements("css selector", "iframe")
                        print(f"📋 Found {len(iframes)} iframes in Excel window")
                        
                        # If there's an iframe, switch to it
                        if iframes:
                            navigator.driver.switch_to.frame(iframes[0])
                            print(f"✅ Switched to Excel iframe")
                            await asyncio.sleep(3)
                
                # Now monitor for Copilot dialog in the current context
                if excel_window_found:
                    print(f"🔍 Check {attempt + 1}/{max_attempts}: Looking for Copilot dialog...")
                    
                    # Check for Copilot dialog with comprehensive selectors
                    copilot_selectors = [
                        "[data-testid*='copilot']",
                        "[class*='copilot']",
                        "[aria-label*='copilot']",
                        "[title*='copilot']",
                        "button[aria-label*='Start with Copilot']",
                        "button[aria-label*='Not now']",
                        "button[aria-label*='Skip']",
                        "button[aria-label*='Later']",
                        "button[aria-label*='Close']",
                        "button[aria-label*='Dismiss']",
                        "[data-testid*='close']",
                        "[data-testid*='dismiss']",
                        "[class*='close']",
                        "[class*='dismiss']",
                        "[role='dialog']",
                        "[role='alertdialog']"
                    ]
                    
                    for selector in copilot_selectors:
                        try:
                            elements = navigator.driver.find_elements("css selector", selector)
                            if elements:
                                print(f"✅ Found potential dialog with selector: {selector}")
                                print(f"  Found {len(elements)} elements")
                                
                                for i, element in enumerate(elements):
                                    try:
                                        text = element.text
                                        aria_label = element.get_attribute("aria-label")
                                        title = element.get_attribute("title")
                                        class_name = element.get_attribute("class")
                                        
                                        print(f"  Element {i}: text='{text}', aria-label='{aria_label}', title='{title}', class='{class_name}'")
                                        
                                        # Check if this looks like a Copilot dialog
                                        if any(word in (text or "").lower() or word in (aria_label or "").lower() or word in (title or "").lower() or word in (class_name or "").lower()
                                               for word in ["copilot", "start with", "not now", "skip", "later", "dismiss", "close"]):
                                            print(f"  🎯 This looks like a Copilot dialog element!")
                                            
                                            # Try to click it
                                            element.click()
                                            print(f"  ✅ Clicked Copilot dialog element!")
                                            await asyncio.sleep(2)
                                            
                                            # Take screenshot after clicking
                                            navigator.driver.save_screenshot(f"copilot_dismissed_{attempt}.png")
                                            print(f"  📸 Screenshot saved: copilot_dismissed_{attempt}.png")
                                            
                                            return True
                                    except Exception as e:
                                        print(f"  ❌ Error with element {i}: {e}")
                                        continue
                        except Exception as e:
                            continue
                    
                    # Take screenshot every 10 attempts
                    if (attempt + 1) % 10 == 0:
                        navigator.driver.save_screenshot(f"copilot_check_{attempt}.png")
                        print(f"  📸 Screenshot saved: copilot_check_{attempt}.png")
                
            except Exception as e:
                print(f"⚠️  Error in check {attempt + 1}: {e}")
                await asyncio.sleep(2)
        
        print("\n🧪 Test complete!")
        
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
    asyncio.run(test_copilot_timing())

