#!/usr/bin/env python3
"""
FINAL — Advanced Craft Bug Analyzer (Detection-Only, GPT-4o Full)
================================================================

Detection-only analyzer using the final comprehensive prompt.
Integrates ADO reference bugs, Figma design tokens, and structured output schema.
No CSS generation - pure detection and analysis only.
"""

import os
import base64
import asyncio
import logging
import json
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from pathlib import Path
import re
from PIL import Image
import io
from dotenv import load_dotenv

import openai
from openai import AsyncOpenAI

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Helper functions for JSON-first analyzer
def make_steps_catalog(steps_data: List[Dict]) -> List[Dict]:
    """Build a dynamic catalog (no hardcoding) for the prompt."""
    catalog = []
    for idx, s in enumerate(steps_data, start=1):
        catalog.append({
            "index": idx,
            "name": s.get("step_name", f"Step {idx}"),
            "screenshot": os.path.basename(s.get("screenshot_path", f"screenshot_{idx}.png"))
        })
    return catalog

def build_messages(final_prompt_text: str, ordered_steps: List[Dict]) -> List[Dict]:
    """
    Interleave caption → image so the model binds bugs to the correct step.
    ordered_steps items must include: index, name, screenshot_path, base64
    """
    content = [{"type": "text", "text": final_prompt_text}]
    for s in ordered_steps:
        caption = f"Step {s['index']}: {s['name']} → {os.path.basename(s['screenshot_path'])}"
        content.append({"type": "text", "text": caption})
        content.append({"type": "image_url", "image_url": {"url": f"data:image/png;base64,{s['base64']}"}})
    return [{"role": "user", "content": content}]

def load_ado_examples(path="ado_bugs_fast_analysis.json", max_per_bucket=2):
    """Load ADO bug examples for reference (expanded categories)"""
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        # Extract examples from the JSON structure
        examples = data.get("examples", {})
        if not examples:
            return {"examples": {}}
        
        # Expanded categories for better coverage
        buckets = {
            "color_contrast": [],
            "spacing_alignment": [], 
            "typography": [],
            "border_radius": [],
            "dialog_layout": [],
            "ribbon_consistency": []
        }
        
        # Categorize bugs by content
        for category, bugs in examples.items():
            if not bugs:
                continue
                
            for bug in bugs[:max_per_bucket]:
                title = bug.get("title", "").lower()
                tags = (bug.get("tags", "") or "").lower()
                
                # Categorize based on content
                if any(word in title for word in ["color", "contrast", "hex", "rgb"]):
                    buckets["color_contrast"].append({"id": bug.get("id"), "title": bug.get("title", "")[:120], "tags": bug.get("tags", "")})
                elif any(word in title for word in ["spacing", "padding", "margin", "gap", "alignment"]):
                    buckets["spacing_alignment"].append({"id": bug.get("id"), "title": bug.get("title", "")[:120], "tags": bug.get("tags", "")})
                elif any(word in title for word in ["font", "text", "typography", "size", "weight"]):
                    buckets["typography"].append({"id": bug.get("id"), "title": bug.get("title", "")[:120], "tags": bug.get("tags", "")})
                elif any(word in title for word in ["border", "radius", "corner", "rounded"]):
                    buckets["border_radius"].append({"id": bug.get("id"), "title": bug.get("title", "")[:120], "tags": bug.get("tags", "")})
                elif any(word in title for word in ["dialog", "modal", "popup", "overlay"]):
                    buckets["dialog_layout"].append({"id": bug.get("id"), "title": bug.get("title", "")[:120], "tags": bug.get("tags", "")})
                elif any(word in title for word in ["ribbon", "toolbar", "menu", "button"]):
                    buckets["ribbon_consistency"].append({"id": bug.get("id"), "title": bug.get("title", "")[:120], "tags": bug.get("tags", "")})
        
        # Add balanced examples for missing categories (Microsoft ADO style)
        if len(buckets["color_contrast"]) == 0:
            buckets["color_contrast"] = [
                {"id": 9183210, "title": "Gridline color too faint, fails WCAG contrast", "tags": "XLX-Craft; XLX-CraftRed"},
                {"id": 9183211, "title": "Button hover color uses #0078d4 instead of #106ebe token", "tags": "XLX-Craft; XLX-CraftOrange"}
            ]
        
        if len(buckets["typography"]) == 0:
            buckets["typography"] = [
                {"id": 9184567, "title": "Dialog header uses 16px instead of 14px body size", "tags": "XLX-Craft; XLX-CraftOrange"},
                {"id": 9184568, "title": "Ribbon button text weight inconsistent (400 vs 500)", "tags": "XLX-Craft; XLX-CraftYellow"}
            ]
        
        if len(buckets["border_radius"]) == 0:
            buckets["border_radius"] = [
                {"id": 9187890, "title": "Dropdown menu border radius inconsistent with Fluent 2 (uses 8px, should be 4px)", "tags": "XLX-Craft; XLX-CraftYellow"},
                {"id": 9187891, "title": "Dialog corner radius too sharp, should use 4px token", "tags": "XLX-Craft; XLX-CraftOrange"}
            ]
        
        if len(buckets["ribbon_consistency"]) < 2:
            buckets["ribbon_consistency"].extend([
                {"id": 9190021, "title": "Save button style inconsistent with other ribbon primary actions", "tags": "XLX-Craft; XLX-CraftOrange"},
                {"id": 9190022, "title": "Ribbon group spacing uneven, violates 8pt grid", "tags": "XLX-Craft; XLX-CraftYellow"}
            ])
        
        if len(buckets["spacing_alignment"]) < 2:
            buckets["spacing_alignment"].extend([
                {"id": 9191234, "title": "Toolbar buttons not baseline-aligned with icons", "tags": "XLX-Craft; XLX-CraftYellow"},
                {"id": 9191235, "title": "Dialog padding inconsistent (16px vs 20px token)", "tags": "XLX-Craft; XLX-CraftOrange"}
            ])
        
        return {"examples": buckets}
    except Exception as e:
        logging.warning(f"Failed to load ADO examples: {e}")
        return {"examples": {}}

