#!/usr/bin/env python3
"""
Focused exploration to find correct Excel cell selectors
"""

import asyncio
import json
import time
from excel_web_selenium_only import get_selenium_navigator

async def find_excel_cell_selectors():
    """Find the correct selectors for Excel cells and input fields"""
    print("🎯 Finding Excel cell selectors...")
    
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
        
        # Wait longer for Excel interface to fully load
        print("⏳ Waiting for Excel interface to fully load...")
        await asyncio.sleep(20)
        
        # Take initial screenshot
        screenshot_path1 = await navigator.take_screenshot("excel_cell_exploration_initial")
        print(f"📸 Initial screenshot: {screenshot_path1}")
        
        # Get page source for analysis
        page_source = navigator.driver.page_source
        
        # Look for any elements systematically
        print("\n🔍 Systematic element exploration...")
        
        # 1. Look for any clickable elements
        clickable_selectors = [
            "button",
            "a",
            "[role='button']",
            "[tabindex]",
            "[onclick]"
        ]
        
        clickable_elements = {}
        for selector in clickable_selectors:
            try:
                elements = navigator.driver.find_elements("css selector", selector)
                if elements:
                    clickable_elements[selector] = len(elements)
                    print(f"  {selector}: {len(elements)} elements")
            except Exception as e:
                print(f"  ❌ Error with {selector}: {e}")
        
        # 2. Look for grid/table elements
        grid_selectors = [
            "table",
            "[role='grid']",
            "[role='table']",
            "[class*='grid']",
            "[class*='table']",
            "[data-testid*='grid']",
            "[data-testid*='table']"
        ]
        
        grid_elements = {}
        for selector in grid_selectors:
            try:
                elements = navigator.driver.find_elements("css selector", selector)
                if elements:
                    grid_elements[selector] = len(elements)
                    print(f"  {selector}: {len(elements)} elements")
            except Exception as e:
                print(f"  ❌ Error with {selector}: {e}")
        
        # 3. Look for cell-like elements
        cell_selectors = [
            "td",
            "th",
            "[role='cell']",
            "[role='gridcell']",
            "[class*='cell']",
            "[data-testid*='cell']",
            "[data-cell]",
            "[aria-label*='cell']"
        ]
        
        cell_elements = {}
        for selector in cell_selectors:
            try:
                elements = navigator.driver.find_elements("css selector", selector)
                if elements:
                    cell_elements[selector] = len(elements)
                    print(f"  {selector}: {len(elements)} elements")
                    
                    # Get details of first few elements
                    for i, elem in enumerate(elements[:3]):
                        attrs = {}
                        for attr in ['class', 'id', 'data-testid', 'role', 'aria-label', 'data-cell']:
                            try:
                                value = elem.get_attribute(attr)
                                if value:
                                    attrs[attr] = value
                            except:
                                pass
                        print(f"    Element {i+1}: {attrs}")
            except Exception as e:
                print(f"  ❌ Error with {selector}: {e}")
        
        # 4. Look for input elements
        input_selectors = [
            "input",
            "[contenteditable='true']",
            "[contenteditable]",
            "[data-testid*='input']",
            "[class*='input']",
            "[role='textbox']",
            "[aria-label*='input']"
        ]
        
        input_elements = {}
        for selector in input_selectors:
            try:
                elements = navigator.driver.find_elements("css selector", selector)
                if elements:
                    input_elements[selector] = len(elements)
                    print(f"  {selector}: {len(elements)} elements")
                    
                    # Get details of first few elements
                    for i, elem in enumerate(elements[:3]):
                        attrs = {}
                        for attr in ['type', 'class', 'id', 'data-testid', 'contenteditable', 'role']:
                            try:
                                value = elem.get_attribute(attr)
                                if value:
                                    attrs[attr] = value
                            except:
                                pass
                        print(f"    Element {i+1}: {attrs}")
            except Exception as e:
                print(f"  ❌ Error with {selector}: {e}")
        
        # 5. Try clicking on different types of elements to see what happens
        print("\n🧪 Testing element interactions...")
        
        # Try clicking on the first cell-like element
        cell_clicked = False
        for selector, count in cell_elements.items():
            if count > 0:
                try:
                    elements = navigator.driver.find_elements("css selector", selector)
                    first_element = elements[0]
                    
                    print(f"  Testing click on {selector}...")
                    first_element.click()
                    print(f"  ✅ Successfully clicked {selector}!")
                    
                    # Wait a moment
                    await asyncio.sleep(2)
                    
                    # Take screenshot after click
                    screenshot_path2 = await navigator.take_screenshot("excel_after_cell_click")
                    print(f"  📸 Screenshot after click: {screenshot_path2}")
                    
                    # Check if any input field appeared
                    input_elements_after = navigator.driver.find_elements("css selector", "input, [contenteditable='true']")
                    if input_elements_after:
                        print(f"  🎯 Found {len(input_elements_after)} input elements after click!")
                        
                        # Try to enter text
                        input_elem = input_elements_after[0]
                        input_elem.send_keys("Test Data Entry")
                        print(f"  ✅ Successfully entered text!")
                        
                        # Wait and take final screenshot
                        await asyncio.sleep(2)
                        screenshot_path3 = await navigator.take_screenshot("excel_with_data_entered")
                        print(f"  📸 Final screenshot: {screenshot_path3}")
                        
                        cell_clicked = True
                        break
                    else:
                        print(f"  ⚠️  No input field appeared after clicking {selector}")
                        
                except Exception as e:
                    print(f"  ❌ Failed to interact with {selector}: {e}")
                    continue
        
        if not cell_clicked:
            print("  ⚠️  Could not successfully interact with any cell elements")
        
        # Save exploration results
        exploration_data = {
            "clickable_elements": clickable_elements,
            "grid_elements": grid_elements,
            "cell_elements": cell_elements,
            "input_elements": input_elements,
            "cell_interaction_successful": cell_clicked,
            "screenshots": [screenshot_path1, screenshot_path2 if 'screenshot_path2' in locals() else None, screenshot_path3 if 'screenshot_path3' in locals() else None]
        }
        
        with open("excel_cell_selectors.json", "w") as f:
            json.dump(exploration_data, f, indent=2)
        
        print(f"\n💾 Cell selector exploration data saved")
        
        # Print summary of findings
        print(f"\n📊 Summary:")
        print(f"  Clickable elements: {sum(clickable_elements.values())}")
        print(f"  Grid elements: {sum(grid_elements.values())}")
        print(f"  Cell elements: {sum(cell_elements.values())}")
        print(f"  Input elements: {sum(input_elements.values())}")
        print(f"  Cell interaction successful: {cell_clicked}")
        
    except Exception as e:
        print(f"❌ Error during cell selector exploration: {e}")
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
    asyncio.run(find_excel_cell_selectors())
