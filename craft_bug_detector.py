"""
Craft Bug Detection Module
Detects intentional craft bugs in web applications to test UX analysis systems.

Categories:
A. Loading/Performance - Slow loading times, delays, performance issues
B. Motion/Animation - Jarring animations, conflicting motion, visual noise
D. Input Handling - Input lag, delayed responses, poor interaction feedback
E. Feedback - Missing hover states, unclear status, poor visual feedback
"""

import asyncio
import json
import time
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from playwright.async_api import Page, Browser, TimeoutError as PlaywrightTimeoutError

@dataclass
class CraftBugFinding:
    """Single craft bug detection result"""
    category: str  # A, B, D, E
    bug_type: str
    severity: str  # 'low', 'medium', 'high', 'critical'
    description: str
    location: str
    metrics: Dict[str, Any]
    timestamp: float

@dataclass
class CraftBugReport:
    """Complete craft bug analysis report"""
    url: str
    analysis_duration: float
    total_bugs_found: int
    bugs_by_category: Dict[str, int]
    findings: List[CraftBugFinding]
    metrics_summary: Dict[str, Any]
    timestamp: float

class CraftBugDetector:
    """Detects intentional craft bugs in web applications"""
    
    def __init__(self):
        self.detection_thresholds = {
            'loading_delay': 2000,      # 2+ seconds = bug
            'input_lag': 100,           # 100+ ms = bug  
            'animation_judder': 16,     # 16+ ms frame time = bug
            'layout_thrash': 3,         # 3+ reflows = bug
            'missing_feedback': 500,    # 500+ ms without feedback = bug
        }
    
    async def analyze_craft_bugs(self, page: Page, url: str) -> CraftBugReport:
        """Main analysis method - detects all craft bug categories"""
        start_time = time.time()
        findings = []
        
        print(f"🔍 Starting craft bug analysis for: {url}")
        
        # Check if we're already on the target URL to avoid reloading and losing metrics
        current_url = page.url
        if current_url != url:
            # Only navigate if we're not already on the target page
            try:
                await page.goto(url, wait_until='domcontentloaded', timeout=30000)
                # Wait longer for JavaScript to execute
                await asyncio.sleep(5)
                
                # Wait for craft bug metrics to be available
                await page.wait_for_function("""
                    () => window.craftBugMetrics || window.excelCraftBugMetrics || window.pptCraftBugMetrics || document.readyState === 'complete'
                """, timeout=10000)
                
            except PlaywrightTimeoutError:
                print(f"⚠️ Timeout loading {url}, continuing with analysis...")
                await asyncio.sleep(2)
        else:
            print(f"📍 Already on target URL, preserving existing page state and metrics")
            # Just wait a moment to ensure metrics are available
            await asyncio.sleep(1)
        
        # Category A: Loading/Performance Detection
        category_a_bugs = await self._detect_loading_performance_bugs(page)
        findings.extend(category_a_bugs)
        
        # Category B: Motion/Animation Detection  
        category_b_bugs = await self._detect_motion_animation_bugs(page)
        findings.extend(category_b_bugs)
        
        # Category D: Input Handling Detection
        category_d_bugs = await self._detect_input_handling_bugs(page)
        findings.extend(category_d_bugs)
        
        # Category E: Feedback Detection
        category_e_bugs = await self._detect_feedback_bugs(page)
        findings.extend(category_e_bugs)
        
        # Generate summary metrics
        analysis_duration = time.time() - start_time
        bugs_by_category = self._categorize_findings(findings)
        metrics_summary = await self._collect_metrics_summary(page)
        
        report = CraftBugReport(
            url=url,
            analysis_duration=analysis_duration,
            total_bugs_found=len(findings),
            bugs_by_category=bugs_by_category,
            findings=findings,
            metrics_summary=metrics_summary,
            timestamp=time.time()
        )
        
        print(f"✅ Analysis complete: {len(findings)} craft bugs detected")
        return report
    
    async def _detect_loading_performance_bugs(self, page: Page) -> List[CraftBugFinding]:
        """Category A: Detect loading and performance issues"""
        findings = []
        
        # Check for intentional loading delays
        try:
            # Look for craft bug metrics in page
            metrics = await page.evaluate("""
                () => {
                    const metrics = window.craftBugMetrics || window.excelCraftBugMetrics || window.pptCraftBugMetrics || {};
                    return {
                        startDelay: metrics.startDelay || 0,
                        loadingTime: metrics.loadingTime || 0,
                        performanceMarks: performance.getEntriesByType('mark').length
                    };
                }
            """)
            
            # Detect start delays (Category A bugs)
            if metrics.get('startDelay', 0) >= self.detection_thresholds['loading_delay']:
                findings.append(CraftBugFinding(
                    category='A',
                    bug_type='intentional_start_delay',
                    severity='high',
                    description=f"Intentional start delay detected: {metrics['startDelay']}ms",
                    location='page_load',
                    metrics={'delay_ms': metrics['startDelay']},
                    timestamp=time.time()
                ))
            
            # Check for slow resource loading
            navigation_timing = await page.evaluate("""
                () => {
                    const timing = performance.timing;
                    return {
                        domContentLoaded: timing.domContentLoadedEventEnd - timing.navigationStart,
                        pageLoad: timing.loadEventEnd - timing.navigationStart
                    };
                }
            """)
            
            if navigation_timing['domContentLoaded'] > 3000:
                findings.append(CraftBugFinding(
                    category='A',
                    bug_type='slow_dom_load',
                    severity='medium',
                    description=f"Slow DOM loading: {navigation_timing['domContentLoaded']}ms",
                    location='document',
                    metrics=navigation_timing,
                    timestamp=time.time()
                ))
                
        except Exception as e:
            print(f"Error in loading detection: {e}")
        
        return findings
    
    async def _detect_motion_animation_bugs(self, page: Page) -> List[CraftBugFinding]:
        """Category B: Detect motion and animation issues"""
        findings = []
        
        try:
            # Check for jarring animations and layout thrash
            animation_metrics = await page.evaluate("""
                () => {
                    const metrics = window.craftBugMetrics || window.excelCraftBugMetrics || window.pptCraftBugMetrics || {};
                    console.log('Raw metrics:', metrics);
                    
                    const result = {
                        layoutThrashCount: (metrics.layoutShifts ? metrics.layoutShifts.length : 0),
                        animationConflicts: (metrics.animationConflicts ? metrics.animationConflicts.length : 0),
                        judderEvents: 0, // Legacy field
                        frameTimes: [],
                        // Enhanced metrics from the mock
                        layoutShifts: metrics.layoutShifts || [],
                        animationConflictList: metrics.animationConflicts || [],
                        // Raw counts for debugging
                        rawLayoutShiftsCount: metrics.layoutShifts ? metrics.layoutShifts.length : 0,
                        rawAnimationConflictsCount: metrics.animationConflicts ? metrics.animationConflicts.length : 0
                    };
                    
                    console.log('Processed metrics:', result);
                    return result;
                }
            """)
            
            # Debug: Check the types of values returned
            print(f"Debug animation_metrics: {animation_metrics}")
            
            # Detect layout thrash (Category B)
            layout_count = animation_metrics.get('layoutThrashCount', 0)
            print(f"Debug layout_count: {layout_count}, threshold: {self.detection_thresholds['layout_thrash']}")
            if isinstance(layout_count, (list, tuple)):
                layout_count = len(layout_count) if layout_count else 0
            if layout_count >= self.detection_thresholds['layout_thrash']:
                print(f"✅ CREATING layout thrash finding!")
                findings.append(CraftBugFinding(
                    category='B',
                    bug_type='layout_thrash',
                    severity='high',
                    description=f"Layout thrash detected: {layout_count} events",
                    location='layout_system',
                    metrics=animation_metrics,
                    timestamp=time.time()
                ))
            else:
                print(f"❌ Layout thrash NOT detected: {layout_count} < {self.detection_thresholds['layout_thrash']}")
            
            # Check for animation conflicts
            conflicts = animation_metrics.get('animationConflicts', 0)
            print(f"Debug conflicts: {conflicts}")
            if isinstance(conflicts, (list, tuple)):
                conflicts = len(conflicts) if conflicts else 0
            if conflicts > 0:
                print(f"✅ CREATING animation conflicts finding!")
                findings.append(CraftBugFinding(
                    category='B',
                    bug_type='animation_conflicts',
                    severity='medium',
                    description=f"Conflicting animations: {conflicts} conflicts",
                    location='animation_system',
                    metrics=animation_metrics,
                    timestamp=time.time()
                ))
            else:
                print(f"❌ Animation conflicts NOT detected: {conflicts} <= 0")
            
            # Detect slide judder (PowerPoint specific)
            judder = animation_metrics.get('judderEvents', 0)
            if isinstance(judder, (list, tuple)):
                judder = len(judder) if judder else 0
            if judder > 0:
                findings.append(CraftBugFinding(
                    category='B',
                    bug_type='slide_judder',
                    severity='medium',
                    description=f"Slide transition judder: {judder} events",
                    location='slide_transitions',
                    metrics=animation_metrics,
                    timestamp=time.time()
                ))
            
            # Check frame times for animation judder
            frame_times = animation_metrics.get('frameTimes', [])
            if isinstance(frame_times, list) and frame_times:
                slow_frames = [ft for ft in frame_times if ft > self.detection_thresholds['animation_judder']]
                if slow_frames:
                    findings.append(CraftBugFinding(
                        category='B',
                        bug_type='animation_judder',
                        severity='medium',
                        description=f"Animation judder detected: {len(slow_frames)} slow frames (>{self.detection_thresholds['animation_judder']}ms)",
                        location='animation_frames',
                        metrics={'slow_frames_count': len(slow_frames), 'max_frame_time': max(slow_frames)},
                        timestamp=time.time()
                    ))
                
        except Exception as e:
            print(f"Error in animation detection: {e}")
            import traceback
            traceback.print_exc()
        
        return findings
    
    async def _detect_input_handling_bugs(self, page: Page) -> List[CraftBugFinding]:
        """Category D: Detect input handling issues"""
        findings = []
        
        try:
            # Test input elements for lag
            input_elements = await page.query_selector_all('input, textarea, [contenteditable="true"]')
            
            for i, element in enumerate(input_elements[:3]):  # Test first 3 elements
                try:
                    # Check if element is visible and enabled
                    is_visible = await element.is_visible()
                    is_enabled = await element.is_enabled()
                    
                    if is_visible and is_enabled:
                        # Measure input response time
                        start_time = time.time() * 1000
                        await element.click(timeout=5000)
                        await element.type('test', delay=0)
                        response_time = (time.time() * 1000) - start_time
                        
                        if response_time > self.detection_thresholds['input_lag']:
                            findings.append(CraftBugFinding(
                                category='D',
                                bug_type='input_lag',
                                severity='high',
                                description=f"Input lag detected: {response_time:.0f}ms response time",
                                location=f'input_element_{i}',
                                metrics={'response_time_ms': response_time},
                                timestamp=time.time()
                            ))
                except Exception as e:
                    # Skip problematic elements but continue testing
                    continue
            
            # Check for craft bug metrics related to input
            input_metrics = await page.evaluate("""
                () => {
                    const metrics = window.craftBugMetrics || window.excelCraftBugMetrics || window.pptCraftBugMetrics || {};
                    const result = {
                        inputLagEvents: (metrics.inputDelays ? metrics.inputDelays.length : 0),
                        delayedResponses: (metrics.buttonResponseTimes ? metrics.buttonResponseTimes.length : 0),
                        textBoxLagEvents: 0,
                        // Enhanced metrics from the mock
                        inputDelays: metrics.inputDelays || [],
                        buttonResponseTimes: metrics.buttonResponseTimes || [],
                        // Raw counts for debugging
                        rawInputDelaysCount: metrics.inputDelays ? metrics.inputDelays.length : 0,
                        rawButtonResponseCount: metrics.buttonResponseTimes ? metrics.buttonResponseTimes.length : 0
                    };
                    console.log('Input metrics:', result);
                    return result;
                }
            """)
            
            print(f"Debug input_metrics: {input_metrics}")
            
            input_lag_events = input_metrics.get('inputLagEvents', 0)
            print(f"Debug input_lag_events: {input_lag_events}")
            if input_lag_events > 0:
                print(f"✅ CREATING input lag finding!")
                findings.append(CraftBugFinding(
                    category='D',
                    bug_type='intentional_input_lag',
                    severity='high',
                    description=f"Intentional input lag: {input_lag_events} events",
                    location='input_system',
                    metrics=input_metrics,
                    timestamp=time.time()
                ))
            else:
                print(f"❌ Input lag NOT detected: {input_lag_events} <= 0")
                
        except Exception as e:
            print(f"Error in input detection: {e}")
        
        return findings
    
    async def _detect_feedback_bugs(self, page: Page) -> List[CraftBugFinding]:
        """Category E: Detect feedback issues"""
        findings = []
        
        try:
            # Test hover states and feedback
            interactive_elements = await page.query_selector_all('button, a, .clickable, [role="button"]')
            
            for i, element in enumerate(interactive_elements[:5]):  # Test first 5 elements
                # Check for hover feedback
                await element.hover()
                await asyncio.sleep(0.1)
                
                # Check if element has hover styles
                has_hover = await element.evaluate("""
                    (el) => {
                        const styles = window.getComputedStyle(el, ':hover');
                        const normalStyles = window.getComputedStyle(el);
                        return styles.cursor !== normalStyles.cursor || 
                               styles.backgroundColor !== normalStyles.backgroundColor ||
                               styles.color !== normalStyles.color;
                    }
                """)
                
                if not has_hover:
                    findings.append(CraftBugFinding(
                        category='E',
                        bug_type='missing_hover_feedback',
                        severity='medium',
                        description=f"Missing hover feedback on interactive element",
                        location=f'element_{i}',
                        metrics={'element_type': await element.evaluate('el => el.tagName')},
                        timestamp=time.time()
                    ))
            
            # Check for silent failures
            failure_metrics = await page.evaluate("""
                () => {
                    const metrics = window.craftBugMetrics || window.excelCraftBugMetrics || window.pptCraftBugMetrics || {};
                    return {
                        silentFailures: metrics.silentFailures || 0,
                        missingFeedback: metrics.missingFeedback || 0,
                        feedbackFailures: metrics.feedbackFailures || []
                    };
                }
            """)
            
            # Check for feedback failures from enhanced mocks
            if failure_metrics.get('feedbackFailures', []):
                failures = failure_metrics['feedbackFailures']
                findings.append(CraftBugFinding(
                    category='E',
                    bug_type='feedback_failures',
                    severity='medium',
                    description=f"Feedback failures detected: {len(failures)} instances",
                    location='feedback_system',
                    metrics={'failure_count': len(failures), 'failures': failures[:3]},  # Show first 3
                    timestamp=time.time()
                ))
            
            if failure_metrics.get('silentFailures', 0) > 0:
                findings.append(CraftBugFinding(
                    category='E',
                    bug_type='silent_failures',
                    severity='high',
                    description=f"Silent failures detected: {failure_metrics['silentFailures']} events",
                    location='error_handling',
                    metrics=failure_metrics,
                    timestamp=time.time()
                ))
                
        except Exception as e:
            print(f"Error in feedback detection: {e}")
        
        return findings
    
    async def _collect_metrics_summary(self, page: Page) -> Dict[str, Any]:
        """Collect overall metrics summary"""
        try:
            return await page.evaluate("""
                () => {
                    const allMetrics = {
                        ...(window.craftBugMetrics || {}),
                        ...(window.excelCraftBugMetrics || {}),
                        ...(window.pptCraftBugMetrics || {})
                    };
                    
                    return {
                        pageTitle: document.title,
                        metricsAvailable: Object.keys(allMetrics).length > 0,
                        performanceEntries: performance.getEntries().length,
                        craftBugMetrics: allMetrics
                    };
                }
            """)
        except:
            return {'error': 'Could not collect metrics'}
    
    def _categorize_findings(self, findings: List[CraftBugFinding]) -> Dict[str, int]:
        """Count findings by category"""
        categories = {'A': 0, 'B': 0, 'D': 0, 'E': 0}
        for finding in findings:
            categories[finding.category] = categories.get(finding.category, 0) + 1
        return categories
    
    def _create_empty_report(self, url: str, duration: float) -> CraftBugReport:
        """Create empty report for failed analysis"""
        return CraftBugReport(
            url=url,
            analysis_duration=duration,
            total_bugs_found=0,
            bugs_by_category={'A': 0, 'B': 0, 'D': 0, 'E': 0},
            findings=[],
            metrics_summary={'error': 'Analysis failed'},
            timestamp=time.time()
        )
    
    def export_report(self, report: CraftBugReport, filepath: str) -> None:
        """Export report to JSON file"""
        with open(filepath, 'w') as f:
            json.dump(asdict(report), f, indent=2, default=str)
        print(f"📄 Report exported to: {filepath}")

# Example usage for testing
async def test_craft_bug_detection():
    """Test the craft bug detector on enhanced mocks"""
    from playwright.async_api import async_playwright
    
    detector = CraftBugDetector()
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        
        # Test URLs for enhanced mocks
        test_urls = [
            'http://localhost:4173/mocks/word/basic-doc.html',
            'http://localhost:4173/mocks/excel/open-format.html', 
            'http://localhost:4173/mocks/powerpoint/basic-deck.html'
        ]
        
        for url in test_urls:
            print(f"\n🔍 Testing: {url}")
            report = await detector.analyze_craft_bugs(page, url)
            
            print(f"📊 Results: {report.total_bugs_found} bugs found")
            for category, count in report.bugs_by_category.items():
                if count > 0:
                    print(f"  Category {category}: {count} bugs")
            
            # Export report
            filename = f"craft_bug_report_{url.split('/')[-1].replace('.html', '')}.json"
            detector.export_report(report, filename)
        
        await browser.close()

if __name__ == "__main__":
    print("🐛 Craft Bug Detector - Testing Enhanced Mocks")
    asyncio.run(test_craft_bug_detection())
