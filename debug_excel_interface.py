#!/usr/bin/env python3
"""
Debug script to explore Excel Web interface and understand element structure
"""

import asyncio
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from excel_web_selenium_only import get_selenium_navigator

async def debug_excel_interface():
    """Debug the Excel Web interface to understand element structure"""
    
    print("🔍 Starting Excel Web Interface Debug...")
    
    # Get navigator
    navigator = await get_selenium_navigator()
    
    try:
        # Initialize and authenticate
        if not await navigator.initialize():
            print("❌ Failed to initialize navigator")
            return
        
        if not await navigator.ensure_authenticated():
            print("❌ Failed to authenticate to Excel Web")
            return
        
        print("✅ Authentication successful")
        
        # Navigate to Excel Web
        await navigator.navigate_to_excel_web()
        print("✅ Navigated to Excel Web")
        
        # Wait for page to load
        await asyncio.sleep(5)
        
        # Click "Blank workbook"
        try:
            # Try XPath first
            blank_workbook = navigator.driver.find_element("xpath", "//span[contains(text(), 'Blank workbook')]")
            blank_workbook.click()
            print("✅ Clicked 'Blank workbook'")
        except Exception as e:
            print(f"❌ Failed to click 'Blank workbook': {e}")
            return
        
        # Wait for workbook to load
        await asyncio.sleep(10)
        
        # Switch to iframe
        try:
            iframes = navigator.driver.find_elements("css selector", "iframe")
            print(f"📋 Found {len(iframes)} iframes")
            
            for i, iframe in enumerate(iframes):
                try:
                    src = iframe.get_attribute("src")
                    print(f"  Iframe {i}: {src}")
                    
                    if "excel" in src.lower() or "office" in src.lower():
                        navigator.driver.switch_to.frame(iframe)
                        print(f"✅ Switched to iframe {i}")
                        break
                except Exception as e:
                    print(f"  ❌ Error with iframe {i}: {e}")
                    continue
        except Exception as e:
            print(f"❌ Failed to switch to iframe: {e}")
            return
        
        # Wait for Excel interface
        await asyncio.sleep(10)
        
        # Explore all elements
        print("\n🔍 Exploring Excel Interface Elements...")
        
        # Get all elements
        all_elements = navigator.driver.find_elements("css selector", "*")
        print(f"📊 Total elements found: {len(all_elements)}")
        
        # Categorize elements
        element_types = {}
        for elem in all_elements:
            tag = elem.tag_name
            if tag not in element_types:
                element_types[tag] = 0
            element_types[tag] += 1
        
        print("\n📋 Element types found:")
        for tag, count in sorted(element_types.items(), key=lambda x: x[1], reverse=True):
            print(f"  {tag}: {count}")
        
        # Look for specific Excel elements
        print("\n🔍 Looking for Excel-specific elements...")
        
        # Check for grid/cell elements
        grid_elements = navigator.driver.find_elements("css selector", "[role='grid'], [role='gridcell'], [data-testid*='grid'], [class*='grid']")
        print(f"📊 Grid elements: {len(grid_elements)}")
        
        # Check for cell elements
        cell_elements = navigator.driver.find_elements("css selector", "[data-testid*='cell'], [class*='cell'], td, [role='gridcell']")
        print(f"📊 Cell elements: {len(cell_elements)}")
        
        # Check for worksheet elements
        worksheet_elements = navigator.driver.find_elements("css selector", "[data-testid*='sheet'], [class*='sheet'], [data-testid*='worksheet'], [class*='worksheet']")
        print(f"📊 Worksheet elements: {len(worksheet_elements)}")
        
        # Check for input elements
        input_elements = navigator.driver.find_elements("css selector", "input, [contenteditable='true'], [role='textbox']")
        print(f"📊 Input elements: {len(input_elements)}")
        
        # Check for button elements
        button_elements = navigator.driver.find_elements("css selector", "button, [role='button']")
        print(f"📊 Button elements: {len(button_elements)}")
        
        # Look for any elements with text
        print("\n🔍 Elements with text content:")
        text_elements = []
        for elem in all_elements[:50]:  # Check first 50 elements
            try:
                text = elem.text.strip()
                if text and len(text) < 100:  # Reasonable text length
                    text_elements.append((elem.tag_name, text))
            except:
                continue
        
        for tag, text in text_elements[:20]:  # Show first 20
            print(f"  {tag}: '{text}'")
        
        # Take a screenshot
        screenshot_path = f"screenshots/excel_web/debug_interface_{int(time.time())}.png"
        navigator.driver.save_screenshot(screenshot_path)
        print(f"📸 Screenshot saved: {screenshot_path}")
        
        # Check if we're in the right context
        print(f"\n🔍 Current URL: {navigator.driver.current_url}")
        print(f"🔍 Page title: {navigator.driver.title}")
        
        # Look for any error messages or dialogs
        error_elements = navigator.driver.find_elements("css selector", "[role='alert'], [class*='error'], [class*='alert']")
        if error_elements:
            print(f"\n⚠️  Found {len(error_elements)} error/alert elements")
            for i, elem in enumerate(error_elements):
                try:
                    print(f"  Error {i}: {elem.text}")
                except:
                    print(f"  Error {i}: [text not accessible]")
        
    except Exception as e:
        print(f"❌ Debug failed: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Close browser
        try:
            navigator.close()
            print("✅ Browser closed")
        except:
            pass

if __name__ == "__main__":
    asyncio.run(debug_excel_interface())

