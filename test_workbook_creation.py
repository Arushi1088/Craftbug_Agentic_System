"""
Test workbook creation to see the interface
"""

import asyncio
from excel_web_selenium_only import get_selenium_navigator


async def test_workbook_creation():
    """Test clicking Blank workbook and see what happens"""
    navigator = await get_selenium_navigator()
    
    try:
        print("🧪 Testing workbook creation...")
        
        # Initialize and authenticate
        if not await navigator.initialize():
            print("❌ Failed to initialize navigator")
            return
        
        if not await navigator.ensure_authenticated():
            print("❌ Failed to authenticate")
            return
        
        print("✅ Successfully authenticated to Excel Web")
        
        # Take screenshot before clicking
        screenshot_path = await navigator.take_screenshot("before_click_blank_workbook")
        print(f"📸 Before screenshot: {screenshot_path}")
        
        # Click Blank workbook
        xpath = "//span[contains(text(), 'Blank workbook')]"
        if await navigator.click_element_by_xpath(xpath, 15):
            print("✅ Successfully clicked 'Blank workbook'")
            
            # Wait a moment for the page to load
            await asyncio.sleep(5)
            
            # Take screenshot after clicking
            screenshot_path = await navigator.take_screenshot("after_click_blank_workbook")
            print(f"📸 After screenshot: {screenshot_path}")
            
            # Get page info
            title = await navigator.get_page_title()
            url = await navigator.get_page_url()
            print(f"📄 Page Title: {title}")
            print(f"🌐 Page URL: {url}")
            
            # Look for common elements on the new page
            print("\n🔍 Looking for elements on the new page...")
            
            # Look for buttons
            buttons = navigator.driver.find_elements("tag name", "button")
            print(f"📋 Found {len(buttons)} buttons:")
            for i, button in enumerate(buttons[:10]):  # Show first 10
                try:
                    text = button.text.strip()
                    classes = button.get_attribute("class")
                    if text:
                        print(f"   Button {i+1}: '{text}' (class: {classes})")
                except:
                    pass
            
            # Look for spans with text
            spans = navigator.driver.find_elements("tag name", "span")
            text_spans = []
            for span in spans:
                try:
                    text = span.text.strip()
                    if text and len(text) > 2 and len(text) < 50:
                        text_spans.append(span)
                except:
                    pass
            
            print(f"\n📝 Found {len(text_spans)} text spans:")
            for i, span in enumerate(text_spans[:15]):  # Show first 15
                try:
                    text = span.text.strip()
                    classes = span.get_attribute("class")
                    print(f"   Span {i+1}: '{text}' (class: {classes})")
                except:
                    pass
            
            print("\n✅ Workbook creation test completed!")
            
        else:
            print("❌ Failed to click 'Blank workbook'")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
    finally:
        await navigator.close()


if __name__ == "__main__":
    asyncio.run(test_workbook_creation())
