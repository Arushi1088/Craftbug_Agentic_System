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
        self.llm_model = os.getenv('OPENAI_MODEL', 'gpt-4o-mini')
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
            'comprehensive_visual_analysis': """LITE PROMPT — STATIC VISUAL UX ANALYSIS (For GPT-4o-mini)

You are an expert UX Designer with 15+ years at Microsoft.
Analyze the provided screenshot for visual craft bugs and give developer-ready, actionable reports.

CONTEXT (Dynamic Input – injected per run)

Scenario: {scenario_description}

Step: {step_number_and_description}

Persona: {persona_type}

🎯 DETECT ISSUES

Check for:

Visual/Layout – misaligned elements, uneven spacing, wrong colors (include hex), typography errors, poor hierarchy.

Accessibility – color contrast, small/unreadable text, missing labels/alt text (if visible).

Interaction Affordance – unclear buttons, small click targets, confusing navigation, missing visual feedback.

AI/Copilot (if visible) – unclear suggestions, poor layout, missing trust indicators.

Consistency/Design System – Fluent compliance, spacing/alignment patterns, professional balance.

📑 OUTPUT FORMAT

For each issue, use this structure:

CRAFT BUG #X

Type: [Visual|Accessibility|Interaction|AI|Design]

Severity: [Red|Orange|Yellow]

Title: [Concise description]

Location: [Top/Bottom/Center + nearby element]

Expected: [Correct state]

Actual: [Observed issue]

Impact: [Effect on user experience]

Fix: [Specific action e.g., adjust margin, increase contrast, align text]

If no issues:
"No visible craft bugs in screenshot."

RULES

Only analyze what is visible in the screenshot.

If something is unclear, mark as [Not Observable].

Group similar issues into one bug.

Keep responses short, precise, developer-ready.""",

            'performance_analysis': """# STATIC VISUAL QUALITY ANALYSIS

You are analyzing a static screenshot for VISUAL quality indicators only. Focus on rendering quality, visual artifacts, and display issues that can be observed in a static image.

## CONTEXT:
- Step: {step_name}
- Scenario: {scenario_description}
- Screenshot: Static image of the current UI state

## VISUAL QUALITY INDICATORS TO LOOK FOR:
1. **Rendering Quality**: Blurry text, pixelated images, or visual artifacts
2. **Display Issues**: Elements that appear broken, cut off, or incorrectly sized
3. **Resource Loading**: Missing images, broken icons, or incomplete content
4. **Visual Consistency**: Inconsistent rendering across similar elements
5. **Color Accuracy**: Incorrect colors, poor contrast, or visual distortion

## CRITICAL RULES:
- ONLY report what you can SEE in the screenshot
- Do NOT invent timing information or interaction delays
- Do NOT report performance issues that require user interaction
- Focus on visual quality and rendering issues only

## 🔄 DEDUPLICATION REQUIREMENTS

IMPORTANT: This screenshot will be analyzed by multiple specialized prompts. To prevent duplicate bug reports:

1. **FOCUS ON YOUR SPECIALTY**: This prompt focuses on VISUAL QUALITY/RENDERING issues only. Only report issues related to rendering quality, display problems, or visual artifacts.

2. **AVOID OVERLAP**: 
   - If an issue is primarily about visual alignment/spacing → Let the Comprehensive Visual prompt handle it
   - If an issue is primarily about interaction design → Let the Interaction Design prompt handle it
   - If an issue is primarily about accessibility → Let the Accessibility prompt handle it

3. **UNIQUE IDENTIFIERS**: Each bug should have a unique combination of:
   - Element location (UI Path)
   - Issue type (Quality/Rendering/Display)
   - Specific problem description

4. **CONSOLIDATE SIMILAR ISSUES**: If you find multiple instances of the same quality problem (e.g., multiple blurry elements), report them as ONE bug with multiple examples.

5. **PRIORITIZE**: Report the most critical quality issues first. Don't duplicate minor issues that other prompts will catch.

## OUTPUT FORMAT:
If visual quality issues are found, describe them specifically with details about:
- What element has the issue
- Where it's located in the UI
- What the problem looks like
- How it affects the user experience

If no visual quality issues are found, respond with: "No visual quality issues detected in this screenshot."

Analyze the screenshot for visual quality indicators only.""",

            'interaction_analysis': """# STATIC VISUAL INTERACTION DESIGN ANALYSIS

You are analyzing a static screenshot for visual interaction design issues only. Focus on visual affordances, button states, and interactive element design.

## CONTEXT:
- Step: {step_name}
- Scenario: {scenario_description}
- Screenshot: Static image of the current UI state

## VISUAL INTERACTION DESIGN ISSUES TO CHECK:
1. **Visual Affordance Issues**: Elements that don't look clickable/interactive
2. **Button State Problems**: Poor button states, unclear interactive areas
3. **Interactive Element Design**: Elements that appear confusing or hard to use
4. **Visual Feedback Issues**: Missing or unclear visual feedback states
5. **Click Target Size**: Elements that appear too small to click (<20px visible area)

## CRITICAL RULES:
- ONLY report visual interaction design issues visible in the screenshot
- Do NOT report actual interaction testing or responsiveness
- Do NOT report delays or timing issues
- Focus on visual design of interactive elements only

## 🔄 DEDUPLICATION REQUIREMENTS

IMPORTANT: This screenshot will be analyzed by multiple specialized prompts. To prevent duplicate bug reports:

1. **FOCUS ON YOUR SPECIALTY**: This prompt focuses on VISUAL INTERACTION DESIGN issues only. Only report issues related to visual affordances, button states, and interactive element design.

2. **AVOID OVERLAP**: 
   - If an issue is primarily about visual alignment/spacing → Let the Comprehensive Visual prompt handle it
   - If an issue is primarily about visual quality/rendering → Let the Visual Quality prompt handle it
   - If an issue is primarily about accessibility → Let the Accessibility prompt handle it

3. **UNIQUE IDENTIFIERS**: Each bug should have a unique combination of:
   - Element location (UI Path)
   - Issue type (Interaction/Affordance/Button State)
   - Specific problem description

4. **CONSOLIDATE SIMILAR ISSUES**: If you find multiple instances of the same interaction problem (e.g., multiple unclear buttons), report them as ONE bug with multiple examples.

5. **PRIORITIZE**: Report the most critical interaction design issues first. Don't duplicate minor issues that other prompts will catch.

## OUTPUT FORMAT:
If visual interaction design issues are found, describe them specifically with details about:
- What interactive element has the issue
- Where it's located in the UI
- What makes it confusing or hard to use
- How it affects user interaction

If no visual interaction design issues are found, respond with: "No visual interaction design issues detected in this screenshot."

Analyze the screenshot for visual interaction design issues only.""",

            'expert_triager': """# EXPERT CRAFT BUG TRIAGER

You are an expert UX triager with 15+ years at Microsoft specializing in craft bug analysis and prioritization. Your role is to evaluate, validate, and prioritize craft bugs based on their real-world impact and confidence level.

## WHAT IS A CRAFT BUG?

Craft bugs are issues that contribute to clunkiness, jarring, or janky user experiences. They include:

### HIGH IMPACT CRAFT BUGS (Priority 1-3):
- **Broken/unusable experiences** - Elements that prevent task completion
- **Obvious visual inconsistencies** - Misaligned elements, wrong colors, inconsistent spacing
- **Usability bugs** - Confusing interfaces, unclear affordances
- **Non-actionable/misleading messaging** - Unclear labels, confusing instructions
- **Accessibility violations** - Poor contrast, missing focus indicators
- **Visual harmony issues** - Stray pixels, poor alignment, inconsistent styling
- **Fluent Design violations** - Wrong corner radius, incorrect theming, improper z-ordering

### MEDIUM IMPACT CRAFT BUGS (Priority 4-6):
- **Minor visual inconsistencies** - Slight misalignments, small spacing issues
- **Polish issues** - Elements that work but feel unrefined
- **Secondary accessibility concerns** - Issues that don't block but reduce usability

### LOW IMPACT CRAFT BUGS (Priority 7-9):
- **Minor polish opportunities** - Very slight visual improvements
- **Edge case issues** - Problems that rarely occur
- **Subjective preferences** - Matters of taste rather than functionality

## TRIAGING FRAMEWORK

### CONFIDENCE SCORING (1-10):
- **10**: Clear, obvious issue with undeniable evidence
- **8-9**: Strong evidence, likely a real issue
- **6-7**: Some evidence, but could be subjective
- **4-5**: Weak evidence, might be hallucination
- **1-3**: Very weak evidence, likely hallucination

### IMPACT SCORING (1-10):
- **10**: Blocks critical workflow, unusable
- **8-9**: Significant user friction, major workflow impact
- **6-7**: Noticeable friction, affects efficiency
- **4-5**: Minor friction, slight workflow impact
- **1-3**: Minimal impact, mostly cosmetic

### PRIORITY CALCULATION:
```
Priority = (Impact Score × 0.7) + (Confidence Score × 0.3)
```

### PRIORITY LEVELS:
- **P1 (Critical)**: Priority 8.5-10 - Must fix immediately
- **P2 (High)**: Priority 7.0-8.4 - Fix in next sprint
- **P3 (Medium)**: Priority 5.5-6.9 - Fix when possible
- **P4 (Low)**: Priority 4.0-5.4 - Nice to have
- **P5 (Reject)**: Priority <4.0 - Not actionable

## VALIDATION CRITERIA

### ACCEPT BUG IF:
- ✅ Clear visual evidence in description
- ✅ Specific location and element identified
- ✅ Impact on user experience is clear
- ✅ Issue is actionable and fixable
- ✅ Confidence score ≥6

### REJECT BUG IF:
- ❌ No specific visual evidence
- ❌ Vague or generic description
- ❌ Subjective preference without UX impact
- ❌ Issue cannot be observed in static screenshot
- ❌ Confidence score <4
- ❌ Impact score <3

## OUTPUT FORMAT

For each bug, provide:

TRIAGED BUG #{bug_number}

ORIGINAL BUG:
[Copy the original bug description]

TRIAGE ANALYSIS:
- **Confidence Score**: [1-10] - [Reasoning]
- **Impact Score**: [1-10] - [Reasoning]
- **Calculated Priority**: [Score] - [P1/P2/P3/P4/P5]
- **Validation**: [Accept/Reject] - [Reason]

PRIORITY JUSTIFICATION:
- **Why this matters**: [Impact on user experience]
- **Evidence quality**: [How clear is the visual evidence]
- **Actionability**: [How easy is it to fix]
- **User segments affected**: [Who will notice this]

RECOMMENDED ACTION:
- **Immediate**: [What should be done right away]
- **Follow-up**: [Additional investigation needed]
- **Alternative**: [If rejected, what could make it actionable]

## CRITICAL REQUIREMENTS

1. **BE RUTHLESS**: Reject bugs with weak evidence or low impact
2. **FOCUS ON REAL IMPACT**: Prioritize issues that actually affect users
3. **VALIDATE EVIDENCE**: Ensure bugs have clear visual evidence
4. **CONSIDER CONTEXT**: Understand the user scenario and workflow
5. **AVOID HALLUCINATIONS**: Don't accept bugs that seem made up
6. **PRIORITIZE OBJECTIVELY**: Use scoring system, not gut feeling

## EXAMPLE TRIAGE

TRIAGED BUG #1

ORIGINAL BUG:
- Type: Visual
- Title: Save Button Misaligned with Adjacent Elements
- Description: Save button appears slightly lower than adjacent buttons

TRIAGE ANALYSIS:
- **Confidence Score**: 8/10 - Clear visual misalignment described with specific location
- **Impact Score**: 6/10 - Affects visual scanning and feels unpolished
- **Calculated Priority**: 6.8 - P3 (Medium)
- **Validation**: Accept - Clear evidence, actionable issue

PRIORITY JUSTIFICATION:
- **Why this matters**: Creates visual inconsistency that affects professional perception
- **Evidence quality**: Specific element and location identified
- **Actionability**: Simple CSS fix for alignment
- **User segments affected**: All users will notice the visual inconsistency

RECOMMENDED ACTION:
- **Immediate**: Fix button alignment in File ribbon component
- **Follow-up**: Check other button groups for similar issues
- **Alternative**: N/A

Analyze the provided bugs using this triaging framework."""
        }
    
    def _prepare_step_context(self, step_data: Dict) -> Dict:
        """Prepare context for LLM analysis"""
        # Extract step number from step name
        step_number = 1
        if 'step' in step_data.get('step_name', '').lower():
            match = re.search(r'(\d+)', step_data.get('step_name', ''))
            if match:
                step_number = int(match.group(1))
        
        # Create step_number_and_description for the new prompt format
        step_number_and_description = f"{step_number} - {step_data.get('step_name', 'Unknown Step')}"
        
        return {
            'step_name': step_data.get('step_name', 'Unknown Step'),
            'step_number': step_number,
            'total_steps': 1,  # Default for single step analysis
            'action_type': step_data.get('action_type', 'unknown'),
            'duration_ms': step_data.get('duration_ms', 0),
            'scenario_name': step_data.get('scenario_description', 'Test Scenario'),  # Map to scenario_name for prompt
            'scenario_description': step_data.get('scenario_description', 'Test Scenario'),
            'persona_type': step_data.get('persona_type', 'User'),
            'expected_behavior': step_data.get('expected_behavior', 'Expected behavior not specified'),
            'current_action': step_data.get('action_type', 'unknown'),  # Add current_action for prompt
            'interaction_timing': step_data.get('duration_ms', 0),  # Add interaction_timing for prompt
            'step_number_and_description': step_number_and_description  # New format for lite prompt
        }
    
    async def analyze_step_with_llm(self, step_data: Dict) -> List[Dict]:
        """Analyze a step using LLM-enhanced detection - ONLY LLM bugs"""
        
        if not self.enable_llm:
            return []
        
        # Perform LLM analysis only
        print(f"🤖 LLM ANALYSIS: Starting analysis for step '{step_data.get('step_name')}'")
        
        # Run async analysis directly
        llm_analysis = await self._perform_llm_analysis(step_data)
        
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
            print("🔍 Starting comprehensive visual analysis...")
            comprehensive_analysis = await self._analyze_comprehensive_visual_with_llm(step_context, screenshot_base64)
            print(f"✅ Comprehensive visual analysis: {type(comprehensive_analysis)}")
            
            print("🔍 Starting performance analysis...")
            performance_analysis = await self._analyze_performance_with_llm(step_context, screenshot_base64)
            print(f"✅ Performance analysis: {type(performance_analysis)}")
            
            print("🔍 Starting interaction analysis...")
            interaction_analysis = await self._analyze_interaction_with_llm(step_context, screenshot_base64)
            print(f"✅ Interaction analysis: {type(interaction_analysis)}")
            
            return {
                'craft_bugs': comprehensive_analysis,
                'performance': performance_analysis,
                'visual_consistency': comprehensive_analysis,  # Use comprehensive analysis for visual consistency too
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
                # Extract basic fields for new lite format
                bug_type = self._extract_field(section, "Type:")
                severity = self._extract_field(section, "Severity:")
                title = self._extract_field(section, "Title:")
                location = self._extract_field(section, "Location:")
                expected = self._extract_field(section, "Expected:")
                actual = self._extract_field(section, "Actual:")
                impact = self._extract_field(section, "Impact:")
                fix = self._extract_field(section, "Fix:")
                
                # Construct description from available fields
                description = f"{actual} when viewing the interface. Expected: {expected}"
                
                bug = {
                    'title': f"LLM Detected: {title}",
                    'type': bug_type or 'Visual',
                    'severity': severity or 'Yellow',
                    'description': description,
                    'category': 'Craft Bugs',
                    'analysis_type': analysis_type,
                    
                    # Location details (simplified)
                    'screen_position': location,
                    'ui_path': location,
                    'element': title,
                    'visual_context': location,
                    'coordinates': '',
                    
                    # Problem details (simplified)
                    'what_wrong': actual,
                    'expected': expected,
                    'impact': impact,
                    
                    # Measurements (simplified)
                    'visual_measurement': actual,
                    'color_measurement': '',
                    'typography_measurement': '',
                    'spacing_measurement': '',
                    
                    # Reproduction (simplified)
                    'prerequisites': '',
                    'visual_check': '',
                    'expected_result': expected,
                    'actual_result': actual,
                    
                    # Developer action (simplified)
                    'immediate_fix': fix,
                    'code_location': '',
                    'visual_target': expected,
                    'testing_approach': '',
                    
                    # Context
                    'step_name': step_data.get('step_name', 'Unknown'),
                    'scenario': step_data.get('scenario_description', 'Unknown'),
                    'persona': step_data.get('persona_type', 'User'),
                    
                    # Screenshot association - CRITICAL for proper bug-to-screenshot mapping
                    'screenshot_path': step_data.get('screenshot_path', ''),
                    'step_index': step_data.get('step_index', 0)
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
        
        # Filter out problematic phrases and "no issues" responses
        problematic_phrases = [
            "i'm sorry", "i can't", "cannot", "unable to", "no visible",
            "guide you", "step-by-step", "approach", "framework",
            "check for", "note any", "assess how", "include exact",
            "ensure you", "provide exact", "analyze the", "focus only",
            "no visual quality issues detected", "no visual interaction design issues detected",
            "no visual issues detected", "no issues detected", "no problems found",
            "appears to be working correctly", "looks good", "no problems observed"
        ]
        
        # Check if the entire response is ONLY a "no issues" message (not mixed with actual issues)
        analysis_lower = analysis_text.lower()
        no_issues_indicators = [
            "no visual quality issues detected",
            "no visual interaction design issues detected", 
            "no visual issues detected",
            "no issues detected",
            "no problems found",
            "appears to be working correctly",
            "looks good",
            "no problems observed"
        ]
        
        # Only filter out if the response is EXCLUSIVELY a "no issues" message
        # Check if the response contains ONLY these phrases and nothing else substantial
        has_only_no_issues = False
        for indicator in no_issues_indicators:
            if indicator in analysis_lower:
                # Check if this is the ONLY substantial content in the response
                # Remove the indicator and see if there's any other meaningful content
                temp_text = analysis_lower.replace(indicator, "").strip()
                # Remove common filler words
                temp_text = re.sub(r'\b(the|a|an|and|or|but|in|on|at|to|for|of|with|by)\b', '', temp_text)
                temp_text = re.sub(r'\s+', ' ', temp_text).strip()
                
                if len(temp_text) < 20:  # If very little content remains, it's likely just a "no issues" response
                    has_only_no_issues = True
                    break
        
        if has_only_no_issues:
            # Only filter out if the response is exclusively "no issues"
            return []
        
        # Debug: Print the actual LLM response for troubleshooting
        print(f"🔍 DEBUG LLM Response ({analysis_type}): {analysis_text[:200]}...")
        
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
                        'persona': step_data.get('persona_type', 'User'),
                        
                        # Screenshot association - CRITICAL for proper bug-to-screenshot mapping
                        'screenshot_path': step_data.get('screenshot_path', ''),
                        'step_index': step_data.get('step_index', 0)
                    }
                    bugs.append(bug)
        
        return bugs
    
    async def _analyze_comprehensive_visual_with_llm(self, context: Dict, screenshot_base64: Optional[str] = None) -> Dict:
        """Analyze comprehensive visual issues using LLM with screenshot"""
        
        prompt = self.analysis_prompts['comprehensive_visual_analysis'].format(**context)
        
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
                
                max_completion_tokens=self.llm_max_tokens
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
                
                max_completion_tokens=self.llm_max_tokens
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
        
        prompt = self.analysis_prompts['comprehensive_visual_analysis'].format(**context)
        
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
                
                max_completion_tokens=self.llm_max_tokens
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
                
                max_completion_tokens=self.llm_max_tokens
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