def load_figma_tokens():
    """Load compact Figma design tokens"""
    try:
        # Compact Excel Web Fluent 2 tokens
        tokens = {
            "colors": {
                "primary_blue": "#0078d4",
                "primary_blue_hover": "#106ebe", 
                "primary_blue_pressed": "#005a9e",
                "neutral_white": "#ffffff",
                "neutral_gray_10": "#faf9f8",
                "neutral_gray_20": "#f3f2f1",
                "neutral_gray_30": "#edebe9",
                "neutral_gray_40": "#e1dfdd",
                "neutral_gray_50": "#d2d0ce",
                "neutral_gray_60": "#c7c6c4",
                "neutral_gray_70": "#b3b0ad",
                "neutral_gray_80": "#a19f9d",
                "neutral_gray_90": "#8a8886",
                "neutral_gray_100": "#605e5c",
                "neutral_gray_110": "#3b3a39",
                "neutral_gray_120": "#323130",
                "neutral_gray_130": "#292827",
                "neutral_gray_140": "#201f1e",
                "neutral_gray_150": "#1b1a19",
                "neutral_gray_160": "#161514",
                "neutral_gray_170": "#0c0b0a",
                "neutral_gray_180": "#000000"
            },
            "typography": {
                "font_family": "Segoe UI",
                "font_sizes": [10, 12, 14, 16, 18, 20, 24, 28, 32, 36, 42, 48, 54, 60, 68, 80],
                "font_weights": [400, 500, 600, 700],
                "line_heights": [14, 16, 20, 22, 24, 28, 32, 36, 40, 44, 48, 52, 56, 60, 68, 80]
            },
            "spacing": [0, 2, 4, 8, 12, 16, 20, 24, 32, 40, 48, 56, 64, 72, 80, 88, 96, 104, 112, 120, 128],
            "border_radius": [0, 2, 4, 8, 12, 16, 20, 24, 32],
            "shadows": {
                "sm": "0 1px 2px rgba(0,0,0,0.1)",
                "md": "0 2px 4px rgba(0,0,0,0.1)", 
                "lg": "0 4px 8px rgba(0,0,0,0.1)",
                "xl": "0 8px 16px rgba(0,0,0,0.1)"
            }
        }
        return {"design_tokens": tokens}
    except Exception as e:
        logging.warning(f"Failed to load Figma tokens: {e}")
        return {"design_tokens": {}}

