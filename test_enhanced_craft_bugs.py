#!/usr/bin/env python3
"""
Test enhanced craft bug detection with improved mocks
"""

import asyncio
import json
import requests
from playwright.async_api import async_playwright

async def test_enhanced_craft_bug_detection():
    """Test the enhanced craft bug detection with improved mocks"""
    
    print("🔍 Testing Enhanced Craft Bug Detection")
    print("=" * 50)
    
    # Test the analysis API with enhanced scenarios
    test_data = {
        "url": "http://localhost:5173/mocks/word/basic-doc.html",
        "scenario_id": "1.4",  # Use the enhanced scenario
        "use_real_browser": True
    }
    
    try:
        print("📤 Sending analysis request...")
        response = requests.post(
            "http://localhost:8000/api/analyze",
            headers={"Content-Type": "application/json"},
            json=test_data,
            timeout=60
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Analysis Completed!")
            print(f"   Analysis ID: {result.get('analysis_id')}")
            print(f"   Status: {result.get('status')}")
            
            # Check for issues
            ux_issues = result.get('ux_issues', [])
            total_issues = result.get('total_issues', 0)
            
            print(f"   Total Issues: {total_issues}")
            print(f"   UX Issues: {len(ux_issues)}")
            
            # Categorize issues by type
            issue_types = {}
            craft_bug_issues = []
            
            for issue in ux_issues:
                issue_type = issue.get('type', 'unknown')
                if issue_type not in issue_types:
                    issue_types[issue_type] = 0
                issue_types[issue_type] += 1
                
                # Check for craft bug issues
                if 'craft' in issue.get('message', '').lower() or issue_type == 'craft_bug':
                    craft_bug_issues.append(issue)
            
            print(f"\n📊 Issue Breakdown:")
            for issue_type, count in issue_types.items():
                print(f"   {issue_type}: {count}")
            
            print(f"\n🐛 Craft Bug Issues: {len(craft_bug_issues)}")
            for i, issue in enumerate(craft_bug_issues):
                print(f"   {i+1}. {issue.get('message')}")
            
            # Check if we're detecting the expected craft bug categories
            expected_categories = ['A', 'B', 'D', 'E']
            detected_categories = []
            
            for issue in craft_bug_issues:
                message = issue.get('message', '')
                for category in expected_categories:
                    if f'Category {category}' in message:
                        detected_categories.append(category)
            
            print(f"\n🎯 Craft Bug Categories Detected: {list(set(detected_categories))}")
            print(f"   Expected: {expected_categories}")
            
            return result
        else:
            print(f"❌ Analysis Failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Analysis Error: {e}")
        return None

async def test_mock_interactions():
    """Test direct interactions with the enhanced mock"""
    
    print("\n🔍 Testing Enhanced Mock Interactions")
    print("=" * 40)
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        try:
            # Navigate to the enhanced mock
            await page.goto("http://localhost:5173/mocks/word/basic-doc.html", wait_until='domcontentloaded')
            
            # Wait for page to load
            await page.wait_for_timeout(2000)
            
            # Click the start button to trigger craft bugs
            start_button = await page.query_selector('.start-button')
            if start_button:
                print("✅ Found start button, clicking to trigger craft bugs...")
                await start_button.click()
                
                # Wait for craft bugs to be triggered
                await page.wait_for_timeout(5000)
                
                # Check for craft bug metrics
                craft_bug_metrics = await page.evaluate("""
                    () => {
                        return {
                            craftBugMetrics: window.craftBugMetrics || {},
                            animationConflicts: window.craftBugMetrics?.animationConflicts || [],
                            layoutShifts: window.craftBugMetrics?.layoutShifts || [],
                            inputDelays: window.craftBugMetrics?.inputDelays || [],
                            buttonResponseTimes: window.craftBugMetrics?.buttonResponseTimes || []
                        };
                    }
                """)
                
                print(f"📊 Craft Bug Metrics:")
                print(f"   Animation Conflicts: {len(craft_bug_metrics.get('animationConflicts', []))}")
                print(f"   Layout Shifts: {len(craft_bug_metrics.get('layoutShifts', []))}")
                print(f"   Input Delays: {len(craft_bug_metrics.get('inputDelays', []))}")
                print(f"   Button Response Times: {len(craft_bug_metrics.get('buttonResponseTimes', []))}")
                
                # Test input lag
                editor = await page.query_selector('#editor')
                if editor:
                    print("✅ Testing input lag simulation...")
                    await editor.click()
                    await editor.type('test input', delay=100)
                    await page.wait_for_timeout(1000)
                    
                    # Check for input delays
                    updated_metrics = await page.evaluate("""
                        () => window.craftBugMetrics?.inputDelays || []
                    """)
                    print(f"   Input Delays Recorded: {len(updated_metrics)}")
            
            await browser.close()
            return True
            
        except Exception as e:
            print(f"❌ Mock interaction test failed: {e}")
            await browser.close()
            return False

async def main():
    """Main test function"""
    print("🎯 Testing Enhanced Craft Bug Detection")
    print("=" * 50)
    
    # Test 1: Enhanced mock interactions
    await test_mock_interactions()
    
    # Test 2: Enhanced craft bug detection
    await test_enhanced_craft_bug_detection()
    
    print("\n🎉 Enhanced Craft Bug Tests Completed!")
    print("\n📊 Expected Craft Bug Categories:")
    print("   A. Loading/Performance - Slow loading, delays")
    print("   B. Motion/Animation - Jarring animations, conflicts")
    print("   D. Input Handling - Input lag, delayed responses")
    print("   E. Feedback - Missing hover states, unclear status")
    
    print("\n🎯 Next Steps:")
    print("   1. Test scenarios in the dashboard")
    print("   2. Verify craft bugs are detected in all categories")
    print("   3. Check that duplicate accessibility tab is removed")
    print("   4. Confirm reports open in overview tab")

if __name__ == "__main__":
    asyncio.run(main())
