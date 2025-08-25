#!/usr/bin/env python3
"""
Multi-Screenshot UX Analysis with GPT-4o
Analyzes multiple screenshots simultaneously to detect and deduplicate craft bugs.
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

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MultiScreenshotAnalyzer:
    """Analyzes multiple screenshots simultaneously using GPT-4o for craft bug detection"""
    
    def __init__(self):
        """Initialize the multi-screenshot analyzer"""
        self.llm_model = "gpt-4o"  # Use GPT-4o for multi-screenshot analysis
        self.llm_max_tokens = 8000  # Higher token limit for comprehensive analysis
        self.llm_temperature = 0.1
        
        # Initialize OpenAI client
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable is required")
        
        self.llm_client = AsyncOpenAI(api_key=api_key)
        
        # Multi-screenshot analysis prompt
        self.multi_screenshot_prompt = """📋 Multi-Screenshot UX Analysis Prompt (GPT-4o Full)

You are an expert UX Designer with 15+ years at Microsoft, analyzing multiple screenshots of an Office-like application.
Your task is to detect unique craft bugs across all screenshots, consolidate duplicates, and produce developer-ready reports.

CONTEXT (Dynamic Input – injected per run)

Scenario: {scenario_description}

Persona: {persona_type}

Steps & Screenshots:

{steps_and_screenshots}

🎯 DETECT CRAFT BUGS IN THESE CATEGORIES

Visual Issues – misalignment, wrong colors, spacing, typography, feedback, hierarchy, overlap.

Accessibility – color contrast, missing labels/alt, poor focus indicators, small/unreadable text.

Visual Interaction Design – unclear affordances, missing button states, small click targets, missing feedback.

AI/Copilot Visual Issues – unclear suggestion layout, poor hierarchy, missing trust indicators, grid integration problems.

Layout & Design System – Fluent violations, inconsistent spacing/alignment, poor balance, responsive issues.

📑 OUTPUT FORMAT (STRICT)

CRAFT BUG #X

ISSUE SUMMARY

Type: [Visual|Accessibility|Interaction|AI|Layout|Design_System]

Severity: [Red|Orange|Yellow]

Title: [Concise descriptive title]

LOCATION & CONTEXT

Affected Steps: [List all steps/screenshots where this occurs]

Screen Position: [Top/Bottom/Left/Right/Center]

UI Path: [Ribbon > Tab > Section > Element]

Element: [Exact button/icon/field name if visible]

Expected: [Correct appearance/behavior]

Actual: [Observed issue]

