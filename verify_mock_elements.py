#!/usr/bin/env python3
"""
Verify that all elements referenced in Word scenarios exist in the mock
"""

import requests
from playwright.sync_api import sync_playwright
import time

def verify_mock_elements():
    """Verify all elements exist in the Word mock"""
    
    print("🔍 VERIFYING WORD MOCK ELEMENTS")
    print("=" * 50)
    
    # Elements that should exist in the mock
    required_elements = [
        "#comments-tab",
        ".resolve-button", 
        ".share-button",
        ".image-insert-btn",
        ".start-button",
        "#editor",
        "textarea",
        ".craft-bug-hover",
        "#review-tab",
        ".track-changes-toggle",
        ".accept-change-btn",
        ".reject-change-btn",
        ".next-change-btn",
        ".email-input",
        ".share-message",
        ".permission-dropdown",
        ".send-share-button"
    ]
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        try:
            # Navigate to the mock
            page.goto("http://127.0.0.1:8080/mocks/word/basic-doc.html")
            page.wait_for_load_state("networkidle")
            
            print("✅ Mock loaded successfully")
            
            # Check each element
            found_elements = []
            missing_elements = []
            
            for selector in required_elements:
                try:
                    element = page.query_selector(selector)
                    if element:
                        found_elements.append(selector)
                        print(f"✅ {selector}")
                    else:
                        missing_elements.append(selector)
                        print(f"❌ {selector} - NOT FOUND")
                except Exception as e:
                    missing_elements.append(selector)
                    print(f"❌ {selector} - ERROR: {e}")
            
            # Test dynamic elements after clicking start button
            print(f"\n🧪 Testing dynamic elements after start button click...")
            
            try:
                # Click start button
                start_button = page.query_selector(".start-button")
                if start_button:
                    start_button.click()
                    time.sleep(5)  # Wait for animations
                    
                    # Check if elements are still available
                    print(f"\n🔍 Checking elements after start button click:")
                    
                    for selector in [".image-insert-btn", ".share-button", "#comments-tab"]:
                        element = page.query_selector(selector)
                        if element:
                            print(f"✅ {selector} - Available after start")
                        else:
                            print(f"❌ {selector} - Missing after start")
                
            except Exception as e:
                print(f"⚠️ Error testing dynamic elements: {e}")
            
            # Summary
            print(f"\n📊 SUMMARY:")
            print(f"✅ Found: {len(found_elements)}/{len(required_elements)} elements")
            print(f"❌ Missing: {len(missing_elements)} elements")
            
            if missing_elements:
                print(f"\n⚠️ Missing elements:")
                for element in missing_elements:
                    print(f"   - {element}")
            
            return len(missing_elements) == 0
            
        except Exception as e:
            print(f"❌ Error loading mock: {e}")
            return False
        finally:
            browser.close()

if __name__ == "__main__":
    verify_mock_elements()