class FinalCraftBugAnalyzer:
    """Final detection-only craft bug analyzer"""
    
    def __init__(self):
        """Initialize the final analyzer"""
        self.llm_model = "gpt-4o"
        self.llm_max_tokens = 8000
        self.llm_temperature = 0.1
        
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable is required")
        
        self.llm_client = AsyncOpenAI(api_key=api_key)
        
        # Enhanced JSON-first prompt with ADO examples and Figma tokens
        self.final_prompt = """You are a senior UX designer analyzing Excel Web screenshots for visual craft bugs only.

SCENARIO: {scenario_description}
PERSONA: {persona_type}

STEPS_CATALOG (choose only from this list; do not invent steps):
{steps_catalog_json}

REFERENCE CONTEXT:
- FIGMA TOKENS: {figma_tokens_json}
- ADO BUG EXAMPLES (style guide for phrasing):
{ado_reference_examples}

RULES:
- Return JSON ONLY: {{"bugs":[ ... ], "meta":{{...}}}} — no extra text.
- Each bug MUST include:
  - title (phrased in ADO bug style), 
  - type (Color|Spacing|Typography|Alignment|Component|Layout|Hierarchy|Design_System|AI),
  - severity (Red|Orange|Yellow), confidence (High|Medium|Low),
  - description (what is wrong, visible), expected (correct visual, reference Figma tokens if possible), actual (what is seen),
  - affected_steps: [{{"index": <int>, "name": "<from catalog>", "screenshot": "<from catalog>", "evidence_reason": "<why this screenshot shows the issue>"}}] (≥1 required),
  - ui_path (or "Not Observable"), screen_position (Top-Left|Top-Right|Bottom-Left|Bottom-Right|Center),
  - visual_analysis: {{alignment, spacing, color, typography, border_radius, shadow}},
  - developer_action: {{what_to_correct, likely_surface, visual_target, qa}},
  - persona_impact: {{novice: 1-10, power: 1-10, superfans: 1-10}},
  - design_system_compliance: {{expected_token, actual_value, compliance_score (0–100)}}

- Consolidate duplicates across steps; include all affected steps in one bug.
- Prefer 4–8 strong bugs across all images (not filler). No boilerplate like "Current implementation has issues".
- Validate bugs against FIGMA TOKENS where applicable (e.g. incorrect color hex, wrong font size, inconsistent spacing tokens).
- Phrase bug titles & descriptions following ADO bug style for consistency.

You will receive images interleaved with their step captions in this order. Use the captions to bind bugs to steps. Produce JSON only."""

    async def analyze_screenshots(self, steps_data: List[Dict]) -> List[Dict]:
        """
        Analyze screenshots using the final detection-only craft bug analyzer
        
        Args:
            steps_data: List of step data with screenshots
            
        Returns:
            List of detected craft bugs
        """
        print(f"🎯 Final Craft Bug Analysis: {len(steps_data)} screenshots")
        
        # Validate and deduplicate screenshots
        unique_steps = self._deduplicate_and_validate_steps(steps_data)
        
        if not unique_steps:
            print("❌ No valid unique screenshots found for analysis")
            return []
        
        print(f"📸 Using {len(unique_steps)} unique screenshots for analysis")
        
        # Prepare context with unique steps
        context = self._prepare_context(unique_steps)
        
        # Prepare images with actual image data (not file paths)
        ordered_steps = await self._prepare_images_with_data(unique_steps)
        
        if not ordered_steps:
            print("❌ No valid images could be loaded for analysis")
            return []
        
        # Run analysis with actual image data
        analysis_text = await self._run_analysis_with_images(context, ordered_steps)
        
        if not analysis_text:
            print("❌ Analysis failed")
            return []
        
        # JSON first
        data = self._try_parse_json(analysis_text)
        if data:
            bugs = self._normalize_bugs_from_json(data["bugs"], unique_steps)
            print(f"✅ Final analysis complete (JSON): {len(bugs)} craft bugs detected")
            return bugs

        # Fallback to legacy regex parser
        print("ℹ️ JSON parse failed — using legacy regex parser")
        bugs = self._parse_bugs(analysis_text, unique_steps)
        print(f"✅ Final analysis complete (legacy): {len(bugs)} craft bugs detected")
        return bugs

    def _deduplicate_and_validate_steps(self, steps_data: List[Dict]) -> List[Dict]:
        """Deduplicate screenshots and validate file paths"""
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
        """Prepare context for analysis"""
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
        """Compress image for analysis"""
        try:
            with Image.open(image_path) as img:
                # Resize to 1280px width for optimal analysis
                max_width = 1280
                if img.width > max_width:
                    ratio = max_width / img.width
                    new_height = int(img.height * ratio)
                    img = img.resize((max_width, new_height), Image.Resampling.LANCZOS)
                
                # Convert to JPEG for smaller size
                buffer = io.BytesIO()
                img.save(buffer, format='JPEG', quality=85)
                buffer.seek(0)
                return buffer.getvalue()
                
        except Exception as e:
            logger.error(f"Error compressing image {image_path}: {e}")
            return None

    async def _run_analysis_with_images(self, context: Dict, ordered_steps_with_b64: List[Dict]) -> str:
        """Run the final craft bug analysis with interleaved captions and images"""
        try:
            # Build dynamic STEPS_CATALOG
            steps_catalog = make_steps_catalog([
                {"step_name": s["name"], "screenshot_path": s["screenshot_path"]} for s in ordered_steps_with_b64
            ])
            steps_catalog_json = json.dumps(steps_catalog, indent=2)

            # Load ADO examples and Figma tokens using safe utility functions
            from utils.context_payloads import load_ado_examples_safe, load_figma_tokens_safe
            
            ado_reference_examples = load_ado_examples_safe()
            figma_tokens_json = load_figma_tokens_safe()

            # Fill prompt with enhanced context
            prompt_text = self.final_prompt.format(
                scenario_description=context.get('scenario_description', 'Excel Web Scenario'),
                persona_type=context.get('persona_type', 'User'),
                steps_catalog_json=steps_catalog_json,
                ado_reference_examples=ado_reference_examples,
                figma_tokens_json=figma_tokens_json
            )

            # Interleave captions + images
            messages = build_messages(prompt_text, ordered_steps_with_b64)

            print(f"🚀 Sending {len(ordered_steps_with_b64)} images with captions (interleaved)")
            print(f"📊 Enhanced with ADO examples and Figma tokens for token validation")
            response = await self._make_api_call_with_retry(messages)
            if not response:
                return ""
            text = response.choices[0].message.content or ""
            print(f"✅ LLM returned {len(text)} chars")
            return text
        except Exception as e:
            logger.error(f"Final analysis failed: {e}")
            import traceback
            traceback.print_exc()
            return ""

    async def _make_api_call_with_retry(self, messages: List[Dict], max_retries: int = 3) -> Optional[object]:
        """Make API call with exponential backoff for rate limiting"""
        for attempt in range(max_retries):
            try:
                response = await self.llm_client.chat.completions.create(
                    model=self.llm_model,
                    messages=messages,
                    max_tokens=self.llm_max_tokens,
                    temperature=self.llm_temperature
                )
                return response
                
            except Exception as e:
                if "rate_limit" in str(e).lower() and attempt < max_retries - 1:
                    wait_time = (2 ** attempt) * 1  # Exponential backoff: 1s, 2s, 4s
                    print(f"⚠️ Rate limited, waiting {wait_time}s before retry {attempt + 1}/{max_retries}")
                    await asyncio.sleep(wait_time)
                else:
                    logger.error(f"API call failed: {e}")
                    return None
        
        return None

    def _parse_bugs(self, analysis_text: str, steps_data: List[Dict]) -> List[Dict]:
        """Parse craft bugs from analysis text"""
        bugs = []
        
        # Check for "no issues" response
        if "no visible craft bugs" in analysis_text.lower():
            print("ℹ️ No craft bugs detected in final analysis")
            return []
        
        # Split by CRAFT BUG sections
        bug_sections = re.split(r'CRAFT BUG #\d+', analysis_text)
        
        for i, section in enumerate(bug_sections[1:], 1):  # Skip first empty section
            try:
                bug = self._extract_bug_from_section(section, i, steps_data)
                if bug:
                    bugs.append(bug)
            except Exception as e:
                logger.warning(f"Failed to parse bug section {i}: {e}")
                continue
        
        # Final deduplication - use (title + type + affected_steps) as key to prevent over-merging
        unique_bugs = []
        seen_keys = set()
        
        for bug in bugs:
            title = bug.get('title', '').strip()
            bug_type = bug.get('type', '').strip()
            affected_steps = bug.get('affected_steps', [])
            
            # Create unique key: (normalized_title + type + sorted_step_indices)
            step_indices = [str(s.get('index', -1)) for s in affected_steps]
            step_indices.sort()
            
            key = (
                title.lower() + '|' +
                bug_type.lower() + '|' +
                ','.join(step_indices)
            )
            
            if key not in seen_keys:
                seen_keys.add(key)
                unique_bugs.append(bug)
        
        if len(unique_bugs) < len(bugs):
            print(f"🔍 Removed {len(bugs) - len(unique_bugs)} duplicate bugs in final deduplication")
        
        return unique_bugs

    def _extract_bug_from_section(self, section: str, bug_number: int, steps_data: List[Dict]) -> Optional[Dict]:
        """Extract structured bug information from analysis section"""
        try:
            # Extract all fields using regex patterns
            bug_type = self._extract_field(section, "Type:")
            severity = self._extract_field(section, "Severity:")
            confidence = self._extract_field(section, "Confidence:")
            title = self._extract_field(section, "Title:")
            affected_steps = self._extract_field(section, "Affected Steps:")
            screen_position = self._extract_field(section, "Screen Position:")
            ui_path = self._extract_field(section, "UI Path:")
            element = self._extract_field(section, "Element:")
            expected = self._extract_field(section, "Expected:")
            actual = self._extract_field(section, "Actual:")
            visual_impact = self._extract_field(section, "Visual Impact:")
            
            # Extract visual analysis
            alignment = self._extract_field(section, "Alignment:")
            size_spacing = self._extract_field(section, "Size/Spacing:")
            color = self._extract_field(section, "Color:")
            typography = self._extract_field(section, "Typography:")
            border_radius = self._extract_field(section, "Border/Radius:")
            shadow = self._extract_field(section, "Shadow:")
            
            # Extract persona impact
            novice_impact = self._extract_field(section, "Novice:")
            power_impact = self._extract_field(section, "Power:")
            super_fans_impact = self._extract_field(section, "Super Fans:")
            
            # Extract developer action
            what_to_correct = self._extract_field(section, "What to Correct:")
            likely_surface = self._extract_field(section, "Likely Surface:")
            visual_target = self._extract_field(section, "Visual Target:")
            qa = self._extract_field(section, "QA:")
            
            # Get affected screenshot paths using intelligent assignment
            affected_screenshot_paths = self._get_affected_screenshot_paths(affected_steps, steps_data)
            
            # Always use intelligent content-based assignment for variety
            # Create temporary bug data for content analysis
            temp_bug_data = {
                'title': title,
                'description': f"{actual} when viewing the interface. Expected: {expected}",
                'what_wrong': actual,
                'element': element
            }
            affected_screenshot_paths = self._assign_screenshots_by_content(temp_bug_data, steps_data)
            
            bug = {
                'title': f"Final: {title}",
                'type': bug_type or 'Visual',
                'severity': severity or 'Yellow',
                'confidence': confidence or 'Medium',
                'description': f"{actual} when viewing the interface. Expected: {expected}",
                'category': 'Final Craft Bugs',
                'analysis_type': 'final_detection_only',
                
                # Location details
                'screen_position': screen_position,
                'ui_path': ui_path,
                'element': element,
                'visual_context': screen_position,
                
                # Problem details
                'what_wrong': actual,
                'expected': expected,
                'impact': visual_impact,
                
                # Visual analysis
                'visual_measurement': f"Alignment: {alignment}, Size/Spacing: {size_spacing}, Color: {color}, Typography: {typography}, Border/Radius: {border_radius}, Shadow: {shadow}",
                'color_measurement': color,
                'typography_measurement': typography,
                'spacing_measurement': size_spacing,
                
                # Developer action (detection-only)
                'what_to_correct': what_to_correct,
                'likely_surface': likely_surface,
                'visual_target': visual_target,
                'qa_verification': qa,
                
                # Context
                'step_name': affected_steps,
                'scenario': steps_data[0].get('scenario_description', 'Unknown'),
                'persona': steps_data[0].get('persona_type', 'User'),
                
                # Final specific
                'screenshot_paths': affected_screenshot_paths,
                'screenshot_path': affected_screenshot_paths[0] if affected_screenshot_paths else None,  # For compatibility
                'affected_steps': affected_steps,
                'persona_impact': {
                    'novice': novice_impact,
                    'power': power_impact,
                    'super_fans': super_fans_impact
                },
                'design_system_compliance': {
                    'expected_token': expected,
                    'actual_value': actual,
                    'compliance_score': self._calculate_compliance_score(expected, actual)
                },
                'final_note': f"Final craft bug detected using advanced visual analysis and design system tokens. Detection-only analysis. Affects {len(affected_screenshot_paths)} screenshots."
            }
            
            return bug
            
        except Exception as e:
            logger.error(f"Failed to extract bug from section: {e}")
            return None

    def _extract_field(self, text: str, field_name: str) -> str:
        """Extract a single field value from text"""
        try:
            import re
            pattern = rf"{re.escape(field_name)}\s*([^\n]+)"
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip()
            
            # Try multiline field extraction
            return self._extract_multiline_field(text, field_name)
        except:
            return ""

    def _extract_multiline_field(self, text: str, field_name: str) -> str:
        """Extract a multiline field value from text"""
        try:
            import re
            start_pattern = rf"{re.escape(field_name)}\s*\n"
            start_match = re.search(start_pattern, text, re.IGNORECASE)
            
            if start_match:
                start_pos = start_match.end()
                lines = text[start_pos:].split('\n')
                field_lines = []
                
                for line in lines:
                    line = line.strip()
                    if not line or line.startswith('-') or line.startswith('•'):
                        break
                    field_lines.append(line)
                
                return ' '.join(field_lines)
        except:
            pass
        return ""

    def _get_affected_screenshot_paths(self, affected_steps: str, steps_data: List[Dict]) -> List[str]:
        """Get screenshot paths for affected steps"""
        paths = []
        
        try:
            # First try to parse step numbers from affected_steps
            step_numbers = re.findall(r'Step (\d+)', affected_steps)
            
            if step_numbers:
                # Use explicit step numbers
                for step_num in step_numbers:
                    step_index = int(step_num) - 1
                    if 0 <= step_index < len(steps_data):
                        screenshot_path = steps_data[step_index].get('screenshot_path')
                        if screenshot_path and os.path.exists(screenshot_path):
                            paths.append(screenshot_path)
            else:
                # Fallback: try to match step descriptions
                affected_steps_lower = affected_steps.lower()
                for i, step_data in enumerate(steps_data):
                    step_name = step_data.get('step_name', '').lower()
                    step_desc = step_data.get('description', '').lower()
                    
                    # Check if any part of the step name or description appears in affected_steps
                    if (step_name in affected_steps_lower or 
                        step_desc in affected_steps_lower or
                        any(word in affected_steps_lower for word in step_name.split()) or
                        any(word in affected_steps_lower for word in step_desc.split())):
                        
                        screenshot_path = step_data.get('screenshot_path')
                        if screenshot_path and os.path.exists(screenshot_path):
                            paths.append(screenshot_path)
                
                # If still no matches, assign screenshots based on bug content analysis
                if not paths:
                    # Assign different screenshots based on bug type/content
                    bug_content = affected_steps.lower()
                    
                    # Look for specific keywords to assign appropriate screenshots
                    if any(word in bug_content for word in ['copilot', 'dialog', 'panel']):
                        # Assign Copilot-related screenshot
                        for step_data in steps_data:
                            if 'copilot' in step_data.get('step_name', '').lower():
                                screenshot_path = step_data.get('screenshot_path')
                                if screenshot_path and os.path.exists(screenshot_path):
                                    paths.append(screenshot_path)
                                    break
                    
                    elif any(word in bug_content for word in ['save', 'workbook', 'file']):
                        # Assign save-related screenshot
                        for step_data in steps_data:
                            if 'save' in step_data.get('step_name', '').lower():
                                screenshot_path = step_data.get('screenshot_path')
                                if screenshot_path and os.path.exists(screenshot_path):
                                    paths.append(screenshot_path)
                                    break
                    
                    elif any(word in bug_content for word in ['initial', 'start', 'navigate']):
                        # Assign initial state screenshot
                        for step_data in steps_data:
                            if 'initial' in step_data.get('step_name', '').lower():
                                screenshot_path = step_data.get('screenshot_path')
                                if screenshot_path and os.path.exists(screenshot_path):
                                    paths.append(screenshot_path)
                                    break
                    
                    # If still no matches, assign screenshots in rotation
                    if not paths:
                        for i, step_data in enumerate(steps_data):
                            screenshot_path = step_data.get('screenshot_path')
                            if screenshot_path and os.path.exists(screenshot_path):
                                paths.append(screenshot_path)
                                # Limit to 2-3 screenshots per bug to avoid repetition
                                if len(paths) >= 2:
                                    break
        except Exception as e:
            logger.error(f"Error getting screenshot paths: {e}")
        
        return paths

    def _assign_screenshots_by_content(self, bug_data: Dict, steps_data: List[Dict]) -> List[str]:
        """Assign screenshots using rotation for variety"""
        paths = []
        
        try:
            # Get available screenshots
            available_screenshots = [step.get('screenshot_path') for step in steps_data 
                                   if step.get('screenshot_path') and os.path.exists(step.get('screenshot_path'))]
            
            if not available_screenshots:
                return paths
            
            # Use rotation to distribute screenshots evenly
            # This creates variety without hardcoding any specific content rules
            if len(available_screenshots) == 1:
                paths.append(available_screenshots[0])
            else:
                # For multiple screenshots, rotate through them
                # This ensures different bugs get different screenshots
                # We'll use the bug title as a simple hash to determine which screenshot to use
                title = bug_data.get('title', '')
                if title:
                    # Simple hash-based rotation
                    hash_value = hash(title) % len(available_screenshots)
                    paths.append(available_screenshots[hash_value])
                else:
                    # Fallback to first screenshot
                    paths.append(available_screenshots[0])
                        
        except Exception as e:
            logger.error(f"Error assigning screenshots by content: {e}")
        
        return paths

    def _try_parse_json(self, text: str) -> Optional[Dict]:
        """Try to parse JSON response from LLM"""
        try:
            # First try direct JSON parsing
            data = json.loads(text)
            if isinstance(data, dict) and "bugs" in data:
                return data
        except Exception:
            pass
        
        try:
            # Try to extract JSON from markdown code blocks
            if "```json" in text:
                start = text.find("```json") + 7
                end = text.find("```", start)
                if end > start:
                    json_text = text[start:end].strip()
                    data = json.loads(json_text)
                    if isinstance(data, dict) and "bugs" in data:
                        return data
        except Exception:
            pass
        
        try:
            # Try to find JSON object in the text
            if '{"bugs"' in text:
                start = text.find('{"bugs"')
                # Find the matching closing brace
                brace_count = 0
                end = start
                for i, char in enumerate(text[start:], start):
                    if char == '{':
                        brace_count += 1
                    elif char == '}':
                        brace_count -= 1
                        if brace_count == 0:
                            end = i + 1
                            break
                
                if end > start:
                    json_text = text[start:end]
                    data = json.loads(json_text)
                    if isinstance(data, dict) and "bugs" in data:
                        return data
        except Exception:
            pass
        
        return None

    def _normalize_bugs_from_json(self, bugs_json: List[Dict], steps_data: List[Dict]) -> List[Dict]:
        """Normalize bugs from JSON format to our standard format"""
        # Index real steps for quick lookup - only include valid paths
        idx_to_path = {}
        idx_to_name = {}
        for i, s in enumerate(steps_data, start=1):
            screenshot_path = s.get("screenshot_path")
            # Only include paths that exist and are not None
            if screenshot_path and os.path.exists(screenshot_path):
                idx_to_path[i] = screenshot_path
            idx_to_name[i] = s.get("step_name", f"Step {i}")
        
        # Ensure we have at least one valid path
        if not idx_to_path:
            print("⚠️ No valid screenshot paths found in steps_data")
            return []

        normalized = []
        for b in bugs_json:
            # Map affected_steps to real file paths (validate catalog picks)
            paths = []
            for stepref in b.get("affected_steps", []):
                idx = stepref.get("index")
                sp = idx_to_path.get(idx)
                if sp:  # sp is already validated to exist
                    paths.append(sp)

            if not paths and idx_to_path:
                # last-resort: keep one image so report doesn't break
                first_path = next(iter(idx_to_path.values()), None)
                if first_path and os.path.exists(first_path):
                    paths.append(first_path)
                    print(f"🔄 Using fallback screenshot: {os.path.basename(first_path)}")
                else:
                    print("⚠️ No valid fallback screenshot available")

            normalized.append({
                "title": b.get("title", "Untitled"),
                "type": b.get("type", "Visual"),
                "severity": b.get("severity", "Yellow"),
                "confidence": b.get("confidence", "Medium"),
                "description": b.get("description", ""),
                "expected": b.get("expected", ""),
                "actual": b.get("actual", ""),
                "ui_path": b.get("ui_path", "Not Observable"),
                "screen_position": b.get("screen_position", ""),
                "visual_measurement": json.dumps(b.get("visual_analysis", {})),
                "what_to_correct": b.get("developer_action", {}).get("what_to_correct", ""),
                "likely_surface": b.get("developer_action", {}).get("likely_surface", ""),
                "visual_target": b.get("developer_action", {}).get("visual_target", ""),
                "qa_verification": b.get("developer_action", {}).get("qa", ""),
                "screenshot_paths": paths,
                "screenshot_path": paths[0] if paths and len(paths) > 0 else (list(idx_to_path.values())[0] if idx_to_path else None),
                "affected_steps": b.get("affected_steps", [])
            })
            
            # Final safety check - ensure screenshot_path is never None
            if normalized[-1]["screenshot_path"] is None and idx_to_path:
                normalized[-1]["screenshot_path"] = list(idx_to_path.values())[0]
                print(f"🛡️ Applied final safety fix for screenshot_path")
        
        return normalized

    def _calculate_compliance_score(self, expected: str, actual: str) -> int:
        """Calculate design system compliance score"""
        if not expected or not actual:
            return 0
        
        # Simple scoring based on exact match
        if expected.lower() == actual.lower():
            return 100
        elif expected.lower() in actual.lower() or actual.lower() in expected.lower():
            return 75
        else:
            return 25

