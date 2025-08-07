#!/usr/bin/env python3
"""
Test script for the comment resolution scenario (1.2)
"""

import time
from playwright.sync_api import sync_playwright

def test_comment_resolution_scenario():
    """Test the comment resolution scenario step by step"""
    
    logs = []
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)  # Set to True for headless mode
        page = browser.new_page()
        
        try:
            # Step 1: Navigate to mock Word app
            print("Step 1: Navigating to mock Word app...")
            start_time = time.time()
            page.goto("http://localhost:3000/mock-word.html")
            logs.append({
                "step": "navigate_to_url",
                "url": "http://localhost:3000/mock-word.html",
                "time_ms": int((time.time() - start_time) * 1000),
                "status": "success"
            })
            
            # Step 2: Wait for and click Comments tab
            print("Step 2: Waiting for comments tab...")
            start_time = time.time()
            comments_tab = page.wait_for_selector('#comments-tab', timeout=5000)
            logs.append({
                "step": "wait_for_element",
                "selector": "#comments-tab",
                "time_ms": int((time.time() - start_time) * 1000),
                "status": "success"
            })
            
            print("Step 3: Clicking comments tab...")
            start_time = time.time()
            comments_tab.click()
            logs.append({
                "step": "click",
                "selector": "#comments-tab",
                "time_ms": int((time.time() - start_time) * 1000),
                "status": "success"
            })
            
            # Step 3: Wait for comments panel
            print("Step 4: Waiting for comments panel...")
            start_time = time.time()
            page.wait_for_selector('.comment-thread', timeout=3000)
            logs.append({
                "step": "wait_for_element",
                "selector": ".comment-thread",
                "time_ms": int((time.time() - start_time) * 1000),
                "status": "success"
            })
            
            # Step 4: Click resolve button on first comment
            print("Step 5: Clicking resolve button...")
            start_time = time.time()
            resolve_button = page.locator('.comment-thread .resolve-button').first
            resolve_button.click()
            logs.append({
                "step": "click",
                "selector": ".comment-thread .resolve-button",
                "time_ms": int((time.time() - start_time) * 1000),
                "status": "success"
            })
            
            # Step 5: Wait for resolved status
            print("Step 6: Waiting for resolved status...")
            start_time = time.time()
            page.wait_for_selector('.comment-thread .resolved', timeout=2000)
            logs.append({
                "step": "wait_for_element",
                "selector": ".comment-thread .resolved",
                "time_ms": int((time.time() - start_time) * 1000),
                "status": "success"
            })
            
            # Step 6: Assert resolved status is visible
            print("Step 7: Verifying resolved status is visible...")
            start_time = time.time()
            resolved_element = page.locator('.comment-thread .resolved').first
            is_visible = resolved_element.is_visible()
            logs.append({
                "step": "assert",
                "selector": ".comment-thread .resolved",
                "expectation": "visible",
                "result": is_visible,
                "time_ms": int((time.time() - start_time) * 1000),
                "status": "success" if is_visible else "failed"
            })
            
            print(f"✅ Scenario completed successfully! Resolved status visible: {is_visible}")
            
            # Take a screenshot for verification
            page.screenshot(path="comment_resolution_test.png")
            print("📸 Screenshot saved as comment_resolution_test.png")
            
            # Wait a moment to see the result
            time.sleep(2)
            
        except Exception as e:
            print(f"❌ Error during scenario execution: {e}")
            logs.append({
                "step": "error",
                "error": str(e),
                "time_ms": 0,
                "status": "failed"
            })
        
        finally:
            browser.close()
    
    return logs

if __name__ == "__main__":
    import json
    
    print("🎯 Testing Comment Resolution Scenario (1.2)")
    print("=" * 50)
    
    result = test_comment_resolution_scenario()
    
    # Save logs
    with open("comment_scenario_log.json", "w") as f:
        json.dump(result, f, indent=2)
    
    print("\n📄 Scenario log saved to comment_scenario_log.json")
    
    # Print summary
    successful_steps = len([step for step in result if step.get('status') == 'success'])
    total_steps = len(result)
    
    print(f"\n📊 Summary:")
    print(f"   Total steps: {total_steps}")
    print(f"   Successful: {successful_steps}")
    print(f"   Success rate: {(successful_steps/total_steps)*100:.1f}%")
    
    if successful_steps == total_steps:
        print("🎉 All steps completed successfully!")
    else:
        print("⚠️  Some steps failed. Check the logs for details.")
