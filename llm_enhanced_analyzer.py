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
        self.llm_model = "gpt-5-nano"
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

You are an expert UX Designer with 15+ years at Microsoft analyzing Excel Web screenshots for craft bugs. Provide ACTIONABLE bug reports that developers can immediately act upon.

## SCREENSHOT CONTEXT:
- Scenario: {scenario_name}
- Step: {step_number} of {total_steps}
- Action: {current_action}
- Expected: {expected_behavior}
- User Persona: {persona_type}

## ANALYZE FOR CRAFT BUGS WITH COMPLETE ACTIONABLE DETAILS:

═══════════════════════════════════════════════════════════════

🎯 CRAFT BUG CATEGORIES TO DETECT

VISUAL ISSUES (Primary Focus):
- Misaligned elements (describe as slightly off, uneven, crooked)
- Wrong colors (specify hex codes)
- Incorrect spacing (describe as too much/little padding, uneven margins)
- Typography errors (font size, weight, family)
- Missing visual feedback
- Inconsistent styling
- Poor visual hierarchy
- Layout problems (overlap, positioning)

ACCESSIBILITY ISSUES (Visual Only):
- Insufficient color contrast (specify ratio)
- Missing alt text/labels (if visible in screenshot)
- Poor visual focus indicators (if visible)
- Screen reader compatibility issues (if detectable)
- Text readability problems (size, contrast, clarity)

VISUAL INTERACTION DESIGN ISSUES (Static Analysis):
- Elements that don't look clickable/interactive
- Poor button states (if visible in screenshot)
- Unclear affordances (visual cues)
- Confusing visual navigation
- Small click targets (appear too small to click)
- Missing visual feedback states

AI/COPILOT VISUAL ISSUES:
- Poor conversation flow layout
- Unclear AI suggestions presentation
- Missing trust indicators
- Integration problems with grid (visual only)
- Poor visual hierarchy in AI responses

LAYOUT & DESIGN SYSTEM ISSUES:
- Fluent Design compliance violations
- Inconsistent spacing patterns
- Poor visual balance
- Unprofessional appearance
- Responsive design problems (if visible)
- Grid alignment issues

═══════════════════════════════════════════════════════════════

📋 REQUIRED OUTPUT FORMAT

For each craft bug detected, provide this EXACT structure:

CRAFT BUG #1

ISSUE SUMMARY:
- Type: [Visual|Accessibility|Interaction_Design|AI|Layout|Design_System]
- Severity: [Red|Orange|Yellow] 
- Title: [Concise descriptive title]

