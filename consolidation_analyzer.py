#!/usr/bin/env python3
"""
Consolidation & Deduplication Analyzer
Takes noisy multi-screenshot bug outputs and consolidates them into clean, unique, developer-ready issues
"""

import os
import asyncio
import logging
from typing import Dict, List, Optional
from datetime import datetime
from dotenv import load_dotenv

import openai
from openai import AsyncOpenAI

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ConsolidationAnalyzer:
    """Consolidates and deduplicates bug reports from multi-screenshot analysis"""
    
    def __init__(self):
        """Initialize the consolidation analyzer"""
        self.llm_model = "gpt-4o"  # Use GPT-4o for consolidation
        self.llm_max_tokens = 6000  # Sufficient for consolidation
        self.llm_temperature = 0.1
        
        # Initialize OpenAI client
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable is required")
        
        self.llm_client = AsyncOpenAI(api_key=api_key)
        
        # Consolidation prompt
        self.consolidation_prompt = """FULL CONSOLIDATION & DEDUPLICATION PROMPT (GPT-4o Full)

You are an expert UX Designer with 15+ years at Microsoft.
You will receive multiple bug reports generated from screenshot analysis.
Some bugs may be duplicates, vague, or hallucinated.
Your task is to produce a single, clean, consolidated bug list that is developer-ready, unique, and actionable.

🔹 INPUT (Dynamic – to be inserted per run)

Scenario: {scenario_description}

Persona: {persona_type}

Steps & Screenshots:

{steps_and_screenshots}

Raw Bug Reports:
{all_bug_reports_from_previous_analysis}

🔹 TASKS

Deduplicate Bugs Across Steps

If the same issue appears in multiple steps (e.g., low color contrast in toolbar, dialog, and save modal), merge them into one bug entry.

In the consolidated entry, list all affected steps and screenshots.

Filter Out Non-Visible Issues

Only include bugs that can be directly observed from static screenshots.

Remove issues that cannot be visually verified, such as:

Animation speed

Performance timing

ARIA attributes / screen reader behavior

Keyboard shortcuts (unless clearly visible on-screen)

Backend error handling not reflected visually

Refine Severity

Severity must be logical and consistent:

Red = Critical, blocks user tasks or major accessibility failures

Orange = High, significantly impacts usability but not blocking

Yellow = Medium, cosmetic or polish issues

Improve Clarity of Reports

Titles should be short, descriptive, and professional.

Expected vs. Actual must be clear and visual.

Fixes must be specific and actionable (e.g., adjust CSS margin, apply WCAG contrast ratio, align to design system).

Keep Schema Strict

Every bug must follow the full schema below.

Do not output vague placeholders like "Issue Type: Visual Affordance".

🔹 OUTPUT FORMAT (STRICT)

For each unique consolidated bug, use this schema:

CRAFT BUG #X

ISSUE SUMMARY

Type: [Visual | Accessibility | Interaction | AI | Layout | Design_System]

Severity: [Red | Orange | Yellow]

Title: [Concise descriptive title]

LOCATION & CONTEXT

Affected Steps: [List all step numbers + screenshot references where this occurs]

Screen Position: [Top-Left | Top-Right | Bottom-Left | Bottom-Right | Center]

UI Path: [Ribbon > Tab > Section > Element]

Element: [Exact element name if visible]

Expected: [What should be correct visually]

Actual: [What is wrong visually]

Visual Impact: [How it affects clarity, usability, or trust]

VISUAL ANALYSIS

Alignment: [slightly off, crooked, uneven, etc.]

Size: [too large/small, inconsistent]

Color: [hex values, poor contrast, wrong palette]

Typography: [font family/weight/size inconsistency]

Spacing: [too much/little, uneven, inconsistent]

REPRO STEPS
Prerequisites: [Browser/Resolution/App state if observable, else Not Observable]
Steps:

Navigate to {scenario_description}

Perform the relevant step(s)

Observe screenshot(s)

See the issue visually

Expected: [Correct visual state]
Actual: [Faulty state]
Repro Rate: [Always | Sometimes]

PERSONA IMPACT

Novice Users: [Impact + frustration score 1–10]

Power Users: [Impact + frustration score 1–10]

Super Fans: [Impact + frustration score 1–10]

DEVELOPER ACTION

Immediate Fix: [Specific CSS/HTML/Component adjustment]

Code Location: [Likely component/file affected]

Visual Target: [What the fix should look like]

Testing: [Steps to confirm visually once fixed]

🔹 RULES

Output only unique bugs — no duplicates or rephrased copies.

Consolidate repeated issues into one bug with all affected steps noted.

If two issues are similar but differ in detail (e.g., "Low contrast in toolbar" vs. "Low contrast in dialog"), merge them and note step-specific contexts.

Use [Not Observable] when details cannot be determined from the screenshot.

If no issues remain after deduplication and filtering, output:
"No visible craft bugs in consolidated report."

Keep output developer-ready, actionable, and precise."""

    async def consolidate_bugs(self, raw_bugs: List[Dict], steps_data: List[Dict]) -> List[Dict]:
        """
        Consolidate and deduplicate raw bug reports
        
        Args:
            raw_bugs: List of raw bug reports from multi-screenshot analysis
            steps_data: Original steps data for context
            
        Returns:
            List of consolidated, unique bugs
        """
        if not raw_bugs:
            return []
        
        print(f"🔍 Starting consolidation of {len(raw_bugs)} raw bugs...")
        
        try:
            # Prepare context for consolidation
            context = self._prepare_consolidation_context(raw_bugs, steps_data)
            
            # Run consolidation analysis
            consolidation_result = await self._run_consolidation_analysis(context)
            
            # Parse consolidated output
            consolidated_bugs = self._parse_consolidated_bugs(consolidation_result, steps_data)
            
            print(f"✅ Consolidation complete: {len(consolidated_bugs)} unique bugs (reduced from {len(raw_bugs)})")
            return consolidated_bugs
            
        except Exception as e:
            logger.error(f"Consolidation failed: {e}")
            print(f"❌ Consolidation failed: {e}")
            return raw_bugs  # Return original bugs if consolidation fails

    def _prepare_consolidation_context(self, raw_bugs: List[Dict], steps_data: List[Dict]) -> Dict:
        """Prepare context for consolidation analysis"""
        
        # Build steps and screenshots section
        steps_and_screenshots = []
        for i, step in enumerate(steps_data, 1):
            step_name = step.get('step_name', step.get('name', f'Step {i}'))
            step_description = step.get('description', '')
            screenshot_path = step.get('screenshot_path', '')
            
            if screenshot_path:
                screenshot_name = os.path.basename(screenshot_path)
                steps_and_screenshots.append(f"Step {i}: {step_name} - {step_description} → {screenshot_name}")
            else:
                steps_and_screenshots.append(f"Step {i}: {step_name} - {step_description} → [no screenshot]")
        
        # Build raw bug reports section
        raw_bug_reports = []
        for i, bug in enumerate(raw_bugs, 1):
            bug_report = f"""
BUG #{i}:
Title: {bug.get('title', 'Unknown')}
Type: {bug.get('type', 'Unknown')}
Severity: {bug.get('severity', 'Unknown')}
Step: {bug.get('step_name', 'Unknown')}
Description: {bug.get('description', 'No description')}
Impact: {bug.get('impact', 'No impact specified')}
Fix: {bug.get('immediate_fix', 'No fix specified')}
"""
            raw_bug_reports.append(bug_report)
        
        context = {
            'scenario_description': steps_data[0].get('scenario_description', 'Excel Web Scenario'),
            'persona_type': steps_data[0].get('persona_type', 'User'),
            'steps_and_screenshots': '\n'.join(steps_and_screenshots),
            'all_bug_reports_from_previous_analysis': '\n'.join(raw_bug_reports)
        }
        
        return context

    async def _run_consolidation_analysis(self, context: Dict) -> str:
        """Run consolidation analysis with GPT-4o"""
        
        try:
            # Format the prompt
            prompt = self.consolidation_prompt.format(**context)
            
            messages = [{"role": "user", "content": prompt}]
            
            print(f"🚀 Running consolidation analysis with GPT-4o...")
            
            # Make API call
            response = await self.llm_client.chat.completions.create(
                model=self.llm_model,
                messages=messages,
                max_tokens=self.llm_max_tokens,
                temperature=self.llm_temperature
            )
            
            content = response.choices[0].message.content.strip()
            
            print(f"✅ Consolidation analysis complete: {len(content)} characters")
            return content
            
        except Exception as e:
            logger.error(f"Consolidation analysis failed: {e}")
            raise

    def _parse_consolidated_bugs(self, consolidation_text: str, steps_data: List[Dict]) -> List[Dict]:
        """Parse consolidated bug information from GPT-4o output"""
        
        bugs = []
        
        # Check for "no issues" response
        if "no visible craft bugs" in consolidation_text.lower():
            print("ℹ️ No craft bugs detected after consolidation")
            return []
        
        # Split by CRAFT BUG sections - handle multiple formats
        import re
        
        # Try different section patterns
        patterns = [
            r"CRAFT BUG #(\d+)",
            r"\*\*CRAFT BUG #(\d+)\*\*",
            r"---\s*\*\*CRAFT BUG #(\d+)\*\*"
        ]
        
        bug_sections = []
        for pattern in patterns:
            matches = re.finditer(pattern, consolidation_text, re.IGNORECASE)
            for match in matches:
                start_pos = match.end()
                # Find the next bug or end of text
                next_match = re.search(pattern, consolidation_text[start_pos:], re.IGNORECASE)
                if next_match:
                    end_pos = start_pos + next_match.start()
                else:
                    end_pos = len(consolidation_text)
                
                section = consolidation_text[start_pos:end_pos].strip()
                if section:
                    bug_sections.append((match.group(1), section))
        
        # If no sections found with patterns, try manual splitting
        if not bug_sections:
            # Look for "CRAFT BUG #" in the text
            if "CRAFT BUG #" in consolidation_text:
                parts = consolidation_text.split("CRAFT BUG #")
                for i, part in enumerate(parts[1:], 1):  # Skip first empty part
                    if part.strip():
                        bug_sections.append((str(i), part.strip()))
        
        for bug_num, section in bug_sections:
            try:
                bug = self._extract_consolidated_bug_from_section(section, int(bug_num), steps_data)
                if bug:
                    bugs.append(bug)
                    
            except Exception as e:
                logger.warning(f"Failed to parse consolidated bug section {bug_num}: {e}")
                continue
        
        # Final deduplication step to remove any remaining duplicates
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

    def _extract_consolidated_bug_from_section(self, section: str, bug_number: int, steps_data: List[Dict]) -> Optional[Dict]:
        """Extract structured bug information from a consolidated section"""
        
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
            affected_screenshot_paths = self._get_affected_screenshot_paths_from_steps(affected_steps, steps_data)
            
            bug = {
                'title': f"Consolidated: {title}",
                'type': bug_type or 'Visual',
                'severity': severity or 'Yellow',
                'description': f"{actual} when viewing the interface. Expected: {expected}",
                'category': 'Craft Bugs (Consolidated)',
                'analysis_type': 'consolidated',
                
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
                
                # Consolidated specific
                'screenshot_paths': affected_screenshot_paths,
                'affected_steps': affected_steps,
                'persona_impact': {
                    'novice': novice_impact,
                    'power': power_impact,
                    'super_fans': super_fans_impact
                },
                'consolidation_note': f"Consolidated from multiple similar issues across {len(affected_screenshot_paths)} screenshots"
            }
            
            return bug
            
        except Exception as e:
            logger.error(f"Failed to extract consolidated bug from section: {e}")
            return None

    def _extract_field(self, text: str, field_name: str) -> str:
        """Extract a single field value from text"""
        try:
            # Look for the field in the text
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

    def _get_affected_screenshot_paths_from_steps(self, affected_steps: str, steps_data: List[Dict]) -> List[str]:
        """Get screenshot paths for affected steps from consolidation output"""
        
        screenshot_paths = []
        
        if not affected_steps:
            return screenshot_paths
        
        # Parse affected steps (e.g., "1, 3, 5" or "1,3,5")
        import re
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

