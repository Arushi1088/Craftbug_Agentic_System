#!/usr/bin/env python3
"""
Test script to explore Excel Web interface after clicking "Blank workbook"
"""

import asyncio
import json
from excel_web_selenium_only import get_selenium_navigator

async def explore_excel_interface():
    """Explore the Excel Web interface to find correct selectors"""
    print("🔍 Exploring Excel Web interface...")
    
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
        
        # Try different selectors for "Blank workbook"
        blank_workbook_selectors = [
            "//span[contains(text(), 'Blank workbook')]",
            "//div[contains(text(), 'Blank workbook')]",
            "//button[contains(text(), 'Blank workbook')]",
            "//a[contains(text(), 'Blank workbook')]",
            ".fui-Text:contains('Blank workbook')",
            "span:contains('Blank workbook')"
        ]
        
        clicked = False
        for selector in blank_workbook_selectors:
            try:
                if selector.startswith("//"):
                    # XPath selector
                    if await navigator.click_element_by_xpath(selector, timeout=5):
                        print(f"✅ Clicked using XPath: {selector}")
                        clicked = True
                        break
                else:
                    # CSS selector
                    if await navigator.click_element(selector, timeout=5):
                        print(f"✅ Clicked using CSS: {selector}")
                        clicked = True
                        break
            except Exception as e:
                print(f"❌ Failed with selector '{selector}': {e}")
                continue
        
        if not clicked:
            print("❌ Could not click 'Blank workbook' with any selector")
            return
        
        # Wait a moment for the page to load
        print("⏳ Waiting for workbook to load...")
        await asyncio.sleep(5)
        
        # Take a screenshot
        screenshot_path = await navigator.take_screenshot("excel_interface_exploration")
        print(f"📸 Screenshot saved: {screenshot_path}")
        
        # Explore the page structure
        print("🔍 Exploring page structure...")
        
        # Get page source
        page_source = navigator.driver.page_source
        
        # Look for common Excel Web elements
        print("\n📋 Looking for Excel Web elements...")
        
        # Check for various selectors that might indicate Excel is loaded
        excel_indicators = [
            "excel-app",
            "workbook",
            "spreadsheet",
            "grid",
            "cell",
            "sheet",
            "formula",
            "ribbon",
            "toolbar"
        ]
        
        found_elements = {}
        for indicator in excel_indicators:
            # Look for data-testid attributes
            testid_elements = navigator.driver.find_elements("css selector", f"[data-testid*='{indicator}']")
            if testid_elements:
                found_elements[f"data-testid*='{indicator}'"] = [elem.get_attribute("data-testid") for elem in testid_elements[:5]]
            
            # Look for class names
            class_elements = navigator.driver.find_elements("css selector", f"[class*='{indicator}']")
            if class_elements:
                found_elements[f"class*='{indicator}'"] = [elem.get_attribute("class") for elem in class_elements[:5]]
            
            # Look for IDs
            id_elements = navigator.driver.find_elements("css selector", f"[id*='{indicator}']")
            if id_elements:
                found_elements[f"id*='{indicator}'"] = [elem.get_attribute("id") for elem in id_elements[:5]]
        
        print("\n🎯 Found Excel Web elements:")
        for selector, elements in found_elements.items():
            print(f"  {selector}: {elements}")
        
        # Look for the current URL
        current_url = navigator.driver.current_url
        print(f"\n🌐 Current URL: {current_url}")
        
        # Look for page title
        page_title = navigator.driver.title
        print(f"📄 Page title: {page_title}")
        
        # Check if we're in an iframe
        iframes = navigator.driver.find_elements("tag name", "iframe")
        print(f"\n🖼️  Found {len(iframes)} iframes")
        
        for i, iframe in enumerate(iframes):
            try:
                iframe_src = iframe.get_attribute("src")
                print(f"  Iframe {i+1}: {iframe_src}")
            except:
                print(f"  Iframe {i+1}: Could not get src")
        
        # Save exploration results
        exploration_data = {
            "url": current_url,
            "title": page_title,
            "found_elements": found_elements,
            "iframe_count": len(iframes),
            "screenshot": screenshot_path
        }
        
        with open("excel_interface_exploration.json", "w") as f:
            json.dump(exploration_data, f, indent=2)
        
        print(f"\n💾 Exploration data saved to excel_interface_exploration.json")
        
    except Exception as e:
        print(f"❌ Error during exploration: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        if navigator.driver:
            await navigator.close_browser()

if __name__ == "__main__":
    asyncio.run(explore_excel_interface())
