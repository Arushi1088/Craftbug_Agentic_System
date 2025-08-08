#!/usr/bin/env python3
"""
Enhanced Scenario Runner with Real Browser Automation
Executes realistic user scenarios end-to-end with AI-powered craft bug detection
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
import uuid
import time
import os

try:
    from playwright.async_api import async_playwright, Browser, Page, TimeoutError as PlaywrightTimeoutError
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False
    print("⚠️ Playwright not installed. Run: pip install playwright && playwright install")

# Import the new AI-powered dynamic analyzer
try:
    from dynamic_ux_analyzer import DynamicUXAnalyzer
    AI_UX_AVAILABLE = True
except ImportError:
    AI_UX_AVAILABLE = False
    print("⚠️ Dynamic UX Analyzer not available")

logger = logging.getLogger(__name__)

def infer_app_type(url: str = None, scenario_name: str = None, default: str = "Unknown") -> str:
    """Infer application type from URL and scenario name"""
    s = (scenario_name or "") + " " + (url or "")
    if "excel" in s.lower():
        return "excel"
    elif "word" in s.lower():
        return "word"
    elif "powerpoint" in s.lower() or "ppt" in s.lower():
        return "powerpoint"
    elif "outlook" in s.lower() or "email" in s.lower():
        return "outlook"
    elif "teams" in s.lower():
        return "teams"
    else:
        return default

class CraftBugDetector:
    """Enhanced craft bug detector with AI-powered dynamic analysis"""
    
    def __init__(self, enable_ai: bool = True):
        self.detected_issues = []
        self.interaction_patterns = []
        self.enable_ai = enable_ai and AI_UX_AVAILABLE
        
        # Initialize AI-powered analyzer
        if self.enable_ai:
            try:
                self.ai_analyzer = DynamicUXAnalyzer()
                logger.info("✅ AI-powered UX analyzer initialized")
            except Exception as e:
                logger.warning(f"⚠️ AI analyzer initialization failed: {e}")
                self.enable_ai = False
                self.ai_analyzer = None
        else:
            self.ai_analyzer = None
            logger.info("📊 Using traditional pattern-based analysis")
    
    async def analyze_page_state(self, page: Page, step_context: Dict) -> List[Dict]:
        """Enhanced page analysis with AI-powered issue generation"""
        all_issues = []
        
        try:
            # Get page HTML for AI analysis
            page_html = ""
            try:
                page_html = await page.content()
            except Exception as e:
                logger.warning(f"Could not get page HTML: {e}")
            
            # AI-powered dynamic analysis (if enabled)
            if self.enable_ai and self.ai_analyzer:
                try:
                    step_description = step_context.get('action', 'unknown action')
                    task_goal = step_context.get('task_goal', 'complete user task')
                    
                    ai_issues = await self.ai_analyzer.generate_dynamic_issues(
                        step_description=step_description,
                        screen_html=page_html,
                        task_goal=task_goal,
                        step_context=step_context
                    )
                    
                    if ai_issues:
                        logger.info(f"🤖 AI generated {len(ai_issues)} UX issues for step: {step_description}")
                        all_issues.extend(ai_issues)
                    
                except Exception as e:
                    logger.warning(f"AI analysis failed, falling back to traditional: {e}")
            
            # Traditional pattern-based analysis (always run as backup/supplement)
            traditional_issues = await self._traditional_analysis(page, step_context)
            all_issues.extend(traditional_issues)
            
            # Remove duplicates based on title similarity
            unique_issues = self._deduplicate_issues(all_issues)
            
            logger.info(f"🔍 Total issues detected: {len(unique_issues)} (AI: {self.enable_ai})")
            
        except Exception as e:
            logger.error(f"Error in page analysis: {e}")
        
        return unique_issues
    
    async def _traditional_analysis(self, page: Page, step_context: Dict) -> List[Dict]:
        """Traditional pattern-based analysis (original implementation)"""
        issues = []
        
        try:
            # 1. Navigation Confusion Detection
            nav_elements = await page.query_selector_all('nav, .navigation, .nav-menu, [role="navigation"]')
            if len(nav_elements) > 3:
                issues.append({
                    "type": "craft_bug",
                    "category": "navigation_confusion",
                    "severity": "medium",
                    "message": f"Multiple navigation elements detected ({len(nav_elements)}) - potential user confusion",
                    "element_count": len(nav_elements),
                    "step": step_context.get("action", "unknown"),
                    "selector": "nav, .navigation, .nav-menu",
                    "recommendation": "Consolidate navigation into a single, clear structure"
                })
            
            # 2. Unclear Button Labels Detection
            buttons = await page.query_selector_all('button, input[type="button"], input[type="submit"], [role="button"]')
            for i, button in enumerate(buttons[:10]):  # Check first 10 buttons
                try:
                    text = await button.inner_text() if button else ""
                    aria_label = await button.get_attribute("aria-label") if button else ""
                    title = await button.get_attribute("title") if button else ""
                    
                    # Check for unclear labels
                    unclear_labels = ["click", "go", "ok", "yes", "no", "submit", "button", ""]
                    effective_label = text or aria_label or title
                    
                    if (not effective_label or 
                        effective_label.lower().strip() in unclear_labels or 
                        len(effective_label.strip()) < 2):
                        
                        outer_html = await button.get_attribute("outerHTML") if button else ""
                        issues.append({
                            "type": "craft_bug", 
                            "category": "unclear_labeling",
                            "severity": "high" if not effective_label else "medium",
                            "message": f"Button with unclear/missing label: '{effective_label}'",
                            "element": outer_html[:200],  # Truncate for readability
                            "step": step_context.get("action", "unknown"),
                            "recommendation": "Use descriptive, action-oriented button labels"
                        })
                except Exception:
                    continue
            
            # 3. Cognitive Load Assessment
            interactive_elements = await page.query_selector_all(
                'button, input, select, textarea, a, [role="button"], [tabindex], [onclick]'
            )
            
            if len(interactive_elements) > 25:
                issues.append({
                    "type": "craft_bug",
                    "category": "cognitive_overload", 
                    "severity": "high",
                    "message": f"High cognitive load: {len(interactive_elements)} interactive elements on page",
                    "element_count": len(interactive_elements),
                    "step": step_context.get("action", "unknown"),
                    "recommendation": "Reduce interface complexity by grouping or hiding secondary actions"
                })
            
            # 4. Accessibility Gaps Detection
            # Missing form labels
            unlabeled_inputs = await page.query_selector_all(
                'input:not([aria-label]):not([aria-labelledby]):not([title]), '
                'textarea:not([aria-label]):not([aria-labelledby]):not([title])'
            )
            
            if unlabeled_inputs:
                issues.append({
                    "type": "craft_bug",
                    "category": "accessibility_gap",
                    "severity": "high", 
                    "message": f"{len(unlabeled_inputs)} form inputs missing accessibility labels",
                    "element_count": len(unlabeled_inputs),
                    "step": step_context.get("action", "unknown"),
                    "recommendation": "Add proper labels, aria-label, or aria-labelledby to all form inputs"
                })
            
            # 5. Performance-Related UX Issues
            # Check for loading states
            loading_elements = await page.query_selector_all('[class*="loading"], [class*="spinner"], [aria-busy="true"]')
            if loading_elements and step_context.get("duration_ms", 0) > 3000:
                issues.append({
                    "type": "craft_bug",
                    "category": "performance_ux",
                    "severity": "medium",
                    "message": f"Long-running operation ({step_context.get('duration_ms', 0)}ms) with loading indicator",
                    "step": step_context.get("action", "unknown"),
                    "recommendation": "Provide progress feedback or break operation into smaller chunks"
                })
            
            # 6. Inconsistent UI Patterns
            # Check for inconsistent button styles
            primary_buttons = await page.query_selector_all('[class*="primary"], [class*="btn-primary"]')
            secondary_buttons = await page.query_selector_all('[class*="secondary"], [class*="btn-secondary"]')
            generic_buttons = await page.query_selector_all('button:not([class*="primary"]):not([class*="secondary"])')
            
            if len(generic_buttons) > len(primary_buttons) + len(secondary_buttons):
                issues.append({
                    "type": "craft_bug",
                    "category": "ui_inconsistency",
                    "severity": "low",
                    "message": f"Inconsistent button styling detected ({len(generic_buttons)} unstyled vs {len(primary_buttons + secondary_buttons)} styled)",
                    "step": step_context.get("action", "unknown"),
                    "recommendation": "Establish consistent button styling patterns across the interface"
                })
            
        except Exception as e:
            logger.warning(f"Error analyzing page state: {e}")
        
        return issues
    
    def _deduplicate_issues(self, issues: List[Dict]) -> List[Dict]:
        """Remove duplicate issues based on title similarity and category"""
        if not issues:
            return []
        
        unique_issues = []
        seen_combinations = set()
        
        for issue in issues:
            # Create a key for deduplication
            title = issue.get('title', issue.get('message', '')).lower()
            category = issue.get('category', 'unknown')
            severity = issue.get('severity', 'unknown')
            
            # Create a simplified key for comparison
            key_words = set(title.split()[:5])  # First 5 words
            key = f"{category}:{severity}:{':'.join(sorted(key_words))}"
            
            if key not in seen_combinations:
                seen_combinations.add(key)
                unique_issues.append(issue)
        
        return unique_issues

    async def run_scenario(self, scenario_config: Dict, browser: Browser = None) -> Dict:
        """Run a complete scenario with AI-powered craft bug detection"""
        scenario_id = scenario_config.get('id', 'unknown')
        logger.info(f"🎬 Starting scenario: {scenario_id}")
        
        # Initialize browser
        if not browser:
            playwright = await async_playwright().start()
            browser = await playwright.chromium.launch(headless=False, slow_mo=500)
        
        page = await browser.new_page()
        
        try:
            # Execute scenario steps
            results = await self._execute_scenario_steps(page, scenario_config)
            
            # Perform AI-powered craft bug analysis
            craft_issues = await self.analyze_page_state(page, {'action': 'final_analysis', 'task_goal': 'scenario completion'})
            
            # Compile final results
            final_results = {
                'scenario_id': scenario_id,
                'timestamp': datetime.now().isoformat(),
                'execution_results': results,
                'craft_issues': craft_issues,
                'ai_analysis_enabled': self.enable_ai,
                'total_issues_found': len(craft_issues)
            }
            
            logger.info(f"✅ Scenario {scenario_id} completed with {len(craft_issues)} issues found")
            return final_results
            
        except Exception as e:
            logger.error(f"❌ Scenario {scenario_id} failed: {e}")
            return {
                'scenario_id': scenario_id,
                'timestamp': datetime.now().isoformat(),
                'error': str(e),
                'craft_issues': [],
                'ai_analysis_enabled': self.enable_ai,
                'total_issues_found': 0
            }
        finally:
            await page.close()
    
    async def _execute_scenario_steps(self, page: Page, scenario_config: Dict) -> Dict:
        """Execute the individual steps of a scenario"""
        steps = scenario_config.get('steps', [])
        results = {
            'steps_executed': [],
            'total_steps': len(steps),
            'execution_time': 0
        }
        
        start_time = time.time()
        
        for i, step in enumerate(steps):
            step_start = time.time()
            
            try:
                await self._execute_step(page, step)
                step_duration = time.time() - step_start
                
                results['steps_executed'].append({
                    'step_number': i + 1,
                    'action': step.get('action', 'unknown'),
                    'target': step.get('target', ''),
                    'duration_ms': round(step_duration * 1000, 2),
                    'status': 'success'
                })
                
            except Exception as e:
                step_duration = time.time() - step_start
                logger.warning(f"Step {i+1} failed: {e}")
                
                results['steps_executed'].append({
                    'step_number': i + 1,
                    'action': step.get('action', 'unknown'),
                    'target': step.get('target', ''),
                    'duration_ms': round(step_duration * 1000, 2),
                    'status': 'failed',
                    'error': str(e)
                })
        
        results['execution_time'] = round((time.time() - start_time) * 1000, 2)
        return results
    
    async def _execute_step(self, page: Page, step: Dict):
        """Execute a single scenario step"""
        action = step.get('action')
        target = step.get('target')
        
        if action == 'navigate':
            await page.goto(target)
            await page.wait_for_load_state('networkidle')
            
        elif action == 'click':
            await page.click(target)
            await asyncio.sleep(0.5)  # Small delay for UI updates
            
        elif action == 'type':
            text = step.get('text', '')
            await page.fill(target, text)
            
        elif action == 'wait':
            duration = step.get('duration', 1000)
            await asyncio.sleep(duration / 1000)
            
        else:
            logger.warning(f"Unknown action: {action}")
    
    def analyze_interaction_patterns(self, step_history: List[Dict]) -> List[Dict]:
        """Analyze patterns across multiple steps to detect workflow issues"""
        pattern_issues = []
        
        if len(step_history) < 2:
            return pattern_issues
        
        # Pattern 1: Too many clicks to reach goal
        click_steps = [s for s in step_history if s.get("action") == "click"]
        navigation_steps = [s for s in step_history if "navigate" in s.get("action", "").lower()]
        
        if len(click_steps) > 5 and len(navigation_steps) > 2:
            pattern_issues.append({
                "type": "craft_bug",
                "category": "navigation_inefficiency",
                "severity": "medium",
                "message": f"User required {len(click_steps)} clicks and {len(navigation_steps)} navigation steps",
                "recommendation": "Simplify user flow by reducing required clicks and navigation depth",
                "pattern_data": {
                    "total_clicks": len(click_steps),
                    "navigation_steps": len(navigation_steps),
                    "avg_step_duration": sum(s.get("duration_ms", 0) for s in step_history) / len(step_history)
                }
            })
        
        # Pattern 2: Repeated failed attempts
        failed_steps = [s for s in step_history if s.get("status") in ["failed", "timeout", "error"]]
        if len(failed_steps) > 1:
            pattern_issues.append({
                "type": "craft_bug",
                "category": "usability_barrier",
                "severity": "high",
                "message": f"Multiple failed attempts detected ({len(failed_steps)} failures)",
                "recommendation": "Investigate and fix usability barriers preventing task completion",
                "pattern_data": {
                    "failed_steps": len(failed_steps),
                    "failure_rate": len(failed_steps) / len(step_history)
                }
            })
        
        # Pattern 3: Slow response times pattern
        slow_steps = [s for s in step_history if s.get("duration_ms", 0) > 2000]
        if len(slow_steps) > len(step_history) * 0.3:  # More than 30% of steps are slow
            pattern_issues.append({
                "type": "craft_bug",
                "category": "performance_pattern",
                "severity": "medium",
                "message": f"Consistent slow response times ({len(slow_steps)}/{len(step_history)} steps > 2s)",
                "recommendation": "Optimize overall application performance and loading times",
                "pattern_data": {
                    "slow_steps": len(slow_steps),
                    "avg_duration": sum(s.get("duration_ms", 0) for s in step_history) / len(step_history)
                }
            })
        
        return pattern_issues

class EnhancedScenarioRunner:
    """Enhanced scenario runner with real browser automation and craft bug detection"""
    
    def __init__(self, headless: bool = True, deterministic_mode: bool = False):
        self.browser: Optional[Browser] = None
        self.page: Optional[Page] = None
        self.craft_bug_detector = CraftBugDetector()
        self.execution_log = []
        self.performance_metrics = []
        self.headless = headless
        self.deterministic_mode = deterministic_mode
        
    async def initialize_browser(self):
        """Initialize Playwright browser"""
        if not PLAYWRIGHT_AVAILABLE:
            raise RuntimeError("Playwright not available. Install with: pip install playwright && playwright install")
        
        playwright = await async_playwright().start()
        self.browser = await playwright.chromium.launch(headless=self.headless)
        
        # Create new page with enhanced configuration
        self.page = await self.browser.new_page()
        
        # Set viewport for consistent testing
        await self.page.set_viewport_size({"width": 1920, "height": 1080})
        
        # Enable performance monitoring
        await self.page.add_init_script("""
            window.performanceMetrics = {
                navigationStart: performance.timeOrigin,
                marks: {},
                timings: {},
                interactions: []
            };
            
            // Track user interactions
            ['click', 'input', 'scroll', 'keydown'].forEach(event => {
                document.addEventListener(event, (e) => {
                    window.performanceMetrics.interactions.push({
                        type: event,
                        target: e.target.tagName + (e.target.className ? '.' + e.target.className : ''),
                        timestamp: performance.now(),
                        x: e.clientX || 0,
                        y: e.clientY || 0
                    });
                });
            });
        """)
    
    async def execute_scenario_step(self, step: Dict, step_index: int) -> Dict[str, Any]:
        """Execute a single scenario step with comprehensive monitoring"""
        start_time = time.time()
        step_result = {
            "step_index": step_index,
            "action": step.get("action"),
            "status": "pending",
            "start_time": start_time,
            "duration_ms": 0,
            "errors": [],
            "craft_bugs": [],
            "performance_metrics": {},
            "screenshot": None  # Changed from screenshot_path to screenshot
        }
        
        # Generate analysis_id for screenshot filenames
        analysis_id = getattr(self, 'analysis_id', None)
        if not analysis_id:
            analysis_id = str(uuid.uuid4())[:8] if not getattr(self, 'deterministic_mode', False) else "test12345"
            self.analysis_id = analysis_id
        
        try:
            action = step.get("action", "")
            
            if action == "navigate_to_url":
                url = step.get("url", "")
                await self.page.goto(url, wait_until="networkidle", timeout=30000)
                step_result["url"] = url
                step_result["status"] = "success"
                
            elif action == "click":
                selector = step.get("selector", "")
                try:
                    element = await self.page.wait_for_selector(selector, timeout=10000)
                    if element:
                        await element.click()
                        await self.page.wait_for_timeout(500)  # Brief pause for UI updates
                        step_result["selector"] = selector
                        step_result["status"] = "success"
                    else:
                        step_result["status"] = "failed"
                        step_result["errors"].append(f"Element not found: {selector}")
                except PlaywrightTimeoutError:
                    step_result["status"] = "timeout"
                    step_result["errors"].append(f"Timeout waiting for element: {selector}")
                
            elif action == "type":
                selector = step.get("selector", "")
                text = step.get("text", "")
                try:
                    await self.page.fill(selector, text)
                    step_result["selector"] = selector
                    step_result["text"] = text
                    step_result["status"] = "success"
                except Exception as e:
                    step_result["status"] = "failed"
                    step_result["errors"].append(f"Failed to type in {selector}: {str(e)}")
                
            elif action == "wait":
                duration = step.get("duration", 1000)
                await asyncio.sleep(duration / 1000)
                step_result["duration_param"] = duration
                step_result["status"] = "success"
                
            elif action == "screenshot":
                # Manual screenshot action (existing functionality)
                timestamp = int(time.time())
                screenshot_dir = Path("reports/screenshots")
                screenshot_dir.mkdir(parents=True, exist_ok=True)
                screenshot_path = screenshot_dir / f"step_{step_index}_{timestamp}.png"
                await self.page.screenshot(path=str(screenshot_path))
                step_result["screenshot"] = f"screenshots/{screenshot_path.name}"
                step_result["status"] = "success"
                
            elif action == "assert_element_visible":
                selector = step.get("selector", "")
                try:
                    element = await self.page.wait_for_selector(selector, timeout=5000)
                    is_visible = await element.is_visible() if element else False
                    step_result["selector"] = selector
                    step_result["is_visible"] = is_visible
                    step_result["status"] = "success" if is_visible else "failed"
                    if not is_visible:
                        step_result["errors"].append(f"Element not visible: {selector}")
                except PlaywrightTimeoutError:
                    step_result["status"] = "failed"
                    step_result["errors"].append(f"Element not found: {selector}")
                
            elif action == "scroll":
                direction = step.get("direction", "down")
                amount = step.get("amount", 500)
                if direction == "down":
                    await self.page.evaluate(f"window.scrollBy(0, {amount})")
                elif direction == "up":
                    await self.page.evaluate(f"window.scrollBy(0, -{amount})")
                step_result["status"] = "success"
                
            elif action == "hover":
                selector = step.get("selector", "")
                try:
                    await self.page.hover(selector)
                    step_result["selector"] = selector
                    step_result["status"] = "success"
                except Exception as e:
                    step_result["status"] = "failed"
                    step_result["errors"].append(f"Failed to hover {selector}: {str(e)}")
                
            else:
                step_result["status"] = "skipped"
                step_result["errors"].append(f"Unknown or unsupported action: {action}")
            
            # 📸 Automatic screenshot capture for each step (NEW FEATURE)
            if self.page and step_result["status"] in ["success", "failed", "timeout"]:
                try:
                    screenshot_dir = Path("reports/screenshots")
                    screenshot_dir.mkdir(parents=True, exist_ok=True)
                    
                    # Generate filename: analysisId_actionName_stepIndex.png
                    action_name = action.replace("_", "").replace(" ", "")
                    screenshot_filename = f"{analysis_id}_{action_name}_{step_index}.png"
                    screenshot_path = screenshot_dir / screenshot_filename
                    
                    await self.page.screenshot(path=str(screenshot_path))
                    step_result["screenshot"] = f"screenshots/{screenshot_filename}"
                    
                    logger.info(f"📸 Screenshot captured: {screenshot_filename}")
                    
                except Exception as e:
                    logger.warning(f"Failed to capture screenshot for step {step_index}: {e}")
            
            # Detect craft bugs after each successful step
            if step_result["status"] in ["success"] and self.page:
                step_result["duration_ms"] = int((time.time() - start_time) * 1000)
                craft_bugs = await self.craft_bug_detector.analyze_page_state(self.page, step_result)
                step_result["craft_bugs"] = craft_bugs
            
            # Collect performance metrics
            try:
                if self.page:
                    metrics = await self.page.evaluate("window.performanceMetrics || {}")
                    step_result["performance_metrics"] = metrics
            except Exception:
                pass
                
        except Exception as e:
            step_result["status"] = "error"
            step_result["errors"].append(f"Unexpected error: {str(e)}")
            
        finally:
            end_time = time.time()
            step_result["duration_ms"] = int((end_time - start_time) * 1000)
            step_result["end_time"] = end_time
        
        self.execution_log.append(step_result)
        return step_result
    
    async def execute_full_scenario(self, scenario_config: Dict) -> Dict[str, Any]:
        """Execute a complete scenario with comprehensive analysis"""
        analysis_id = str(uuid.uuid4())[:8] if not self.deterministic_mode else "test12345"
        start_time = time.time()
        
        scenario_result = {
            "analysis_id": analysis_id,
            "scenario_name": scenario_config.get("name", "Enhanced Scenario"),
            "app_type": infer_app_type(
                url=scenario_config.get("steps", [{}])[0].get("url") if scenario_config.get("steps") else None,
                scenario_name=scenario_config.get("name", ""),
                default="web"
            ),
            "start_time": start_time,
            "status": "running",
            "steps": [],
            "craft_bugs_detected": [],
            "pattern_issues": [],
            "performance_summary": {},
            "overall_score": 0,
            "type": "realistic_scenario"
        }
        
        try:
            # Initialize browser for real execution
            await self.initialize_browser()
            
            # Extract steps from scenario configuration
            steps = []
            if "scenarios" in scenario_config and scenario_config["scenarios"]:
                first_scenario = scenario_config["scenarios"][0]
                steps = first_scenario.get("steps", [])
            elif "steps" in scenario_config:
                steps = scenario_config["steps"]
            
            successful_steps = 0
            total_craft_bugs = []
            
            # Execute each step
            for i, step in enumerate(steps):
                logger.info(f"🎯 Executing step {i+1}/{len(steps)}: {step.get('action')}")
                step_result = await self.execute_scenario_step(step, i)
                scenario_result["steps"].append(step_result)
                
                if step_result["status"] == "success":
                    successful_steps += 1
                    
                # Collect craft bugs from each step
                step_bugs = step_result.get("craft_bugs", [])
                total_craft_bugs.extend(step_bugs)
                
                # Brief pause between steps for realistic simulation
                if not self.deterministic_mode:
                    await asyncio.sleep(0.5)
            
            # Analyze interaction patterns
            pattern_issues = self.craft_bug_detector.analyze_interaction_patterns(scenario_result["steps"])
            scenario_result["pattern_issues"] = pattern_issues
            
            # Calculate scores
            success_rate = successful_steps / len(steps) if steps else 0
            craft_bug_penalty = min(len(total_craft_bugs) * 3, 25)  # Max 25 point penalty
            pattern_penalty = min(len(pattern_issues) * 5, 20)     # Max 20 point penalty
            
            base_score = int(success_rate * 100)
            scenario_result["overall_score"] = max(0, base_score - craft_bug_penalty - pattern_penalty)
            
            # Performance summary
            durations = [s.get("duration_ms", 0) for s in scenario_result["steps"]]
            scenario_result["performance_summary"] = {
                "total_steps": len(steps),
                "successful_steps": successful_steps,
                "avg_step_duration_ms": sum(durations) / len(durations) if durations else 0,
                "max_step_duration_ms": max(durations) if durations else 0,
                "total_craft_bugs": len(total_craft_bugs),
                "pattern_issues": len(pattern_issues)
            }
            
            scenario_result["craft_bugs_detected"] = total_craft_bugs
            scenario_result["status"] = "completed"
            
            # Check if any steps have screenshots
            has_screenshots = any(step.get("screenshot") for step in scenario_result["steps"])
            scenario_result["has_screenshots"] = has_screenshots
            
        except Exception as e:
            scenario_result["status"] = "failed"
            scenario_result["error"] = str(e)
            logger.error(f"❌ Scenario execution failed: {e}")
            
        finally:
            # Clean up browser
            if self.browser:
                await self.browser.close()
            
            end_time = time.time()
            scenario_result["end_time"] = end_time
            scenario_result["total_duration_ms"] = int((end_time - start_time) * 1000)
            scenario_result["timestamp"] = datetime.now().isoformat()
        
        return scenario_result

async def execute_realistic_scenario(url: str, scenario_path: str, headless: bool = True) -> Dict[str, Any]:
    """Execute a realistic user scenario end-to-end"""
    
    # Load scenario configuration
    try:
        if scenario_path.endswith('.yaml') or scenario_path.endswith('.yml'):
            import yaml
            with open(scenario_path, 'r') as f:
                scenario_data = yaml.safe_load(f)
        else:
            with open(scenario_path, 'r') as f:
                scenario_data = json.load(f)
    except Exception as e:
        return {
            "error": f"Failed to load scenario: {e}",
            "status": "failed",
            "analysis_id": str(uuid.uuid4())[:8]
        }
    
    # Create and execute scenario
    runner = EnhancedScenarioRunner(headless=headless)
    
    # Modify scenario to include the target URL
    if "scenarios" in scenario_data and scenario_data["scenarios"]:
        scenario_config = scenario_data["scenarios"][0]
        # Update navigation steps with the provided URL
        for step in scenario_config.get("steps", []):
            if step.get("action") == "navigate_to_url":
                if "{server_url}" in step.get("url", ""):
                    step["url"] = step["url"].replace("{server_url}", url)
                elif not step.get("url"):
                    step["url"] = url
    else:
        # Create a simple scenario if none exists
        scenario_config = {
            "name": "Simple URL Test",
            "steps": [
                {"action": "navigate_to_url", "url": url},
                {"action": "wait", "duration": 2000},
                {"action": "screenshot"}
            ]
        }
    
    result = await runner.execute_full_scenario(scenario_config)
    
    # Add URL to result
    result["url"] = url
    result["scenario_path"] = scenario_path
    
    return result

if __name__ == "__main__":
    # Example usage with AI-powered analysis
    async def main():
        # Test the new AI-powered CraftBugDetector
        detector = CraftBugDetector(enable_ai=True)
        
        # Load a scenario config
        scenario_config = {
            "id": "ai_test_scenario",
            "name": "AI-Powered UX Analysis Test",
            "steps": [
                {"action": "navigate", "target": "http://localhost:3000/public/mock-word.html"},
                {"action": "wait", "duration": 1000},
                {"action": "click", "target": "#comments-tab"},
                {"action": "wait", "duration": 500}
            ]
        }
        
        # Run scenario with AI analysis
        result = await detector.run_scenario(scenario_config)
        print("🤖 AI-Powered Analysis Results:")
        print(json.dumps(result, indent=2, default=str))
        
        # Also test the legacy function for comparison
        legacy_result = await execute_realistic_scenario(
            "http://localhost:3000/mock-word.html", 
            "scenarios/office_tests.yaml",
            headless=False  # Show browser for demo
        )
        print("\n📊 Legacy Analysis Results:")
        print(json.dumps(legacy_result, indent=2, default=str))
    
    asyncio.run(main())
