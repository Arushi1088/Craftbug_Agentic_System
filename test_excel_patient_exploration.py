#!/usr/bin/env python3
"""
Patient exploration of Excel interface with longer wait times and different strategies
"""

import asyncio
import json
import time
from excel_web_selenium_only import get_selenium_navigator

async def patient_explore_excel():
    """Patient exploration of Excel interface"""
    print("⏳ Patient exploration of Excel interface...")
    
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
        
        # Patiently wait for Excel interface with multiple checks
        print("⏳ Patiently waiting for Excel interface...")
        
        max_wait_time = 60  # Wait up to 60 seconds
        check_interval = 5  # Check every 5 seconds
        attempts = max_wait_time // check_interval
        
        excel_loaded = False
        for attempt in range(attempts):
            print(f"  Attempt {attempt + 1}/{attempts} - Waiting {check_interval} seconds...")
            await asyncio.sleep(check_interval)
            
            # Take screenshot
            screenshot_path = await navigator.take_screenshot(f"excel_patient_wait_{attempt + 1}")
            print(f"  📸 Screenshot: {screenshot_path}")
            
            # Check for any elements
            all_elements = navigator.driver.find_elements("css selector", "*")
            print(f"  Total elements found: {len(all_elements)}")
            
            # Check for specific Excel elements
            excel_indicators = [
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
            
            found_indicators = []
            for indicator in excel_indicators:
                try:
                    elements = navigator.driver.find_elements("css selector", indicator)
                    if elements:
                        found_indicators.append(f"{indicator}: {len(elements)}")
                except:
                    pass
            
            if found_indicators:
                print(f"  🎯 Found Excel indicators: {found_indicators}")
                excel_loaded = True
                break
            elif len(all_elements) > 20:
                print(f"  📈 Interface appears to be loading ({len(all_elements)} elements)")
            else:
                print(f"  ⏳ Still waiting... ({len(all_elements)} elements)")
        
        if not excel_loaded:
            print("⚠️  Excel interface may not be fully loaded, but continuing...")
        
        # Try to find any elements we can interact with
        print("\n🔍 Looking for any interactive elements...")
        
        # Get current URL and title
        try:
            current_url = navigator.driver.current_url
            page_title = navigator.driver.title
            print(f"🌐 Current URL: {current_url}")
            print(f"📄 Page title: {page_title}")
        except Exception as e:
            print(f"⚠️  Could not get URL/title: {e}")
        
        # Look for any elements with common attributes
        element_analysis = {}
        
        # Check for elements with various attributes
        attribute_checks = [
            ("data-testid", "[data-testid]"),
            ("class", "[class]"),
            ("id", "[id]"),
            ("role", "[role]"),
            ("aria-label", "[aria-label]"),
            ("tabindex", "[tabindex]"),
            ("onclick", "[onclick]")
        ]
        
        for attr_name, selector in attribute_checks:
            try:
                elements = navigator.driver.find_elements("css selector", selector)
                if elements:
                    element_analysis[attr_name] = []
                    for elem in elements[:5]:  # First 5 elements
                        attr_value = elem.get_attribute(attr_name)
                        if attr_value:
                            element_analysis[attr_name].append(attr_value)
                    print(f"  {attr_name}: {len(elements)} elements found")
            except Exception as e:
                print(f"  ❌ Error checking {attr_name}: {e}")
        
        # Try clicking on any element to see what happens
        print("\n🧪 Testing any available interactions...")
        
        # Get all elements
        all_elements = navigator.driver.find_elements("css selector", "*")
        print(f"Total elements available: {len(all_elements)}")
        
        interaction_successful = False
        for i, elem in enumerate(all_elements[:10]):  # Try first 10 elements
            try:
                elem_type = elem.tag_name
                elem_class = elem.get_attribute("class") or ""
                
                # Skip non-interactive elements
                if elem_type in ['html', 'head', 'body', 'meta', 'link', 'script', 'style']:
                    continue
                
                print(f"  Testing element {i+1}: {elem_type} (class: {elem_class[:30]})")
                
                # Try to click
                elem.click()
                print(f"    ✅ Successfully clicked!")
                
                # Wait a moment
                await asyncio.sleep(2)
                
                # Take screenshot
                screenshot_path = await navigator.take_screenshot(f"excel_after_interaction_{i+1}")
                print(f"    📸 Screenshot: {screenshot_path}")
                
                # Check if anything changed
                input_elements = navigator.driver.find_elements("css selector", "input, [contenteditable='true']")
                if input_elements:
                    print(f"    🎯 Found {len(input_elements)} input elements!")
                    interaction_successful = True
                    break
                
                # Check if more elements appeared
                new_elements = navigator.driver.find_elements("css selector", "*")
                if len(new_elements) > len(all_elements):
                    print(f"    📈 More elements appeared: {len(new_elements)} vs {len(all_elements)}")
                
            except Exception as e:
                print(f"    ❌ Failed to interact: {e}")
                continue
        
        # Save exploration results
        exploration_data = {
            "excel_loaded": excel_loaded,
            "total_elements": len(all_elements),
            "element_analysis": element_analysis,
            "interaction_successful": interaction_successful,
            "current_url": current_url if 'current_url' in locals() else None,
            "page_title": page_title if 'page_title' in locals() else None
        }
        
        with open("excel_patient_exploration.json", "w") as f:
            json.dump(exploration_data, f, indent=2)
        
        print(f"\n💾 Patient exploration data saved")
        print(f"📊 Summary:")
        print(f"  Excel loaded: {excel_loaded}")
        print(f"  Total elements: {len(all_elements)}")
        print(f"  Interaction successful: {interaction_successful}")
        
    except Exception as e:
        print(f"❌ Error during patient exploration: {e}")
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
    asyncio.run(patient_explore_excel())
