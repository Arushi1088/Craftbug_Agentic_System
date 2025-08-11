#!/usr/bin/env python3
"""
Complete Craft Bug Integration Test
This replicates the exact flow that should happen in the scenario executor
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from playwright.async_api import async_playwright
from craft_bug_detector import CraftBugDetector

async def simulate_scenario_execution():
    """Simulate the exact scenario execution flow with craft bug detection"""
    
    print("🎯 COMPLETE CRAFT BUG INTEGRATION TEST")
    print("=" * 60)
    
    async with async_playwright() as p:
        print("🚀 Launching browser (like scenario executor)...")
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        
        url = "http://localhost:8080/mocks/word/basic-doc.html"
        print(f"📄 Step 1: Navigate to {url}")
        await page.goto(url)
        await page.wait_for_load_state("networkidle")
        
        print("⏱️ Step 2: Wait 1s")
        await asyncio.sleep(1)
        
        print("🖱️ Step 3: Click #comments-tab")
        try:
            await page.click("#comments-tab")
            print("   ✅ Comments tab clicked successfully")
        except Exception as e:
            print(f"   ❌ Failed to click comments tab: {e}")
        
        print("⏱️ Step 4: Wait 0.5s")
        await asyncio.sleep(0.5)
        
        print("\n🎭 Additional interactions to trigger craft bugs:")
        
        # Perform interactions that should trigger craft bugs
        try:
            print("🖱️ Hover over craft-bug-hover elements...")
            craft_elements = await page.query_selector_all(".craft-bug-hover")
            print(f"Found {len(craft_elements)} craft bug elements")
            
            for i, element in enumerate(craft_elements):
                print(f"   Hovering over element {i+1}...")
                await page.hover(f".craft-bug-hover:nth-of-type({i+1})")
                await asyncio.sleep(0.3)
                
            print("🖱️ Click share button...")
            await page.click(".share-button.craft-bug-hover")
            await asyncio.sleep(0.5)
            
            print("⌨️ Type in comment area...")
            await page.fill("textarea", "Test comment for input lag detection")
            await asyncio.sleep(0.5)
            
        except Exception as e:
            print(f"   ⚠️ Some interactions failed: {e}")
        
        print(f"\n🐛 Running craft bug detection (like UX heuristics module)...")
        detector = CraftBugDetector()
        
        # This is exactly what scenario_executor.py does
        craft_bug_results = await detector.analyze_craft_bugs(page, url)
        
        print(f"\n📊 CRAFT BUG ANALYSIS RESULTS:")
        print(f"Total bugs found: {craft_bug_results.total_bugs_found}")
        print(f"Analysis duration: {craft_bug_results.analysis_duration:.2f}s")
        
        if craft_bug_results.findings:
            print(f"\n🔍 CRAFT BUGS DETECTED ({len(craft_bug_results.findings)}):")
            for i, finding in enumerate(craft_bug_results.findings, 1):
                print(f"  {i}. Category {finding.category}: {finding.description}")
                print(f"     Severity: {finding.severity}")
                print(f"     Location: {finding.location}")
                print(f"     Metrics: {finding.metrics}")
                
                # Convert to UX issue format (like scenario_executor.py does)
                ux_issue = {
                    "type": "craft_bug",
                    "message": f"Craft Bug (Category {finding.category}): {finding.description}",
                    "severity": finding.severity,
                    "element": finding.location,
                    "recommendation": "Fix craft bug interaction issue",
                    "category": f"Craft Bug Category {finding.category}",
                    "craft_bug": True,
                    "metric_value": finding.metrics
                }
                print(f"     UX Issue Format: {ux_issue}")
        else:
            print("⚠️ No craft bugs detected")
            
        print("\n🔍 Summary:")
        print(f"- Browser interactions: ✅ Completed")
        print(f"- Craft bug detection: ✅ Ran successfully")
        print(f"- Bugs found: {craft_bug_results.total_bugs_found}")
        print(f"- Integration format: ✅ Ready for UX heuristics")
        
        await browser.close()
        return craft_bug_results

if __name__ == "__main__":
    results = asyncio.run(simulate_scenario_execution())
