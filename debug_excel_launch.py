#!/usr/bin/env python3
"""
Debug script to properly handle Excel launch after clicking "Blank workbook"
"""
import asyncio
import time
from excel_web_selenium_only import get_selenium_navigator

async def debug_excel_launch():
    """Debug Excel launch after clicking 'Blank workbook'"""
    print("🔍 Debugging Excel launch...")
    
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
        
        # Take screenshot before clicking
        navigator.driver.save_screenshot("launch_before_click.png")
        print("📸 Screenshot saved: launch_before_click.png")
        
        # Click "Blank workbook"
        print("🖱️  Clicking 'Blank workbook'...")
        try:
            blank_workbook = navigator.driver.find_element("xpath", "//span[contains(text(), 'Blank workbook')]")
            blank_workbook.click()
            print("✅ Clicked 'Blank workbook'")
        except Exception as e:
            print(f"❌ Failed to click 'Blank workbook': {e}")
            return
        
        # Monitor for changes
        print("⏳ Monitoring for Excel launch...")
        for i in range(30):  # Monitor for 30 seconds
            await asyncio.sleep(2)
            print(f"\n📊 Check {i+1}/30 at {time.strftime('%H:%M:%S')}:")
            
            # Check current URL
            current_url = navigator.driver.current_url
            print(f"  URL: {current_url}")
            
            # Check if URL changed
            if current_url != initial_url:
                print(f"  ✅ URL changed from {initial_url} to {current_url}")
            
            # Check for new windows/tabs
            all_windows = navigator.driver.window_handles
            print(f"  Windows: {len(all_windows)} (handles: {all_windows})")
            
            if len(all_windows) > 1:
                print(f"  ✅ New window detected! Switching to it...")
                # Switch to the new window
                new_window = [w for w in all_windows if w != initial_window][0]
                navigator.driver.switch_to.window(new_window)
                new_url = navigator.driver.current_url
                print(f"  ✅ Switched to new window: {new_url}")
                
                # Check iframes in new window
                iframes = navigator.driver.find_elements("css selector", "iframe")
                print(f"  Iframes in new window: {len(iframes)}")
                for j, iframe in enumerate(iframes):
                    try:
                        src = iframe.get_attribute("src")
                        print(f"    Iframe {j}: {src}")
                    except:
                        print(f"    Iframe {j}: [src not accessible]")
                
                # Take screenshot of new window
                screenshot_path = f"launch_new_window_{i+1}.png"
                navigator.driver.save_screenshot(screenshot_path)
                print(f"  📸 Screenshot saved: {screenshot_path}")
                
                # Check if this looks like Excel
                if "excel" in new_url.lower() or "office" in new_url.lower():
                    print(f"  ✅ This looks like Excel! URL: {new_url}")
                    break
            
            # Check iframes in current window
            iframes = navigator.driver.find_elements("css selector", "iframe")
            print(f"  Iframes in current window: {len(iframes)}")
            
            for j, iframe in enumerate(iframes):
                try:
                    src = iframe.get_attribute("src")
                    print(f"    Iframe {j}: {src}")
                except:
                    print(f"    Iframe {j}: [src not accessible]")
            
            # Check for any popup dialogs or alerts
            try:
                alert = navigator.driver.switch_to.alert
                alert_text = alert.text
                print(f"  ⚠️  Alert detected: {alert_text}")
                alert.accept()
            except:
                pass  # No alert
            
            # Take screenshot every 10 seconds
            if (i + 1) % 5 == 0:
                screenshot_path = f"launch_check_{i+1}.png"
                navigator.driver.save_screenshot(screenshot_path)
                print(f"  📸 Screenshot saved: {screenshot_path}")
        
        print("\n🔍 Launch debug complete!")
        
    except Exception as e:
        print(f"❌ Debug failed: {e}")
        import traceback
        traceback.print_exc()
    finally:
        try:
            await navigator.close()
            print("✅ Browser closed")
        except:
            pass

if __name__ == "__main__":
    asyncio.run(debug_excel_launch())

