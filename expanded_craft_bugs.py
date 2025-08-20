#!/usr/bin/env python3
"""
Expanded Craft Bug Examples
===========================

Comprehensive collection of 40 Craft bug examples covering all categories
for enhanced training and detection capabilities.
"""

def get_expanded_craft_bugs() -> list:
    """Get comprehensive list of 40 Craft bug examples"""
    return [
        # Visual Inconsistency Bugs (8 examples)
        {
            'id': 'CRAFT-001',
            'title': 'Excel Ribbon Button Alignment Inconsistency',
            'description': 'Ribbon buttons are not perfectly aligned - some are 1-2px off from the grid. This creates visual noise and feels unpolished.',
            'state': 'Active', 'severity': 'Medium', 'tags': 'Craft, Alignment, Ribbon, Visual',
            'craft_bug_type': 'Visual Inconsistency', 'surface_level': 'L1', 'user_impact': 'Medium',
            'created_date': '2024-01-15', 'assigned_to': 'UX Team'
        },
        {
            'id': 'CRAFT-002',
            'title': 'Dialog Shadow Inconsistency',
            'description': 'Dialog shadow uses 0 4px 8px instead of the standard 0 2px 4px. This creates inconsistent elevation perception.',
            'state': 'Active', 'severity': 'Low', 'tags': 'Craft, Shadow, Dialog, Elevation',
            'craft_bug_type': 'Visual Inconsistency', 'surface_level': 'L2', 'user_impact': 'Low',
            'created_date': '2024-01-16', 'assigned_to': 'Design Team'
        },
        {
            'id': 'CRAFT-003',
            'title': 'Icon Size Mismatch in Toolbar',
            'description': 'Icons in the toolbar have inconsistent sizes - some are 16px, others are 20px. This breaks visual harmony.',
            'state': 'Active', 'severity': 'Medium', 'tags': 'Craft, Icons, Size, Visual',
            'craft_bug_type': 'Visual Inconsistency', 'surface_level': 'L1', 'user_impact': 'Medium',
            'created_date': '2024-01-17', 'assigned_to': 'Design Team'
        },
        {
            'id': 'CRAFT-004',
            'title': 'Border Radius Inconsistency',
            'description': 'Some buttons use 4px border radius while others use 2px. This creates visual inconsistency across the interface.',
            'state': 'Active', 'severity': 'Low', 'tags': 'Craft, Border Radius, Buttons, Visual',
            'craft_bug_type': 'Visual Inconsistency', 'surface_level': 'L1', 'user_impact': 'Low',
            'created_date': '2024-01-18', 'assigned_to': 'Design Team'
        },
        {
            'id': 'CRAFT-005',
            'title': 'Grid Line Color Mismatch',
            'description': 'Grid lines use #e1dfdd instead of the correct #edebe9. This creates subtle but noticeable color inconsistency.',
            'state': 'Active', 'severity': 'Low', 'tags': 'Craft, Grid, Color, Visual',
            'craft_bug_type': 'Visual Inconsistency', 'surface_level': 'L1', 'user_impact': 'Low',
            'created_date': '2024-01-19', 'assigned_to': 'Design Team'
        },
        {
            'id': 'CRAFT-006',
            'title': 'Panel Header Alignment Issue',
            'description': 'Panel headers are not perfectly aligned with their content - 1px offset creates visual noise.',
            'state': 'Active', 'severity': 'Low', 'tags': 'Craft, Alignment, Panel, Visual',
            'craft_bug_type': 'Visual Inconsistency', 'surface_level': 'L2', 'user_impact': 'Low',
            'created_date': '2024-01-20', 'assigned_to': 'Design Team'
        },
        {
            'id': 'CRAFT-007',
            'title': 'Text Baseline Misalignment',
            'description': 'Text elements have inconsistent baseline alignment - some are 1px higher than others.',
            'state': 'Active', 'severity': 'Low', 'tags': 'Craft, Typography, Baseline, Visual',
            'craft_bug_type': 'Visual Inconsistency', 'surface_level': 'L1', 'user_impact': 'Low',
            'created_date': '2024-01-21', 'assigned_to': 'Design Team'
        },
        {
            'id': 'CRAFT-008',
            'title': 'Background Color Inconsistency',
            'description': 'Some panels use #ffffff while others use #faf9f8. This creates subtle background inconsistency.',
            'state': 'Active', 'severity': 'Low', 'tags': 'Craft, Background, Color, Visual',
            'craft_bug_type': 'Visual Inconsistency', 'surface_level': 'L2', 'user_impact': 'Low',
            'created_date': '2024-01-22', 'assigned_to': 'Design Team'
        },

        # Performance UX Bugs (6 examples)
        {
            'id': 'CRAFT-009',
            'title': 'Copilot Dialog Animation Stutter',
            'description': 'When Copilot dialog appears, there is a slight stutter in the animation. The transition is not smooth and feels jarring.',
            'state': 'Active', 'severity': 'Low', 'tags': 'Craft, Animation, Copilot, Performance',
            'craft_bug_type': 'Performance UX', 'surface_level': 'L2', 'user_impact': 'Low',
            'created_date': '2024-01-23', 'assigned_to': 'Performance Team'
        },
        {
            'id': 'CRAFT-010',
            'title': 'Slow Cell Selection Response',
            'description': 'Cell selection takes 600ms instead of the target 400ms. This exceeds Doherty Threshold and feels sluggish.',
            'state': 'Active', 'severity': 'Medium', 'tags': 'Craft, Performance, Cells, Timing',
            'craft_bug_type': 'Performance UX', 'surface_level': 'L1', 'user_impact': 'Medium',
            'created_date': '2024-01-24', 'assigned_to': 'Performance Team'
        },
        {
            'id': 'CRAFT-011',
            'title': 'Ribbon Animation Frame Drop',
            'description': 'Ribbon animations drop frames during transitions, creating choppy visual experience.',
            'state': 'Active', 'severity': 'Low', 'tags': 'Craft, Animation, Ribbon, Performance',
            'craft_bug_type': 'Performance UX', 'surface_level': 'L1', 'user_impact': 'Low',
            'created_date': '2024-01-25', 'assigned_to': 'Performance Team'
        },
        {
            'id': 'CRAFT-012',
            'title': 'Dialog Opening Delay',
            'description': 'Dialog opening takes 800ms instead of 400ms. This creates noticeable lag in user interactions.',
            'state': 'Active', 'severity': 'Medium', 'tags': 'Craft, Performance, Dialog, Timing',
            'craft_bug_type': 'Performance UX', 'surface_level': 'L2', 'user_impact': 'Medium',
            'created_date': '2024-01-26', 'assigned_to': 'Performance Team'
        },
        {
            'id': 'CRAFT-013',
            'title': 'Scroll Performance Issue',
            'description': 'Scrolling through large datasets causes frame drops and stuttering animation.',
            'state': 'Active', 'severity': 'Medium', 'tags': 'Craft, Performance, Scroll, Animation',
            'craft_bug_type': 'Performance UX', 'surface_level': 'L1', 'user_impact': 'Medium',
            'created_date': '2024-01-27', 'assigned_to': 'Performance Team'
        },
        {
            'id': 'CRAFT-014',
            'title': 'Button Click Response Lag',
            'description': 'Button clicks have 500ms response time instead of 400ms, exceeding Doherty Threshold.',
            'state': 'Active', 'severity': 'Low', 'tags': 'Craft, Performance, Buttons, Timing',
            'craft_bug_type': 'Performance UX', 'surface_level': 'L1', 'user_impact': 'Low',
            'created_date': '2024-01-28', 'assigned_to': 'Performance Team'
        },

        # Design System Violation Bugs (6 examples)
        {
            'id': 'CRAFT-015',
            'title': 'Cell Selection Color Mismatch',
            'description': 'Selected cell border color uses #0078d4 instead of the correct #106ebe. This creates a color inconsistency in the design system.',
            'state': 'Active', 'severity': 'Medium', 'tags': 'Craft, Color, Cells, Design System',
            'craft_bug_type': 'Design System Violation', 'surface_level': 'L1', 'user_impact': 'Medium',
            'created_date': '2024-01-29', 'assigned_to': 'Design Team'
        },
        {
            'id': 'CRAFT-016',
            'title': 'Button Color System Violation',
            'description': 'Secondary button uses #323130 instead of the correct #605e5c from the design system.',
            'state': 'Active', 'severity': 'Low', 'tags': 'Craft, Color, Buttons, Design System',
            'craft_bug_type': 'Design System Violation', 'surface_level': 'L1', 'user_impact': 'Low',
            'created_date': '2024-01-30', 'assigned_to': 'Design Team'
        },
        {
            'id': 'CRAFT-017',
            'title': 'Typography Scale Violation',
            'description': 'Panel headers use 18px instead of the correct 16px from the typography scale.',
            'state': 'Active', 'severity': 'Low', 'tags': 'Craft, Typography, Scale, Design System',
            'craft_bug_type': 'Design System Violation', 'surface_level': 'L2', 'user_impact': 'Low',
            'created_date': '2024-02-01', 'assigned_to': 'Design Team'
        },
        {
            'id': 'CRAFT-018',
            'title': 'Spacing Token Violation',
            'description': 'Dialog padding uses 20px instead of the correct 24px spacing token.',
            'state': 'Active', 'severity': 'Low', 'tags': 'Craft, Spacing, Dialog, Design System',
            'craft_bug_type': 'Design System Violation', 'surface_level': 'L2', 'user_impact': 'Low',
            'created_date': '2024-02-02', 'assigned_to': 'Design Team'
        },
        {
            'id': 'CRAFT-019',
            'title': 'Icon Color System Violation',
            'description': 'Icons use #323130 instead of the correct #605e5c from the icon color system.',
            'state': 'Active', 'severity': 'Low', 'tags': 'Craft, Icons, Color, Design System',
            'craft_bug_type': 'Design System Violation', 'surface_level': 'L1', 'user_impact': 'Low',
            'created_date': '2024-02-03', 'assigned_to': 'Design Team'
        },
        {
            'id': 'CRAFT-020',
            'title': 'Border Color Violation',
            'description': 'Input borders use #d2d0ce instead of the correct #e1dfdd from the border color system.',
            'state': 'Active', 'severity': 'Low', 'tags': 'Craft, Borders, Color, Design System',
            'craft_bug_type': 'Design System Violation', 'surface_level': 'L1', 'user_impact': 'Low',
            'created_date': '2024-02-04', 'assigned_to': 'Design Team'
        },

        # Typography Inconsistency Bugs (5 examples)
        {
            'id': 'CRAFT-021',
            'title': 'Save Button Typography Inconsistency',
            'description': 'Save button text uses 14px font size instead of the standard 12px. This breaks typography hierarchy and feels inconsistent.',
            'state': 'Active', 'severity': 'Low', 'tags': 'Craft, Typography, Buttons, Hierarchy',
            'craft_bug_type': 'Typography Inconsistency', 'surface_level': 'L1', 'user_impact': 'Low',
            'created_date': '2024-02-05', 'assigned_to': 'Design Team'
        },
        {
            'id': 'CRAFT-022',
            'title': 'Panel Header Font Weight Issue',
            'description': 'Panel headers use 500 weight instead of the correct 600 weight, breaking typography hierarchy.',
            'state': 'Active', 'severity': 'Low', 'tags': 'Craft, Typography, Headers, Weight',
            'craft_bug_type': 'Typography Inconsistency', 'surface_level': 'L2', 'user_impact': 'Low',
            'created_date': '2024-02-06', 'assigned_to': 'Design Team'
        },
        {
            'id': 'CRAFT-023',
            'title': 'Tooltip Font Size Inconsistency',
            'description': 'Tooltip text uses 12px instead of the correct 10px, making it too prominent.',
            'state': 'Active', 'severity': 'Low', 'tags': 'Craft, Typography, Tooltip, Size',
            'craft_bug_type': 'Typography Inconsistency', 'surface_level': 'L3', 'user_impact': 'Low',
            'created_date': '2024-02-07', 'assigned_to': 'Design Team'
        },
        {
            'id': 'CRAFT-024',
            'title': 'Menu Item Typography Mismatch',
            'description': 'Menu items use 14px instead of 12px, creating inconsistent text hierarchy.',
            'state': 'Active', 'severity': 'Low', 'tags': 'Craft, Typography, Menu, Hierarchy',
            'craft_bug_type': 'Typography Inconsistency', 'surface_level': 'L3', 'user_impact': 'Low',
            'created_date': '2024-02-08', 'assigned_to': 'Design Team'
        },
        {
            'id': 'CRAFT-025',
            'title': 'Label Font Weight Inconsistency',
            'description': 'Form labels use 400 weight instead of 500, making them less prominent than intended.',
            'state': 'Active', 'severity': 'Low', 'tags': 'Craft, Typography, Labels, Weight',
            'craft_bug_type': 'Typography Inconsistency', 'surface_level': 'L1', 'user_impact': 'Low',
            'created_date': '2024-02-09', 'assigned_to': 'Design Team'
        },

        # Surface Level Violation Bugs (4 examples)
        {
            'id': 'CRAFT-026',
            'title': 'Format Panel Surface Level Violation',
            'description': 'Format panel uses L1 elevation (0px) instead of L2 (4px). This breaks the surface hierarchy and makes it feel flat.',
            'state': 'Active', 'severity': 'Medium', 'tags': 'Craft, Surface Level, Panel, Elevation',
            'craft_bug_type': 'Surface Level Violation', 'surface_level': 'L2', 'user_impact': 'Medium',
            'created_date': '2024-02-10', 'assigned_to': 'Design Team'
        },
        {
            'id': 'CRAFT-027',
            'title': 'Dropdown Surface Elevation Issue',
            'description': 'Dropdown menu uses L2 elevation instead of L3, breaking surface hierarchy.',
            'state': 'Active', 'severity': 'Low', 'tags': 'Craft, Surface Level, Dropdown, Elevation',
            'craft_bug_type': 'Surface Level Violation', 'surface_level': 'L3', 'user_impact': 'Low',
            'created_date': '2024-02-11', 'assigned_to': 'Design Team'
        },
        {
            'id': 'CRAFT-028',
            'title': 'Tooltip Shadow Violation',
            'description': 'Tooltip uses 0 2px 4px shadow instead of 0 4px 8px, breaking L3 surface specification.',
            'state': 'Active', 'severity': 'Low', 'tags': 'Craft, Surface Level, Tooltip, Shadow',
            'craft_bug_type': 'Surface Level Violation', 'surface_level': 'L3', 'user_impact': 'Low',
            'created_date': '2024-02-12', 'assigned_to': 'Design Team'
        },
        {
            'id': 'CRAFT-029',
            'title': 'Dialog Surface Level Mismatch',
            'description': 'Dialog uses L3 elevation instead of L2, creating incorrect surface hierarchy.',
            'state': 'Active', 'severity': 'Medium', 'tags': 'Craft, Surface Level, Dialog, Elevation',
            'craft_bug_type': 'Surface Level Violation', 'surface_level': 'L2', 'user_impact': 'Medium',
            'created_date': '2024-02-13', 'assigned_to': 'Design Team'
        },

        # Spacing Inconsistency Bugs (4 examples)
        {
            'id': 'CRAFT-030',
            'title': 'Ribbon Tab Spacing Inconsistent',
            'description': 'Spacing between ribbon tabs varies - some are 8px apart, others are 12px. This breaks visual rhythm and feels unpolished.',
            'state': 'Active', 'severity': 'Medium', 'tags': 'Craft, Spacing, Ribbon, Visual Rhythm',
            'craft_bug_type': 'Spacing Inconsistency', 'surface_level': 'L1', 'user_impact': 'Medium',
            'created_date': '2024-02-14', 'assigned_to': 'Design Team'
        },
        {
            'id': 'CRAFT-031',
            'title': 'Dropdown Menu Spacing Inconsistency',
            'description': 'Dropdown menu items have inconsistent spacing - some are 8px apart, others are 12px. This breaks visual rhythm.',
            'state': 'Active', 'severity': 'Low', 'tags': 'Craft, Spacing, Dropdown, Visual Rhythm',
            'craft_bug_type': 'Spacing Inconsistency', 'surface_level': 'L3', 'user_impact': 'Low',
            'created_date': '2024-02-15', 'assigned_to': 'Design Team'
        },
        {
            'id': 'CRAFT-032',
            'title': 'Panel Content Spacing Issue',
            'description': 'Panel content has inconsistent padding - some sections use 16px, others use 20px.',
            'state': 'Active', 'severity': 'Low', 'tags': 'Craft, Spacing, Panel, Content',
            'craft_bug_type': 'Spacing Inconsistency', 'surface_level': 'L2', 'user_impact': 'Low',
            'created_date': '2024-02-16', 'assigned_to': 'Design Team'
        },
        {
            'id': 'CRAFT-033',
            'title': 'Button Group Spacing Violation',
            'description': 'Button groups have inconsistent spacing between buttons - some are 4px, others are 8px.',
            'state': 'Active', 'severity': 'Low', 'tags': 'Craft, Spacing, Buttons, Groups',
            'craft_bug_type': 'Spacing Inconsistency', 'surface_level': 'L1', 'user_impact': 'Low',
            'created_date': '2024-02-17', 'assigned_to': 'Design Team'
        },

        # Animation Timing Issue Bugs (3 examples)
        {
            'id': 'CRAFT-034',
            'title': 'Tooltip Animation Timing Issue',
            'description': 'Tooltip appears too quickly (100ms) instead of the standard 300ms delay. This feels jarring and interrupts user flow.',
            'state': 'Active', 'severity': 'Low', 'tags': 'Craft, Animation, Tooltip, Timing',
            'craft_bug_type': 'Animation Timing Issue', 'surface_level': 'L3', 'user_impact': 'Low',
            'created_date': '2024-02-18', 'assigned_to': 'UX Team'
        },
        {
            'id': 'CRAFT-035',
            'title': 'Button Hover Animation Speed',
            'description': 'Button hover animation is too fast (150ms) instead of the standard 200ms, feeling abrupt.',
            'state': 'Active', 'severity': 'Low', 'tags': 'Craft, Animation, Buttons, Timing',
            'craft_bug_type': 'Animation Timing Issue', 'surface_level': 'L1', 'user_impact': 'Low',
            'created_date': '2024-02-19', 'assigned_to': 'UX Team'
        },
        {
            'id': 'CRAFT-036',
            'title': 'Dialog Transition Timing',
            'description': 'Dialog transition takes 500ms instead of the standard 300ms, feeling sluggish.',
            'state': 'Active', 'severity': 'Low', 'tags': 'Craft, Animation, Dialog, Timing',
            'craft_bug_type': 'Animation Timing Issue', 'surface_level': 'L2', 'user_impact': 'Low',
            'created_date': '2024-02-20', 'assigned_to': 'UX Team'
        },

        # Interaction State Issue Bugs (3 examples)
        {
            'id': 'CRAFT-037',
            'title': 'Button Hover State Interaction Issue',
            'description': 'Button hover state color transition is too abrupt - no smooth transition between normal and hover states.',
            'state': 'Active', 'severity': 'Low', 'tags': 'Craft, Interaction, Buttons, Hover',
            'craft_bug_type': 'Interaction State Issue', 'surface_level': 'L1', 'user_impact': 'Low',
            'created_date': '2024-02-21', 'assigned_to': 'UX Team'
        },
        {
            'id': 'CRAFT-038',
            'title': 'Focus State Visual Feedback',
            'description': 'Focus states lack proper visual feedback - users cannot clearly see which element is focused.',
            'state': 'Active', 'severity': 'Medium', 'tags': 'Craft, Interaction, Focus, Feedback',
            'craft_bug_type': 'Interaction State Issue', 'surface_level': 'L1', 'user_impact': 'Medium',
            'created_date': '2024-02-22', 'assigned_to': 'UX Team'
        },
        {
            'id': 'CRAFT-039',
            'title': 'Disabled State Clarity',
            'description': 'Disabled button states are not clearly distinguishable from enabled states.',
            'state': 'Active', 'severity': 'Medium', 'tags': 'Craft, Interaction, Disabled, States',
            'craft_bug_type': 'Interaction State Issue', 'surface_level': 'L1', 'user_impact': 'Medium',
            'created_date': '2024-02-23', 'assigned_to': 'UX Team'
        },

        # Additional Complex Bugs (1 example)
        {
            'id': 'CRAFT-040',
            'title': 'Multi-Surface Consistency Violation',
            'description': 'Similar elements across L1/L2/L3 surfaces have inconsistent styling - buttons look different in ribbon vs panels vs dropdowns.',
            'state': 'Active', 'severity': 'High', 'tags': 'Craft, Consistency, Multi-Surface, Design',
            'craft_bug_type': 'Visual Inconsistency', 'surface_level': 'L1', 'user_impact': 'High',
            'created_date': '2024-02-24', 'assigned_to': 'Design Team'
        }
    ]

if __name__ == "__main__":
    bugs = get_expanded_craft_bugs()
    print(f"✅ Generated {len(bugs)} comprehensive Craft bug examples")
    
    # Analyze distribution
    bug_types = {}
    surface_levels = {}
    severities = {}
    
    for bug in bugs:
        bug_type = bug['craft_bug_type']
        surface_level = bug['surface_level']
        severity = bug['severity']
        
        bug_types[bug_type] = bug_types.get(bug_type, 0) + 1
        surface_levels[surface_level] = surface_levels.get(surface_level, 0) + 1
        severities[severity] = severities.get(severity, 0) + 1
    
    print(f"\n📊 Bug Type Distribution:")
    for bug_type, count in bug_types.items():
        print(f"   {bug_type}: {count}")
    
    print(f"\n📊 Surface Level Distribution:")
    for level, count in surface_levels.items():
        print(f"   {level}: {count}")
    
    print(f"\n📊 Severity Distribution:")
    for severity, count in severities.items():
        print(f"   {severity}: {count}")