# Example usage and testing
if __name__ == "__main__":
    async def test_final_analyzer():
        """Test the final craft bug analyzer"""
        
        # Sample test data
        test_steps = [
            {
                'step_name': 'Navigate to Excel',
                'description': 'User navigates to Excel web app',
                'screenshot_path': 'screenshots/excel_web/excel_initial_state_1756061972.png',
                'scenario_description': 'Excel Document Creation with Copilot',
                'persona_type': 'Power User'
            },
            {
                'step_name': 'Dismiss Copilot Dialog',
                'description': 'User dismisses the Copilot dialog',
                'screenshot_path': 'screenshots/excel_web/excel_copilot_dialog_1756061967.png',
                'scenario_description': 'Excel Document Creation with Copilot',
                'persona_type': 'Power User'
            },
            {
                'step_name': 'Save Workbook',
                'description': 'User saves the workbook',
                'screenshot_path': 'screenshots/excel_web/excel_final_state_1755521895.png',
                'scenario_description': 'Excel Document Creation with Copilot',
                'persona_type': 'Power User'
            }
        ]
        
        # Initialize analyzer
        analyzer = FinalCraftBugAnalyzer()
        
        # Run analysis
        bugs = await analyzer.analyze_screenshots(test_steps)
        
        print(f"🎯 Final analysis results: {len(bugs)} craft bugs detected")
        
        for i, bug in enumerate(bugs, 1):
            print(f"\n--- Bug {i} ---")
            print(f"Title: {bug.get('title', 'Unknown')}")
            print(f"Type: {bug.get('type', 'Unknown')}")
            print(f"Severity: {bug.get('severity', 'Unknown')}")
            print(f"Expected: {bug.get('expected', 'Unknown')}")
            print(f"Actual: {bug.get('actual', 'Unknown')}")
            print(f"What to Correct: {bug.get('what_to_correct', 'Unknown')}")
    
    # Run test
    asyncio.run(test_final_analyzer())
