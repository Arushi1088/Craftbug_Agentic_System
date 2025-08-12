#!/usr/bin/env python3
"""
Comprehensive test to verify all improvements work correctly
"""

import asyncio
import json
import requests
from playwright.async_api import async_playwright

async def test_comprehensive_improvements():
    """Test all improvements comprehensively"""
    
    print("🎯 Testing Comprehensive Improvements")
    print("=" * 50)
    
    # Test 1: Enhanced scenario execution
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
            timeout=90  # Longer timeout for comprehensive test
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
            accessibility_issues = []
            performance_issues = []
            
            for issue in ux_issues:
                issue_type = issue.get('type', 'unknown')
                message = issue.get('message', '').lower()
                
                if issue_type not in issue_types:
                    issue_types[issue_type] = 0
                issue_types[issue_type] += 1
                
                # Categorize issues
                if 'craft' in message or issue_type == 'craft_bug':
                    craft_bug_issues.append(issue)
                elif 'accessibility' in message or 'alt' in message or 'contrast' in message:
                    accessibility_issues.append(issue)
                elif 'performance' in message or 'loading' in message:
                    performance_issues.append(issue)
            
            print(f"\n📊 Issue Breakdown:")
            for issue_type, count in issue_types.items():
                print(f"   {issue_type}: {count}")
            
            print(f"\n🐛 Craft Bug Issues: {len(craft_bug_issues)}")
            for i, issue in enumerate(craft_bug_issues):
                print(f"   {i+1}. {issue.get('message')}")
            
            print(f"\n♿ Accessibility Issues: {len(accessibility_issues)}")
            for i, issue in enumerate(accessibility_issues[:3]):  # Show first 3
                print(f"   {i+1}. {issue.get('message')}")
            
            print(f"\n⚡ Performance Issues: {len(performance_issues)}")
            for i, issue in enumerate(performance_issues):
                print(f"   {i+1}. {issue.get('message')}")
            
            # Check craft bug categories
            expected_categories = ['A', 'B', 'D', 'E']
            detected_categories = []
            
            for issue in craft_bug_issues:
                message = issue.get('message', '')
                for category in expected_categories:
                    if f'Category {category}' in message:
                        detected_categories.append(category)
            
            print(f"\n🎯 Craft Bug Categories Detected: {list(set(detected_categories))}")
            print(f"   Expected: {expected_categories}")
            
            # Check step execution
            step_results = result.get('step_results', [])
            failed_steps = [step for step in step_results if step.get('status') == 'error']
            warning_steps = [step for step in step_results if step.get('status') == 'warning']
            
            print(f"\n📋 Step Execution Results:")
            print(f"   Total Steps: {len(step_results)}")
            print(f"   Failed Steps: {len(failed_steps)}")
            print(f"   Warning Steps: {len(warning_steps)}")
            print(f"   Success Rate: {((len(step_results) - len(failed_steps)) / len(step_results) * 100):.1f}%" if step_results else "N/A")
            
            return result
        else:
            print(f"❌ Analysis Failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Analysis Error: {e}")
        return None

