"""
Excel Web Interface Explorer
Explores the actual Excel Web interface to find correct selectors
"""

import asyncio
import time
from excel_web_selenium_only import get_selenium_navigator


async def explore_excel_web():
    """Explore Excel Web interface to find actual elements"""
    navigator = await get_selenium_navigator()
    
    try:
        print("🔍 Exploring Excel Web interface...")
        
        # Initialize and authenticate
        if not await navigator.initialize():
            print("❌ Failed to initialize navigator")
            return
        
        if not await navigator.ensure_authenticated():
            print("❌ Failed to authenticate")
            return
        
        print("✅ Successfully authenticated to Excel Web")
        
        # Take initial screenshot
        screenshot_path = await navigator.take_screenshot("excel_web_explorer_initial")
        print(f"📸 Initial screenshot: {screenshot_path}")
        
        # Get page info
        title = await navigator.get_page_title()
        url = await navigator.get_page_url()
        print(f"📄 Page Title: {title}")
        print(f"🌐 Page URL: {url}")
        
        # Get page source to analyze
        page_source = navigator.driver.page_source
        
        # Look for common Excel Web elements
        print("\n🔍 Analyzing page for Excel Web elements...")
        
        # Look for buttons
        buttons = navigator.driver.find_elements("tag name", "button")
        print(f"📋 Found {len(buttons)} buttons:")
        for i, button in enumerate(buttons[:10]):  # Show first 10
            try:
                text = button.text.strip()
                classes = button.get_attribute("class")
                id_attr = button.get_attribute("id")
                if text:
                    print(f"   Button {i+1}: '{text}' (class: {classes}, id: {id_attr})")
            except:
                pass
        
        # Look for links
        links = navigator.driver.find_elements("tag name", "a")
        print(f"\n🔗 Found {len(links)} links:")
        for i, link in enumerate(links[:10]):  # Show first 10
            try:
                text = link.text.strip()
                href = link.get_attribute("href")
                classes = link.get_attribute("class")
                if text:
                    print(f"   Link {i+1}: '{text}' -> {href} (class: {classes})")
            except:
                pass
        
        # Look for input fields
        inputs = navigator.driver.find_elements("tag name", "input")
        print(f"\n📝 Found {len(inputs)} input fields:")
        for i, input_field in enumerate(inputs[:5]):  # Show first 5
            try:
                input_type = input_field.get_attribute("type")
                placeholder = input_field.get_attribute("placeholder")
                classes = input_field.get_attribute("class")
                print(f"   Input {i+1}: type={input_type}, placeholder='{placeholder}' (class: {classes})")
            except:
                pass
        
        # Look for divs with specific classes
        divs = navigator.driver.find_elements("tag name", "div")
        excel_related_divs = []
        for div in divs:
            try:
                classes = div.get_attribute("class")
                if classes and any(keyword in classes.lower() for keyword in ['excel', 'workbook', 'new', 'create', 'sheet']):
                    excel_related_divs.append(div)
            except:
                pass
        
        print(f"\n📊 Found {len(excel_related_divs)} Excel-related divs:")
        for i, div in enumerate(excel_related_divs[:10]):  # Show first 10
            try:
                classes = div.get_attribute("class")
                text = div.text.strip()[:50]  # First 50 chars
                print(f"   Div {i+1}: class='{classes}', text='{text}...'")
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
        
        # Take another screenshot after exploration
        screenshot_path = await navigator.take_screenshot("excel_web_explorer_after_analysis")
        print(f"\n📸 Final screenshot: {screenshot_path}")
        
        print("\n✅ Excel Web interface exploration completed!")
        print("📋 Use the information above to create proper selectors for automation")
        
    except Exception as e:
        print(f"❌ Exploration failed: {e}")
    finally:
        await navigator.close()


if __name__ == "__main__":
    asyncio.run(explore_excel_web())
