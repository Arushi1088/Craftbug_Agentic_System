#!/usr/bin/env python3
"""
Advanced Craft Bug Analyzer (GPT-4o Full)
=========================================

Integrates three critical ingredients:
1. ADO Reference Bugs - Types of issues to catch
2. Figma Design Tokens - Source of truth for expected values  
3. Structured Schema - Developer-ready, deduplicated output

Uses the final comprehensive prompt for maximum accuracy.
"""

import os
import base64
import asyncio
import logging
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

class AdvancedCraftBugAnalyzer:
    """Advanced craft bug analyzer with design system integration"""
    
    def __init__(self):
        """Initialize the advanced analyzer"""
        self.llm_model = "gpt-4o"
        self.llm_max_tokens = 8000
        self.llm_temperature = 0.1
        
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable is required")
        
        self.llm_client = AsyncOpenAI(api_key=api_key)
        
        # Final comprehensive prompt with all three ingredients
        self.advanced_prompt = """Final Prompt for Advanced Craft Bug Analyzer (GPT-4o Full)
You are an expert UX Designer with 15+ years at Microsoft, analyzing Excel Web screenshots for craft bugs. 
Your job is to detect **subtle but high-value design quality issues** using both visual inspection AND the provided design system tokens as the source of truth. 
Output must be developer-ready, unique, and actionable.

───────────────────────────────
📌 CONTEXT (dynamic per run)
- Scenario: {scenario_description}
- Persona: {persona_type}
- Screenshots:
  - Step 1: {step_description_1} → {screenshot_1}
  - Step 2: {step_description_2} → {screenshot_2}
  - …

───────────────────────────────
🎨 DESIGN SYSTEM REFERENCE (from Figma)
Colors:
- primary_blue: #0078d4
- primary_blue_hover: #106ebe
- primary_blue_pressed: #005a9e
- neutral_white: #ffffff
- neutral_gray_10: #faf9f8
- neutral_gray_20: #f3f2f1
- neutral_gray_30: #edebe9
- neutral_gray_40: #e1dfdd
- neutral_gray_50: #d2d0ce
- neutral_gray_60: #c8c6c4
- neutral_gray_70: #b3b0ad
- neutral_gray_80: #a19f9d
- neutral_gray_90: #8a8886
- neutral_gray_100: #605e5c
- neutral_gray_110: #3b3a39
- neutral_gray_120: #323130
- neutral_gray_130: #292827
- neutral_gray_140: #201f1e
- neutral_gray_150: #1b1a19
- neutral_gray_160: #161514
- neutral_black: #000000
- semantic_error: #d13438
- semantic_warning: #ffaa44
- semantic_success: #107c10
- semantic_info: #0078d4

Typography:
- font_family_primary: Segoe UI
- font_family_monospace: Consolas
- font_size_xs: 10px
- font_size_sm: 12px
- font_size_md: 14px
- font_size_lg: 16px
- font_size_xl: 18px
- font_size_xxl: 20px
- font_size_xxxl: 24px
- font_weight_regular: 400
- font_weight_medium: 500
- font_weight_semibold: 600
- font_weight_bold: 700
- line_height_tight: 1.2
- line_height_normal: 1.4
- line_height_relaxed: 1.6

Spacing (8pt system):
- spacing_xs: 4px
- spacing_sm: 8px
- spacing_md: 12px
- spacing_lg: 16px
- spacing_xl: 20px
- spacing_xxl: 24px
- spacing_xxxl: 32px

Border Radius:
- border_radius_none: 0px
- border_radius_sm: 2px
- border_radius_md: 4px
- border_radius_lg: 8px
- border_radius_xl: 12px

Shadows:
- shadow_sm: 0 1px 2px rgba(0, 0, 0, 0.1)
- shadow_md: 0 2px 4px rgba(0, 0, 0, 0.1)
- shadow_lg: 0 4px 8px rgba(0, 0, 0, 0.1)
- shadow_xl: 0 8px 16px rgba(0, 0, 0, 0.1)

Components:
- button_primary: radius=md (4px), font=14px Segoe UI medium, padding sm/md
- button_secondary: transparent bg, blue border, 4px radius
- input: white bg, gray border, 4px radius, 14px font
- dialog: white bg, gray border, 8px radius, lg shadow, lg padding

(Use these as ground truth when judging screenshots.)

───────────────────────────────
🧩 BUG CATEGORIES TO CHECK
1. **Color & Contrast**
   - Wrong token hex used (e.g., #0078d4 vs expected #106ebe)
   - Wrong hover/active state colors
   - Contrast < WCAG 4.5:1 (if visibly clear)

2. **Spacing & Layout**
   - Inconsistent paddings/margins between similar elements
   - Violations of 8pt spacing system
   - Uneven gaps breaking rhythm

3. **Typography**
   - Wrong font size, weight, or hierarchy vs. design tokens
   - Misuse of Segoe UI vs monospace Consolas

4. **Border & Radius**
   - Border-radius mismatch (e.g., 8px vs expected 4px)
   - Stroke thickness inconsistent

5. **Shadow & Elevation**
   - Wrong elevation token applied (sm vs md vs lg vs xl)
   - Shadow too subtle/too strong vs spec

6. **Alignment & Positioning**
   - Dialogs off-center relative to viewport or grid
   - Baseline misalignments (icons, labels, buttons)
   - Crooked chevrons, caret, input text

7. **Iconography**
   - Inconsistent icon sizing/optical weight
   - Uneven icon↔text spacing

8. **Animation & Timing (only if visible/token mismatch)**
   - Animation duration deviates from 400ms standard
   - Inconsistent easing (if inferable)

───────────────────────────────
📑 OUTPUT FORMAT (STRICT)

CRAFT BUG #X

ISSUE SUMMARY
- Type: [Color|Spacing|Typography|Border|Shadow|Alignment|Iconography|Animation]
- Severity: [Red|Orange|Yellow]
- Title: [Concise descriptive title]

LOCATION & CONTEXT
- Affected Steps: [List step numbers + screenshots]
- Screen Position: [Top/Bottom/Left/Right/Center]
- UI Path: [Ribbon > Tab > Section > Element]
- Element: [Exact element if visible]
- Expected: [Correct token/system value from Figma]
- Actual: [Observed mismatch]
- Visual Impact: [Effect on clarity, trust, or usability]

VISUAL ANALYSIS
- Alignment: [slightly off, uneven, crooked]
- Size/Spacing: [too much/little, inconsistent scale]
- Color: [hex mismatch, wrong token]
- Typography: [wrong size/weight/family]
- Border/Radius: [too round/flat, inconsistent]
- Shadow: [too weak/strong, wrong elevation]

REPRO STEPS
Prerequisites: [Browser/resolution/app state if observable]
Steps:
1. Navigate to {scenario}
2. Perform {step}
3. Observe mismatch visually
Expected: [Correct token/system spec]
Actual: [Mismatch visible]
Repro Rate: [Always | Sometimes]

PERSONA IMPACT
- Novice Users: [Impact + frustration 1–10]
- Power Users: [Impact + frustration 1–10]
- Super Fans: [Impact + frustration 1–10]

DEVELOPER ACTION
- Immediate Fix: [CSS variable or design token correction]
- Code Location: [Likely stylesheet/component file]
- Visual Target: [Correct token/system alignment]
- Testing: [Check against Figma design tokens]

───────────────────────────────
⚖️ RULES
- Report only issues that can be **visually confirmed** from the screenshots.
- Exclude non-visible ARIA/keyboard shortcut/animation issues unless clearly tied to tokens.
- Deduplicate: consolidate similar issues and list all affected steps.
- Prefer systemic craft issues (alignment, spacing, token mismatch) over generic accessibility unless accessibility is severe.
- If no valid issues: output *"No visible craft bugs across provided screenshots."*

───────────────────────────────
🔍 REFERENCE BUG PATTERNS (from ADO)
Based on real Microsoft bug reports, look for:
- Cell selection color mismatch (#0078d4 vs #106ebe)
- Save dialog typography inconsistency (16px vs 14px)
- Tooltip shadow elevation wrong (L2 vs L3)
- Icon spacing inconsistent (8px vs 12px)
- Dropdown border radius mismatch (8px vs 4px)
- Button hover state color wrong (#106ebe vs #005a9e)
- Panel padding inconsistent (20px vs 16px)
- Loading animation too fast (200ms vs 400ms)
- Ribbon button alignment inconsistency
- Dialog positioning obscures content

Use these patterns to guide your analysis."""

    async def analyze_multiple_screenshots(self, steps_data: List[Dict]) -> List[Dict]:
        """
        Analyze multiple screenshots using the advanced craft bug detection
        
        Args:
            steps_data: List of step data with screenshots
            
        Returns:
            List of detected craft bugs
        """
        print(f"🔍 Advanced Craft Bug Analysis: {len(steps_data)} screenshots")
        
        # Prepare context
        context = self._prepare_advanced_context(steps_data)
        
        # Prepare images
        image_files = await self._prepare_images_for_analysis(steps_data)
        
        if not image_files:
            print("❌ No valid images found for analysis")
            return []
        
        # Run analysis
        analysis_text = await self._run_advanced_analysis(context, image_files)
        
        if not analysis_text:
            print("❌ Analysis failed")
            return []
        
        # Parse results
        bugs = self._parse_advanced_bugs(analysis_text, steps_data)
        
        print(f"✅ Advanced analysis complete: {len(bugs)} craft bugs detected")
        return bugs

    def _prepare_advanced_context(self, steps_data: List[Dict]) -> Dict:
        """Prepare context for advanced analysis"""
        scenario_description = steps_data[0].get('scenario_description', 'Excel Web Scenario')
        persona_type = steps_data[0].get('persona_type', 'User')
        
        # Build screenshots list
        screenshots_list = []
        for i, step in enumerate(steps_data, 1):
            step_desc = step.get('description', f'Step {i}')
            screenshot_name = os.path.basename(step.get('screenshot_path', f'screenshot_{i}.png'))
            screenshots_list.append(f"  - Step {i}: {step_desc} → {screenshot_name}")
        
        screenshots_text = "\n".join(screenshots_list)
        
        return {
            'scenario_description': scenario_description,
            'persona_type': persona_type,
            'screenshots_text': screenshots_text
        }

    async def _prepare_images_for_analysis(self, steps_data: List[Dict]) -> List[Tuple[str, bytes]]:
        """Prepare images for analysis"""
        image_files = []
        
        for step in steps_data:
            screenshot_path = step.get('screenshot_path')
            if screenshot_path and os.path.exists(screenshot_path):
                compressed_image = await self._compress_image(screenshot_path)
                if compressed_image:
                    image_files.append((screenshot_path, compressed_image))
        
        return image_files

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

    async def _run_advanced_analysis(self, context: Dict, image_files: List[Tuple[str, bytes]]) -> str:
        """Run the advanced craft bug analysis"""
        try:
            # Format the prompt with context
            prompt = self.advanced_prompt.format(
                scenario_description=context['scenario_description'],
                persona_type=context['persona_type'],
                step_description_1="Step 1",
                screenshot_1="screenshot_1",
                step_description_2="Step 2", 
                screenshot_2="screenshot_2"
            )
            
            # Add screenshots context
            prompt += f"\n\n📸 SCREENSHOTS TO ANALYZE:\n{context['screenshots_text']}"
            
            # Prepare messages with images
            messages = [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt}
                    ]
                }
            ]
            
            # Add images to the message
            for i, (image_path, image_data) in enumerate(image_files):
                base64_image = base64.b64encode(image_data).decode('utf-8')
                messages[0]["content"].append({
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{base64_image}"
                    }
                })
            
            print(f"🚀 Running advanced craft bug analysis with {len(image_files)} screenshots...")
            
            # Make API call
            response = await self.llm_client.chat.completions.create(
                model=self.llm_model,
                messages=messages,
                max_tokens=self.llm_max_tokens,
                temperature=self.llm_temperature
            )
            
            analysis_text = response.choices[0].message.content
            print(f"✅ Advanced analysis complete: {len(analysis_text)} characters")
            
            return analysis_text
            
        except Exception as e:
            logger.error(f"Advanced analysis failed: {e}")
            return ""

    def _parse_advanced_bugs(self, analysis_text: str, steps_data: List[Dict]) -> List[Dict]:
        """Parse advanced craft bugs from analysis text"""
        bugs = []
        
        # Check for "no issues" response
        if "no visible craft bugs" in analysis_text.lower():
            print("ℹ️ No craft bugs detected in advanced analysis")
            return []
        
        # Split by CRAFT BUG sections
        bug_sections = re.split(r'CRAFT BUG #\d+', analysis_text)
        
        for i, section in enumerate(bug_sections[1:], 1):  # Skip first empty section
            try:
                bug = self._extract_advanced_bug_from_section(section, i, steps_data)
                if bug:
                    bugs.append(bug)
            except Exception as e:
                logger.warning(f"Failed to parse advanced bug section {i}: {e}")
                continue
        
        # Final deduplication
        unique_bugs = []
        seen_titles = set()
        
        for bug in bugs:
            title = bug.get('title', '').lower().strip()
            if title and title not in seen_titles:
                seen_titles.add(title)
                unique_bugs.append(bug)
        
        if len(unique_bugs) < len(bugs):
            print(f"🔍 Removed {len(bugs) - len(unique_bugs)} duplicate bugs in final deduplication")
        
        return unique_bugs

    def _extract_advanced_bug_from_section(self, section: str, bug_number: int, steps_data: List[Dict]) -> Optional[Dict]:
        """Extract structured bug information from advanced analysis section"""
        try:
            # Extract all fields using regex patterns
            bug_type = self._extract_field(section, "Type:")
            severity = self._extract_field(section, "Severity:")
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
            novice_impact = self._extract_field(section, "Novice Users:")
            power_impact = self._extract_field(section, "Power Users:")
            super_fans_impact = self._extract_field(section, "Super Fans:")
            
            # Extract developer action
            immediate_fix = self._extract_field(section, "Immediate Fix:")
            code_location = self._extract_field(section, "Code Location:")
            visual_target = self._extract_field(section, "Visual Target:")
            testing = self._extract_field(section, "Testing:")
            
            # Get affected screenshot paths
            affected_screenshot_paths = self._get_affected_screenshot_paths(affected_steps, steps_data)
            
            bug = {
                'title': f"Advanced: {title}",
                'type': bug_type or 'Visual',
                'severity': severity or 'Yellow',
                'description': f"{actual} when viewing the interface. Expected: {expected}",
                'category': 'Advanced Craft Bugs',
                'analysis_type': 'advanced_design_system',
                
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
                
                # Developer action
                'immediate_fix': immediate_fix,
                'code_location': code_location,
                'visual_target': visual_target,
                'testing_approach': testing,
                
                # Context
                'step_name': affected_steps,
                'scenario': steps_data[0].get('scenario_description', 'Unknown'),
                'persona': steps_data[0].get('persona_type', 'User'),
                
                # Advanced specific
                'screenshot_paths': affected_screenshot_paths,
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
                'advanced_note': f"Advanced craft bug detected using design system tokens as ground truth. Affects {len(affected_screenshot_paths)} screenshots."
            }
            
            return bug
            
        except Exception as e:
            logger.error(f"Failed to extract advanced bug from section: {e}")
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
            # Parse step numbers from affected_steps
            step_numbers = re.findall(r'Step (\d+)', affected_steps)
            
            for step_num in step_numbers:
                step_index = int(step_num) - 1
                if 0 <= step_index < len(steps_data):
                    screenshot_path = steps_data[step_index].get('screenshot_path')
                    if screenshot_path and os.path.exists(screenshot_path):
                        paths.append(screenshot_path)
        except:
            pass
        
        return paths

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
    async def test_advanced_analyzer():
        """Test the advanced craft bug analyzer"""
        
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
            }
        ]
        
        # Initialize analyzer
        analyzer = AdvancedCraftBugAnalyzer()
        
        # Run analysis
        bugs = await analyzer.analyze_multiple_screenshots(test_steps)
        
        print(f"🎯 Advanced analysis results: {len(bugs)} craft bugs detected")
        
        for i, bug in enumerate(bugs, 1):
            print(f"\n--- Bug {i} ---")
            print(f"Title: {bug.get('title', 'Unknown')}")
            print(f"Type: {bug.get('type', 'Unknown')}")
            print(f"Severity: {bug.get('severity', 'Unknown')}")
            print(f"Expected: {bug.get('expected', 'Unknown')}")
            print(f"Actual: {bug.get('actual', 'Unknown')}")
            print(f"Fix: {bug.get('immediate_fix', 'Unknown')}")
    
    # Run test
    asyncio.run(test_advanced_analyzer())