# Test the consolidation analyzer
if __name__ == "__main__":
    async def test_consolidation_analyzer():
        print("🚀 Testing Consolidation Analyzer...")
        
        analyzer = ConsolidationAnalyzer()
        
        # Test with sample raw bugs (simplified version of our 36 bugs)
        sample_raw_bugs = [
            {
                'title': 'Low color contrast in toolbar',
                'type': 'Accessibility',
                'severity': 'Red',
                'step_name': 'Navigate to Excel',
                'description': 'Text elements have insufficient contrast ratios',
                'impact': 'Makes content difficult to read for users with visual impairments',
                'immediate_fix': 'Increase contrast ratio to meet WCAG guidelines'
            },
            {
                'title': 'Low color contrast in dialog',
                'type': 'Accessibility',
                'severity': 'Red',
                'step_name': 'Dismiss Copilot Dialog',
                'description': 'Dialog text has poor contrast against background',
                'impact': 'Difficult to read for users with visual impairments',
                'immediate_fix': 'Increase text contrast ratio'
            },
            {
                'title': 'Inconsistent button styling',
                'type': 'Design',
                'severity': 'Orange',
                'step_name': 'Dismiss Copilot Dialog',
                'description': 'Dialog buttons don\'t match main interface styling',
                'impact': 'Breaks visual consistency across the application',
                'immediate_fix': 'Standardize button styling with main interface'
            }
        ]
        
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
        
        consolidated_bugs = await analyzer.consolidate_bugs(sample_raw_bugs, sample_steps)
        
        print(f"✅ Test complete: {len(consolidated_bugs)} consolidated bugs")
        for i, bug in enumerate(consolidated_bugs, 1):
            print(f"🐛 Bug {i}: {bug.get('title')}")
            print(f"   Affected Steps: {bug.get('affected_steps')}")
            print(f"   Screenshots: {len(bug.get('screenshot_paths', []))} files")
            print()

    asyncio.run(test_consolidation_analyzer())
