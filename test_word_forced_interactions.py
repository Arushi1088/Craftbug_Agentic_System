#!/usr/bin/env python3
"""
Word Analysis with Forced Craft Bug Interactions
This will make an API call and then manually trigger additional interactions
"""

import asyncio
import requests
import time
from playwright.async_api import async_playwright
from datetime import datetime
import json

async def word_analysis_with_forced_interactions():
    """Run Word analysis and then add interactions to trigger craft bugs"""
    
    print("🎯 WORD ANALYSIS WITH FORCED CRAFT BUG INTERACTIONS")
    print("=" * 60)
    
    # First, run the normal API analysis
    print("📤 Step 1: Running standard API analysis...")
    
    analysis_request = {
        "url": "http://localhost:8080/mocks/word/basic-doc.html",
        "options": {
            "browser": True,
            "performance": True,
            "accessibility": True,
            "ux_heuristics": True
        }
    }
    
    try:
        response = requests.post(
            "http://localhost:8000/api/analyze",
            json=analysis_request,
            timeout=60
        )
        
        if response.status_code == 200:
            result = response.json()
            analysis_id = result.get("analysis_id")
            print(f"✅ Standard analysis completed: {analysis_id}")
            
            # Wait for completion
            time.sleep(8)
            
            # Get initial results
            report_response = requests.get(f"http://localhost:8000/api/reports/{analysis_id}")
            if report_response.status_code == 200:
                initial_report = report_response.json()
                print(f"📊 Initial results: {initial_report.get('total_issues', 0)} issues found")
                
                # Now run additional interactions to trigger craft bugs
                print("\n🎭 Step 2: Running additional craft bug interactions...")
                
                async with async_playwright() as p:
                    browser = await p.chromium.launch(headless=False)
                    page = await browser.new_page()
                    
                    # Navigate to the same URL
                    url = "http://localhost:8080/mocks/word/basic-doc.html"
                    await page.goto(url)
                    await page.wait_for_load_state("networkidle")
                    
                    print("🖱️ Performing craft bug triggering interactions...")
                    
                    # Interactions that should trigger craft bugs
                    interactions = [
                        ("click", "#comments-tab", "Click comments tab"),
                        ("wait", 500, "Wait for comments panel"),
                        ("hover", ".craft-bug-hover", "Hover craft bug element 1"),
                        ("wait", 300, "Wait for hover metrics"),
                        ("hover", ".share-button.craft-bug-hover", "Hover share button"),
                        ("wait", 300, "Wait for hover metrics"),
                        ("click", ".craft-bug-hover", "Click craft bug element"),
                        ("wait", 500, "Wait for click response"),
                        ("type", "textarea", "Testing input lag in textarea"),
                        ("wait", 1000, "Wait for input lag metrics"),
                        ("click", ".image-insert-btn.craft-bug-hover", "Click image insert"),
                        ("wait", 2000, "Final wait for all metrics")
                    ]
                    
                    for action, target, description in interactions:
                        try:
                            print(f"   {description}...")
                            if action == "click":
                                await page.click(target)
                            elif action == "hover":
                                await page.hover(target)
                            elif action == "type":
                                await page.fill("textarea", target)
                            elif action == "wait":
                                await asyncio.sleep(target / 1000.0)
                        except Exception as e:
                            print(f"   ⚠️ {description} failed: {e}")
                    
                    print("🐛 Running craft bug detection after interactions...")
                    
                    # Import and run craft bug detection
                    import sys
                    import os
                    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
                    from craft_bug_detector import CraftBugDetector
                    
                    detector = CraftBugDetector()
                    craft_results = await detector.analyze_craft_bugs(page, url)
                    
                    print(f"\n📊 CRAFT BUG RESULTS:")
                    print(f"Total bugs found: {craft_results.total_bugs_found}")
                    print(f"Analysis duration: {craft_results.analysis_duration:.2f}s")
                    
                    if craft_results.findings:
                        print(f"\n🔍 CRAFT BUG FINDINGS ({len(craft_results.findings)}):")
                        for i, finding in enumerate(craft_results.findings, 1):
                            print(f"  {i}. Category {finding.category}: {finding.description}")
                            print(f"     Severity: {finding.severity}")
                            print(f"     Location: {finding.location}")
                            print(f"     Metrics: {finding.metrics}")
                    else:
                        print("⚠️ No craft bugs detected even after interactions")
                    
                    await browser.close()
                
                # Final summary combining both analyses
                print(f"\n🎯 COMPLETE ANALYSIS SUMMARY:")
                print(f"✅ Standard API analysis: {initial_report.get('total_issues', 0)} issues")
                print(f"✅ Additional craft bug detection: {craft_results.total_bugs_found} craft bugs")
                print(f"✅ Total comprehensive issues: {initial_report.get('total_issues', 0) + craft_results.total_bugs_found}")
                
                # Save combined results
                combined_results = {
                    "standard_analysis": initial_report,
                    "craft_bug_analysis": {
                        "total_bugs_found": craft_results.total_bugs_found,
                        "findings": [
                            {
                                "category": f.category,
                                "description": f.description,
                                "severity": f.severity,
                                "location": f.location,
                                "metrics": f.metrics,
                                "timestamp": f.timestamp
                            } for f in craft_results.findings
                        ],
                        "analysis_duration": craft_results.analysis_duration
                    },
                    "analysis_timestamp": datetime.now().isoformat()
                }
                
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"word_combined_analysis_{timestamp}.json"
                with open(filename, 'w') as f:
                    json.dump(combined_results, f, indent=2)
                print(f"💾 Combined analysis saved to: {filename}")
                
                return combined_results
            else:
                print(f"❌ Failed to get initial report: {report_response.status_code}")
        else:
            print(f"❌ Standard analysis failed: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"❌ Analysis error: {e}")
        import traceback
        traceback.print_exc()
    
    return None

if __name__ == "__main__":
    result = asyncio.run(word_analysis_with_forced_interactions())
    if result:
        print("\n🎉 WORD COMPLETE END-TO-END ANALYSIS SUCCESSFUL!")
        total_issues = result["standard_analysis"].get("total_issues", 0)
        craft_bugs = result["craft_bug_analysis"]["total_bugs_found"]
        print(f"📊 Final Score: {total_issues + craft_bugs} total issues detected")
        print(f"🐛 Craft Bugs: {craft_bugs} detected via targeted interactions")
    else:
        print("\n💥 Analysis failed!")
