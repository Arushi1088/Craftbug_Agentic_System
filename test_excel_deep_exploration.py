#!/usr/bin/env python3
"""
Deep exploration of Excel Web interface to find the actual Excel application
"""

import asyncio
import json
import time
from excel_web_selenium_only import get_selenium_navigator

async def deep_explore_excel():
    """Deep exploration of Excel Web interface"""
    print("🔍 Deep exploring Excel Web interface...")
    
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
        
        # Wait longer for Excel to load
        print("⏳ Waiting for Excel to fully load...")
        await asyncio.sleep(10)
        
        # Take initial screenshot
        screenshot_path1 = await navigator.take_screenshot("excel_loading_initial")
        print(f"📸 Initial screenshot: {screenshot_path1}")
        
        # Find and switch to the main iframe
        iframe_selectors = [
            "iframe[src*='webshell.suite.office.com']",
            "iframe[src*='excel']",
            "iframe[src*='office.com']"
        ]
        
        main_iframe = None
        for selector in iframe_selectors:
            try:
                if await navigator.wait_for_element(selector, timeout=10):
                    main_iframe = navigator.driver.find_element("css selector", selector)
                    navigator.driver.switch_to.frame(main_iframe)
                    print(f"✅ Switched to main iframe: {selector}")
                    break
            except Exception as e:
                print(f"❌ Failed to switch to iframe '{selector}': {e}")
                continue
        
        if not main_iframe:
            print("❌ Could not find main iframe")
            return
        
        # Wait a bit more and take screenshot
        await asyncio.sleep(5)
        screenshot_path2 = await navigator.take_screenshot("excel_after_main_iframe")
        print(f"📸 After main iframe screenshot: {screenshot_path2}")
        
        # Look for nested iframes
        print("🔍 Looking for nested iframes...")
        nested_iframes = navigator.driver.find_elements("tag name", "iframe")
        print(f"Found {len(nested_iframes)} nested iframes")
        
        for i, iframe in enumerate(nested_iframes):
            try:
                iframe_src = iframe.get_attribute("src")
                iframe_id = iframe.get_attribute("id")
                iframe_class = iframe.get_attribute("class")
                print(f"  Iframe {i+1}: src={iframe_src}, id={iframe_id}, class={iframe_class}")
                
                # Try switching to this iframe
                navigator.driver.switch_to.frame(iframe)
                print(f"  ✅ Switched to nested iframe {i+1}")
                
                # Wait a moment
                await asyncio.sleep(3)
                
                # Take screenshot
                screenshot_path = await navigator.take_screenshot(f"excel_nested_iframe_{i+1}")
                print(f"  📸 Screenshot: {screenshot_path}")
                
                # Look for Excel elements in this iframe
                print(f"  🔍 Looking for Excel elements in iframe {i+1}...")
                
                # Check for common Excel selectors
                excel_selectors = [
                    "[data-testid*='cell']",
                    "[class*='cell']",
                    "td",
                    "[role='gridcell']",
                    "[data-testid*='grid']",
                    "[class*='grid']",
                    "[data-testid*='sheet']",
                    "[class*='sheet']",
                    "[data-testid*='excel']",
                    "[class*='excel']",
                    "[data-testid*='workbook']",
                    "[class*='workbook']"
                ]
                
                found_elements = {}
                for selector in excel_selectors:
                    try:
                        elements = navigator.driver.find_elements("css selector", selector)
                        if elements:
                            found_elements[selector] = {
                                "count": len(elements),
                                "sample_attributes": {}
                            }
                            
                            # Get attributes from first few elements
                            for j, elem in enumerate(elements[:3]):
                                attrs = {}
                                for attr in ['data-testid', 'class', 'id', 'role', 'data-cell']:
                                    try:
                                        value = elem.get_attribute(attr)
                                        if value:
                                            attrs[attr] = value
                                    except:
                                        pass
                                found_elements[selector]["sample_attributes"][f"element_{j+1}"] = attrs
                            
                            print(f"    {selector}: {len(elements)} elements found")
                    except Exception as e:
                        print(f"    ❌ Error with selector '{selector}': {e}")
                
                # If we found Excel elements, try to interact
                if found_elements:
                    print(f"  🎯 Found Excel elements in iframe {i+1}!")
                    
                    # Try clicking on a cell
                    for selector in ["td:first-child", "[data-testid*='cell']:first-child", "[class*='cell']:first-child"]:
                        try:
                            elements = navigator.driver.find_elements("css selector", selector)
                            if elements:
                                print(f"    🧪 Testing cell click with selector: {selector}")
                                elements[0].click()
                                print(f"    ✅ Successfully clicked cell!")
                                
                                # Wait and take screenshot
                                await asyncio.sleep(2)
                                screenshot_path_click = await navigator.take_screenshot(f"excel_cell_clicked_iframe_{i+1}")
                                print(f"    📸 Screenshot after click: {screenshot_path_click}")
                                break
                        except Exception as e:
                            print(f"    ❌ Failed to click with selector '{selector}': {e}")
                    
                    # Save the successful iframe data
                    iframe_data = {
                        "iframe_index": i + 1,
                        "iframe_src": iframe_src,
                        "iframe_id": iframe_id,
                        "iframe_class": iframe_class,
                        "found_elements": found_elements,
                        "screenshots": [screenshot_path, screenshot_path_click if 'screenshot_path_click' in locals() else None]
                    }
                    
                    with open(f"excel_successful_iframe_{i+1}.json", "w") as f:
                        json.dump(iframe_data, f, indent=2)
                    
                    print(f"    💾 Saved iframe {i+1} data")
                    break
                
                # Switch back to main iframe for next iteration
                navigator.driver.switch_to.parent_frame()
                
            except Exception as e:
                print(f"  ❌ Error exploring iframe {i+1}: {e}")
                # Try to switch back to main iframe
                try:
                    navigator.driver.switch_to.parent_frame()
                except:
                    pass
        
        # Save overall exploration data
        exploration_data = {
            "main_iframe_selector": iframe_selectors[0] if main_iframe else None,
            "nested_iframes_count": len(nested_iframes),
            "screenshots": [screenshot_path1, screenshot_path2]
        }
        
        with open("excel_deep_exploration.json", "w") as f:
            json.dump(exploration_data, f, indent=2)
        
        print(f"\n💾 Deep exploration data saved")
        
    except Exception as e:
        print(f"❌ Error during deep exploration: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        if navigator.driver:
            try:
                # Switch back to default content
                navigator.driver.switch_to.default_content()
            except:
                pass
            await navigator.close()

if __name__ == "__main__":
    asyncio.run(deep_explore_excel())
