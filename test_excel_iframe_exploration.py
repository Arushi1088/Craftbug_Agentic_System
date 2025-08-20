#!/usr/bin/env python3
"""
Test script to explore Excel Web interface within the iframe
"""

import asyncio
import json
from excel_web_selenium_only import get_selenium_navigator

async def explore_excel_iframe():
    """Explore the Excel Web interface within the iframe"""
    print("🔍 Exploring Excel Web interface within iframe...")
    
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
        
        # Click using XPath
        if await navigator.click_element_by_xpath("//span[contains(text(), 'Blank workbook')]", timeout=15):
            print("✅ Clicked 'Blank workbook'")
        else:
            print("❌ Could not click 'Blank workbook'")
            return
        
        # Wait for iframe to load
        print("⏳ Waiting for Excel iframe to load...")
        await asyncio.sleep(5)
        
        # Find and switch to the Excel iframe
        iframe_selectors = [
            "iframe[src*='webshell.suite.office.com']",
            "iframe[src*='excel']",
            "iframe[src*='office.com']"
        ]
        
        iframe_found = False
        for selector in iframe_selectors:
            try:
                if await navigator.wait_for_element(selector, timeout=10):
                    iframe = navigator.driver.find_element("css selector", selector)
                    navigator.driver.switch_to.frame(iframe)
                    print(f"✅ Switched to iframe: {selector}")
                    iframe_found = True
                    break
            except Exception as e:
                print(f"❌ Failed to switch to iframe '{selector}': {e}")
                continue
        
        if not iframe_found:
            print("❌ Could not find or switch to Excel iframe")
            return
        
        # Take a screenshot of the iframe content
        screenshot_path = await navigator.take_screenshot("excel_iframe_content")
        print(f"📸 Screenshot saved: {screenshot_path}")
        
        # Explore the iframe content
        print("🔍 Exploring iframe content...")
        
        # Get current URL and title within iframe
        try:
            current_url = navigator.driver.current_url
            page_title = navigator.driver.title
            print(f"🌐 Iframe URL: {current_url}")
            print(f"📄 Iframe title: {page_title}")
        except Exception as e:
            print(f"⚠️  Could not get iframe URL/title: {e}")
        
        # Look for Excel-specific elements
        print("\n📋 Looking for Excel elements...")
        
        excel_elements = {}
        
        # Look for grid/cell elements
        cell_selectors = [
            "[data-testid*='cell']",
            "[class*='cell']",
            "[id*='cell']",
            "td",
            "[role='gridcell']",
            "[data-cell]"
        ]
        
        for selector in cell_selectors:
            try:
                elements = navigator.driver.find_elements("css selector", selector)
                if elements:
                    excel_elements[selector] = {
                        "count": len(elements),
                        "sample_attributes": {}
                    }
                    
                    # Get attributes from first few elements
                    for i, elem in enumerate(elements[:3]):
                        attrs = {}
                        for attr in ['data-testid', 'class', 'id', 'data-cell', 'role']:
                            try:
                                value = elem.get_attribute(attr)
                                if value:
                                    attrs[attr] = value
                            except:
                                pass
                        excel_elements[selector]["sample_attributes"][f"element_{i+1}"] = attrs
                        
                        # Get text content
                        try:
                            text = elem.text
                            if text:
                                attrs['text'] = text[:50]  # First 50 chars
                        except:
                            pass
                    
                    print(f"  {selector}: {len(elements)} elements found")
            except Exception as e:
                print(f"  ❌ Error with selector '{selector}': {e}")
        
        # Look for input elements
        input_selectors = [
            "input[type='text']",
            "input[type='number']",
            "[contenteditable='true']",
            "[data-testid*='input']",
            "[class*='input']"
        ]
        
        for selector in input_selectors:
            try:
                elements = navigator.driver.find_elements("css selector", selector)
                if elements:
                    excel_elements[selector] = {
                        "count": len(elements),
                        "sample_attributes": {}
                    }
                    
                    for i, elem in enumerate(elements[:3]):
                        attrs = {}
                        for attr in ['data-testid', 'class', 'id', 'type', 'contenteditable']:
                            try:
                                value = elem.get_attribute(attr)
                                if value:
                                    attrs[attr] = value
                            except:
                                pass
                        excel_elements[selector]["sample_attributes"][f"element_{i+1}"] = attrs
                    
                    print(f"  {selector}: {len(elements)} elements found")
            except Exception as e:
                print(f"  ❌ Error with selector '{selector}': {e}")
        
        # Look for toolbar/ribbon elements
        toolbar_selectors = [
            "[data-testid*='toolbar']",
            "[class*='toolbar']",
            "[class*='ribbon']",
            "[data-testid*='ribbon']",
            "[role='toolbar']"
        ]
        
        for selector in toolbar_selectors:
            try:
                elements = navigator.driver.find_elements("css selector", selector)
                if elements:
                    excel_elements[selector] = {
                        "count": len(elements),
                        "sample_attributes": {}
                    }
                    
                    for i, elem in enumerate(elements[:3]):
                        attrs = {}
                        for attr in ['data-testid', 'class', 'id', 'role']:
                            try:
                                value = elem.get_attribute(attr)
                                if value:
                                    attrs[attr] = value
                            except:
                                pass
                        excel_elements[selector]["sample_attributes"][f"element_{i+1}"] = attrs
                    
                    print(f"  {selector}: {len(elements)} elements found")
            except Exception as e:
                print(f"  ❌ Error with selector '{selector}': {e}")
        
        # Save exploration results
        exploration_data = {
            "iframe_url": current_url if 'current_url' in locals() else None,
            "iframe_title": page_title if 'page_title' in locals() else None,
            "excel_elements": excel_elements,
            "screenshot": screenshot_path
        }
        
        with open("excel_iframe_exploration.json", "w") as f:
            json.dump(exploration_data, f, indent=2)
        
        print(f"\n💾 Exploration data saved to excel_iframe_exploration.json")
        
        # Try to click on a cell to see what happens
        print("\n🧪 Testing cell interaction...")
        
        # Try different cell selectors
        cell_test_selectors = [
            "td:first-child",
            "[data-testid*='cell']:first-child",
            "[class*='cell']:first-child",
            "[role='gridcell']:first-child"
        ]
        
        for selector in cell_test_selectors:
            try:
                elements = navigator.driver.find_elements("css selector", selector)
                if elements:
                    print(f"  Testing selector: {selector}")
                    elements[0].click()
                    print(f"  ✅ Successfully clicked element with selector: {selector}")
                    
                    # Wait a moment and take another screenshot
                    await asyncio.sleep(2)
                    screenshot_path2 = await navigator.take_screenshot("excel_after_cell_click")
                    print(f"  📸 Screenshot after click: {screenshot_path2}")
                    break
            except Exception as e:
                print(f"  ❌ Failed to click with selector '{selector}': {e}")
        
    except Exception as e:
        print(f"❌ Error during exploration: {e}")
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
    asyncio.run(explore_excel_iframe())
