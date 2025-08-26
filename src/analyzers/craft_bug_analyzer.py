"""
Refactored Craft Bug Analyzer using the new architecture.
This module provides a clean, maintainable implementation of the craft bug analyzer.
"""

import os
import json
import base64
import asyncio
from typing import List, Dict, Optional, Any
from pathlib import Path

from openai import AsyncOpenAI

from config.settings import get_settings
from config.constants import BUG_TYPES, SEVERITY_LEVELS, CONFIDENCE_LEVELS, DEFAULT_UI_PATH
from src.core.base_analyzer import BaseAnalyzer
from src.core.exceptions import AnalysisError, ScreenshotError, ParsingError
from src.core.types import BugData, StepData, AnalysisResult, LLMResponse


class CraftBugAnalyzer(BaseAnalyzer):
    """Refactored craft bug analyzer with clean architecture."""
    
    def __init__(self, settings=None):
        """Initialize the craft bug analyzer."""
        super().__init__(settings)
        
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
        """Analyze screenshots for craft bugs."""
        try:
            steps_data = data.get('steps_data', [])
            print(f"🎯 Final Craft Bug Analysis: {len(steps_data)} screenshots")
            
            # Validate and deduplicate screenshots
            unique_steps = self._deduplicate_and_validate_steps(steps_data)
            
            if not unique_steps:
                print("❌ No valid unique screenshots found for analysis")
                return AnalysisResult(
                    bugs=[],
                    meta={"error": "No valid screenshots"},
                    debug_counters=self.debug_counters,
                    success=False,
                    error_message="No valid screenshots found"
                )
            
            print(f"📸 Using {len(unique_steps)} unique screenshots for analysis")
            
            # Prepare context and images
            context = self._prepare_context(unique_steps)
            ordered_steps = await self._prepare_images_with_data(unique_steps)
            
            if not ordered_steps:
                print("❌ No valid images could be loaded for analysis")
                return AnalysisResult(
                    bugs=[],
                    meta={"error": "No valid images"},
                    debug_counters=self.debug_counters,
                    success=False,
                    error_message="No valid images could be loaded"
                )
            
            # Run analysis
            analysis_text = await self._run_analysis_with_images(context, ordered_steps)
            
            if not analysis_text:
                print("❌ Analysis failed")
                return AnalysisResult(
                    bugs=[],
                    meta={"error": "Analysis failed"},
                    debug_counters=self.debug_counters,
                    success=False,
                    error_message="Analysis failed"
                )
            
            # Parse results
            bugs = self._parse_analysis_results(analysis_text, unique_steps)
            
            self.debug_counters["successful_analyses"] += 1
            self.debug_counters["bugs_detected"] = len(bugs)
            
            print(f"✅ Final analysis complete (JSON): {len(bugs)} craft bugs detected")
            print(f"📊 Debug counters: {self.debug_counters}")
            
            return AnalysisResult(
                bugs=bugs,
                meta={"total_bugs": len(bugs), "screenshots_analyzed": len(unique_steps)},
                debug_counters=self.debug_counters,
                success=True
            )
            
        except Exception as e:
            self.debug_counters["failed_analyses"] += 1
            self.debug_counters["errors"] += 1
            print(f"❌ Analysis failed: {e}")
            
            return AnalysisResult(
                bugs=[],
                meta={"error": str(e)},
                debug_counters=self.debug_counters,
                success=False,
                error_message=str(e)
            )

    def _deduplicate_and_validate_steps(self, steps_data: List[Dict]) -> List[Dict]:
        """Deduplicate screenshots and validate file paths."""
        unique_steps = []
        seen_paths = set()
        seen_images = set()
        
        for step in steps_data:
            screenshot_path = step.get('screenshot_path')
            
            # Skip if no path or file doesn't exist
            if not screenshot_path or not os.path.exists(screenshot_path):
                print(f"⚠️ Skipping step '{step.get('step_name', 'Unknown')}': Invalid screenshot path")
                continue
            
            # Check for duplicate paths
            if screenshot_path in seen_paths:
                print(f"⚠️ Skipping duplicate path: {screenshot_path}")
                continue
            
            # Check for duplicate images (by file size as a simple check)
            try:
                file_size = os.path.getsize(screenshot_path)
                if file_size in seen_images:
                    print(f"⚠️ Skipping duplicate image (same size): {screenshot_path}")
                    continue
                seen_images.add(file_size)
            except:
                pass
            
            seen_paths.add(screenshot_path)
            unique_steps.append(step)
        
        # Warn if too many duplicates
        if len(unique_steps) < len(steps_data) * 0.5:
            print(f"⚠️ Warning: More than 50% of steps use duplicate screenshots")
        
        return unique_steps

    def _prepare_context(self, steps_data: List[Dict]) -> Dict:
        """Prepare context for analysis."""
        scenario_description = steps_data[0].get('scenario_description', 'Excel Web Scenario')
        persona_type = steps_data[0].get('persona_type', 'User')
        
        return {
            'scenario_description': scenario_description,
            'persona_type': persona_type
        }

    async def _prepare_images_with_data(self, steps_data: List[Dict]) -> List[Dict]:
        """Return ordered steps with base64 image payload for interleaving."""
        ordered = []
        for idx, step in enumerate(steps_data, start=1):
            screenshot_path = step.get('screenshot_path')
            if not screenshot_path or not os.path.exists(screenshot_path):
                print(f"⚠️ Skipping: missing screenshot for {step.get('step_name','Unknown')}")
                continue
            try:
                # Prefer PNG or high-quality JPEG
                img_bytes = await self._compress_image(screenshot_path)
                if not img_bytes:
                    continue
                b64 = base64.b64encode(img_bytes).decode('utf-8')
                ordered.append({
                    "index": idx,
                    "name": step.get("step_name", f"Step {idx}"),
                    "screenshot_path": screenshot_path,
                    "base64": b64
                })
                print(f"✅ Loaded image for {step.get('step_name', f'Step {idx}')}: {len(img_bytes)} bytes")
            except Exception as e:
                print(f"❌ Image load error for {screenshot_path}: {e}")
        return ordered

    async def _compress_image(self, image_path: str) -> Optional[bytes]:
        """Compress image for analysis."""
        try:
            from PIL import Image
            import io
            
            # Open and compress image
            with Image.open(image_path) as img:
                # Convert to RGB if necessary
                if img.mode in ('RGBA', 'LA', 'P'):
                    img = img.convert('RGB')
                
                # Resize if too large (keep width >= 1600px for quality)
                if img.width < 1600:
                    # Calculate new height maintaining aspect ratio
                    ratio = 1600 / img.width
                    new_height = int(img.height * ratio)
                    img = img.resize((1600, new_height), Image.Resampling.LANCZOS)
                
                # Save as high-quality JPEG
                buffer = io.BytesIO()
                img.save(buffer, format='JPEG', quality=95, optimize=True)
                return buffer.getvalue()
                
        except ImportError:
            # Fallback: read file directly
            with open(image_path, 'rb') as f:
                return f.read()
        except Exception as e:
            print(f"❌ Image compression failed for {image_path}: {e}")
            return None

    async def _run_analysis_with_images(self, context: Dict, ordered_steps: List[Dict]) -> str:
        """Run analysis with images using the LLM."""
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

            # Build messages with interleaved images
            messages = self._build_messages_with_images(prompt_text, ordered_steps)

            print(f"🚀 Sending {len(ordered_steps)} images with captions (interleaved)")
            print(f"📊 Enhanced with inline Figma tokens and ADO-style bug detection")

            # Make LLM call
            llm_response = await self._make_llm_call(messages)
            
            if not llm_response.success:
                raise AnalysisError(f"LLM call failed: {llm_response.error}")
            
            print(f"✅ LLM returned {len(llm_response.content)} chars")
            print(f"🔍 LLM Response Preview: {llm_response.content[:500]}...")
            
            return llm_response.content
            
        except Exception as e:
            raise AnalysisError(f"Analysis failed: {e}")

    def _build_messages_with_images(self, prompt_text: str, ordered_steps: List[Dict]) -> List[Dict]:
        """Build messages with interleaved images and captions."""
        messages = [{"role": "user", "content": prompt_text}]
        
        for step in ordered_steps:
            # Add step caption
            caption = f"Step {step['index']}: {step['name']}"
            messages.append({"role": "user", "content": caption})
            
            # Add image
            image_url = f"data:image/jpeg;base64,{step['base64']}"
            messages.append({
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {"url": image_url}
                    }
                ]
            })
        
        return messages

    def _parse_analysis_results(self, analysis_text: str, steps_data: List[Dict]) -> List[BugData]:
        """Parse analysis results and return normalized bug data."""
        # Handle new structure with bugs_strong and bugs_minor
        all_bugs = []
        debug_counters = {
            "generated_strong": 0,
            "generated_minor": 0,
            "dropped_missing_fields": 0,
            "dropped_dedup": 0,
            "kept_strong": 0,
            "kept_minor": 0
        }
        
        # Parse JSON
        data = self._try_parse_json(analysis_text)
        if not data:
            print("ℹ️ JSON parse failed — using legacy regex parser")
            return self._parse_bugs_legacy(analysis_text, steps_data)
        
        # Process strong bugs
        if "bugs_strong" in data and data["bugs_strong"]:
            strong_bugs = self._normalize_bugs_from_json(data["bugs_strong"], steps_data, debug_counters, "strong")
            all_bugs.extend(strong_bugs)
            debug_counters["kept_strong"] = len(strong_bugs)
        
        # Process minor bugs
        if "bugs_minor" in data and data["bugs_minor"]:
            minor_bugs = self._normalize_bugs_from_json(data["bugs_minor"], steps_data, debug_counters, "minor")
            all_bugs.extend(minor_bugs)
            debug_counters["kept_minor"] = len(minor_bugs)
        
        # Fallback to old structure if new structure not found
        if "bugs" in data and data["bugs"] and not all_bugs:
            fallback_bugs = self._normalize_bugs_from_json(data["bugs"], steps_data, debug_counters, "fallback")
            all_bugs.extend(fallback_bugs)
        
        return all_bugs

    def _normalize_bugs_from_json(self, bugs_json: List[Dict], steps_data: List[Dict], debug_counters: Dict = None, bug_category: str = "unknown") -> List[BugData]:
        """Normalize bugs from JSON format to our standard format."""
        # Index real steps for quick lookup
        idx_to_path = {}
        for i, s in enumerate(steps_data, start=1):
            screenshot_path = s.get("screenshot_path")
            if screenshot_path and os.path.exists(screenshot_path):
                idx_to_path[i] = screenshot_path
        
        if not idx_to_path:
            print("⚠️ No valid screenshot paths found in steps_data")
            return []

        normalized = []
        for b in bugs_json:
            # Enhanced validation with debug counters
            if debug_counters:
                debug_counters[f"generated_{bug_category}"] = debug_counters.get(f"generated_{bug_category}", 0) + 1
            
            # Validate required fields - be more lenient for minor bugs
            required_fields = ["title", "type", "severity", "confidence"]
            missing_fields = [field for field in required_fields if not b.get(field)]
            
            if missing_fields and bug_category == "strong":
                if debug_counters:
                    debug_counters["dropped_missing_fields"] += 1
                print(f"⚠️ Dropping strong bug with missing fields: {missing_fields}")
                continue
            
            # For minor bugs, fill in missing fields with defaults
            if missing_fields and bug_category == "minor":
                if not b.get("title"):
                    b["title"] = f"Minor {b.get('type', 'Visual')} Issue"
                if not b.get("type"):
                    b["type"] = "Visual"
                if not b.get("severity"):
                    b["severity"] = "Yellow"
                if not b.get("confidence"):
                    b["confidence"] = "Low"
            
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
                    print(f"🔄 Using fallback screenshot: {os.path.basename(first_path)}")

            # Create normalized bug data
            normalized_bug = BugData(
                title=b.get("title", "Untitled"),
                type=b.get("type", "Visual"),
                severity=b.get("severity", "Yellow"),
                confidence=b.get("confidence", "Medium"),
                description=b.get("description", ""),
                expected=b.get("expected", ""),
                actual=b.get("actual", ""),
                ui_path=b.get("ui_path", DEFAULT_UI_PATH),
                screen_position=b.get("screen_position", "Center"),
                visual_analysis=b.get("visual_analysis", {}),
                developer_action=b.get("developer_action", {}),
                design_system_compliance=b.get("design_system_compliance", {}),
                persona_impact=b.get("persona_impact", {}),
                screenshot_paths=paths,
                affected_steps=b.get("affected_steps", []),
                bug_category=bug_category
            )
            
            normalized.append(normalized_bug)
        
        return normalized

    def _parse_bugs_legacy(self, analysis_text: str, steps_data: List[Dict]) -> List[BugData]:
        """Legacy regex-based bug parsing (fallback)."""
        # This is a simplified version of the legacy parser
        # In a real implementation, you would include the full regex parsing logic
        print("ℹ️ Using legacy regex parser")
        return []
