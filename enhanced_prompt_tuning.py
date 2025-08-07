#!/usr/bin/env python3
"""
Enhanced UX Prompt Tuning System
Advanced AI prompt optimization for Office application UX analysis
"""

import os
import json
import re
from typing import Dict, List, Any, Optional
from datetime import datetime
from dataclasses import dataclass

@dataclass
class PromptTemplate:
    """Structure for AI prompt templates"""
    name: str
    app_type: str
    scenario_type: str
    template: str
    parameters: Dict[str, Any]
    effectiveness_score: float = 0.0

@dataclass
class AnalysisValidation:
    """Structure for analysis validation results"""
    is_valid: bool
    quality_score: float
    issues_found: List[str]
    recommendations: List[str]

class EnhancedUXPromptEngine:
    """Advanced prompt engineering for UX analysis"""
    
    def __init__(self):
        self.prompt_templates = self._initialize_prompt_templates()
        self.validation_criteria = self._initialize_validation_criteria()
        
    def _initialize_prompt_templates(self) -> Dict[str, PromptTemplate]:
        """Initialize comprehensive prompt templates for each application"""
        
        templates = {}
        
        # Word Application Prompts
        templates["word_navigation"] = PromptTemplate(
            name="Word Navigation Analysis",
            app_type="word",
            scenario_type="navigation",
            template="""You are a UX expert analyzing Microsoft Word's navigation features. 

SCENARIO CONTEXT:
- Application: Microsoft Word
- Focus Area: Navigation and Review panels
- User Scenario: {scenario_description}

ANALYSIS FRAMEWORK:
1. ACCESSIBILITY ASSESSMENT:
   - Keyboard navigation efficiency
   - Screen reader compatibility
   - Color contrast and visual indicators
   - Focus management and tab order

2. USABILITY EVALUATION:
   - Cognitive load and mental models
   - Task completion efficiency
   - Error prevention and recovery
   - User control and freedom

3. INTERFACE DESIGN:
   - Visual hierarchy and information architecture
   - Consistency with Office design language
   - Responsive behavior and adaptability
   - Integration with overall workflow

SPECIFIC WORD FEATURES TO ANALYZE:
- Review panel track changes visibility
- Comment threading and organization
- Navigation pane structure and search
- Ribbon organization and discoverability
- Document sharing and collaboration features

Provide detailed UX analysis with specific, actionable recommendations.""",
            parameters={"scenario_description": ""}
        )
        
        templates["word_collaboration"] = PromptTemplate(
            name="Word Collaboration Analysis",
            app_type="word",
            scenario_type="collaboration",
            template="""You are a UX expert specializing in collaborative software experiences.

ANALYSIS TARGET: Microsoft Word collaboration features
SCENARIO: {scenario_description}

COLLABORATION UX DIMENSIONS:
1. AWARENESS & PRESENCE:
   - Real-time user presence indicators
   - Activity notifications and updates
   - Change attribution and authorship clarity

2. COORDINATION MECHANISMS:
   - Comment and suggestion workflows
   - Version control and conflict resolution
   - Permission management and access controls

3. COMMUNICATION INTEGRATION:
   - In-context discussion capabilities
   - External communication tool integration
   - Notification timing and relevance

EVALUATE FOR:
- Multi-user workflow efficiency
- Conflict resolution patterns
- Trust and transparency in changes
- Learning curve for collaboration features

Identify specific pain points and propose UX improvements.""",
            parameters={"scenario_description": ""}
        )
        
        # Excel Application Prompts
        templates["excel_formula"] = PromptTemplate(
            name="Excel Formula Interface Analysis",
            app_type="excel",
            scenario_type="formula",
            template="""You are a UX expert analyzing data manipulation interfaces in Excel.

TARGET: Excel formula bar and calculation features
SCENARIO: {scenario_description}

ANALYSIS FRAMEWORK:
1. FORMULA AUTHORING EXPERIENCE:
   - Formula bar usability and feedback
   - Function discovery and auto-completion
   - Error messaging and debugging support
   - Formula validation and preview

2. DATA VISUALIZATION:
   - Cell highlighting and dependencies
   - Result preview and calculation flow
   - Error indication and resolution paths
   - Performance feedback for complex formulas

3. COGNITIVE SUPPORT:
   - Mental model alignment with spreadsheet concepts
   - Progressive disclosure of advanced features
   - Context-aware help and guidance
   - Undo/redo clarity for formula changes

EXCEL-SPECIFIC CONSIDERATIONS:
- Cross-sheet reference management
- Array formula handling
- Function library organization
- Cell formatting interaction with formulas

Provide specific recommendations for improving formula experience.""",
            parameters={"scenario_description": ""}
        )
        
        templates["excel_visualization"] = PromptTemplate(
            name="Excel Data Visualization Analysis",
            app_type="excel",
            scenario_type="visualization",
            template="""You are a UX expert focused on data visualization and presentation.

TARGET: Excel sheet management and formatting features
SCENARIO: {scenario_description}

VISUALIZATION UX ASSESSMENT:
1. DATA PRESENTATION:
   - Sheet tab organization and navigation
   - Cell formatting consistency and hierarchy
   - Color usage and accessibility compliance
   - Print and export layout considerations

2. INTERACTION PATTERNS:
   - Multi-sheet workflow efficiency
   - Copy/paste behavior across sheets
   - Selection and range management
   - Zoom and view customization

3. INFORMATION ARCHITECTURE:
   - Data organization and grouping
   - Header and label clarity
   - Filtering and sorting accessibility
   - Cross-sheet data relationship clarity

EVALUATE FOR:
- Visual noise and information density
- Responsive design for different screen sizes
- Accessibility for users with visual impairments
- Consistency with Excel's mental model

Recommend specific improvements for data presentation.""",
            parameters={"scenario_description": ""}
        )
        
        # PowerPoint Application Prompts
        templates["powerpoint_creation"] = PromptTemplate(
            name="PowerPoint Creation Workflow Analysis",
            app_type="powerpoint",
            scenario_type="creation",
            template="""You are a UX expert analyzing presentation creation workflows.

TARGET: PowerPoint slide creation and editing features
SCENARIO: {scenario_description}

CREATION WORKFLOW ANALYSIS:
1. CONTENT AUTHORING:
   - Slide layout selection and customization
   - Text editing and formatting efficiency
   - Media insertion and positioning
   - Template application and modification

2. DESIGN SUPPORT:
   - Design suggestion intelligence
   - Consistency checking and enforcement
   - Brand guideline integration
   - Visual hierarchy guidance

3. PRODUCTIVITY FEATURES:
   - Slide duplication and reordering
   - Bulk editing capabilities
   - Content library and reuse
   - Collaboration on design decisions

POWERPOINT-SPECIFIC FOCUS:
- Animation timeline and preview
- Transition selection and timing
- Speaker notes integration
- Slide sorter view efficiency

Provide actionable recommendations for improving creation experience.""",
            parameters={"scenario_description": ""}
        )
        
        templates["powerpoint_presentation"] = PromptTemplate(
            name="PowerPoint Presentation Delivery Analysis",
            app_type="powerpoint",
            scenario_type="presentation",
            template="""You are a UX expert specializing in presentation delivery experiences.

TARGET: PowerPoint presenter view and delivery features
SCENARIO: {scenario_description}

PRESENTATION DELIVERY UX:
1. PRESENTER INTERFACE:
   - Presenter view layout and information density
   - Note display and readability
   - Timer and progress indicators
   - Next slide preview utility

2. AUDIENCE INTERACTION:
   - Slide navigation responsiveness
   - Pointer and annotation tools
   - Screen sharing optimization
   - Remote presentation features

3. TECHNICAL RELIABILITY:
   - Display configuration handling
   - Performance during transitions
   - Recovery from technical issues
   - Backup and contingency options

DELIVERY-SPECIFIC CONSIDERATIONS:
- Stress and pressure context of use
- Multi-monitor setup optimization
- Accessibility for presenters with disabilities
- Integration with video conferencing tools

Recommend improvements for confident, smooth presentation delivery.""",
            parameters={"scenario_description": ""}
        )
        
        return templates
    
    def _initialize_validation_criteria(self) -> Dict[str, Any]:
        """Initialize validation criteria for analysis quality"""
        
        return {
            "required_elements": [
                "specific UX issues identified",
                "actionable recommendations",
                "accessibility considerations",
                "usability principles applied"
            ],
            "quality_indicators": [
                "concrete examples provided",
                "user impact assessment",
                "implementation feasibility",
                "measurable success criteria"
            ],
            "depth_requirements": {
                "minimum_word_count": 200,
                "issue_categories": 3,
                "recommendation_count": 5
            }
        }
    
    def get_analysis_prompt(self, app_type: str, scenario_description: str, scenario_type: str = "general") -> str:
        """Get optimized prompt for specific application and scenario"""
        
        # Find best matching template
        template_key = f"{app_type}_{scenario_type}"
        
        if template_key not in self.prompt_templates:
            # Fall back to general template for the app
            general_templates = {k: v for k, v in self.prompt_templates.items() if k.startswith(app_type)}
            if general_templates:
                template = next(iter(general_templates.values()))
            else:
                template = self._get_fallback_template(app_type)
        else:
            template = self.prompt_templates[template_key]
        
        # Fill in scenario description
        prompt = template.template.format(scenario_description=scenario_description)
        
        # Add context-specific enhancements
        prompt = self._enhance_prompt_with_context(prompt, app_type, scenario_type)
        
        return prompt
    
    def _get_fallback_template(self, app_type: str) -> PromptTemplate:
        """Get fallback template for unknown app types"""
        
        return PromptTemplate(
            name=f"General {app_type.title()} Analysis",
            app_type=app_type,
            scenario_type="general",
            template="""You are a UX expert analyzing {app_type} application features.

SCENARIO: {scenario_description}

ANALYSIS FRAMEWORK:
1. USABILITY ASSESSMENT:
   - Task completion efficiency
   - Error prevention and recovery
   - User control and freedom
   - Consistency and standards

2. ACCESSIBILITY EVALUATION:
   - Keyboard navigation
   - Screen reader compatibility
   - Visual accessibility
   - Motor accessibility

3. USER EXPERIENCE:
   - Satisfaction and engagement
   - Learning curve and discoverability
   - Performance and responsiveness
   - Integration with user workflows

Provide detailed analysis with specific, actionable recommendations.""".format(app_type=app_type.title()),
            parameters={"scenario_description": ""}
        )
    
    def _enhance_prompt_with_context(self, prompt: str, app_type: str, scenario_type: str) -> str:
        """Enhance prompt with additional context and guidance"""
        
        enhancements = []
        
        # Add app-specific context
        app_contexts = {
            "word": "Focus on document authoring, collaboration, and review workflows.",
            "excel": "Emphasize data manipulation, calculation accuracy, and visualization clarity.",
            "powerpoint": "Consider presentation creation efficiency and delivery confidence."
        }
        
        if app_type in app_contexts:
            enhancements.append(f"\nAPPLICATION CONTEXT: {app_contexts[app_type]}")
        
        # Add scenario-specific guidance
        scenario_guidance = {
            "navigation": "Pay special attention to information architecture and wayfinding.",
            "collaboration": "Focus on multi-user coordination and communication clarity.",
            "creation": "Emphasize creative workflow efficiency and tool discoverability.",
            "presentation": "Consider performance anxiety and technical reliability needs."
        }
        
        if scenario_type in scenario_guidance:
            enhancements.append(f"\nSCENARIO FOCUS: {scenario_guidance[scenario_type]}")
        
        # Add output format requirements
        enhancements.append("""
OUTPUT REQUIREMENTS:
- Structure findings as specific, actionable issues
- Include severity assessment (high/medium/low)
- Provide implementation recommendations
- Consider accessibility and inclusive design
- Reference established UX principles and heuristics""")
        
        return prompt + "\n".join(enhancements)
    
    def validate_analysis_quality(self, analysis_text: str) -> AnalysisValidation:
        """Validate the quality of UX analysis output"""
        
        issues = []
        recommendations = []
        quality_score = 0.0
        
        # Check for required elements
        required_elements = self.validation_criteria["required_elements"]
        elements_found = 0
        
        for element in required_elements:
            if any(keyword in analysis_text.lower() for keyword in element.split()):
                elements_found += 1
            else:
                issues.append(f"Missing: {element}")
        
        element_score = (elements_found / len(required_elements)) * 30
        
        # Check quality indicators
        quality_indicators = self.validation_criteria["quality_indicators"]
        indicators_found = 0
        
        for indicator in quality_indicators:
            if any(keyword in analysis_text.lower() for keyword in indicator.split()):
                indicators_found += 1
        
        indicator_score = (indicators_found / len(quality_indicators)) * 30
        
        # Check depth requirements
        depth_reqs = self.validation_criteria["depth_requirements"]
        depth_score = 0
        
        # Word count check
        word_count = len(analysis_text.split())
        if word_count >= depth_reqs["minimum_word_count"]:
            depth_score += 10
        else:
            issues.append(f"Analysis too brief: {word_count} words (minimum {depth_reqs['minimum_word_count']})")
        
        # Issue categories check
        category_keywords = ["navigation", "accessibility", "usability", "visual", "performance", "workflow"]
        categories_mentioned = sum(1 for keyword in category_keywords if keyword in analysis_text.lower())
        if categories_mentioned >= depth_reqs["issue_categories"]:
            depth_score += 10
        else:
            issues.append(f"Insufficient category coverage: {categories_mentioned} categories")
        
        # Recommendation count check
        recommendation_indicators = ["recommend", "suggest", "improve", "consider", "should"]
        recommendations_count = sum(analysis_text.lower().count(indicator) for indicator in recommendation_indicators)
        if recommendations_count >= depth_reqs["recommendation_count"]:
            depth_score += 20
        else:
            issues.append(f"Insufficient recommendations: {recommendations_count} indicators")
        
        # Calculate overall quality score
        quality_score = element_score + indicator_score + depth_score
        
        # Generate recommendations for improvement
        if quality_score < 70:
            recommendations.append("Increase analysis depth and specificity")
        if element_score < 20:
            recommendations.append("Include more required UX analysis elements")
        if indicator_score < 20:
            recommendations.append("Add more specific examples and concrete recommendations")
        if depth_score < 20:
            recommendations.append("Expand analysis length and cover more UX categories")
        
        return AnalysisValidation(
            is_valid=quality_score >= 60,
            quality_score=quality_score,
            issues_found=issues,
            recommendations=recommendations
        )
    
    def optimize_prompt_based_on_feedback(self, template_name: str, analysis_result: str, quality_score: float):
        """Optimize prompt template based on analysis results and quality feedback"""
        
        if template_name in self.prompt_templates:
            template = self.prompt_templates[template_name]
            
            # Update effectiveness score
            current_score = template.effectiveness_score
            template.effectiveness_score = (current_score + quality_score) / 2 if current_score > 0 else quality_score
            
            # If quality is low, add more specific guidance
            if quality_score < 60:
                self._enhance_template_with_guidance(template_name, analysis_result)
    
    def _enhance_template_with_guidance(self, template_name: str, analysis_result: str):
        """Enhance template with additional guidance based on poor results"""
        
        template = self.prompt_templates[template_name]
        
        # Add more specific instructions
        additional_guidance = """
        
ENHANCED GUIDANCE:
- Provide at least 5 specific, actionable recommendations
- Include severity levels for each issue identified
- Reference specific UI elements and interactions
- Consider accessibility implications for all recommendations
- Suggest measurable success criteria for improvements"""
        
        template.template += additional_guidance
    
    def get_prompt_effectiveness_report(self) -> Dict[str, Any]:
        """Generate report on prompt template effectiveness"""
        
        report = {
            "generated_at": datetime.now().isoformat(),
            "total_templates": len(self.prompt_templates),
            "templates": {},
            "effectiveness_summary": {}
        }
        
        effectiveness_scores = []
        
        for name, template in self.prompt_templates.items():
            report["templates"][name] = {
                "app_type": template.app_type,
                "scenario_type": template.scenario_type,
                "effectiveness_score": template.effectiveness_score,
                "template_length": len(template.template)
            }
            
            if template.effectiveness_score > 0:
                effectiveness_scores.append(template.effectiveness_score)
        
        if effectiveness_scores:
            report["effectiveness_summary"] = {
                "average_score": sum(effectiveness_scores) / len(effectiveness_scores),
                "highest_score": max(effectiveness_scores),
                "lowest_score": min(effectiveness_scores),
                "total_evaluated": len(effectiveness_scores)
            }
        
        return report
    
    def save_prompt_templates(self, filename: str = "enhanced_prompt_templates.json"):
        """Save prompt templates to file"""
        
        templates_data = {}
        for name, template in self.prompt_templates.items():
            templates_data[name] = {
                "name": template.name,
                "app_type": template.app_type,
                "scenario_type": template.scenario_type,
                "template": template.template,
                "parameters": template.parameters,
                "effectiveness_score": template.effectiveness_score
            }
        
        try:
            with open(filename, 'w') as f:
                json.dump(templates_data, f, indent=2)
            print(f"💾 Prompt templates saved to: {filename}")
        except Exception as e:
            print(f"❌ Failed to save templates: {e}")

