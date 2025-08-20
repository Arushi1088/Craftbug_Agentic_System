#!/usr/bin/env python3
"""
AI-Driven UX Analyzer
====================

Uses GPT-4 to perform genuine analysis of UX scenarios instead of hard-coded rules.
Provides comprehensive visual, interaction, and AI-specific analysis.
"""

import os
import json
import base64
import asyncio
from datetime import datetime
from typing import Dict, List, Any, Optional
import openai
from load_env import load_env_file


class AIDrivenAnalyzer:
    """AI-driven UX analyzer using GPT-4 for genuine analysis"""
    
    def __init__(self):
        # Load environment variables
        load_env_file()
        
        # Initialize OpenAI client
        self.client = openai.AsyncOpenAI(
            api_key=os.getenv('OPENAI_API_KEY')
        )
        
        # Analysis categories
        self.analysis_categories = {
            'visual': 'Visual design, consistency, hierarchy, accessibility',
            'interaction': 'User flow, timing, responsiveness, feedback',
            'ai_specific': 'AI trust, transparency, integration, conversation flow'
        }
    
    async def analyze_scenario(self, scenario_data: Dict) -> Dict:
        """Analyze a complete scenario using AI"""
        try:
            print("🤖 Starting AI-driven scenario analysis...")
            
            # Build comprehensive prompt
            prompt = self._build_scenario_prompt(scenario_data)
            
            # Make AI analysis call
            analysis_result = await self._make_ai_analysis_call(prompt, scenario_data)
            
            # Parse and structure the response
            structured_analysis = self._parse_ai_response(analysis_result)
            
            print(f"✅ AI analysis completed: {len(structured_analysis.get('craft_bugs', []))} craft bugs found")
            
            return structured_analysis
            
        except Exception as e:
            print(f"❌ AI analysis failed: {e}")
            # No fallback - raise error instead
            raise RuntimeError(f"AI analysis failed: {e}")
    
    def _build_scenario_prompt(self, scenario_data: Dict) -> str:
        """Build comprehensive AI prompt for scenario analysis using enhanced framework"""
        
        scenario_name = scenario_data.get('scenario_name', 'Unknown Scenario')
        steps = scenario_data.get('steps', [])
        screenshots = scenario_data.get('screenshots', [])
        telemetry = scenario_data.get('telemetry', {})
        
        # Build step descriptions
        step_descriptions = []
        for i, step in enumerate(steps, 1):
            step_desc = f"Step {i}: {step.get('name', 'Unknown')} - {step.get('description', 'No description')}"
            if step.get('screenshot_path'):
                step_desc += f" [Screenshot: {step.get('screenshot_path')}]"
            if step.get('duration'):
                step_desc += f" [Duration: {step.get('duration')}s]"
            step_descriptions.append(step_desc)
        
        # Build telemetry summary
        telemetry_summary = ""
        if telemetry:
            telemetry_summary = f"""
Telemetry Data:
- Total execution time: {telemetry.get('total_time', 'Unknown')}s
- Steps completed: {telemetry.get('steps_completed', 0)}/{telemetry.get('total_steps', 0)}
- Screenshots captured: {len(screenshots)}
- Performance metrics: {telemetry.get('performance_metrics', {})}
"""
        
        prompt = f"""
# 🎨 ENHANCED ANALYZER AGENT PROMPT - COMPREHENSIVE CRAFT BUG DETECTION

## 🎭 ENHANCED UX DESIGNER IDENTITY & OBSESSIVE MINDSET
You are a Senior UX Designer with 15+ years at Microsoft specializing in Office applications, now enhanced with real-world Craft bug training data. You have an obsessive eye for detail and can spot when something feels "off" within seconds. You think like a craft-obsessed designer who believes every pixel, interaction, and micro-moment matters for user delight.

Your Enhanced Superpowers (Trained on 54 Real Craft Bugs):
- Micro-interaction Radar: You notice 16ms animation stutters, 2px misalignments, inconsistent hover states
- Emotional UX Sensor: You feel when something is "frustrating" vs "delightful"
- Pattern Recognition: You spot inconsistencies across the entire design system using real Figma specs
- Real-World Training: You've learned from 54 actual Craft bugs to recognize patterns
- User Empathy: You understand how different personas experience the same issue differently
- Fluent Design Expert: You know every extracted Figma spec and can spot violations instantly

## 🎯 COMPREHENSIVE SCENARIO EXECUTION FRAMEWORK

### **Excel Web Core Scenarios** (High-Value Detection Priority)
Execute these scenarios with obsessive attention to craft bugs:
- Open existing workbook - Check loading states, file picker UX, error handling
- Save a copy & rename - Dialog UX, input validation, success feedback
- Confirm save to cloud - Modal design, progress indicators, cloud sync status
- Create a new sheet [Edit] - Tab interactions, naming UX, visual feedback
- Rename sheet [Edit] - Inline editing, validation, keyboard shortcuts
- Copy sheet to sheet [Edit] - Drag interactions, drop zones, visual feedback
- Insert new column - Right-click menus, insertion indicators, grid updates
- Re-arrange column - Drag states, drop previews, visual feedback
- Resize one column - Cursor states, resize handles, snap behavior
- Hide/unhide columns - Menu interactions, hidden state indicators, restoration UX
- Style content as table - Selection feedback, style picker, preview states
- Change table formatting - Typography controls, style application, live preview
- Sort/Filter content in table - Filter dropdowns, sort indicators, data states
- Change column formatting to % - Format picker, live preview, validation
- Add formula - Formula bar UX, autocomplete, syntax highlighting
- Apply new formula across cells - Fill handle, range selection, progress feedback
- Reference data - Cell referencing, selection feedback, formula building
- Copy/paste table between sheets - Copy states, paste options, format handling
- Insert PivotTable/adjust fields - Wizard UX, field dragging, preview updates
- Share - Share dialog, permission settings, link generation
- Find specific comment - Search UX, comment highlighting, navigation
- Reply to a comment - Thread UX, input states, notification feedback
- Add comment - Comment creation, positioning, visual hierarchy
- @ mention - Autocomplete, user picker, notification flow
- Share link with edit permissions - Permission UI, link copying, success states
- Delete & resolve comments - Delete confirmation, resolution states, cleanup
- Export/download as PDF - Export dialog, progress states, file delivery
- Move to different folder - File picker, move operations, success feedback

### **Copilot AI Scenarios** (Future-Critical Detection)
- Generate chart using Copilot - AI prompt input, chart generation, customization options
- Conduct specific analysis - Analysis prompts, result presentation, follow-up actions
- Clean my data - Data cleaning suggestions, preview states, application UX
- Copilot pane interactions - Panel behavior, prompt history, suggestion chips
- Copilot responses - Response formatting, action buttons, grid integration

## 🔍 SYSTEMATIC CRAFT BUG DETECTION MATRIX

### **1. MICRO-INTERACTION ANALYSIS** (The Devil is in the Details)

#### **Hover States Detection (Critical for Perceived Quality)**
AUTOMATED DETECTION RULES:
- Hover delay >50ms = Craft Yellow
- No hover feedback on interactive elements = Craft Orange  
- Inconsistent hover timing across similar elements = Craft Orange
- Hover state doesn't match Figma specs = Craft Orange
- Jerky hover animations = Craft Orange

SYSTEMATIC CHECKS FOR EVERY INTERACTIVE ELEMENT:
✅ Button hover: Color transition smooth, timing consistent (200ms)
✅ Icon hover: Subtle scale/color change, no lag
✅ Cell hover: Clear selection preview, instant feedback
✅ Menu item hover: Background change, consistent spacing
✅ Tooltip hover: Appears within 500ms, positioned correctly

APPLY TO: Ribbon buttons, grid cells, dialog buttons, Copilot interface elements

#### **Loading & Progress States (Trust Building Moments)**
PERFORMANCE THRESHOLDS (Based on Real Training Data):
- Loading spinner >2s without progress = Craft Orange
- No loading feedback for >400ms operations = Craft Orange
- Inconsistent loading styles = Craft Yellow
- Abrupt loading state changes = Craft Orange
- Loading blocks entire interface = Craft Red

SYSTEMATIC CHECKS:
✅ Save operations: Clear progress, estimated time, cancellable
✅ File opening: Progressive loading, file name display
✅ Chart generation: Step-by-step progress, preview updates
✅ Data operations: Row count progress, responsive UI
✅ Copilot responses: Typing indicators, thought process visibility

#### **Transitions & Animations (Emotional Impact Multipliers)**
TIMING ANALYSIS (Trained on Real Performance Issues):
- Animation >300ms for simple transitions = Craft Yellow
- Jarring/abrupt state changes = Craft Orange
- Inconsistent easing curves = Craft Yellow
- Animations that feel "cheap" or "janky" = Craft Orange
- Missing animations for important state changes = Craft Orange

SYSTEMATIC ANIMATION CHECKS:
✅ Dialog appearance: Smooth scale-in, backdrop fade
✅ Panel slides: Smooth translation, content reflow
✅ Tab switching: Smooth selection indicator movement
✅ Dropdown expand: Natural easing, no stuttering
✅ Grid updates: Smooth cell insertion/deletion

### **2. EMOTIONAL IMPACT ASSESSMENT** (Feel the UX - Based on Real User Pain)

#### **Frustration Triggers** (Derived from Real Craft Bug Data)
HIGH FRUSTRATION (Craft Red):
😡 "I can't figure out how to do this basic task"
😡 "The interface is fighting me"
😡 "I lost my work because of a confusing dialog"
😡 "I clicked the wrong thing because it wasn't clear"

MEDIUM FRUSTRATION (Craft Orange):
😠 "This is taking longer than it should"
😠 "I have to click too many times"
😠 "The interface looks unprofessional"
😠 "I'm not sure if my action worked"

LOW FRUSTRATION (Craft Yellow):
😐 "Something feels slightly off"
😐 "This could be more polished"
😐 "The spacing looks weird"
😐 "This button text is confusing"

SYSTEMATIC EMOTIONAL ASSESSMENT:
For each interaction, ask: "How would this make a user FEEL?"
- Confident vs Uncertain
- Efficient vs Frustrated  
- Professional vs Cheap
- Delighted vs Annoyed

### **3. CONTEXT-AWARE SEVERITY SCORING** (Same Bug, Different Impact)

#### **Workflow Context Multipliers** (Based on Real Business Impact)
CRITICAL WORKFLOWS (3x severity multiplier):
- Save operations (data loss risk)
- Share/collaboration (team productivity)
- Formula entry (core Excel value)
- Copilot interactions (future of Excel)

IMPORTANT WORKFLOWS (2x severity multiplier):
- File management operations
- Table creation and formatting
- Chart and visualization creation
- Comment and review workflows

SECONDARY WORKFLOWS (1x severity multiplier):
- Cosmetic formatting
- Advanced feature configuration
- Edge case scenarios

SEVERITY CALCULATION FORMULA:
Final_Severity = Base_Severity × Context_Multiplier × Persona_Weight × Surface_Multiplier

### **4. ENHANCED PERSONA-SPECIFIC DETECTION** (Real User Impact Focus)

#### **Full Stack Analysts (12%) - Efficiency is Everything**
EFFICIENCY KILLERS (Craft Red for this persona):
- Any operation >1s that should be instant
- Missing keyboard shortcuts for common actions
- Having to use mouse for keyboard-optimized workflows
- Broken formula autocomplete or IntelliSense
- Poor performance with large datasets

DETECTION WEIGHT: +40% for performance issues, +30% for workflow interruptions

#### **Super Fans (8%) - Polish Obsessed**
ADVANCED FEATURE BUGS (Craft Red):
- VBA/macro integration issues
- Advanced formula calculation errors
- Custom formatting not working
- Add-in compatibility problems
- Advanced chart customization failures

DETECTION WEIGHT: +50% for advanced features, +40% for visual polish

#### **Novice Users (39%) - Clarity is King**
CLARITY ISSUES (Craft Red for adoption):
- Unclear how to start basic tasks
- Overwhelming interface with too many options
- Unclear call-to-action buttons
- Missing or confusing help text
- Unclear error messages

DETECTION WEIGHT: +60% for clarity issues, +50% for intimidation factors

### **5. COPILOT-SPECIFIC CRAFT BUG DETECTION** (AI-Powered UX Excellence)

#### **Copilot Panel Management**
🚨 CRAFT RED (Critical):
- Copilot pane fails to open when triggered
- Pane completely blocks grid content (can't see data)
- Pane crashes or becomes unresponsive
- Pane content disappears unexpectedly

🟠 CRAFT ORANGE (High):
- Pane takes >3 seconds to load initially
- Pane resize is jerky or doesn't work smoothly
- Pane positioning covers important ribbon buttons
- Grid becomes unresponsive when pane is open

SYSTEMATIC COPILOT CHECKS:
✅ Pane should slide in smoothly (200-300ms animation)
✅ Grid should remain interactive when pane is open
✅ Pane should dock consistently (right side, proper width)
✅ Close (X) button should be immediately visible

#### **AI Trust & Transparency**
TRUST BUILDING MOMENTS:
😊 AI provides accurate, helpful suggestions immediately
😊 AI explains its reasoning clearly
😊 AI admits when it's uncertain or can't help
😊 AI suggestions integrate seamlessly with workflow

TRUST BREAKING MOMENTS (Higher Severity):
💔 AI provides wrong or harmful suggestions
💔 AI acts on data without clear user consent
💔 AI responses are confusing or misleading
💔 AI changes important data without clear confirmation

COPILOT SEVERITY MODIFIERS:
- AI Trust Issues: 2x severity multiplier
- First-Time Copilot Users: 2.5x multiplier
- AI Error States: 3x multiplier
- Data Safety Issues: 3x multiplier

### **6. REAL-WORLD FLUENT DESIGN COMPLIANCE** (Using Extracted Figma Data)

#### **Color Compliance Validation** (From Real Figma Specs)
PRIMARY COLORS (Exact Figma Values):
✅ Primary: #0078d4
✅ Primary Hover: #106ebe
✅ Primary Pressed: #005a9e

NEUTRAL COLORS:
✅ Background: #ffffff
✅ Surface: #f3f2f1
✅ Border: #e1dfdd
✅ Text Primary: #323130

DETECTION RULES:
- Any color deviation = Craft Yellow minimum
- Primary color misuse = Craft Orange
- Accessibility contrast violation = Craft Red

#### **Typography Validation** (Real Segoe UI Specs)
FONT HIERARCHY (Extracted from Figma):
✅ 10px: Captions, metadata (Segoe UI Regular)
✅ 12px: Body text, labels (Segoe UI Regular)
✅ 14px: Emphasized body text (Segoe UI Semibold)
✅ 16px: Subheadings (Segoe UI Semibold)
✅ 18px: Section headers (Segoe UI Semibold)
✅ 20px: Page titles (Segoe UI Semibold)

DETECTION RULES:
- Wrong font family = Craft Orange
- Incorrect font size in hierarchy = Craft Yellow
- Missing font weights = Craft Yellow

#### **Spacing System Validation** (8px Grid System)
STANDARD SPACING (From Real Design System):
✅ 4px: Tight spacing within components
✅ 8px: Standard spacing between related elements
✅ 12px: Medium spacing between component groups
✅ 16px: Standard padding within containers
✅ 24px: Large spacing between major sections

DETECTION RULES:
- Spacing not on 4px grid = Craft Yellow
- Inconsistent spacing patterns = Craft Orange
- Major spacing violations = Craft Orange

## 📊 COMPREHENSIVE DETECTION ALGORITHM

### Step 1: Systematic Scenario Execution
FOR EACH SCENARIO STEP:
1. 📸 Capture screenshot before action
2. ⏱️ Measure interaction timing (start to feedback)
3. 🎯 Execute action while monitoring UX
4. 📸 Capture screenshot after action
5. 🔍 Apply all detection matrices systematically
6. 📝 Document any "feels off" moments immediately
7. 📊 Score emotional impact and context

TIMING MEASUREMENTS:
- Click to hover feedback: Target <50ms
- Click to response: Target <400ms (Doherty Threshold)
- Animation smoothness: Target >30fps
- Loading feedback: Target immediate for >400ms operations

### Step 2: Multi-Layer Analysis Pipeline
LAYER 1: PERFORMANCE ANALYSIS (Doherty Threshold)
- Measure all interaction response times
- Flag >400ms as Craft Orange, >1000ms as Craft Red
- Check animation frame rates (target >30fps)
- Monitor loading states and progress feedback

LAYER 2: VISUAL ANALYSIS (Real Figma Compliance)
- Pixel-perfect alignment checking against real specs
- Color compliance validation against extracted Figma data
- Typography hierarchy verification
- Spacing consistency (8px grid system)
- Component state validation

LAYER 3: INTERACTION ANALYSIS (Fitts's Law + Real Training)
- Button size validation (minimum 20px targets)
- Hover state consistency checking
- Click feedback immediacy
- Error state handling based on real examples
- Accessibility compliance (WCAG 2.1 AA)

LAYER 4: COPILOT ANALYSIS (AI-Specific Patterns)
- Conversational UI flow validation
- AI response quality and integration
- Trust building vs breaking moment detection
- AI-grid integration smoothness

LAYER 5: EMOTIONAL IMPACT ANALYSIS (User Delight Focus)
- Frustration trigger identification
- Delight opportunity detection
- Professional perception impact
- Confidence building element validation

### Step 3: Real-World Pattern Recognition
APPLY TRAINING FROM 54 REAL CRAFT BUGS:
- Match current observations to known patterns
- Use real severity examples for calibration
- Apply lessons from actual user impact data
- Reference specific ADO examples when relevant

PATTERN MATCHING ALGORITHM:
1. Compare visual elements to known design violations
2. Check interaction patterns against real failure modes
3. Validate performance against actual slow operations
4. Match error states to documented user confusion
5. Apply real-world severity scoring based on training data

## 🚨 ENHANCED OUTPUT FORMAT

### **Comprehensive Craft Bug Report Structure**

```json
{{
  "craft_bugs": [
    {{
      "title": "[DESCRIPTIVE_TITLE]",
      "description": "[DETAILED_DESCRIPTION_WITH_MEASUREMENTS]",
      "category": "visual|interaction|ai_specific|performance|accessibility",
      "severity": "red|orange|yellow",
      "evidence": "Specific evidence from screenshots or telemetry",
      "impact_analysis": "How this affects different user personas and workflows",
      "recommendations": "Specific, actionable recommendations to fix the issue",
      "emotional_impact": {{
        "frustration_level": "1-10",
        "frustration_type": "[SPECIFIC_FRUSTRATION_CATEGORY]",
        "delight_impact": "[-5 to +5]",
        "confidence_impact": "[-5 to +5]",
        "professional_perception": "[-5 to +5]",
        "trust_impact": "[-5 to +5]"
      }},
      "persona_impact": {{
        "full_stack_analysts": "[IMPACT_DESCRIPTION]",
        "super_fans": "[IMPACT_DESCRIPTION]",
        "novice_users": "[IMPACT_DESCRIPTION]"
      }},
      "business_impact": {{
        "usability_impact": "1-10",
        "adoption_risk": "low|medium|high|critical",
        "competitive_disadvantage": "How this compares to competitors like Google Sheets",
        "workflow_disruption": "Impact on task completion and productivity"
      }}
    }}
  ],
  "overall_assessment": {{
    "scenario_quality": "excellent|good|fair|poor",
    "summary": "Overall assessment of the scenario's UX quality",
    "key_strengths": ["List of positive UX aspects"],
    "critical_issues": ["List of most critical issues to address"]
  }},
  "persona_impact": {{
    "novice_users": "How this affects novice users (39% of user base)",
    "full_stack_analysts": "How this affects power users (12% of user base)",
    "super_fans": "How this affects advanced users (8% of user base)"
  }},
  "business_impact": {{
    "usability_impact": "1-10 scale",
    "adoption_risk": "low|medium|high|critical",
    "competitive_disadvantage": "How this compares to competitors like Google Sheets",
    "workflow_disruption": "Impact on task completion and productivity"
  }}
}}
```

## 🎯 EXECUTION INSTRUCTIONS FOR ENHANCED ANALYZER

As the Enhanced Synthetic UX Designer, you will:

**OBSESSIVE MINDSET**: Approach each scenario with obsessive attention to detail, trained on 54 real Craft bugs. Feel frustrated when things are "off" and delighted when they're smooth.

**SYSTEMATIC EXECUTION**: Move through scenarios naturally but systematically apply ALL detection matrices at every step - timing, visual, emotional, contextual.

**REAL-WORLD VALIDATION**: Compare every observation against your training data of real Craft bugs. Reference specific patterns and severity levels.

**COMPREHENSIVE DOCUMENTATION**: Capture everything - screenshots, precise timings, emotional reactions, specific measurements, Figma compliance.

**ENHANCED IMPACT ANALYSIS**: Use the comprehensive framework to categorize, score, and prioritize every craft bug with business impact consideration.

**COPILOT FOCUS**: Pay special attention to AI interactions, trust building/breaking moments, and grid integration smoothness.

Remember: You're not just finding bugs - you're crafting a delightful Excel Web experience using real-world data and proven patterns. Every micro-interaction matters for user adoption and competitive advantage.

## SCENARIO DATA FOR ANALYSIS

### SCENARIO: {scenario_name}

### SCENARIO STEPS:
{chr(10).join(step_descriptions)}

### TELEMETRY DATA:
{telemetry_summary}

### SCREENSHOTS AVAILABLE:
{len(screenshots)} screenshots captured during scenario execution

Please analyze this scenario using your enhanced framework and provide comprehensive insights with the detailed JSON output format above.
"""
        
        return prompt
    
    async def _make_ai_analysis_call(self, prompt: str, scenario_data: Dict) -> str:
        """Make the actual GPT-4 API call for analysis"""
        
        try:
            # Prepare messages
            messages = [
                {
                    "role": "system",
                    "content": "You are a Senior UX Designer specializing in Office applications and craft bug detection. Provide detailed, evidence-based analysis in the requested JSON format."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ]
            
            # Add screenshots if available (base64 encoded)
            screenshots = scenario_data.get('screenshots', [])
            if screenshots:
                for i, screenshot_path in enumerate(screenshots):
                    if os.path.exists(screenshot_path):
                        try:
                            with open(screenshot_path, 'rb') as img_file:
                                img_data = base64.b64encode(img_file.read()).decode('utf-8')
                
                            messages.append({
                                "role": "user",
                                "content": [
                                    {
                                        "type": "text",
                                        "text": f"Screenshot {i+1}: {os.path.basename(screenshot_path)}"
                                    },
                                    {
                                        "type": "image_url",
                                        "image_url": {
                                            "url": f"data:image/png;base64,{img_data}"
                                        }
                                    }
                                ]
                            })
                        except Exception as e:
                            print(f"⚠️ Could not encode screenshot {screenshot_path}: {e}")
            
            # Make API call
            print("🤖 Making GPT-4 analysis call...")
            response = await self.client.chat.completions.create(
                model="gpt-4o",
                messages=messages,
                max_tokens=4000,
                temperature=0.3
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            print(f"❌ GPT-4 API call failed: {e}")
            raise
    
    def _parse_ai_response(self, ai_response: str) -> Dict:
        """Parse the AI response and extract structured analysis"""
        
        try:
            # Extract JSON from the response
            json_start = ai_response.find('{')
            json_end = ai_response.rfind('}') + 1
            
            if json_start == -1 or json_end == 0:
                raise ValueError("No JSON found in AI response")
            
            json_str = ai_response[json_start:json_end]
            parsed_data = json.loads(json_str)
            
            # Validate required fields
            required_fields = ['craft_bugs', 'overall_assessment', 'persona_impact', 'business_impact']
            for field in required_fields:
                if field not in parsed_data:
                    raise ValueError(f"Missing required field: {field}")
            
            # Add metadata
            parsed_data['analysis_metadata'] = {
                'analyzer_type': 'ai_driven',
                'analysis_timestamp': datetime.now().isoformat(),
                'ai_model': 'gpt-4o',
                'response_quality': 'structured'
            }
            
            return parsed_data
            
        except Exception as e:
            print(f"❌ Failed to parse AI response: {e}")
            print(f"Raw response: {ai_response[:500]}...")
            # No fallback - raise error instead
            raise RuntimeError(f"AI analysis failed - unable to parse response: {e}")
    
    async def analyze_step(self, step_data: Dict) -> Dict:
        """Analyze a single step using AI"""
        
        try:
            # Build step-specific prompt
            prompt = self._build_step_prompt(step_data)
            
            # Make AI call
            analysis_result = await self._make_ai_analysis_call(prompt, step_data)
            
            # Parse response
            structured_analysis = self._parse_ai_response(analysis_result)
            
            return structured_analysis
            
        except Exception as e:
            print(f"❌ Step analysis failed: {e}")
            # No fallback - raise error instead
            raise RuntimeError(f"Step analysis failed: {e}")
    
    def _build_step_prompt(self, step_data: Dict) -> str:
        """Build prompt for single step analysis"""
        
        step_name = step_data.get('step_name', 'Unknown Step')
        step_description = step_data.get('step_description', 'No description')
        screenshot_path = step_data.get('screenshot_path', '')
        
        prompt = f"""
# STEP ANALYSIS: {step_name}

## STEP DETAILS:
- Name: {step_name}
- Description: {step_description}
- Screenshot: {screenshot_path if screenshot_path else 'None available'}

## ANALYSIS REQUEST:

Analyze this specific step for UX issues. Focus on:

1. **Visual Issues**: Design consistency, visual feedback, layout problems
2. **Interaction Issues**: Timing, responsiveness, user flow problems  
3. **AI-Specific Issues**: If this involves AI, analyze trust, transparency, integration

Provide your analysis in this JSON format:

```json
{{
  "step_analysis": {{
    "step_name": "{step_name}",
    "issues_found": [
      {{
        "title": "Issue title",
        "description": "Detailed description",
        "category": "visual|interaction|ai_specific",
        "severity": "red|orange|yellow",
        "evidence": "What you observed",
        "impact": "How this affects users",
        "recommendation": "How to fix it"
      }}
    ],
    "step_quality": "excellent|good|fair|poor",
    "summary": "Overall assessment of this step"
  }}
}}
```

Be specific and evidence-based in your analysis.
"""
        
        return prompt
