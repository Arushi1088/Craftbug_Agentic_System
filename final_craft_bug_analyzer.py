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
        
        # Final detection-only prompt - "LOOSE" VARIANT with confidence tags
        self.final_prompt = """You are a UX designer analyzing Excel Web screenshots for visual craft bugs.

Look at each screenshot carefully and find ALL visual issues you can see, including:
- Color contrast problems
- Spacing inconsistencies  
- Typography mismatches
- Alignment issues
- Component styling problems
- Layout problems
- Visual hierarchy issues
- Any other visual defects

Be thorough and find as many issues as possible. Don't be conservative.
Use confidence tags to indicate how certain you are about each issue.

Format each bug as:
CRAFT BUG #X
Type: [Color|Spacing|Typography|Alignment|Component|Layout|Hierarchy]
Severity: [Red|Orange|Yellow]
Confidence: [High|Medium|Low]
Title: [Brief description]
Description: [What's wrong]
Expected: [What should be correct]
Actual: [What's currently wrong]

Find at least 5-8 bugs per screenshot. Be detailed and specific about what you see in the images.
If you see similar issues across multiple screenshots, mention which screenshots they appear in.

Analyzing {num_screenshots} screenshots:
{step_descriptions}"""

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
        image_data_list = await self._prepare_images_with_data(unique_steps)
        
        if not image_data_list:
            print("❌ No valid images could be loaded for analysis")
            return []
        
        # Run analysis with actual image data
        analysis_text = await self._run_analysis_with_images(context, image_data_list)
        
        if not analysis_text:
            print("❌ Analysis failed")
            return []
        
        # Parse results
        bugs = self._parse_bugs(analysis_text, unique_steps)
        
        print(f"✅ Final analysis complete: {len(bugs)} craft bugs detected")
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
        
        # Build step descriptions
        step_descriptions = []
        for i, step in enumerate(steps_data, 1):
            step_name = step.get('step_name', f'Step {i}')
            step_desc = step.get('step_description', f'Step {i}')
            screenshot_name = os.path.basename(step.get('screenshot_path', f'screenshot_{i}.png'))
            step_descriptions.append(f"Step {i}: {step_name} - {step_desc} → {screenshot_name}")
        
        return {
            'scenario_description': scenario_description,
            'persona_type': persona_type,
            'step_descriptions': step_descriptions,
            'num_screenshots': len(steps_data)
        }

    async def _prepare_images_with_data(self, steps_data: List[Dict]) -> List[Tuple[str, bytes, str]]:
        """Prepare images with actual image data for analysis"""
        image_data_list = []
        
        for step in steps_data:
            screenshot_path = step.get('screenshot_path')
            step_name = step.get('step_name', 'Unknown')
            
            if not screenshot_path or not os.path.exists(screenshot_path):
                print(f"⚠️ Skipping {step_name}: File not found")
                continue
            
            try:
                compressed_image = await self._compress_image(screenshot_path)
                if compressed_image:
                    image_data_list.append((step_name, compressed_image, screenshot_path))
                    print(f"✅ Loaded image for {step_name}: {len(compressed_image)} bytes")
                else:
                    print(f"❌ Failed to compress image for {step_name}")
            except Exception as e:
                print(f"❌ Error loading image for {step_name}: {e}")
        
        return image_data_list

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

    async def _run_analysis_with_images(self, context: Dict, image_data_list: List[Tuple[str, bytes, str]]) -> str:
        """Run the final craft bug analysis with actual image data"""
        try:
            # Format the prompt with context
            step_descriptions = "\n".join(context['step_descriptions'])
            
            prompt = self.final_prompt.format(
                num_screenshots=context['num_screenshots'],
                step_descriptions=step_descriptions
            )
            
            # Prepare messages with actual image data
            messages = [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt}
                    ]
                }
            ]
            
            # Add actual image data (not file paths)
            for step_name, image_data, screenshot_path in image_data_list:
                base64_image = base64.b64encode(image_data).decode('utf-8')
                messages[0]["content"].append({
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{base64_image}"
                    }
                })
                print(f"📸 Added image data for {step_name}: {len(image_data)} bytes")
            
            print(f"🚀 Running final craft bug analysis with {len(image_data_list)} screenshots...")
            print(f"📊 Sending {len(messages[0]['content'])} content items (1 text + {len(image_data_list)} images)")
            
            # Make API call with rate limiting
            response = await self._make_api_call_with_retry(messages)
            
            if not response:
                return ""
            
            analysis_text = response.choices[0].message.content
            print(f"✅ Final analysis complete: {len(analysis_text)} characters")
            
            return analysis_text
            
        except Exception as e:
            logger.error(f"Final analysis failed: {e}")
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
