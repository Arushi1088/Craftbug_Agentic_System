#!/usr/bin/env python3
"""
Test script to verify new window detection and Copilot dialog handling
"""
import asyncio
import time
from excel_web_selenium_only import get_selenium_navigator

async def test_new_window_detection():
    """Test new window detection and Copilot dialog handling"""
    print("🧪 Testing new window detection and Copilot dialog...")
    
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
        
        # Wait for new window
        print("⏳ Waiting for new window...")
        max_attempts = 30
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
                        
                        # Wait for Excel to load
                        await asyncio.sleep(5)
                        
                        # Take screenshot
                        navigator.driver.save_screenshot("excel_new_window.png")
                        print("📸 Screenshot saved: excel_new_window.png")
                        
                        # Check for Copilot dialog
                        print("🔍 Checking for Copilot dialog...")
                        copilot_selectors = [
                            "[data-testid*='copilot']",
                            "[class*='copilot']",
                            "[aria-label*='copilot']",
                            "[title*='copilot']",
                            "button[aria-label*='Start with Copilot']",
                            "button[aria-label*='Not now']",
                            "button[aria-label*='Skip']",
                            "button[aria-label*='Later']"
                        ]
                        
                        for selector in copilot_selectors:
                            try:
                                elements = navigator.driver.find_elements("css selector", selector)
                                if elements:
                                    print(f"✅ Found Copilot dialog with selector: {selector}")
                                    print(f"  Found {len(elements)} elements")
                                    
                                    # Try to dismiss
                                    for element in elements:
                                        try:
                                            text = element.text
                                            aria_label = element.get_attribute("aria-label")
                                            title = element.get_attribute("title")
                                            print(f"  Element text: '{text}', aria-label: '{aria_label}', title: '{title}'")
                                            
                                            # Click dismiss buttons
                                            if any(word in (text or "").lower() or word in (aria_label or "").lower() or word in (title or "").lower() 
                                                   for word in ["not now", "skip", "later", "dismiss", "close"]):
                                                element.click()
                                                print(f"  ✅ Clicked dismiss button: {text or aria_label or title}")
                                                await asyncio.sleep(2)
                                                break
                                        except Exception as e:
                                            print(f"  ❌ Error clicking element: {e}")
                                            continue
                                    break
                            except Exception as e:
                                continue
                        
                        # Check iframes
                        iframes = navigator.driver.find_elements("css selector", "iframe")
                        print(f"📋 Found {len(iframes)} iframes in Excel window")
                        
                        for i, iframe in enumerate(iframes):
                            try:
                                src = iframe.get_attribute("src")
                                print(f"  Iframe {i}: {src}")
                            except:
                                print(f"  Iframe {i}: [src not accessible]")
                        
                        # If there's an iframe, switch to it
                        if iframes:
                            navigator.driver.switch_to.frame(iframes[0])
                            print(f"✅ Switched to Excel iframe")
                            await asyncio.sleep(3)
                            
                            # Check elements in iframe
                            all_elements = navigator.driver.find_elements("css selector", "*")
                            print(f"📊 Found {len(all_elements)} elements in Excel iframe")
                            
                            # Take screenshot after iframe switch
                            navigator.driver.save_screenshot("excel_iframe.png")
                            print("📸 Screenshot saved: excel_iframe.png")
                        
                        break
                    else:
                        print(f"⚠️  New window doesn't look like Excel: {new_url}")
                        # Switch back to original window and continue waiting
                        navigator.driver.switch_to.window(initial_window)
                
            except Exception as e:
                print(f"⚠️  Error checking for new window: {e}")
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
    asyncio.run(test_new_window_detection())

