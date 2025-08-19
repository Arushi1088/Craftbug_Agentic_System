# 🎨 UX Designer Prompt Engineering Framework
## Enhanced Craft Bug Detection System

---

## 📋 Table of Contents
1. [UX Designer Thinking Process](#ux-designer-thinking-process)
2. [Craft Bug Definition & Categories](#craft-bug-definition--categories)
3. [Surface Level Analysis (L1/L2/L3)](#surface-level-analysis-l1l2l3)
4. [Success & Failure Criteria](#success--failure-criteria)
5. [Excel User Personas](#excel-user-personas)
6. [Enhanced Prompt Engineering Strategy](#enhanced-prompt-engineering-strategy)
7. [Integration Resources](#integration-resources)
8. [Implementation Roadmap](#implementation-roadmap)

---

## 🎭 UX Designer Thinking Process

### Core Analysis Framework
As a UX Designer, I follow this systematic approach:

1. **Scenario Selection**: Pick high-value scenarios that users use most frequently
2. **Step-by-Step Execution**: Perform each step carefully to ensure scenario completion
3. **Surface Level Analysis**: Analyze L1, L2, L3 surfaces for interactions
4. **Element-by-Element Review**: Check every component on screen (icons, colors, text, buttons)
5. **Craft Bug Identification**: Mark anything that feels unnatural or "off"
6. **Documentation**: Log issues with screenshots, videos, and detailed descriptions
7. **Triage & Prioritization**: Categorize bugs by impact and fix complexity

### What Makes Something "Off" (Craft Bugs)
- **Visual Inconsistencies**: Different rule divider weights, misaligned icons
- **Animation Issues**: Non-smooth scroll animations, jarring transitions
- **Interaction Problems**: Buttons appearing disabled, overlapping elements
- **Labeling Issues**: "Got it" vs "Done" - non-intuitive text
- **Performance UX**: Long loaders causing confusion about system state
- **Accessibility Problems**: Missing tooltips, unclear element purposes

---

## 🐛 Craft Bug Definition & Categories

### What is a Craft Bug?
> **Craft Bug (noun)**: An unintended issue that affects the usability, perception, and polish of the product. Examples: missing icons, unsuitable strings, wrong button states, etc.

### Craft Bug Categories

#### 🔴 **RED (P1 - Critical) - Craft Red**
- **Severity**: Critical usability issues
- **Impact**: Broken workflows, hindering task completion
- **Visibility**: Noticeable by everyone, across L1 surfaces
- **Examples**: 
  - Glaring inconsistencies
  - Glitches and flashes
  - Critical workflow breakdowns

#### 🟠 **ORANGE (P1 - High) - Craft Orange**
- **Severity**: Usability issues
- **Impact**: Broken workflows across secondary workflows
- **Visibility**: Seen across L2 surfaces
- **Examples**:
  - Noticeable craft issues
  - UI inconsistencies
  - Misleading text

#### 🟡 **YELLOW (P2 - Medium) - Craft Yellow**
- **Severity**: Subtle inconsistencies
- **Impact**: Design mismatches, alignment issues
- **Visibility**: Noticed by some on L3 surfaces
- **Examples**:
  - Stray pixels
  - Alignment issues
  - Design mismatches

### Craft Bug Types

#### Visual Craft Bugs
- Icon alignment issues
- Color inconsistencies
- Stray pixels
- Visual harmony problems
- Pixel alignment issues

#### Interaction Craft Bugs
- Button state problems
- Hover behavior issues
- Tooltip problems
- Element overlapping
- Disabled state confusion

#### Performance Craft Bugs
- Non-smooth animations
- Long loading states
- Frame rate issues
- Abrupt layout shifts

#### Usability Craft Bugs
- Misleading labels
- Broken workflows
- Accessibility issues
- Non-actionable strings

#### Fluent Design Compliance
- Theme inconsistencies
- Corner radius mismatches
- Z-ordering problems
- Background acrylic/transparency issues

---

## 🎯 Surface Level Analysis (L1/L2/L3)

### Level 1 (L1) - Primary Surfaces
- **Definition**: Main UI elements, primary interaction surfaces
- **Examples**: Excel ribbon, main toolbar, primary navigation, grid canvas
- **Focus**: Critical workflow elements, high-visibility components
- **Design Specs**: Background #ffffff, elevation 0px, border 1px solid #e1dfdd, shadow none

### Level 2 (L2) - Secondary Surfaces
- **Definition**: Secondary UI elements, panels, dialogs
- **Examples**: Right-side panels, dialog boxes, secondary toolbars, Copilot panel
- **Focus**: Supporting workflow elements, contextual interfaces
- **Design Specs**: Background #ffffff, elevation 4px, shadow 0 2px 4px rgba(0,0,0,0.1)
- **Components**: Dialog (8px radius, 24px padding, max-width 600px), Panel (4px radius, 16px padding, width 320px)

### Level 3 (L3) - Tertiary Surfaces
- **Definition**: Detailed UI elements, dropdowns, tooltips
- **Examples**: Dropdown menus, tooltips, micro-interactions, context menus
- **Focus**: Fine details, precision interactions
- **Design Specs**: Background #ffffff, elevation 8px, shadow 0 4px 8px rgba(0,0,0,0.1)
- **Components**: Tooltip (4px radius, 8px 12px padding, max-width 300px), Dropdown (4px radius, 4px 0 padding, min-width 200px)

---

## 📊 Success & Failure Criteria

### Success Metrics

#### Detection Accuracy
- **Craft Bug Detection Rate**: 90%+ of actual UX issues identified
- **False Positive Rate**: <10% irrelevant issues flagged
- **Severity Classification Accuracy**: Correctly categorizing Red/Orange/Yellow
- **Surface Level Coverage**: L1/L2/L3 surface analysis completeness

#### UX Quality Metrics
- **Fluent Design Compliance Score**: % adherence to design system
- **Interaction Smoothness**: Animation frame rate, transition quality
- **Cognitive Load Assessment**: Mental effort required per task
- **Accessibility Compliance**: WCAG guidelines adherence

#### Business Impact Metrics
- **User Delight Score**: Based on smooth interactions and visual polish
- **Task Completion Efficiency**: Time and steps to complete scenarios
- **Error Recovery Rate**: How easily users can recover from mistakes
- **Learning Curve Assessment**: Intuitiveness for different user types

#### Technical Performance
- **Response Time Analysis**: <400ms for Doherty Threshold compliance
- **Visual Consistency Score**: Color, spacing, typography uniformity
- **Component Reusability**: Design system component usage
- **Cross-Surface Harmony**: Consistency across L1/L2/L3 surfaces

### Failure Criteria
- **Missing Obvious Issues**: Failing to catch glaring UX problems
- **Over-Engineering**: Flagging minor issues as critical
- **Generic Feedback**: Not specific to Excel Web context
- **Poor Prioritization**: Not ranking issues by user impact
- **Lack of Actionability**: Vague or unhelpful recommendations

---

## 👥 Excel User Personas

### 🎯 Target Users (33% - Advanced + Super Fans)

#### 1. Full Stack Analysts (12%)
- **Analytical Need**: Strongest
- **Tools**: Excel + Relational Databases + R/Python + Tableau
- **Behavior**: "Do everything" power users, complex data analysis
- **Craft Bug Sensitivity**: High - they notice performance and workflow issues
- **Pain Points**: Slow interactions, broken analytics workflows, inconsistent data visualization

#### 2. Super Fans (8%)
- **Analytical Need**: Highest
- **Tools**: Excel + Full breadth of capabilities
- **Behavior**: Highly engaged, leverage maximum Excel features
- **Craft Bug Sensitivity**: Very High - they push boundaries and notice edge cases
- **Pain Points**: Advanced feature bugs, workflow interruptions, visual inconsistencies

#### 3. Advanced Users (25%)
- **Analytical Need**: High
- **Tools**: Excel + Tables + PivotTables + Formulas + Analysis ToolPak
- **Behavior**: Use analytics features but not at maximum efficiency
- **Craft Bug Sensitivity**: High - they rely on Excel for work value
- **Pain Points**: Inconsistent interactions, broken formulas, poor performance

### 🎯 Secondary Users (67% - Others)

#### 4. Intermediate Users (28%)
- **Analytical Need**: Medium
- **Tools**: Excel + Basic Tables + PivotTables
- **Behavior**: Grasped fundamentals, use some advanced features
- **Craft Bug Sensitivity**: Medium - they notice obvious issues
- **Pain Points**: Confusing interfaces, broken basic workflows

#### 5. Novice Users (39% - Readers + Info Gatherers)
- **Analytical Need**: Low
- **Tools**: Primarily Excel for consumption and basic tasks
- **Behavior**: Consume workbooks, basic data entry, intimidated by complexity
- **Craft Bug Sensitivity**: Low - but critical for adoption
- **Pain Points**: Overwhelming interfaces, unclear navigation, broken basic functions

---

## 🚀 Enhanced Prompt Engineering Strategy

### Core UX Designer Persona
```
"You are a Senior UX Designer with 10+ years of experience analyzing Microsoft Office applications. 
You think in terms of user journeys, cognitive load, and emotional responses. You notice everything 
that feels 'off' - from pixel misalignments to broken workflows. You understand Fluent Design 
principles deeply and can spot inconsistencies instantly."
```

### Analysis Framework
```
"For each interaction, analyze:
1. L1/L2/L3 surface hierarchy and consistency
2. Visual craft (alignment, colors, spacing, typography)
3. Interaction craft (smoothness, feedback, states)
4. Performance craft (speed, animations, loading)
5. Usability craft (clarity, accessibility, workflow)
6. Fluent Design compliance (themes, components, patterns)"
```

### Craft Bug Classification
```
"Classify each issue as:
- RED (P1): Critical usability, broken workflows, glaring inconsistencies
- ORANGE (P1): Usability issues, secondary workflow problems  
- YELLOW (P2): Subtle inconsistencies, alignment issues, design mismatches"
```

### UX Laws Integration
Apply these 21 UX laws systematically:
- **Aesthetic-Usability Effect**: Users perceive aesthetically pleasing design as more usable
- **Choice Overload**: People get overwhelmed with too many options
- **Cognitive Load**: Amount of mental resources needed to understand interface
- **Doherty Threshold**: Productivity soars when interaction pace is <400ms
- **Fitts's Law**: Time to acquire target is function of distance and size
- **Hick's Law**: Decision time increases with number and complexity of choices
- **Jakob's Law**: Users prefer your site to work like other sites they know
- **Law of Proximity**: Objects near each other tend to be grouped together
- **Miller's Law**: Average person can only keep 7±2 items in working memory
- **Peak-End Rule**: People judge experience by peak and end moments
- **Tesler's Law**: For any system, there's complexity that cannot be reduced
- **Von Restorff Effect**: Items that differ from the rest are most remembered
- **Zeigarnik Effect**: People remember uncompleted tasks better than completed ones

---

## 🔗 Integration Resources

### **Figma Design System Integration**
- **Excel Web Fluent 2**: [Figma Link](https://www.figma.com/design/WIhOBHqKHheLMqZMJimsgF/Excel-Web-Fluent-2?m=auto&node-id=2054-46829&t=FlbG02SE3oLVooB2-1)
- **Office Icons**: [Figma Link](https://www.figma.com/design/llkQlCJaz2PfmpgpcEsuVc/Office-Icons?m=auto&node-id=0-1&t=ihs4JguInELPnU7Y-1)
- **Excel Copilot UI Kit**: [Figma Link](https://www.figma.com/design/75lT8qsOZiWMLG89cQmBtq/Excel-Copilot-UI-kit?node-id=0-1&t=Ljr9wW3VopiaDgQA-1)
- **Excel Win32 Ribbon**: [Figma Link](https://www.figma.com/design/xOiHWqiGKpFnbkMsq9CLfB/Excel-Win32-Ribbon?node-id=2054-46829&t=Kw37AwiqUUklEZlV-1)
- **Excel Fluent Surfaces**: [Figma Link](https://www.figma.com/design/sh8HH85iScfeMv5FjRivVS/Excel-Fluent-Surfaces?m=auto&node-id=174-2&t=fUH5Wl5pzTlOWzvT-1)
- **Office Win32 Variables**: [Figma Link](https://www.figma.com/design/3WKpAYNqciKghBlF9vPuaP/Office-Win32-Variables?node-id=13-287&t=J4qztYnrpEcReDnF-1)

**Implementation Status:**
- ✅ **Figma Integration Module Created**: `figma_integration.py`
- ✅ **Design Specifications Extracted**: All 6 design systems
- ✅ **Design Compliance Checking**: Color, typography, spacing validation
- ✅ **Surface Level Analysis**: L1/L2/L3 surface specifications
- ✅ **Ribbon Interface**: Win32 ribbon component specifications
- ✅ **Theme Variables**: Light/dark theme support
- 🔄 **API Integration**: Ready for Figma REST API with access token

**Design System Coverage:**
- **Excel Web Fluent 2**: 22 colors, 12 typography, 7 spacing, 5 border radius, 4 shadows
- **Office Icons**: 6 sizes, 6 color variants
- **Excel Copilot**: Chat panel, message bubbles, suggestion chips
- **Excel Win32 Ribbon**: Tab structure, groups, buttons, icons
- **Excel Fluent Surfaces**: L1/L2/L3 surface levels, components (dialog, panel, tooltip, dropdown)
- **Office Win32 Variables**: Theme variables, design tokens, light/dark themes

### **ADO Integration**
- **Dashboard**: [ADO Dashboard](https://office.visualstudio.com/OC/_dashboards/dashboard/2fe1c91c-5952-4e32-ad56-be87f9055980)
- **Bug Collection**: Azure DevOps CLI and REST API integration
- **PAT Authentication**: Personal Access Token for API access

**Implementation Status:**
- ✅ **Enhanced ADO Integration**: `enhanced_ado_integration.py` created
- ✅ **Craft Bug Examples**: 10 comprehensive Craft bug examples with detailed analysis
- ✅ **Pattern Analysis**: Bug type distribution, surface level focus, common keywords
- ✅ **Prompt Engineering Insights**: Detection priorities and enhancement recommendations
- 🔄 **Real-time Fetching**: Ready for PAT-based API access to live ADO data

**Craft Bug Categories Identified:**
- **Design System Violation**: Color mismatches, typography inconsistencies, border radius issues
- **Spacing Inconsistency**: Inconsistent padding, margins, icon spacing
- **Visual Inconsistency**: Alignment issues, visual rhythm problems
- **Performance UX**: Animation stutters, timing issues, smoothness problems
- **Typography Inconsistency**: Font size mismatches, hierarchy violations
- **Surface Level Violation**: Incorrect elevation, shadow mismatches
- **Animation Timing Issue**: Too fast/slow animations, unpolished feel
- **Interaction State Issue**: Wrong hover states, color transitions

### **UX Laws Reference**
- **Laws of UX**: https://lawsofux.com/

### **Excel History & Context**
- **Microsoft Excel Wikipedia**: https://en.wikipedia.org/wiki/Microsoft_Excel

---

## 🛣️ Implementation Roadmap

### Phase 1: Foundation (✅ COMPLETED)
- ✅ Basic Craft bug detection
- ✅ Telemetry collection
- ✅ HTML report generation
- ✅ Excel automation
- ✅ UX Designer persona framework
- ✅ Enhanced prompt engineering framework

### Phase 2: Enhanced Analysis (🔄 IN PROGRESS)
- ✅ **Figma Design System Integration**: `figma_integration.py` created
- ✅ **Design Specifications**: All 6 design systems (Excel Web Fluent 2, Office Icons, Excel Copilot, Win32 Ribbon, Fluent Surfaces, Win32 Variables)
- ✅ **Design Compliance Checking**: Color, typography, spacing validation
- ✅ **Enhanced ADO Integration**: `enhanced_ado_integration.py` created with 10 Craft bug examples
- ✅ **Craft Bug Pattern Analysis**: Bug type distribution, surface level focus, detection priorities
- 🔄 **L1/L2/L3 Surface Analysis**: Framework defined, implementation pending
- 🔄 **UX Laws Integration**: Framework defined, implementation pending
- 🔄 **Enhanced Persona Analysis**: Framework defined, implementation pending

### Phase 3: Advanced Features (📋 PLANNED)
- [ ] Real-time visual analysis with design compliance
- [ ] Performance monitoring with UX laws
- [ ] Accessibility compliance checking
- [ ] Cross-surface consistency validation
- [ ] Advanced Craft bug detection with Fluent Design rules

### Phase 4: Integration (📋 PLANNED)
- [ ] ADO automatic bug logging with enhanced categorization
- [ ] Dashboard enhancements with design compliance metrics
- [ ] Real-time monitoring with UX score tracking
- [ ] Predictive bug detection using historical patterns

---

## 📝 Notes & Modifications

### Recent Updates
- **Date**: January 19, 2025
- **Changes**: 
  - ✅ Created comprehensive UX Designer Prompt Engineering Framework
  - ✅ Implemented Figma Design System Integration (`figma_integration.py`) with 6 design systems
  - ✅ Extracted design specifications from Excel Web Fluent 2, Office Icons, Excel Copilot, Win32 Ribbon, Fluent Surfaces, Win32 Variables
  - ✅ Added design compliance checking capabilities
  - ✅ Updated framework with detailed UX designer thinking process
  - ✅ Enhanced ADO Integration (`enhanced_ado_integration.py`) with 10 comprehensive Craft bug examples
  - ✅ Added Craft bug pattern analysis and prompt engineering insights
  - ✅ Generated detailed Craft bug categories and detection priorities
- **Next Steps**: 
  - 🔄 Integrate Figma API with access token for real-time design updates
  - 🔄 Implement L1/L2/L3 surface analysis in Craft bug detection
  - 🔄 Add UX laws integration to analyzer
  - 🔄 Enhance persona-specific detection rules
  - 🔄 Integrate enhanced Craft bug examples into analyzer

### To-Do Items
- ✅ Extract design tokens from Figma files (implemented with fallback specs)
- 🔄 Fetch additional ADO bug examples with PAT (ready for implementation)
- 🔄 Implement surface-level analysis framework (framework defined)
- 🔄 Add UX laws integration (framework defined)
- 🔄 Create persona-specific detection rules (framework defined)
- 🔄 Integrate design compliance checking into Craft bug detection
- 🔄 Add real-time Figma API integration with access token

---

*This document is a living framework that should be continuously updated and enhanced based on new insights, user feedback, and system improvements.*
