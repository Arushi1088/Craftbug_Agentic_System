#!/usr/bin/env python3
"""
Test script to explore dialog content and find dismiss buttons
"""
import asyncio
import time
from excel_web_selenium_only import get_selenium_navigator

async def test_dialog_exploration():
    """Test to explore dialog content and find dismiss buttons"""
    print("🔍 Exploring dialog content...")
    
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
        
        # Wait for new window and switch to Excel
        print("⏳ Waiting for new window...")
        max_attempts = 30
        for attempt in range(max_attempts):
            await asyncio.sleep(2)
            
            all_windows = navigator.driver.window_handles
            if len(all_windows) > 1:
                new_window = [w for w in all_windows if w != initial_window][0]
                navigator.driver.switch_to.window(new_window)
                new_url = navigator.driver.current_url
                
                if "sharepoint.com" in new_url and ":x:" in new_url:
                    print(f"✅ Switched to Excel: {new_url}")
                    break
        
        # Wait for Excel to load
        await asyncio.sleep(5)
        
        # Check iframes
        iframes = navigator.driver.find_elements("css selector", "iframe")
        print(f"📋 Found {len(iframes)} iframes in Excel window")
        
        # Switch to Excel iframe
        if iframes:
            navigator.driver.switch_to.frame(iframes[0])
            print(f"✅ Switched to Excel iframe")
            await asyncio.sleep(3)
        
        # Now explore the dialog
        print("🔍 Exploring dialog content...")
        
        # Find the dialog
        dialog = navigator.driver.find_element("css selector", "[role='dialog']")
        print(f"✅ Found dialog: {dialog.get_attribute('class')}")
        
        # Explore all elements inside the dialog
        print("🔍 Exploring dialog contents...")
        
        # Get all child elements of the dialog
        dialog_children = dialog.find_elements("css selector", "*")
        print(f"📊 Dialog has {len(dialog_children)} child elements")
        
        # Look for text content
        text_elements = []
        for i, child in enumerate(dialog_children):
            try:
                text = child.text.strip()
                tag_name = child.tag_name
                class_name = child.get_attribute("class")
                aria_label = child.get_attribute("aria-label")
                title = child.get_attribute("title")
                
                if text:
                    text_elements.append({
                        'index': i,
                        'tag': tag_name,
                        'text': text,
                        'class': class_name,
                        'aria_label': aria_label,
                        'title': title
                    })
                    print(f"  Text element {i}: <{tag_name}> '{text}' (class: {class_name})")
            except Exception as e:
                continue
        
        print(f"📊 Found {len(text_elements)} text elements in dialog")
        
        # Look for buttons specifically
        buttons = dialog.find_elements("css selector", "button")
        print(f"📊 Found {len(buttons)} buttons in dialog")
        
        for i, button in enumerate(buttons):
            try:
                text = button.text.strip()
                aria_label = button.get_attribute("aria-label")
                title = button.get_attribute("title")
                class_name = button.get_attribute("class")
                
                print(f"  Button {i}: text='{text}', aria-label='{aria_label}', title='{title}', class='{class_name}'")
                
                # Check if this looks like a dismiss button
                if any(word in (text or "").lower() or word in (aria_label or "").lower() or word in (title or "").lower()
                       for word in ["not now", "skip", "later", "dismiss", "close", "no thanks"]):
                    print(f"    🎯 This looks like a dismiss button!")
                    
                    # Try to click it
                    button.click()
                    print(f"    ✅ Clicked dismiss button!")
                    await asyncio.sleep(2)
                    
                    # Take screenshot
                    navigator.driver.save_screenshot("dialog_dismissed.png")
                    print(f"    📸 Screenshot saved: dialog_dismissed.png")
                    return True
                    
            except Exception as e:
                print(f"    ❌ Error with button {i}: {e}")
                continue
        
        # Look for any clickable elements
        clickable_selectors = [
            "[role='button']",
            "[tabindex]",
            "a",
            "[onclick]",
            "[class*='clickable']",
            "[class*='button']"
        ]
        
        for selector in clickable_selectors:
            try:
                elements = dialog.find_elements("css selector", selector)
                if elements:
                    print(f"📊 Found {len(elements)} clickable elements with selector: {selector}")
                    
                    for i, element in enumerate(elements):
                        try:
                            text = element.text.strip()
                            aria_label = element.get_attribute("aria-label")
                            title = element.get_attribute("title")
                            
                            if text or aria_label or title:
                                print(f"  Clickable {i}: text='{text}', aria-label='{aria_label}', title='{title}'")
                                
                                # Check if this looks like a dismiss button
                                if any(word in (text or "").lower() or word in (aria_label or "").lower() or word in (title or "").lower()
                                       for word in ["not now", "skip", "later", "dismiss", "close", "no thanks"]):
                                    print(f"    🎯 This looks like a dismiss button!")
                                    
                                    # Try to click it
                                    element.click()
                                    print(f"    ✅ Clicked dismiss button!")
                                    await asyncio.sleep(2)
                                    
                                    # Take screenshot
                                    navigator.driver.save_screenshot("dialog_dismissed.png")
                                    print(f"    📸 Screenshot saved: dialog_dismissed.png")
                                    return True
                        except Exception as e:
                            continue
            except Exception as e:
                continue
        
        # Take final screenshot
        navigator.driver.save_screenshot("dialog_exploration.png")
        print("📸 Screenshot saved: dialog_exploration.png")
        
        print("\n🔍 Dialog exploration complete!")
        
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
    asyncio.run(test_dialog_exploration())
