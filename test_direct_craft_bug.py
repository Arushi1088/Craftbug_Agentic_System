#!/usr/bin/env python3
"""
Direct Craft Bug Detection Test
Test the CraftBugDetector class directly to isolate issues
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from playwright.async_api import async_playwright
from craft_bug_detector import CraftBugDetector

async def direct_craft_bug_test():
    """Test craft bug detection directly with Playwright"""
    
    print("🎯 DIRECT CRAFT BUG DETECTION TEST")
    print("=" * 50)
    
    async with async_playwright() as p:
        print("🚀 Launching browser...")
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        url = "http://localhost:8080/mocks/word/basic-doc.html"
        print(f"📄 Navigating to: {url}")
        
        await page.goto(url)
        await page.wait_for_load_state("networkidle")
        
        print("🔍 Checking for craft bug elements...")
        
        # Check if craft bug elements exist
        craft_elements = await page.query_selector_all(".craft-bug-hover")
        print(f"Found {len(craft_elements)} craft-bug-hover elements")
        
        # Check specific elements we know exist
        comments_tab = await page.query_selector("#comments-tab.craft-bug-hover")
        share_button = await page.query_selector(".share-button.craft-bug-hover")
        
        print(f"Comments tab found: {comments_tab is not None}")
        print(f"Share button found: {share_button is not None}")
        
        print("\n🐛 Running CraftBugDetector...")
        detector = CraftBugDetector()
        
        # Run craft bug analysis
        results = await detector.analyze_craft_bugs(page, url)
        
        print(f"\n📊 CRAFT BUG RESULTS:")
        print(f"Total bugs found: {results.total_bugs_found}")
        print(f"Analysis duration: {results.analysis_duration:.2f}s")
        print(f"URL: {results.url}")
        
        findings = results.findings
        if findings:
            print(f"\n🔍 FINDINGS ({len(findings)}):")
            for i, finding in enumerate(findings, 1):
                print(f"  {i}. Category {finding.category}: {finding.description}")
                print(f"     Severity: {finding.severity}")
                print(f"     Location: {finding.location}")
                print(f"     Metrics: {finding.metrics}")
        else:
            print("⚠️ No craft bugs detected")
            
        # Test manual interactions
        print("\n🎭 MANUAL INTERACTION TEST:")
        
        # Test hover on craft bug element
        if comments_tab:
            print("Testing hover on comments tab...")
            await page.hover("#comments-tab.craft-bug-hover")
            await asyncio.sleep(1)
            
        if share_button:
            print("Testing hover on share button...")
            await page.hover(".share-button.craft-bug-hover")
            await asyncio.sleep(1)
            
        # Run detection again after interactions
        print("\n🐛 Running CraftBugDetector after interactions...")
        results_after = await detector.analyze_craft_bugs(page, url)
        
        print(f"\n📊 RESULTS AFTER INTERACTIONS:")
        print(f"Total bugs found: {results_after.total_bugs_found}")
        print(f"Analysis duration: {results_after.analysis_duration:.2f}s")
        
        findings_after = results_after.findings
        if findings_after:
            print(f"\n🔍 FINDINGS AFTER INTERACTIONS ({len(findings_after)}):")
            for i, finding in enumerate(findings_after, 1):
                print(f"  {i}. Category {finding.category}: {finding.description}")
                print(f"     Severity: {finding.severity}")
                print(f"     Location: {finding.location}")
                print(f"     Metrics: {finding.metrics}")
        else:
            print("⚠️ No craft bugs detected after interactions")
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(direct_craft_bug_test())
