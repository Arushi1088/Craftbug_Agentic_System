#!/usr/bin/env python3
"""
Demo: How to trigger craft bugs in Word mock
This shows exactly which interactions trigger craft bugs
"""

import asyncio
from playwright.async_api import async_playwright
import time

async def demo_craft_bug_interactions():
    """Demo the exact interactions that trigger craft bugs"""
    
    print("🎯 CRAFT BUG INTERACTION DEMO")
    print("=" * 50)
    print("This will open a browser and show you which interactions trigger craft bugs...")
    
    async with async_playwright() as p:
        # Launch browser visibly so you can see what happens
        browser = await p.chromium.launch(headless=False, slow_mo=1000)
        page = await browser.new_page()
        
        # Navigate to Word mock
        url = "http://localhost:8080/mocks/word/basic-doc.html"
        print(f"🌐 Opening: {url}")
        await page.goto(url)
        await page.wait_for_load_state("networkidle")
        
        print("\n📋 CRAFT BUG ELEMENTS IN WORD MOCK:")
        print("1. Comments Tab (button#comments-tab.craft-bug-hover)")
        print("2. Help Button (.craft-bug-hover)")  
        print("3. Pictures Button (.image-insert-btn.craft-bug-hover)")
        print("4. Share Button (.share-button.craft-bug-hover)")
        print("5. Textarea (for input lag testing)")
        
        print("\n🎭 PERFORMING CRAFT BUG TRIGGERING INTERACTIONS:")
        
        # Wait for user to see the page
        await asyncio.sleep(3)
        
        print("1. 🖱️ Hovering over Comments tab (triggers hover craft bug)...")
        await page.hover("#comments-tab")
        await asyncio.sleep(2)
        
        print("2. 🖱️ Clicking Comments tab...")
        await page.click("#comments-tab")
        await asyncio.sleep(2)
        
        print("3. 🖱️ Hovering over Share button (triggers more hover bugs)...")
        await page.hover(".share-button.craft-bug-hover")
        await asyncio.sleep(2)
        
        print("4. 🖱️ Hovering over Pictures button...")
        await page.hover(".image-insert-btn.craft-bug-hover")
        await asyncio.sleep(2)
        
        print("5. ⌨️ Testing input lag in textarea...")
        try:
            await page.fill("textarea", "Testing input lag here...")
            await asyncio.sleep(2)
        except:
            print("   (No textarea found, that's ok)")
        
        print("6. 🖱️ Clicking Pictures button...")
        await page.click(".image-insert-btn.craft-bug-hover")
        await asyncio.sleep(2)
        
        print("\n🔍 NOW RUNNING CRAFT BUG DETECTION...")
        
        # Import craft bug detector
        import sys
        import os
        sys.path.append(os.path.dirname(os.path.abspath(__file__)))
        from craft_bug_detector import CraftBugDetector
        
        detector = CraftBugDetector()
        craft_results = await detector.analyze_craft_bugs(page, url)
        
        print(f"\n📊 CRAFT BUG DETECTION RESULTS:")
        print(f"✅ Total craft bugs found: {craft_results.total_bugs_found}")
        print(f"⏱️ Analysis duration: {craft_results.analysis_duration:.2f}s")
        
        if craft_results.findings:
            print(f"\n🐛 DETAILED CRAFT BUG FINDINGS:")
            for i, finding in enumerate(craft_results.findings, 1):
                print(f"\n  Bug #{i}:")
                print(f"    📂 Category: {finding.category}")
                print(f"    📝 Description: {finding.description}")
                print(f"    ⚠️ Severity: {finding.severity}")
                print(f"    📍 Location: {finding.location}")
                print(f"    📊 Metrics: {finding.metrics}")
        else:
            print("❌ No craft bugs detected")
            print("This might mean:")
            print("  - The interactions didn't trigger the JavaScript properly")
            print("  - The craft bug detection logic needs adjustment")
            print("  - The timing was off")
        
        print(f"\n🎯 CRAFT BUG TRIGGER SUMMARY:")
        print(f"The interactions that SHOULD trigger craft bugs are:")
        print(f"✅ Hover over .craft-bug-hover elements (animation conflicts)")
        print(f"✅ Click interactions with .craft-bug-hover elements") 
        print(f"✅ Input typing (input lag simulation)")
        print(f"✅ Multiple rapid interactions (layout thrash)")
        
        print(f"\n⌚ Keeping browser open for 10 seconds so you can inspect...")
        await asyncio.sleep(10)
        
        await browser.close()
        
        return craft_results

if __name__ == "__main__":
    result = asyncio.run(demo_craft_bug_interactions())
    print(f"\n🎉 Demo completed!")
    if result and result.total_bugs_found > 0:
        print(f"✅ Successfully triggered {result.total_bugs_found} craft bugs")
    else:
        print(f"❌ No craft bugs detected - might need debugging")