Visual Impact: [How it affects user's experience]

VISUAL ANALYSIS

Alignment: [slightly off, crooked, uneven]

Size: [too large/small, inconsistent]

Color: [hex/contrast ratio]

Typography: [font size/weight/family]

Spacing: [too much/little, uneven]

REPRO STEPS
Prerequisites: [Browser/Resolution/App state if observable]
Steps:

Open {scenario_description}

Perform actions in listed step(s)

Observe issue visually

Expected: [Correct visual state]
Actual: [Faulty state]
Repro Rate: [Always/Sometimes]

PERSONA IMPACT

Novice Users: [Impact + frustration 1–10]

Power Users: [Impact + frustration 1–10]

Super Fans: [Impact + frustration 1–10]

DEVELOPER ACTION

Immediate Fix: [Specific CSS/HTML/Component adjustment]

Code Location: [Likely component/file]

Visual Target: [Desired fixed appearance]

Testing: [Steps to confirm fix visually]

RULES

Analyze all screenshots together.

Do not repeat or rephrase the same bug across steps → consolidate into one bug and list affected steps.

Use [Not Observable] for unknowns.

If no issues: "No visible craft bugs across provided screenshots."

Output only unique, developer-ready issues."""

    async def analyze_multiple_screenshots(self, steps_data: List[Dict]) -> List[Dict]:
        """
        Analyze multiple screenshots simultaneously using GPT-4o
        
        Args:
            steps_data: List of step data with screenshots
            
        Returns:
            List of deduplicated craft bugs
        """
        if not steps_data:
            return []
        
        print(f"🔍 Starting multi-screenshot analysis with {len(steps_data)} steps...")
        
        try:
            # Prepare context and screenshots
            context = self._prepare_multi_screenshot_context(steps_data)
            
            # Compress and prepare images
            image_files = await self._prepare_images_for_analysis(steps_data)
            
            if not image_files:
                print("⚠️ No valid screenshots found for analysis")
                return []
            
            # Run GPT-4o analysis
            analysis_result = await self._run_gpt4o_analysis(context, image_files)
            
            # Parse structured output
            bugs = self._parse_structured_bugs(analysis_result, steps_data)
            
            print(f"✅ Multi-screenshot analysis complete: {len(bugs)} unique bugs found")
            return bugs
            
        except Exception as e:
            logger.error(f"Multi-screenshot analysis failed: {e}")
            print(f"❌ Multi-screenshot analysis failed: {e}")
            return []

    def _prepare_multi_screenshot_context(self, steps_data: List[Dict]) -> Dict:
        """Prepare context for multi-screenshot analysis"""
        
        # Build steps and screenshots section
        steps_and_screenshots = []
        for i, step in enumerate(steps_data, 1):
            step_name = step.get('step_name', step.get('name', f'Step {i}'))
            step_description = step.get('description', '')
            screenshot_path = step.get('screenshot_path', '')
            
            if screenshot_path:
                steps_and_screenshots.append(f"Step {i}: {step_name} - {step_description} → [screenshot{i}]")
            else:
                steps_and_screenshots.append(f"Step {i}: {step_name} - {step_description} → [no screenshot]")
        
        context = {
            'scenario_description': steps_data[0].get('scenario_description', 'Excel Web Scenario'),
            'persona_type': steps_data[0].get('persona_type', 'User'),
            'steps_and_screenshots': '\n'.join(steps_and_screenshots)
        }
        
        return context

    async def _prepare_images_for_analysis(self, steps_data: List[Dict]) -> List[Tuple[str, bytes]]:
        """Prepare and compress images for GPT-4o analysis"""
        
        image_files = []
        
        for i, step in enumerate(steps_data):
            screenshot_path = step.get('screenshot_path')
            
            if not screenshot_path or not os.path.exists(screenshot_path):
                print(f"⚠️ Screenshot not found for step {i+1}: {screenshot_path}")
                continue
            
            try:
                # Load and compress image
                compressed_image = await self._compress_image(screenshot_path)
                if compressed_image:
                    image_files.append((f"screenshot{i+1}", compressed_image))
                    print(f"📸 Prepared screenshot {i+1}: {screenshot_path}")
                
            except Exception as e:
                logger.warning(f"Failed to prepare screenshot {screenshot_path}: {e}")
                print(f"⚠️ Failed to prepare screenshot {screenshot_path}: {e}")
        
        return image_files

    async def _compress_image(self, image_path: str) -> Optional[bytes]:
        """Compress image to optimal size for GPT-4o analysis"""
        
        try:
            with Image.open(image_path) as img:
                # Convert to RGB if necessary
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                
                # Resize to optimal size (1280px width as discussed)
                max_width = 1280
                if img.width > max_width:
                    ratio = max_width / img.width
                    new_height = int(img.height * ratio)
                    img = img.resize((max_width, new_height), Image.Resampling.LANCZOS)
                
                # Save to bytes with compression
                buffer = io.BytesIO()
                img.save(buffer, format='JPEG', quality=85, optimize=True)
                buffer.seek(0)
                
                return buffer.getvalue()
                
        except Exception as e:
            logger.error(f"Image compression failed for {image_path}: {e}")
            return None

    async def _run_gpt4o_analysis(self, context: Dict, image_files: List[Tuple[str, bytes]]) -> str:
        """Run GPT-4o analysis with multiple screenshots"""
        
        try:
            # Format the prompt
            prompt = self.multi_screenshot_prompt.format(**context)
            
            # Prepare messages with images
            content = [{"type": "text", "text": prompt}]
            
            # Add images as separate parts
            for image_name, image_data in image_files:
                content.append({
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{base64.b64encode(image_data).decode('utf-8')}"
                    }
                })
            
            messages = [{"role": "user", "content": content}]
            
            print(f"🚀 Sending {len(image_files)} screenshots to GPT-4o for analysis...")
            
            # Make API call
            response = await self.llm_client.chat.completions.create(
                model=self.llm_model,
                messages=messages,
                max_tokens=self.llm_max_tokens,
                temperature=self.llm_temperature
            )
            
            content = response.choices[0].message.content.strip()
            
            print(f"✅ GPT-4o analysis complete: {len(content)} characters")
            return content
            
        except Exception as e:
            logger.error(f"GPT-4o analysis failed: {e}")
            raise

    def _parse_structured_bugs(self, analysis_text: str, steps_data: List[Dict]) -> List[Dict]:
        """Parse structured bug information from GPT-4o output"""
        
        bugs = []
        
        # Check for "no issues" response
        if "no visible craft bugs" in analysis_text.lower():
            print("ℹ️ No craft bugs detected across screenshots")
            return []
        
        # Split by CRAFT BUG sections
        bug_sections = analysis_text.split("CRAFT BUG #")[1:]  # Skip the first empty part
        
        for i, section in enumerate(bug_sections, 1):
            try:
                bug = self._extract_bug_from_section(section, i, steps_data)
                if bug:
                    bugs.append(bug)
                    
            except Exception as e:
                logger.warning(f"Failed to parse bug section {i}: {e}")
                continue
        
        return bugs

    def _extract_bug_from_section(self, section: str, bug_number: int, steps_data: List[Dict]) -> Optional[Dict]:
        """Extract structured bug information from a section"""
        
        try:
            # Extract basic fields
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
            size = self._extract_field(section, "Size:")
            color = self._extract_field(section, "Color:")
            typography = self._extract_field(section, "Typography:")
            spacing = self._extract_field(section, "Spacing:")
            
            # Extract persona impact
            novice_impact = self._extract_field(section, "Novice Users:")
            power_impact = self._extract_field(section, "Power Users:")
            super_fans_impact = self._extract_field(section, "Super Fans:")
            
            # Extract developer action
            immediate_fix = self._extract_field(section, "Immediate Fix:")
            code_location = self._extract_field(section, "Code Location:")
            visual_target = self._extract_field(section, "Visual Target:")
            testing = self._extract_field(section, "Testing:")
            
            # Determine affected screenshot paths
            affected_screenshot_paths = self._get_affected_screenshot_paths(affected_steps, steps_data)
            
            bug = {
                'title': f"Multi-Screenshot: {title}",
                'type': bug_type or 'Visual',
                'severity': severity or 'Yellow',
                'description': f"{actual} when viewing the interface. Expected: {expected}",
                'category': 'Craft Bugs',
                'analysis_type': 'multi_screenshot',
                
                # Location details
                'screen_position': screen_position,
                'ui_path': ui_path,
                'element': element,
                'visual_context': screen_position,
                'coordinates': '',
                
                # Problem details
                'what_wrong': actual,
                'expected': expected,
                'impact': visual_impact,
                
                # Visual analysis
                'visual_measurement': f"Alignment: {alignment}, Size: {size}, Color: {color}, Typography: {typography}, Spacing: {spacing}",
                'color_measurement': color,
                'typography_measurement': typography,
                'spacing_measurement': spacing,
                
                # Reproduction
                'prerequisites': '',
                'visual_check': '',
                'expected_result': expected,
                'actual_result': actual,
                
                # Developer action
                'immediate_fix': immediate_fix,
                'code_location': code_location,
                'visual_target': visual_target,
                'testing_approach': testing,
                
                # Context
                'step_name': affected_steps,
                'scenario': steps_data[0].get('scenario_description', 'Unknown'),
                'persona': steps_data[0].get('persona_type', 'User'),
                
                # Multi-screenshot specific
                'screenshot_paths': affected_screenshot_paths,
                'affected_steps': affected_steps,
                'persona_impact': {
                    'novice': novice_impact,
                    'power': power_impact,
                    'super_fans': super_fans_impact
                }
            }
            
            return bug
            
        except Exception as e:
            logger.error(f"Failed to extract bug from section: {e}")
            return None

    def _extract_field(self, text: str, field_name: str) -> str:
        """Extract a single field value from text"""
        try:
            # Look for the field in the text
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
            # Find the field start
            start_pattern = rf"{re.escape(field_name)}\s*\n"
            start_match = re.search(start_pattern, text, re.IGNORECASE)
            
            if start_match:
                start_pos = start_match.end()
                
                # Find the next field or end of section
                lines = text[start_pos:].split('\n')
                field_lines = []
                
                for line in lines:
                    line = line.strip()
                    if not line:
                        continue
                    
                    # Check if this line starts a new field
                    if re.match(r'^[A-Z][a-z]+:', line):
                        break
                    
                    field_lines.append(line)
                
                return ' '.join(field_lines).strip()
        except:
            pass
        
        return ""

    def _get_affected_screenshot_paths(self, affected_steps: str, steps_data: List[Dict]) -> List[str]:
        """Get screenshot paths for affected steps"""
        
        screenshot_paths = []
        
        if not affected_steps:
            return screenshot_paths
        
        # Parse affected steps (e.g., "1, 3, 5" or "1,3,5")
        step_numbers = re.findall(r'\d+', affected_steps)
        
        for step_num in step_numbers:
            try:
                step_index = int(step_num) - 1  # Convert to 0-based index
                if 0 <= step_index < len(steps_data):
                    screenshot_path = steps_data[step_index].get('screenshot_path')
                    if screenshot_path and screenshot_path not in screenshot_paths:
                        screenshot_paths.append(screenshot_path)
            except ValueError:
                continue
        
        return screenshot_paths

# Test the multi-screenshot analyzer
if __name__ == "__main__":
    async def test_multi_screenshot_analyzer():
        print("🚀 Testing Multi-Screenshot Analyzer...")
        
        analyzer = MultiScreenshotAnalyzer()
        
        # Test with sample data
        sample_steps = [
            {
                'step_name': 'Navigate to Excel',
                'description': 'User navigates to Excel web app',
                'screenshot_path': 'screenshots/excel_web/excel_initial_state_1756061972.png',
                'scenario_description': 'Excel Document Creation',
                'persona_type': 'User'
            },
            {
                'step_name': 'Dismiss Copilot Dialog',
                'description': 'User dismisses the Copilot dialog',
                'screenshot_path': 'screenshots/excel_web/excel_copilot_dialog_1756061967.png',
                'scenario_description': 'Excel Document Creation',
                'persona_type': 'User'
            }
        ]
        
        bugs = await analyzer.analyze_multiple_screenshots(sample_steps)
        
        print(f"✅ Test complete: {len(bugs)} bugs found")
        for i, bug in enumerate(bugs, 1):
            print(f"🐛 Bug {i}: {bug.get('title')}")
            print(f"   Affected Steps: {bug.get('affected_steps')}")
            print(f"   Screenshots: {len(bug.get('screenshot_paths', []))} files")
            print()

    asyncio.run(test_multi_screenshot_analyzer())