async def test_mock_interactions_comprehensive():
    """Test comprehensive mock interactions"""
    
    print("\n🔍 Testing Comprehensive Mock Interactions")
    print("=" * 50)
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        try:
            # Navigate to the enhanced mock
            await page.goto("http://localhost:5173/mocks/word/basic-doc.html", wait_until='domcontentloaded')
            
            # Wait for page to load
            await page.wait_for_timeout(2000)
            
            # Click the start button to trigger all craft bugs
            start_button = await page.query_selector('.start-button')
            if start_button:
                print("✅ Found start button, clicking to trigger all craft bugs...")
                await start_button.click()
                
                # Wait for craft bugs to be triggered
                await page.wait_for_timeout(5000)
                
                # Test various interactions
                print("✅ Testing various interactions...")
                
                # Test clicking craft bug buttons
                craft_bug_buttons = await page.query_selector_all('.craft-bug-hover')
                for i, button in enumerate(craft_bug_buttons[:3]):
                    await button.click()
                    await page.wait_for_timeout(500)
                
                # Test typing in editor
                editor = await page.query_selector('#editor')
                if editor:
                    await editor.click()
                    await editor.type('Testing input lag and craft bug detection', delay=50)
                    await page.wait_for_timeout(1000)
                
                # Check for craft bug metrics
                craft_bug_metrics = await page.evaluate("""
                    () => {
                        return {
                            craftBugMetrics: window.craftBugMetrics || {},
                            animationConflicts: window.craftBugMetrics?.animationConflicts || [],
                            layoutShifts: window.craftBugMetrics?.layoutShifts || [],
                            inputDelays: window.craftBugMetrics?.inputDelays || [],
                            buttonResponseTimes: window.craftBugMetrics?.buttonResponseTimes || [],
                            feedbackFailures: window.craftBugMetrics?.feedbackFailures || [],
                            loadingDelay: window.craftBugMetrics?.loadingDelay || 0
                        };
                    }
                """)
                
                print(f"📊 Comprehensive Craft Bug Metrics:")
                print(f"   Animation Conflicts: {len(craft_bug_metrics.get('animationConflicts', []))}")
                print(f"   Layout Shifts: {len(craft_bug_metrics.get('layoutShifts', []))}")
                print(f"   Input Delays: {len(craft_bug_metrics.get('inputDelays', []))}")
                print(f"   Button Response Times: {len(craft_bug_metrics.get('buttonResponseTimes', []))}")
                print(f"   Feedback Failures: {len(craft_bug_metrics.get('feedbackFailures', []))}")
                print(f"   Loading Delay: {craft_bug_metrics.get('loadingDelay', 0)}ms")
                
                # Test accessibility issues
                accessibility_issues = await page.evaluate("""
                    () => {
                        const issues = [];
                        
                        // Check for images without alt text
                        const imagesWithoutAlt = document.querySelectorAll('img:not([alt])');
                        issues.push(`Images without alt text: ${imagesWithoutAlt.length}`);
                        
                        // Check for form inputs without labels
                        const inputsWithoutLabels = document.querySelectorAll('input:not([id]), textarea:not([id])');
                        issues.push(`Form inputs without labels: ${inputsWithoutLabels.length}`);
                        
                        // Check for color contrast issues (simplified)
                        const lowContrastElements = document.querySelectorAll('.low-contrast, [style*="color: #ccc"]');
                        issues.push(`Potential contrast issues: ${lowContrastElements.length}`);
                        
                        return issues;
                    }
                """)
                
                print(f"\n♿ Accessibility Issues Found:")
                for issue in accessibility_issues:
                    print(f"   - {issue}")
            
            await browser.close()
            return True
            
        except Exception as e:
            print(f"❌ Mock interaction test failed: {e}")
            await browser.close()
            return False

async def main():
    """Main test function"""
    print("🎯 Testing All Comprehensive Improvements")
    print("=" * 50)
    
    # Test 1: Comprehensive mock interactions
    await test_mock_interactions_comprehensive()
    
    # Test 2: Comprehensive analysis
    await test_comprehensive_improvements()
    
    print("\n🎉 Comprehensive Improvement Tests Completed!")
    print("\n📊 Summary of Expected Improvements:")
    print("   ✅ Better step execution reliability (fewer timeouts)")
    print("   ✅ Enhanced craft bug detection across all categories")
    print("   ✅ More realistic accessibility issues")
    print("   ✅ Better performance issue detection")
    print("   ✅ Improved error handling and recovery")
    
    print("\n🎯 Expected Results:")
    print("   - Higher success rate in step execution")
    print("   - More craft bugs detected (Categories A, B, D, E)")
    print("   - Better quality accessibility issues")
    print("   - More comprehensive performance analysis")
    print("   - Fewer 'Step X failed' errors")

if __name__ == "__main__":
    asyncio.run(main())
