#!/usr/bin/env python3
"""
Test script to debug iframe detection in Excel window
"""
import asyncio
import time
from excel_web_selenium_only import get_selenium_navigator

async def test_iframe_debug():
    """Test iframe detection in Excel window"""
    print("🔍 Testing iframe detection in Excel window...")
    
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
                                    
                                    # Look for cells specifically
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
                                                cell.click()
                                                print(f"  ✅ Clicked on cell")
                                                await asyncio.sleep(2)
                                                
                                                # Try to type something
                                                try:
                                                    from selenium.webdriver.common.keys import Keys
                                                    cell.send_keys("Test Data")
                                                    print(f"  ✅ Typed 'Test Data' in cell")
                                                    
                                                    # Take screenshot
                                                    navigator.driver.save_screenshot("excel_cell_test.png")
                                                    print(f"  📸 Screenshot saved: excel_cell_test.png")
                                                    
                                                    return True
                                                except Exception as e:
                                                    print(f"  ❌ Failed to type in cell: {e}")
                                                
                                                break
                                        except Exception as e:
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
    asyncio.run(test_iframe_debug())
