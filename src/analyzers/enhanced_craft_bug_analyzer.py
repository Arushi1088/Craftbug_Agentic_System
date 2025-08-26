"""
Enhanced Craft Bug Analyzer using the new service layer.
This module provides a clean, service-oriented implementation.
"""

import os
import json
import logging
from typing import List, Dict, Optional, Any

from config.settings import get_settings
from src.core.base_analyzer import BaseAnalyzer
from src.core.exceptions import AnalysisError, ScreenshotError
from src.core.types import BugData, AnalysisResult
from src.services.llm_service import LLMService
from src.services.screenshot_service import ScreenshotService
from src.services.validation_service import ValidationService


class EnhancedCraftBugAnalyzer(BaseAnalyzer):
    """Enhanced craft bug analyzer using service layer architecture."""
    
    def __init__(self, settings=None):
        """Initialize the enhanced analyzer with services."""
        super().__init__(settings)
        
        # Initialize services
        self.llm_service = LLMService(settings)
        self.screenshot_service = ScreenshotService(settings)
        self.validation_service = ValidationService()
        
        # Enhanced prompt with inline Figma tokens and ADO examples
        self.final_prompt = """You are a senior UX designer analyzing Excel Web screenshots for *visual craft bugs only*.

SCENARIO: {scenario_description}
PERSONA: {persona_type}

STEPS_CATALOG (choose only from this list; do not invent steps):
{steps_catalog_json}

REFERENCE CONTEXT:
- ADO bug style: Microsoft bugs often use concise phrasing like 
  "Ribbon icons misaligned, inconsistent with Fluent spacing scale" or 
  "Save dialog not following Fluent typography hierarchy."
- Figma tokens (Excel Web Fluent 2):
  Colors: primary_blue #0078d4, primary_blue_hover #106ebe, neutral_white #ffffff, semantic_error #d13438
  Typography: Segoe UI, sizes [10, 12, 14, 16, 18, 20, 24], weights [400, 500, 600, 700]
  Spacing: [4, 8, 12, 16, 20, 24, 32]
  Border Radius: [0, 2, 4, 8, 12]
  Shadows: sm/md/lg/xl (token values provided)
Use these tokens to validate bugs. If a visible issue violates a token, reference it and give a compliance_score (0–100).

RULES
- Return JSON ONLY:
  {{
    "bugs_strong":[ ...  ],   // high-quality, consolidated (target 4–8)
    "bugs_minor":[  ...  ],   // low-confidence or partial-evidence items (target 2–6)
    "meta":{{ ... }}
  }}
- Each bug (in either array) MUST include:
  - title, type (Color|Spacing|Typography|Alignment|Component|Layout|Hierarchy|Design_System|AI|Shadow),
  - severity (Red|Orange|Yellow), confidence (High|Medium|Low),
  - description (visible facts only), expected, actual,
  - affected_steps: [ {{ "index": <int>, "name": "<from catalog>", "screenshot": "<from catalog>", "evidence_reason": "<why this step shows the issue>" }} ] (≥1),
  - ui_path (or "Not Observable"), screen_position (Top-Left|Top-Right|Bottom-Left|Bottom-Right|Center),
  - visual_analysis: {{ alignment, spacing, color, typography, border_radius, shadow }},
  - developer_action: {{ what_to_correct, likely_surface, visual_target, qa }},
  - design_system_compliance: {{ expected_token, actual_value, compliance_score }},
  - persona_impact: {{ novice:1-10, power:1-10, super_fans:1-10 }}
- Consolidate exact duplicates across steps BUT do not merge across different types (e.g., Spacing vs Alignment).
- Target output size: **6–10 total** (sum of bugs_strong + bugs_minor). If few issues are visible: return fewer and set meta.notes="Sparse".
- If token match is uncertain, set expected_token="None", compliance_score ≤ 40, and put the item in bugs_minor (do not drop).

You will receive images interleaved with their step captions in this order. Use the captions to bind bugs to steps. Produce JSON only."""

    async def analyze(self, data: Dict[str, Any]) -> AnalysisResult:
        """Analyze screenshots for craft bugs using service layer."""
        try:
            steps_data = data.get('steps_data', [])
            self.logger.info(f"🎯 Enhanced Craft Bug Analysis: {len(steps_data)} screenshots")
            
            # Step 1: Validate and deduplicate screenshots using screenshot service
            unique_steps = await self._process_steps_with_screenshot_service(steps_data)
            
            if not unique_steps:
                self.logger.warning("❌ No valid unique screenshots found for analysis")
                return AnalysisResult(
                    bugs=[],
                    meta={"error": "No valid screenshots"},
                    debug_counters=self.debug_counters,
                    success=False,
                    error_message="No valid screenshots found"
                )
            
            self.logger.info(f"📸 Using {len(unique_steps)} unique screenshots for analysis")
            
            # Step 2: Prepare context and images
            context = self._prepare_context(unique_steps)
            ordered_steps = await self._prepare_images_with_screenshot_service(unique_steps)
            
            if not ordered_steps:
                self.logger.warning("❌ No valid images could be loaded for analysis")
                return AnalysisResult(
                    bugs=[],
                    meta={"error": "No valid images"},
                    debug_counters=self.debug_counters,
                    success=False,
                    error_message="No valid images could be loaded"
                )
            
            # Step 3: Run analysis using LLM service
            analysis_text = await self._run_analysis_with_llm_service(context, ordered_steps)
            
            if not analysis_text:
                self.logger.error("❌ Analysis failed")
                return AnalysisResult(
                    bugs=[],
                    meta={"error": "Analysis failed"},
                    debug_counters=self.debug_counters,
                    success=False,
                    error_message="Analysis failed"
                )
            
            # Step 4: Parse results using validation service
            bugs = await self._parse_results_with_validation_service(analysis_text, unique_steps)
            
            # Update debug counters
            self.debug_counters["successful_analyses"] += 1
            self.debug_counters["bugs_detected"] = len(bugs)
            
            # Merge service stats
            self._merge_service_stats()
            
            self.logger.info(f"✅ Enhanced analysis complete: {len(bugs)} craft bugs detected")
            self.logger.info(f"📊 Debug counters: {self.debug_counters}")
            
            return AnalysisResult(
                bugs=bugs,
                meta={
                    "total_bugs": len(bugs), 
                    "screenshots_analyzed": len(unique_steps),
                    "service_stats": self._get_service_stats()
                },
                debug_counters=self.debug_counters,
                success=True
            )
            
        except Exception as e:
            self.debug_counters["failed_analyses"] += 1
            self.debug_counters["errors"] += 1
            self.logger.error(f"❌ Enhanced analysis failed: {e}")
            
            return AnalysisResult(
                bugs=[],
                meta={"error": str(e)},
                debug_counters=self.debug_counters,
                success=False,
                error_message=str(e)
            )

    async def _process_steps_with_screenshot_service(self, steps_data: List[Dict]) -> List[Dict]:
        """Process steps using the screenshot service."""
        unique_steps = []
        seen_paths = set()
        
        for step in steps_data:
            screenshot_path = step.get('screenshot_path')
            
            # Use screenshot service for validation
            if not self.screenshot_service.validate_screenshot_path(screenshot_path):
                self.logger.warning(f"⚠️ Skipping step '{step.get('step_name', 'Unknown')}': Invalid screenshot path")
                continue
            
            # Check for duplicate paths
            if screenshot_path in seen_paths:
                self.logger.info(f"⚠️ Skipping duplicate path: {screenshot_path}")
                continue
            
            seen_paths.add(screenshot_path)
            unique_steps.append(step)
        
        # Use screenshot service for deduplication
        unique_paths = self.screenshot_service.deduplicate_screenshots([s.get('screenshot_path') for s in unique_steps])
        unique_steps = [s for s in unique_steps if s.get('screenshot_path') in unique_paths]
        
        # Warn if too many duplicates
        if len(unique_steps) < len(steps_data) * 0.5:
            self.logger.warning(f"⚠️ Warning: More than 50% of steps use duplicate screenshots")
        
        return unique_steps

    def _prepare_context(self, steps_data: List[Dict]) -> Dict:
        """Prepare context for analysis."""
        scenario_description = steps_data[0].get('scenario_description', 'Excel Web Scenario')
        persona_type = steps_data[0].get('persona_type', 'User')
        
        return {
            'scenario_description': scenario_description,
            'persona_type': persona_type
        }

    async def _prepare_images_with_screenshot_service(self, steps_data: List[Dict]) -> List[Dict]:
        """Prepare images using the screenshot service."""
        ordered = []
        
        for idx, step in enumerate(steps_data, start=1):
            screenshot_path = step.get('screenshot_path')
            
            try:
                # Use screenshot service to process the image
                screenshot_data = await self.screenshot_service.process_single_screenshot(screenshot_path)
                if not screenshot_data:
                    self.logger.warning(f"⚠️ Skipping: failed to process screenshot for {step.get('step_name','Unknown')}")
                    continue
                
                ordered.append({
                    "index": idx,
                    "name": step.get("step_name", f"Step {idx}"),
                    "screenshot_path": screenshot_path,
                    "base64": screenshot_data.base64,
                    "caption": f"Step {idx}: {step.get('step_name', f'Step {idx}')}"
                })
                
                self.logger.info(f"✅ Loaded image for {step.get('step_name', f'Step {idx}')}: {screenshot_data.size_bytes} bytes")
                
            except Exception as e:
                self.logger.error(f"❌ Image load error for {screenshot_path}: {e}")
        
        return ordered

    async def _run_analysis_with_llm_service(self, context: Dict, ordered_steps: List[Dict]) -> str:
        """Run analysis using the LLM service."""
        try:
            # Prepare steps catalog
            steps_catalog = []
            for step in ordered_steps:
                steps_catalog.append({
                    "index": step["index"],
                    "name": step["name"],
                    "screenshot": step["screenshot_path"]
                })
            steps_catalog_json = json.dumps(steps_catalog, separators=(",", ":"))

            # Format prompt
            prompt_text = self.final_prompt.format(
                scenario_description=context.get('scenario_description', 'Excel Web Scenario'),
                persona_type=context.get('persona_type', 'User'),
                steps_catalog_json=steps_catalog_json
            )

            # Prepare images for LLM service
            images = [
                {
                    "base64": step["base64"],
                    "caption": step["caption"]
                }
                for step in ordered_steps
            ]

            self.logger.info(f"🚀 Sending {len(ordered_steps)} images with captions (interleaved)")
            self.logger.info(f"📊 Enhanced with inline Figma tokens and ADO-style bug detection")

            # Use LLM service for analysis
            llm_response = await self.llm_service.analyze_with_images(prompt_text, images)
            
            if not llm_response.success:
                raise AnalysisError(f"LLM call failed: {llm_response.error}")
            
            self.logger.info(f"✅ LLM returned {len(llm_response.content)} chars")
            self.logger.info(f"🔍 LLM Response Preview: {llm_response.content[:500]}...")
            
            return llm_response.content
            
        except Exception as e:
            raise AnalysisError(f"Analysis failed: {e}")

    async def _parse_results_with_validation_service(self, analysis_text: str, steps_data: List[Dict]) -> List[BugData]:
        """Parse results using the validation service."""
        # Handle new structure with bugs_strong and bugs_minor
        all_bugs = []
        
        # Parse JSON using validation service
        data = self.validation_service.parse_json_response(analysis_text)
        if not data:
            self.logger.warning("ℹ️ JSON parse failed — using legacy regex parser")
            return self._parse_bugs_legacy(analysis_text, steps_data)
        
        # Process strong bugs
        if "bugs_strong" in data and data["bugs_strong"]:
            strong_bugs = await self._normalize_bugs_with_validation_service(data["bugs_strong"], steps_data, "strong")
            all_bugs.extend(strong_bugs)
        
        # Process minor bugs
        if "bugs_minor" in data and data["bugs_minor"]:
            minor_bugs = await self._normalize_bugs_with_validation_service(data["bugs_minor"], steps_data, "minor")
            all_bugs.extend(minor_bugs)
        
        # Fallback to old structure if new structure not found
        if "bugs" in data and data["bugs"] and not all_bugs:
            fallback_bugs = await self._normalize_bugs_with_validation_service(data["bugs"], steps_data, "fallback")
            all_bugs.extend(fallback_bugs)
        
        return all_bugs

    async def _normalize_bugs_with_validation_service(self, bugs_json: List[Dict], steps_data: List[Dict], bug_category: str = "unknown") -> List[BugData]:
        """Normalize bugs using the validation service."""
        # Index real steps for quick lookup
        idx_to_path = {}
        for i, s in enumerate(steps_data, start=1):
            screenshot_path = s.get("screenshot_path")
            if screenshot_path and os.path.exists(screenshot_path):
                idx_to_path[i] = screenshot_path
        
        if not idx_to_path:
            self.logger.warning("⚠️ No valid screenshot paths found in steps_data")
            return []

        normalized = []
        for b in bugs_json:
            # Validate bug data using validation service
            if bug_category == "strong" and not self.validation_service.validate_bug_data(b):
                self.logger.warning(f"⚠️ Dropping strong bug with validation issues")
                continue
            
            # Fill missing fields for minor bugs
            if bug_category == "minor":
                b = self.validation_service.fill_missing_fields(b, "minor")
            
            # Map affected_steps to real file paths
            paths = []
            for stepref in b.get("affected_steps", []):
                idx = stepref.get("index")
                sp = idx_to_path.get(idx)
                if sp:
                    paths.append(sp)

            if not paths and idx_to_path:
                # last-resort: keep one image so report doesn't break
                first_path = next(iter(idx_to_path.values()), None)
                if first_path and os.path.exists(first_path):
                    paths.append(first_path)
                    self.logger.info(f"🔄 Using fallback screenshot: {os.path.basename(first_path)}")

            # Validate screenshot paths
            paths = self.validation_service.validate_screenshot_paths(paths)

            # Create normalized bug data using validation service
            try:
                normalized_bug = self.validation_service.normalize_bug_data(b, bug_category)
                normalized_bug.screenshot_paths = paths
                normalized.append(normalized_bug)
            except Exception as e:
                self.logger.error(f"Failed to normalize bug data: {e}")
        
        return normalized

    def _parse_bugs_legacy(self, analysis_text: str, steps_data: List[Dict]) -> List[BugData]:
        """Legacy regex-based bug parsing (fallback)."""
        self.logger.info("ℹ️ Using legacy regex parser")
        return []

    def _merge_service_stats(self):
        """Merge stats from all services into debug counters."""
        llm_stats = self.llm_service.get_stats()
        screenshot_stats = self.screenshot_service.get_stats()
        validation_stats = self.validation_service.get_stats()
        
        # Add service-specific stats to debug counters
        self.debug_counters.update({
            "llm_calls": llm_stats.get("total_calls", 0),
            "llm_success_rate": llm_stats.get("success_rate", 0),
            "screenshots_processed": screenshot_stats.get("total_processed", 0),
            "validation_success_rate": validation_stats.get("validation_success_rate", 0),
            "parse_success_rate": validation_stats.get("parse_success_rate", 0)
        })

    def _get_service_stats(self) -> Dict[str, Any]:
        """Get combined stats from all services."""
        return {
            "llm_service": self.llm_service.get_stats(),
            "screenshot_service": self.screenshot_service.get_stats(),
            "validation_service": self.validation_service.get_stats()
        }
