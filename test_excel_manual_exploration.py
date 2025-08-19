#!/usr/bin/env python3
"""
Manual exploration of current Excel interface to find correct selectors
"""

import asyncio
import json
from excel_web_selenium_only import get_selenium_navigator

async def manual_explore_excel():
    """Manually explore the current Excel interface"""
    print("🔍 Manually exploring current Excel interface...")
    
    navigator = await get_selenium_navigator()
    
    try:
        # Initialize and authenticate
        if not await navigator.initialize():
            print("❌ Failed to initialize navigator")
            return
        
        if not await navigator.ensure_authenticated():
            print("❌ Failed to authenticate")
            return
        
        print("✅ Authenticated successfully")
        
        # Click "Blank workbook" to create new workbook
        print("📝 Clicking 'Blank workbook'...")
        
        if await navigator.click_element_by_xpath("//span[contains(text(), 'Blank workbook')]", timeout=15):
            print("✅ Clicked 'Blank workbook'")
        else:
            print("❌ Could not click 'Blank workbook'")
            return
        
        # Wait for Excel to load
        print("⏳ Waiting for Excel to load...")
        await asyncio.sleep(10)
        
        # Switch to iframe
        if await navigator.wait_for_element("iframe[src*='webshell.suite.office.com']", timeout=30):
            iframe = navigator.driver.find_element("css selector", "iframe[src*='webshell.suite.office.com']")
            navigator.driver.switch_to.frame(iframe)
            print("✅ Switched to Excel iframe")
        else:
            print("❌ Could not find Excel iframe")
            return
        
        # Wait for Excel interface
        print("⏳ Waiting for Excel interface...")
        await asyncio.sleep(15)
        
        # Take screenshot
        screenshot_path = await navigator.take_screenshot("excel_manual_exploration")
        print(f"📸 Screenshot: {screenshot_path}")
        
        # Get page source to analyze
        page_source = navigator.driver.page_source
        
        # Look for any elements with common patterns
        print("\n🔍 Looking for any elements...")
        
        # Try to find any clickable elements
        all_elements = navigator.driver.find_elements("css selector", "*")
        print(f"Total elements found: {len(all_elements)}")
        
        # Look for elements with specific attributes
        element_types = {}
        
        # Elements with data-testid
        testid_elements = navigator.driver.find_elements("css selector", "[data-testid]")
        if testid_elements:
            element_types["data-testid"] = []
            for elem in testid_elements[:10]:  # First 10
                testid = elem.get_attribute("data-testid")
                element_types["data-testid"].append(testid)
                print(f"  data-testid: {testid}")
        
        # Elements with class containing 'cell'
        cell_elements = navigator.driver.find_elements("css selector", "[class*='cell']")
        if cell_elements:
            element_types["class*='cell'"] = []
            for elem in cell_elements[:5]:  # First 5
                class_name = elem.get_attribute("class")
                element_types["class*='cell'"].append(class_name)
                print(f"  class*='cell': {class_name}")
        
        # Elements with role
        role_elements = navigator.driver.find_elements("css selector", "[role]")
        if role_elements:
            element_types["role"] = []
            for elem in role_elements[:10]:  # First 10
                role = elem.get_attribute("role")
                element_types["role"].append(role)
                print(f"  role: {role}")
        
        # Elements with aria-label
        aria_elements = navigator.driver.find_elements("css selector", "[aria-label]")
        if aria_elements:
            element_types["aria-label"] = []
            for elem in aria_elements[:10]:  # First 10
                aria_label = elem.get_attribute("aria-label")
                element_types["aria-label"].append(aria_label)
                print(f"  aria-label: {aria_label}")
        
        # Try to click on any element to see what happens
        print("\n🧪 Testing element interactions...")
        
        # Try clicking on the first few elements
        for i, elem in enumerate(all_elements[:20]):
            try:
                elem_type = elem.tag_name
                elem_class = elem.get_attribute("class") or ""
                elem_id = elem.get_attribute("id") or ""
                
                # Skip body, html, head elements
                if elem_type in ['body', 'html', 'head', 'meta', 'link', 'script']:
                    continue
                
                print(f"  Testing element {i+1}: {elem_type} (class: {elem_class[:50]}, id: {elem_id[:20]})")
                
                # Try to click
                elem.click()
                print(f"    ✅ Successfully clicked!")
                
                # Wait a moment
                await asyncio.sleep(1)
                
                # Take screenshot
                screenshot_path2 = await navigator.take_screenshot(f"excel_after_click_{i+1}")
                print(f"    📸 Screenshot: {screenshot_path2}")
                
                # Check if any input field appeared
                input_elements = navigator.driver.find_elements("css selector", "input, [contenteditable='true']")
                if input_elements:
                    print(f"    🎯 Found {len(input_elements)} input elements!")
                    for j, input_elem in enumerate(input_elements[:3]):
                        input_type = input_elem.get_attribute("type") or "contenteditable"
                        input_class = input_elem.get_attribute("class") or ""
                        print(f"      Input {j+1}: type={input_type}, class={input_class[:50]}")
                    
                    # Try to enter text
                    if input_elements:
                        input_elem = input_elements[0]
                        input_elem.send_keys("Test Data")
                        print(f"    ✅ Entered test data!")
                        
                        # Take final screenshot
                        screenshot_path3 = await navigator.take_screenshot(f"excel_with_data_{i+1}")
                        print(f"    📸 Final screenshot: {screenshot_path3}")
                        break
                
                break  # Stop after first successful click
                
            except Exception as e:
                print(f"    ❌ Failed to interact: {e}")
                continue
        
        # Save exploration results
        exploration_data = {
            "total_elements": len(all_elements),
            "element_types": element_types,
            "screenshots": [screenshot_path, screenshot_path2 if 'screenshot_path2' in locals() else None, screenshot_path3 if 'screenshot_path3' in locals() else None]
        }
        
        with open("excel_manual_exploration.json", "w") as f:
            json.dump(exploration_data, f, indent=2)
        
        print(f"\n💾 Manual exploration data saved")
        
    except Exception as e:
        print(f"❌ Error during manual exploration: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        if navigator.driver:
            try:
                navigator.driver.switch_to.default_content()
            except:
                pass
            await navigator.close()

if __name__ == "__main__":
    asyncio.run(manual_explore_excel())
