"""
Simple test for craft bug detector
"""
import asyncio
import sys
import os
sys.path.append('/Users/arushitandon/Desktop/analyzer')

from craft_bug_detector import CraftBugDetector
from playwright.async_api import async_playwright

async def test_single_mock():
    """Test craft bug detection on Word mock"""
    
    detector = CraftBugDetector()
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        
        # Test the Word mock first
        url = 'http://127.0.0.1:9000/mocks/word/basic-doc.html'
        print(f"\n🔍 Testing craft bug detection on: {url}")
        
        try:
            # Let's check what content is actually loaded
            page_content = await page.content()
            print(f"📄 Page content length: {len(page_content)} characters")
            
            # Check the first 500 characters
            print(f"📄 Page content preview: {page_content[:500]}...")
            
            # First, let's check if the page loaded correctly
            title = await page.title()
            print(f"📄 Page title: '{title}'")
            
            # Check if craft bug metrics are available
            metrics_check = await page.evaluate("""
                () => {
                    return {
                        hasCraftBugMetrics: typeof window.craftBugMetrics !== 'undefined',
                        metricsKeys: window.craftBugMetrics ? Object.keys(window.craftBugMetrics) : [],
                        startDelay: window.craftBugMetrics ? window.craftBugMetrics.startDelay : 'N/A',
                        readyState: document.readyState
                    };
                }
            """)
            print(f"🔧 Craft Bug Metrics Check: {metrics_check}")
            
            report = await detector.analyze_craft_bugs(page, url)
            
            print(f"\n📊 CRAFT BUG ANALYSIS RESULTS")
            print(f"{'='*50}")
            print(f"URL: {report.url}")
            print(f"Analysis Duration: {report.analysis_duration:.2f}s")
            print(f"Total Bugs Found: {report.total_bugs_found}")
            print(f"\nBugs by Category:")
            for category, count in report.bugs_by_category.items():
                if count > 0:
                    print(f"  📍 Category {category}: {count} bugs")
            
            print(f"\n🔍 DETAILED FINDINGS:")
            print(f"{'='*50}")
            for i, finding in enumerate(report.findings, 1):
                print(f"{i}. [{finding.category}] {finding.bug_type}")
                print(f"   Severity: {finding.severity}")
                print(f"   Description: {finding.description}")
                print(f"   Location: {finding.location}")
                print(f"   Metrics: {finding.metrics}")
                print()
            
            # Export report
            filename = f"test_craft_bug_report.json"
            detector.export_report(report, filename)
            
        except Exception as e:
            print(f"❌ Error during analysis: {e}")
        
        await browser.close()

if __name__ == "__main__":
    print("🐛 Testing Craft Bug Detector on Enhanced Word Mock")
    asyncio.run(test_single_mock())