LOCATION & CONTEXT:
- Screen Position: [Top-Left|Top-Right|Bottom-Left|Bottom-Right|Center and specific area]
- UI Path: [Ribbon > Tab > Section > Element]
- Element: [Exact button/icon/field name]
- Visual Context: [What's nearby for reference]
- Scenario Step: Step {step_number} of {total_steps} - "{step_name}"
- User Action: [What user was doing when issue occurred]
- Expected Behavior: [What should have happened]
- Actual Behavior: [What actually happened]
- Visual Impact: [How this affects the user's visual experience]

VISUAL ANALYSIS:
- Visual Issues: [Describe misalignments, spacing issues in generic terms]
- Size: [Element dimensions if relevant - describe as too large/small]
- Color: [Hex codes if color issues, contrast ratios]
- Typography: [Font issues if relevant - describe as too large/small, wrong weight]
- Spacing: [Describe padding/margin issues as too much/little, uneven, inconsistent]

REPRODUCTION STEPS:
Prerequisites:
- Browser: [Chrome/Edge version]
- Resolution: [Screen size and zoom]
- Excel State: [Blank workbook/with data/etc]

Steps to Reproduce:
1. [Exact step-by-step instructions]
2. [Include navigation path]
3. [Specify exact user actions]
4. [How to observe the issue visually]
5. [How to verify the visual problem]

Expected Result: [What should happen visually]
Actual Result: [What actually happens visually]
Reproduction Rate: [How often this occurs]

PERSONA IMPACT:
- Novice Users: [How this affects new users visually]
- Power Users: [How this affects efficiency-focused users]  
- Super Fans: [How this affects quality-obsessed users]
- Frustration Level: [1-10 for each persona]

DEVELOPER ACTION:
- Immediate Fix: [Specific visual change needed]
- Code Location: [Which component/file likely needs updating]
- Visual Target: [Specific visual improvement criteria]
- Testing Approach: [How to verify the visual fix works]

═══════════════════════════════════════════════════════════════

🎯 ANALYSIS INSTRUCTIONS

1. EXAMINE EVERY VISIBLE ELEMENT
   - Scan systematically: top-left to bottom-right
   - Check alignment, spacing, colors, typography
   - Verify visual consistency across similar elements
   - Look for visual design system violations

2. MEASURE APPROXIMATELY
   - Use descriptive terms like "slightly off", "too much spacing", "uneven alignment"
   - Compare similar elements for consistency
   - Check against Microsoft Fluent Design standards
   - Note visual quality and rendering issues

3. CONSIDER USER JOURNEY
   - How does this visual issue affect task completion?
   - What would different user types think/feel about the visual design?
   - How does this impact overall scenario success?
   - What is the business/competitive visual impact?

4. PROVIDE ACTIONABLE DETAILS
   - Every finding must be visually reproducible
   - Include exact steps developers can follow
   - Specify measurable visual success criteria
   - Give specific visual fix recommendations

═══════════════════════════════════════════════════════════════

🔄 DEDUPLICATION REQUIREMENTS

IMPORTANT: This screenshot will be analyzed by multiple specialized prompts. To prevent duplicate bug reports:

1. **FOCUS ON YOUR SPECIALTY**: This prompt focuses on COMPREHENSIVE VISUAL ANALYSIS. Only report issues that are primarily visual in nature.

2. **AVOID OVERLAP**: 
   - If an issue is primarily about visual quality/rendering → Let the Visual Quality prompt handle it
   - If an issue is primarily about interaction design → Let the Interaction Design prompt handle it
   - If an issue is primarily about accessibility → Let the Accessibility prompt handle it

3. **UNIQUE IDENTIFIERS**: Each bug should have a unique combination of:
   - Element location (UI Path)
   - Issue type (Visual/Accessibility/Interaction/Quality)
   - Specific problem description

4. **CONSOLIDATE SIMILAR ISSUES**: If you find multiple instances of the same visual problem (e.g., multiple misaligned buttons), report them as ONE bug with multiple examples.

5. **PRIORITIZE**: Report the most critical visual issues first. Don't duplicate minor issues that other prompts will catch.

═══════════════════════════════════════════════════════════════

EXAMPLE PERFECT RESPONSE:

CRAFT BUG #1

ISSUE SUMMARY:
- Type: Visual
- Severity: Orange
- Title: Save Button Misaligned with Adjacent Elements

LOCATION & CONTEXT:
- Screen Position: Top-Right quadrant, main ribbon area
- UI Path: File > Save button (leftmost in File menu)
- Element: "Save" button with disk icon
- Visual Context: Next to "Save As" and "Export" buttons
- Scenario Step: Step 8 of 12 - "Save workbook with new chart"
- User Action: Looking at File menu options
- Expected Behavior: All buttons should be perfectly aligned
- Actual Behavior: Save button appears slightly lower than adjacent buttons
- Visual Impact: Creates visual inconsistency and feels unpolished

VISUAL ANALYSIS:
- Visual Issues: Save button appears slightly misaligned vertically with adjacent buttons
- Size: Button size appears appropriate
- Color: #0078d4 (correct Fluent Design blue)
- Typography: Segoe UI appears correct size and weight
- Spacing: Horizontal spacing between buttons appears consistent

REPRODUCTION STEPS:
Prerequisites:
- Browser: Chrome 118+ or Edge 110+
- Resolution: 1920x1080, 100% zoom
- Excel State: Workbook with content ready to save

Steps to Reproduce:
1. Open Excel Web with any workbook containing data
2. Navigate to File tab in ribbon (top-left)
3. Observe Save button alignment with adjacent buttons
4. Compare visual alignment across all buttons in the group
5. Note any misalignment in the button row

Expected Result: All buttons perfectly aligned horizontally
Actual Result: Save button appears slightly lower than Save As and Export buttons
Reproduction Rate: 10/10 attempts show this misalignment

PERSONA IMPACT:
- Novice Users: Mild confusion (3/10) - interface feels slightly off
- Power Users: Noticeable frustration (6/10) - affects visual scanning
- Super Fans: Quality concern (8/10) - feels unpolished vs desktop Excel
- Business Impact: Reduces confidence in Excel Web visual quality

DEVELOPER ACTION:
- Immediate Fix: Adjust Save button vertical alignment to match adjacent buttons
- Code Location: File ribbon component button alignment
- Visual Target: Perfect horizontal alignment with no visible misalignment
- Testing Approach: Visual regression testing on button alignment

═══════════════════════════════════════════════════════════════

CRITICAL REQUIREMENTS:
- Find ALL visible issues, not just obvious ones
- Provide EXACT locations developers can find
- Include COMPLETE reproduction steps
- Give SPECIFIC visual observations using descriptive terms only
- Specify ACTIONABLE visual fixes, not generic suggestions
- Consider impact on ALL user personas
- Report ZERO issues only if screenshot is genuinely perfect
- Focus ONLY on what you can SEE in this static screenshot
- Do NOT report timing, performance, or interaction issues that cannot be observed visually
- Use ONLY generic descriptions - NO pixel measurements or exact coordinates
- Describe spacing as "too much", "too little", "uneven", "inconsistent"
- Describe alignment as "slightly off", "misaligned", "crooked", "uneven"
- FOCUS ON YOUR SPECIALTY: Report only comprehensive visual issues, avoid overlap with other prompts
- CONSOLIDATE SIMILAR ISSUES: Group related problems into single bug reports

Analyze the provided screenshot now using this comprehensive framework.""",

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
If visual quality issues are found, describe them specifically. If none are visible, report "No visual quality issues detected in this screenshot."

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
If visual interaction design issues are found, describe them specifically. If none are visible, report "No visual interaction design issues detected in this screenshot."

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
            'interaction_timing': step_data.get('duration_ms', 0)  # Add interaction_timing for prompt
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

