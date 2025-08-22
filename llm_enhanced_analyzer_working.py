#!/usr/bin/env python3
"""
LLM Enhanced UX Analyzer
========================

This module provides LLM-enhanced UX analysis capabilities for detecting
Craft bugs and other UX issues using OpenAI's GPT-4 Vision model.
"""

import os
import base64
import json
import re
import asyncio
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path
import logging

from openai import AsyncOpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LLMEnhancedAnalyzer:
    """LLM-enhanced UX analyzer for detecting Craft bugs and UX issues"""
    
    def __init__(self):
        """Initialize the LLM-enhanced analyzer"""
        self.enable_llm = True
        self.llm_model = "gpt-4o-mini"
        self.llm_temperature = 0.1
        self.llm_max_tokens = 2000
        
        # Initialize OpenAI client
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable not set")
        
        self.llm_client = AsyncOpenAI(api_key=api_key)
        
        # Load analysis prompts
        self.analysis_prompts = self._load_current_prompts()
        
        print("✅ LLM Enhanced Analyzer initialized")
    
    def _load_current_prompts(self) -> Dict[str, str]:
        """Load the current analysis prompts"""
        return {
            'comprehensive_visual_analysis': """# COMPREHENSIVE STATIC VISUAL UX ANALYSIS

You are analyzing a static screenshot of a web interface. You can ONLY report issues that are VISUALLY OBSERVABLE in this single image. Do NOT invent interactions, performance issues, or user actions that cannot be seen.

## CONTEXT:
- Step: {step_name}
- Scenario: {scenario_description}
- Persona: {persona_type}
- Screenshot: Static image of the current UI state

## COMPREHENSIVE VISUAL ANALYSIS FOCUS:

### 1. VISUAL CONSISTENCY & DESIGN SYSTEM ISSUES
- **Alignment Problems**: Elements that appear misaligned, crooked, or uneven
- **Spacing Issues**: Inconsistent padding, margins, or gaps between elements
- **Color Inconsistencies**: Elements using wrong colors, poor contrast, or inconsistent color schemes
- **Typography Issues**: Wrong font sizes, inconsistent font weights, or poor text hierarchy
- **Fluent Design Compliance**: Elements following Microsoft's design system
- **Elevation Problems**: Inconsistent shadows, depth, or layering

### 2. ACCESSIBILITY ISSUES (VISUAL ONLY)
- **Color Contrast**: Text that's hard to read due to poor background contrast
- **Focus Indicators**: Missing or unclear focus states (if visible)
- **Text Readability**: Text that's too small, blurry, or hard to read
- **Visual Hierarchy**: Poor organization that makes information hard to scan

### 3. LAYOUT & DESIGN ISSUES
- **Element Positioning**: Elements that appear in wrong locations or overlap
- **Responsive Design**: Elements that look broken or cramped
- **Visual Balance**: Uneven distribution of elements or poor proportions
- **Professional Appearance**: Elements that look unpolished or inconsistent

### 4. VISUAL INTERACTION DESIGN ISSUES
- **Visual Affordance Issues**: Elements that don't look clickable/interactive
- **Button State Problems**: Poor button states, unclear interactive areas
- **Usability Indicators**: Elements that appear confusing or hard to use

## CRITICAL RULES:
1. **NO INTERACTION ANALYSIS**: Do not report delays, responsiveness, or user actions
2. **NO PERFORMANCE ISSUES**: Do not report loading times or speed problems
3. **NO MADE-UP ACTIONS**: Do not invent clicks, hovers, or user interactions
4. **VISUAL EVIDENCE ONLY**: Every issue must be clearly visible in the screenshot
5. **BE SPECIFIC**: Point to exact elements and describe what's visually wrong
6. **NO PIXEL MEASUREMENTS**: Use descriptive terms, not specific pixel values

## OUTPUT FORMAT:
For each VISUAL issue found, provide:

CRAFT BUG #1

**ISSUE SUMMARY:**
- Type: Visual/Accessibility/Layout/Interaction Design
- Severity: Red/Orange/Yellow/Green
- Title: [Specific visual problem]

**VISUAL EVIDENCE:**
- Screen Position: [Where in the screenshot- keep this generic like top, top left, top right, center, bottom, bottom left, bottom right]
- UI Path: [Element location- generic location no px reference]
- Element: [Specific element name]
- Visual Context: [What's around it]

**VISUAL PROBLEM:**
- What's Wrong: [Describe the visual issue]
- Expected: [How it should look]
- Impact: [Why it matters visually]

**MEASUREMENTS (if applicable):**
- Visual: [No specific measurements like "2px misalignment- make it generic like slight misalignment, slight off position, off center etc."]
- Colors: [Color values if relevant]
- Typography: [Font sizes, weights if relevant]
- Spacing: [Padding/margin issues if relevant]

**REPRODUCTION:**
- Prerequisites: [What state the UI needs to be in]
- Visual Check: [What to look for in the screenshot]
- Expected Result: [How it should appear]
- Actual Result: [How it currently appears]

**DEVELOPER ACTION:**
- Immediate Fix: [What needs to be changed visually]
- Visual Target: [Specific visual improvement]
- Testing Approach: [How to verify the fix]

## EXAMPLE VALID ISSUES:
✅ "Font size dropdown lower than adjacent icons"
✅ "Share button has insufficient color contrast (ratio 2.1:1)"
✅ "Copilot dialog box is misaligned with the page grid"
✅ "Ribbon elements have inconsistent padding"
✅ "Button appears disabled but should be enabled"

## EXAMPLE INVALID ISSUES (DO NOT REPORT):
❌ "User clicks button and there's a delay" (interaction)
❌ "Page loads slowly" (performance)
❌ "Button is unresponsive" (interaction)
❌ "User enters text" (made-up action)
❌ "dont report in actual pixels always report approximately in words"

Focus ONLY on what you can SEE in this static screenshot. If no visual issues are apparent, report "No visual issues detected in this screenshot."

Analyze the provided screenshot now using this comprehensive framework.""",

            'performance_analysis': """# STATIC VISUAL PERFORMANCE ANALYSIS

You are analyzing a static screenshot for VISUAL performance indicators only. Do NOT report timing, responsiveness, or interaction performance that cannot be observed in a static image.

## CONTEXT:
- Step: {step_name}
- Scenario: {scenario_description}
- Screenshot: Static image of the current UI state

## VISUAL PERFORMANCE INDICATORS TO LOOK FOR:
1. **Loading States**: Visual indicators of loading (spinners, progress bars, skeleton screens)
2. **Animation Quality**: Visible animation artifacts, stuttering, or poor rendering
3. **Rendering Issues**: Blurry text, pixelated images, or visual glitches
4. **Visual Responsiveness Indicators**: Elements that appear broken or incorrectly sized
5. **Resource Loading**: Missing images, broken icons, or incomplete content

## CRITICAL RULES:
- ONLY report what you can SEE in the screenshot
- Do NOT invent timing information or interaction delays
- Do NOT report performance issues that require user interaction
- Focus on visual quality and rendering issues

## OUTPUT FORMAT:
If visual performance issues are found, describe them specifically. If none are visible, report "No visual performance issues detected in this screenshot."

Analyze the screenshot for visual performance indicators only.""",

            'interaction_analysis': """# STATIC VISUAL INTERACTION ANALYSIS

You are analyzing a static screenshot for visual interaction design issues only. Focus on visual affordances and accessibility indicators.

## CONTEXT:
- Step: {step_name}
- Scenario: {scenario_description}
- Screenshot: Static image of the current UI state

## VISUAL INTERACTION ISSUES TO CHECK:
1. **Visual Affordance Issues**: Elements that don't look clickable/interactive
2. **Accessibility Indicators (Visual)**: Missing focus states, poor contrast for interactive elements
3. **Interaction Design Issues (Visual)**: Poor button states, unclear interactive areas
4. **Usability Indicators (Visual)**: Elements that appear confusing or hard to use

## CRITICAL RULES:
- ONLY report visual interaction design issues visible in the screenshot
- Do NOT report actual interaction testing or responsiveness
- Do NOT report delays or timing issues
- Focus on visual design of interactive elements

## OUTPUT FORMAT:
If visual interaction design issues are found, describe them specifically. If none are visible, report "No visual interaction design issues detected in this screenshot."

Analyze the screenshot for visual interaction design issues only."""
        }
    
    def _prepare_step_context(self, step_data: Dict) -> Dict:
        """Prepare context for LLM analysis"""
        # Extract step number from step name
        step_number = 1
        if 'step' in step_data.get('step_name', '').lower():
            match = re.search(r'(\d+)', step_data.get('step_name', ''))
            if match:
                step_number = int(match.group(1))
        
        return {
            'step_name': step_data.get('step_name', 'Unknown Step'),
            'step_number': step_number,
            'total_steps': 1,  # Default for single step analysis
            'action_type': step_data.get('action_type', 'unknown'),
            'duration_ms': step_data.get('duration_ms', 0),
            'scenario_description': step_data.get('scenario_description', 'Test Scenario'),
            'persona_type': step_data.get('persona_type', 'User'),
            'expected_behavior': step_data.get('expected_behavior', 'Expected behavior not specified')
        }
    
    def analyze_step_with_llm(self, step_data: Dict) -> List[Dict]:
        """Analyze a step using LLM-enhanced detection - ONLY LLM bugs"""
        
        if not self.enable_llm:
            return []
        
        # Perform LLM analysis only
        print(f"🤖 LLM ANALYSIS: Starting analysis for step '{step_data.get('step_name')}'")
        
        # Run async analysis in sync context
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            llm_analysis = loop.run_until_complete(self._perform_llm_analysis(step_data))
        finally:
            loop.close()
        
        # Extract LLM-generated bugs from analysis
        llm_generated_bugs = self._extract_llm_bugs_from_analysis(llm_analysis, step_data)
        print(f"🤖 LLM ANALYSIS: Extracted {len(llm_generated_bugs)} bugs from step '{step_data.get('step_name')}'")
        
        # Return ONLY LLM-generated results
        return llm_generated_bugs
    
    async def _perform_llm_analysis(self, step_data: Dict) -> Dict:
        """Perform LLM-based analysis on step data with screenshots"""
        
        try:
            # Prepare step context
            step_context = self._prepare_step_context(step_data)
            
            # Get screenshot if available
            screenshot_path = step_data.get('screenshot_path')
            screenshot_base64 = None
            
            if screenshot_path and os.path.exists(screenshot_path):
                try:
                    with open(screenshot_path, 'rb') as f:
                        screenshot_bytes = f.read()
                        screenshot_base64 = base64.b64encode(screenshot_bytes).decode('utf-8')
                        print(f"📸 Loaded screenshot for LLM analysis: {screenshot_path} (size: {len(screenshot_bytes)} bytes)")
                        logger.info(f"📸 Loaded screenshot for LLM analysis: {screenshot_path}")
                except Exception as e:
                    print(f"❌ Failed to load screenshot {screenshot_path}: {e}")
                    logger.warning(f"Failed to load screenshot {screenshot_path}: {e}")
            else:
                print(f"⚠️ Screenshot not found: {screenshot_path}")
            
            # Perform different types of LLM analysis with screenshot
            print("🔍 Starting craft bug analysis...")
            craft_bug_analysis = await self._analyze_craft_bugs_with_llm(step_context, screenshot_base64)
            print(f"✅ Craft bug analysis: {type(craft_bug_analysis)}")
            
            print("🔍 Starting performance analysis...")
            performance_analysis = await self._analyze_performance_with_llm(step_context, screenshot_base64)
            print(f"✅ Performance analysis: {type(performance_analysis)}")
            
            print("🔍 Starting visual analysis...")
            visual_analysis = await self._analyze_visual_consistency_with_llm(step_context, screenshot_base64)
            print(f"✅ Visual analysis: {type(visual_analysis)}")
            
            print("🔍 Starting interaction analysis...")
            interaction_analysis = await self._analyze_interaction_with_llm(step_context, screenshot_base64)
            print(f"✅ Interaction analysis: {type(interaction_analysis)}")
            
            return {
                'craft_bugs': craft_bug_analysis,
                'performance': performance_analysis,
                'visual_consistency': visual_analysis,
                'interaction': interaction_analysis,
                'timestamp': datetime.now().isoformat()
            }
                
        except Exception as e:
            logger.error(f"LLM analysis failed: {e}")
            return {
                'craft_bugs': {'analysis': f'Error: {e}', 'confidence': False},
                'performance': {'analysis': f'Error: {e}', 'confidence': False},
                'visual_consistency': {'analysis': f'Error: {e}', 'confidence': False},
                'interaction': {'analysis': f'Error: {e}', 'confidence': False}
            }
    
    def _extract_llm_bugs_from_analysis(self, analysis: Dict, step_data: Dict) -> List[Dict]:
        """Extract structured bug information from LLM analysis"""
        
        all_bugs = []
        
        # Process each analysis type
        for analysis_type, analysis_result in analysis.items():
            if isinstance(analysis_result, dict) and 'analysis' in analysis_result:
                analysis_text = analysis_result['analysis']
                if analysis_text and not analysis_text.startswith('Error:'):
                    bugs = self._parse_analysis_for_bugs(analysis_text, analysis_type, step_data)
                    all_bugs.extend(bugs)
        
        return all_bugs
    
    def _parse_analysis_for_bugs(self, analysis_text: str, analysis_type: str, step_data: Dict) -> List[Dict]:
        """Parse LLM analysis text to extract structured bug information"""
        
        bugs = []
        
        # First, try to find structured format
        if "CRAFT BUG #" in analysis_text:
            bugs = self._extract_structured_bug_info(analysis_text, analysis_type, step_data)
        else:
            # Fallback to generic parsing
            bugs = self._extract_generic_issues(analysis_text, analysis_type, step_data)
        
        return bugs
    
    def _extract_structured_bug_info(self, analysis_text: str, analysis_type: str, step_data: Dict) -> List[Dict]:
        """Extract structured bug information from detailed LLM output"""
        
        bugs = []
        bug_sections = analysis_text.split("CRAFT BUG #")[1:]  # Skip the first empty part
        
        for i, section in enumerate(bug_sections, 1):
            try:
                # Extract basic fields
                title = self._extract_field(section, "Title:")
                bug_type = self._extract_field(section, "Type:")
                severity = self._extract_field(section, "Severity:")
                
                # Extract location details
                screen_position = self._extract_field(section, "Screen Position:")
                ui_path = self._extract_field(section, "UI Path:")
                element = self._extract_field(section, "Element:")
                visual_context = self._extract_field(section, "Visual Context:")
                coordinates = self._extract_field(section, "Coordinates:")
                
                # Extract problem details
                what_wrong = self._extract_field(section, "What's Wrong:")
                expected = self._extract_field(section, "Expected:")
                impact = self._extract_field(section, "Impact:")
                
                # Extract measurements
                visual_measurement = self._extract_field(section, "Visual:")
                color_measurement = self._extract_field(section, "Colors:")
                typography_measurement = self._extract_field(section, "Typography:")
                spacing_measurement = self._extract_field(section, "Spacing:")
                
                # Extract reproduction details
                prerequisites = self._extract_field(section, "Prerequisites:")
                visual_check = self._extract_field(section, "Visual Check:")
                expected_result = self._extract_field(section, "Expected Result:")
                actual_result = self._extract_field(section, "Actual Result:")
                
                # Extract developer action
                immediate_fix = self._extract_field(section, "Immediate Fix:")
                code_location = self._extract_field(section, "Code Location:")
                visual_target = self._extract_field(section, "Visual Target:")
                testing_approach = self._extract_field(section, "Testing Approach:")
                
                # Construct description from available fields
                description = f"{what_wrong} when viewing the interface. Expected: {expected}"
                
                bug = {
                    'title': f"LLM Detected: {title}",
                    'type': bug_type or 'Visual',
                    'severity': severity or 'Yellow',
                    'description': description,
                    'category': 'Craft Bugs',
                    'analysis_type': analysis_type,
                    
                    # Location details
                    'screen_position': screen_position,
                    'ui_path': ui_path,
                    'element': element,
                    'visual_context': visual_context,
                    'coordinates': coordinates,
                    
                    # Problem details
                    'what_wrong': what_wrong,
                    'expected': expected,
                    'impact': impact,
                    
                    # Measurements
                    'visual_measurement': visual_measurement,
                    'color_measurement': color_measurement,
                    'typography_measurement': typography_measurement,
                    'spacing_measurement': spacing_measurement,
                    
                    # Reproduction
                    'prerequisites': prerequisites,
                    'visual_check': visual_check,
                    'expected_result': expected_result,
                    'actual_result': actual_result,
                    
                    # Developer action
                    'immediate_fix': immediate_fix,
                    'code_location': code_location,
                    'visual_target': visual_target,
                    'testing_approach': testing_approach,
                    
                    # Context
                    'step_name': step_data.get('step_name', 'Unknown'),
                    'scenario': step_data.get('scenario_description', 'Unknown'),
                    'persona': step_data.get('persona_type', 'User')
                }
                
                bugs.append(bug)
                
            except Exception as e:
                logger.warning(f"Failed to parse structured bug #{i}: {e}")
                continue
        
        return bugs
    
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
    
    def _extract_generic_issues(self, analysis_text: str, analysis_type: str, step_data: Dict) -> List[Dict]:
        """Extract basic bug information when LLM doesn't follow structured format"""
        
        bugs = []
        
        # Filter out problematic phrases
        problematic_phrases = [
            "i'm sorry", "i can't", "cannot", "unable to", "no visible",
            "guide you", "step-by-step", "approach", "framework",
            "check for", "note any", "assess how", "include exact",
            "ensure you", "provide exact", "analyze the", "focus only"
        ]
        
        # Split into lines and look for issues
        lines = analysis_text.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line or len(line) < 10:
                continue
            
            # Skip problematic guidance text
            if any(phrase in line.lower() for phrase in problematic_phrases):
                continue
            
            # Look for issue indicators
            issue_keywords = [
                "delay", "misaligned", "inconsistent", "missing", "unresponsive",
                "slow", "poor", "broken", "faulty", "problem", "issue", "error"
            ]
            
            if any(keyword in line.lower() for keyword in issue_keywords):
                # Extract a title from the line
                title = line[:100].strip()
                if len(title) > 5 and not any(phrase in title.lower() for phrase in problematic_phrases):
                    bug = {
                        'title': f"LLM Detected: {title}",
                        'type': 'Visual',
                        'severity': 'Yellow',
                        'description': line,
                        'category': 'Craft Bugs',
                        'analysis_type': analysis_type,
                        'step_name': step_data.get('step_name', 'Unknown'),
                        'scenario': step_data.get('scenario_description', 'Unknown'),
                        'persona': step_data.get('persona_type', 'User')
                    }
                    bugs.append(bug)
        
        return bugs
    
    async def _analyze_craft_bugs_with_llm(self, context: Dict, screenshot_base64: Optional[str] = None) -> Dict:
        """Analyze craft bugs using LLM with screenshot"""
        
        prompt = self.analysis_prompts['craft_bug_detection'].format(**context)
        
        try:
            messages = [{"role": "user", "content": prompt}]
            
            # Add screenshot if available
            if screenshot_base64:
                messages[0]["content"] = [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{screenshot_base64}"}}
                ]
            
            response = await self.llm_client.chat.completions.create(
                model=self.llm_model,
                messages=messages,
                temperature=self.llm_temperature,
                max_tokens=self.llm_max_tokens
            )
            
            content = response.choices[0].message.content.strip()
            
            return {
                'analysis': content,
                'confidence': response.choices[0].finish_reason == 'stop'
            }
                
        except Exception as e:
            logger.error(f"Craft bug LLM analysis failed: {e}")
            return {
                'analysis': '',
                'confidence': False,
                'error': str(e)
            }
    
    async def _analyze_performance_with_llm(self, context: Dict, screenshot_base64: Optional[str] = None) -> Dict:
        """Analyze performance using LLM with screenshot"""
        
        prompt = self.analysis_prompts['performance_analysis'].format(**context)
        
        try:
            messages = [{"role": "user", "content": prompt}]
            
            # Add screenshot if available
            if screenshot_base64:
                messages[0]["content"] = [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{screenshot_base64}"}}
                ]
            
            response = await self.llm_client.chat.completions.create(
                model=self.llm_model,
                messages=messages,
                temperature=self.llm_temperature,
                max_tokens=self.llm_max_tokens
            )
            
            content = response.choices[0].message.content.strip()
            
            return {
                'analysis': content,
                'confidence': response.choices[0].finish_reason == 'stop'
            }
                
        except Exception as e:
            logger.error(f"Performance LLM analysis failed: {e}")
            return {
                'analysis': '',
                'confidence': False,
                'error': str(e)
            }
    
    async def _analyze_visual_consistency_with_llm(self, context: Dict, screenshot_base64: Optional[str] = None) -> Dict:
        """Analyze visual consistency using LLM with screenshot"""
        
        prompt = self.analysis_prompts['visual_consistency'].format(**context)
        
        try:
            messages = [{"role": "user", "content": prompt}]
            
            # Add screenshot if available
            if screenshot_base64:
                messages[0]["content"] = [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{screenshot_base64}"}}
                ]
            
            response = await self.llm_client.chat.completions.create(
                model=self.llm_model,
                messages=messages,
                temperature=self.llm_temperature,
                max_tokens=self.llm_max_tokens
            )
            
            content = response.choices[0].message.content.strip()
            
            return {
                'analysis': content,
                'confidence': response.choices[0].finish_reason == 'stop'
            }
                
        except Exception as e:
            logger.error(f"Visual consistency LLM analysis failed: {e}")
            return {
                'analysis': '',
                'confidence': False,
                'error': str(e)
            }
    
    async def _analyze_interaction_with_llm(self, context: Dict, screenshot_base64: Optional[str] = None) -> Dict:
        """Analyze interaction using LLM with screenshot"""
        
        prompt = self.analysis_prompts['interaction_analysis'].format(**context)
        
        try:
            messages = [{"role": "user", "content": prompt}]
            
            # Add screenshot if available
            if screenshot_base64:
                messages[0]["content"] = [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{screenshot_base64}"}}
                ]
            
            response = await self.llm_client.chat.completions.create(
                model=self.llm_model,
                messages=messages,
                temperature=self.llm_temperature,
                max_tokens=self.llm_max_tokens
            )
            
            content = response.choices[0].message.content.strip()
            
            return {
                'analysis': content,
                'confidence': response.choices[0].finish_reason == 'stop'
            }
                
        except Exception as e:
            logger.error(f"Interaction LLM analysis failed: {e}")
            return {
                'analysis': '',
                'confidence': False,
                'error': str(e)
            }