def main():
    """Main execution for prompt tuning demonstration"""
    
    print("🤖 Enhanced UX Prompt Tuning System - Phase 2.4")
    print("=" * 50)
    
    # Initialize prompt engine
    engine = EnhancedUXPromptEngine()
    
    # Test prompt generation for each application
    test_scenarios = [
        ("word", "Review panel navigation and track changes visibility", "navigation"),
        ("excel", "Formula bar usage and calculation workflow", "formula"),
        ("powerpoint", "Slide creation and presenter view setup", "creation")
    ]
    
    print("📝 Testing Enhanced Prompt Generation:")
    
    for app_type, scenario_desc, scenario_type in test_scenarios:
        print(f"\n🎯 {app_type.title()} - {scenario_type.title()} Scenario:")
        prompt = engine.get_analysis_prompt(app_type, scenario_desc, scenario_type)
        print(f"   ✅ Generated {len(prompt)} character prompt")
        print(f"   📊 Key elements: UX framework, {app_type} specifics, output requirements")
    
    # Test analysis validation
    print(f"\n🔍 Testing Analysis Validation:")
    
    sample_analysis = """
    The navigation panel in Word shows good visual hierarchy but has accessibility issues. 
    The track changes feature lacks clear indicators for different types of edits.
    Recommendations: 1) Improve color contrast 2) Add keyboard shortcuts 3) Enhance screen reader support
    4) Simplify the review workflow 5) Add user preference settings.
    Performance is adequate but could be optimized for large documents.
    """
    
    validation = engine.validate_analysis_quality(sample_analysis)
    print(f"   ✅ Validation completed - Quality Score: {validation.quality_score:.1f}/100")
    print(f"   📈 Analysis Valid: {validation.is_valid}")
    print(f"   📋 Issues Found: {len(validation.issues_found)}")
    print(f"   💡 Recommendations: {len(validation.recommendations)}")
    
    # Generate effectiveness report
    print(f"\n📊 Prompt Template Effectiveness Report:")
    report = engine.get_prompt_effectiveness_report()
    print(f"   📝 Total Templates: {report['total_templates']}")
    print(f"   🎯 Application Coverage: Word, Excel, PowerPoint")
    print(f"   🔧 Scenario Types: Navigation, Collaboration, Formula, Creation, Presentation")
    
    # Save templates
    engine.save_prompt_templates()
    
    print(f"\n✅ Enhanced UX Prompt Tuning System fully operational!")

if __name__ == "__main__":
    main()
