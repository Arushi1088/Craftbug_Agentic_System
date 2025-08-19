#!/usr/bin/env python3
"""
Debug script to understand what happens after clicking "Blank workbook"
"""
import asyncio
import time
from excel_web_selenium_only import get_selenium_navigator

async def debug_workbook_click():
    """Debug what happens after clicking 'Blank workbook'"""
    print("🔍 Debugging Excel workbook click...")
    
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
        
        # Take screenshot before clicking
        navigator.driver.save_screenshot("debug_before_click.png")
        print("📸 Screenshot saved: debug_before_click.png")
        
        # Click "Blank workbook"
        print("🖱️  Clicking 'Blank workbook'...")
        try:
            blank_workbook = navigator.driver.find_element("xpath", "//span[contains(text(), 'Blank workbook')]")
            blank_workbook.click()
            print("✅ Clicked 'Blank workbook'")
        except Exception as e:
            print(f"❌ Failed to click 'Blank workbook': {e}")
            return
        
        # Monitor what happens over time
        print("⏳ Monitoring page changes after click...")
        for i in range(30):  # Monitor for 30 seconds
            await asyncio.sleep(2)
            print(f"\n📊 Check {i+1}/30 at {time.strftime('%H:%M:%S')}:")
            
            # Check current URL
            current_url = navigator.driver.current_url
            print(f"  URL: {current_url}")
            
            # Check iframes
            iframes = navigator.driver.find_elements("css selector", "iframe")
            print(f"  Iframes found: {len(iframes)}")
            
            for j, iframe in enumerate(iframes):
                try:
                    src = iframe.get_attribute("src")
                    print(f"    Iframe {j}: {src}")
                except:
                    print(f"    Iframe {j}: [src not accessible]")
            
            # Check for any Excel-related elements
            excel_indicators = [
                "excel",
                "workbook", 
                "spreadsheet",
                "grid",
                "cell"
            ]
            
            for indicator in excel_indicators:
                try:
                    elements = navigator.driver.find_elements("xpath", f"//*[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '{indicator}')]")
                    if elements:
                        print(f"    Found {len(elements)} elements with '{indicator}' text")
                except:
                    pass
            
            # Check for any loading indicators
            loading_selectors = [
                "[class*='loading']",
                "[class*='spinner']", 
                "[class*='progress']",
                "[aria-label*='loading']",
                "[aria-label*='progress']"
            ]
            
            for selector in loading_selectors:
                try:
                    elements = navigator.driver.find_elements("css selector", selector)
                    if elements:
                        print(f"    Found {len(elements)} loading elements with selector: {selector}")
                except:
                    pass
            
            # Take screenshot every 10 seconds
            if (i + 1) % 5 == 0:
                screenshot_path = f"debug_after_click_{i+1}.png"
                navigator.driver.save_screenshot(screenshot_path)
                print(f"  📸 Screenshot saved: {screenshot_path}")
        
        print("\n🔍 Debug complete!")
        
    except Exception as e:
        print(f"❌ Debug failed: {e}")
        import traceback
        traceback.print_exc()
    finally:
        try:
            navigator.close()
            print("✅ Browser closed")
        except:
            pass

if __name__ == "__main__":
    asyncio.run(debug_workbook_click())

