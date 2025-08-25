#!/usr/bin/env python3
"""
Test Full Consolidation Pipeline
Takes the full 36 bugs and consolidates them into unique, developer-ready issues
"""

import asyncio
from consolidation_analyzer import ConsolidationAnalyzer

async def test_full_consolidation():
    """Test consolidation with the full set of 36 bugs"""
    
    print("🚀 FULL CONSOLIDATION TEST")
    print("=" * 60)
    
    analyzer = ConsolidationAnalyzer()
    
    # Full set of 36 bugs from our analysis
    full_bugs = [
        # Screenshot 1: excel_initial_state_1756061972.png (10 bugs)
        {
            'title': 'Misaligned spacing in toolbar',
            'type': 'Visual',
            'severity': 'Orange',
            'step_name': 'Navigate to Excel',
            'description': 'Toolbar elements have inconsistent spacing',
            'impact': 'Reduces visual hierarchy and professional appearance',
            'immediate_fix': 'Standardize spacing between toolbar elements'
        },
        {
            'title': 'Low color contrast',
            'type': 'Accessibility',
            'severity': 'Red',
            'step_name': 'Navigate to Excel',
            'description': 'Text elements have insufficient contrast ratios',
            'impact': 'Makes content difficult to read for users with visual impairments',
            'immediate_fix': 'Increase contrast ratio to meet WCAG guidelines'
        },
        {
            'title': 'Small click targets for toolbar icons',
            'type': 'Interaction',
            'severity': 'Yellow',
            'step_name': 'Navigate to Excel',
            'description': 'Toolbar buttons are too small for comfortable clicking',
            'impact': 'Increases user effort and potential for misclicks',
            'immediate_fix': 'Increase button size to minimum 44x44px'
        },
        {
            'title': 'Lack of clear visual feedback for AI suggestions',
            'type': 'AI',
            'severity': 'Yellow',
            'step_name': 'Navigate to Excel',
            'description': 'AI features lack clear visual indicators',
            'impact': 'Users may not understand AI capabilities',
            'immediate_fix': 'Add clear visual indicators for AI-powered features'
        },
        {
            'title': 'Inconsistent alignment of text in cells',
            'type': 'Design',
            'severity': 'Orange',
            'step_name': 'Navigate to Excel',
            'description': 'Cell content alignment varies inconsistently',
            'impact': 'Reduces data readability and professional appearance',
            'immediate_fix': 'Standardize cell alignment based on content type'
        },
        {
            'title': 'Poor visual hierarchy in ribbon',
            'type': 'Visual',
            'severity': 'Orange',
            'step_name': 'Navigate to Excel',
            'description': 'Ribbon sections lack clear visual separation',
            'impact': 'Makes navigation confusing for users',
            'immediate_fix': 'Improve visual separation between ribbon sections'
        },
        {
            'title': 'Missing hover states for interactive elements',
            'type': 'Interaction',
            'severity': 'Yellow',
            'step_name': 'Navigate to Excel',
            'description': 'Buttons lack clear hover feedback',
            'impact': 'Users can\'t tell which elements are interactive',
            'immediate_fix': 'Add consistent hover states for all interactive elements'
        },
        {
            'title': 'Inconsistent icon sizing',
            'type': 'Visual',
            'severity': 'Yellow',
            'step_name': 'Navigate to Excel',
            'description': 'Icons have varying sizes across the interface',
            'impact': 'Reduces visual consistency and professional appearance',
            'immediate_fix': 'Standardize icon sizes across all interface elements'
        },
        {
            'title': 'Poor spacing around form elements',
            'type': 'Layout',
            'severity': 'Orange',
            'step_name': 'Navigate to Excel',
            'description': 'Form elements lack adequate spacing',
            'impact': 'Makes forms difficult to read and interact with',
            'immediate_fix': 'Increase spacing between form elements'
        },
        {
            'title': 'Inconsistent typography scale',
            'type': 'Design',
            'severity': 'Yellow',
            'step_name': 'Navigate to Excel',
            'description': 'Text sizes don\'t follow a consistent scale',
            'impact': 'Reduces readability and visual hierarchy',
            'immediate_fix': 'Implement consistent typography scale'
        },
        
        # Screenshot 2: excel_copilot_dialog_1756061967.png (18 bugs)
        {
            'title': 'Copilot dialog input field visual affordance',
            'type': 'Interaction',
            'severity': 'Orange',
            'step_name': 'Dismiss Copilot Dialog',
            'description': 'Input field lacks clear visual indication of interactivity',
            'impact': 'Users may not realize they can type in the field',
            'immediate_fix': 'Add clear visual affordances for input field'
        },
        {
            'title': 'Dialog positioning blocks content',
            'type': 'Layout',
            'severity': 'Red',
            'step_name': 'Dismiss Copilot Dialog',
            'description': 'Dialog appears in position that obscures important content',
            'impact': 'Users can\'t see underlying spreadsheet data',
            'immediate_fix': 'Reposition dialog to avoid content obstruction'
        },
        {
            'title': 'Insufficient contrast in dialog text',
            'type': 'Accessibility',
            'severity': 'Orange',
            'step_name': 'Dismiss Copilot Dialog',
            'description': 'Dialog text has poor contrast against background',
            'impact': 'Difficult to read for users with visual impairments',
            'immediate_fix': 'Increase text contrast ratio'
        },
        {
            'title': 'Missing close button accessibility',
            'type': 'Accessibility',
            'severity': 'Red',
            'step_name': 'Dismiss Copilot Dialog',
            'description': 'Close button lacks proper accessibility attributes',
            'impact': 'Screen readers can\'t identify the close function',
            'immediate_fix': 'Add proper ARIA labels and keyboard navigation'
        },
        {
            'title': 'Dialog shadow too subtle',
            'type': 'Visual',
            'severity': 'Yellow',
            'step_name': 'Dismiss Copilot Dialog',
            'description': 'Dialog shadow doesn\'t provide enough depth',
            'impact': 'Dialog doesn\'t appear elevated from background',
            'immediate_fix': 'Increase shadow depth for better visual separation'
        },
        {
            'title': 'Inconsistent button styling',
            'type': 'Design',
            'severity': 'Orange',
            'step_name': 'Dismiss Copilot Dialog',
            'description': 'Dialog buttons don\'t match main interface styling',
            'impact': 'Breaks visual consistency across the application',
            'immediate_fix': 'Standardize button styling with main interface'
        },
        {
            'title': 'Poor focus indicators',
            'type': 'Accessibility',
            'severity': 'Orange',
            'step_name': 'Dismiss Copilot Dialog',
            'description': 'Focus indicators are too subtle or missing',
            'impact': 'Keyboard users can\'t see which element is focused',
            'immediate_fix': 'Add clear, visible focus indicators'
        },
        {
            'title': 'Dialog animation too fast',
            'type': 'Interaction',
            'severity': 'Yellow',
            'step_name': 'Dismiss Copilot Dialog',
            'description': 'Dialog appears/disappears too quickly',
            'impact': 'Users may miss the dialog or feel disoriented',
            'immediate_fix': 'Slow down dialog animation for better UX'
        },
        {
            'title': 'Missing loading states',
            'type': 'Interaction',
            'severity': 'Yellow',
            'step_name': 'Dismiss Copilot Dialog',
            'description': 'No visual feedback during AI processing',
            'impact': 'Users don\'t know if their request is being processed',
            'immediate_fix': 'Add loading indicators for AI operations'
        },
        {
            'title': 'Inconsistent spacing in dialog',
            'type': 'Layout',
            'severity': 'Yellow',
            'step_name': 'Dismiss Copilot Dialog',
            'description': 'Dialog elements have inconsistent spacing',
            'impact': 'Reduces visual hierarchy and professional appearance',
            'immediate_fix': 'Standardize spacing throughout dialog'
        },
        {
            'title': 'Poor error handling visualization',
            'type': 'Interaction',
            'severity': 'Orange',
            'step_name': 'Dismiss Copilot Dialog',
            'description': 'Error states lack clear visual indicators',
            'impact': 'Users may not understand when something goes wrong',
            'immediate_fix': 'Add clear error state visualizations'
        },
        {
            'title': 'Missing keyboard shortcuts',
            'type': 'Accessibility',
            'severity': 'Yellow',
            'step_name': 'Dismiss Copilot Dialog',
            'description': 'Dialog lacks keyboard navigation shortcuts',
            'impact': 'Power users can\'t efficiently navigate with keyboard',
            'immediate_fix': 'Add keyboard shortcuts for common actions'
        },
        {
            'title': 'Inconsistent icon usage',
            'type': 'Design',
            'severity': 'Yellow',
            'step_name': 'Dismiss Copilot Dialog',
            'description': 'Icons don\'t follow consistent design language',
            'impact': 'Reduces visual consistency and user understanding',
            'immediate_fix': 'Standardize icon usage across dialog'
        },
        {
            'title': 'Poor responsive behavior',
            'type': 'Layout',
            'severity': 'Orange',
            'step_name': 'Dismiss Copilot Dialog',
            'description': 'Dialog doesn\'t adapt well to different screen sizes',
            'impact': 'Poor experience on different devices',
            'immediate_fix': 'Improve responsive design for dialog'
        },
        {
            'title': 'Missing progress indicators',
            'type': 'Interaction',
            'severity': 'Yellow',
            'step_name': 'Dismiss Copilot Dialog',
            'description': 'No indication of AI processing progress',
            'impact': 'Users don\'t know how long operations will take',
            'immediate_fix': 'Add progress indicators for long operations'
        },
        {
            'title': 'Inconsistent color usage',
            'type': 'Visual',
            'severity': 'Yellow',
            'step_name': 'Dismiss Copilot Dialog',
            'description': 'Colors don\'t match main application palette',
            'impact': 'Breaks visual consistency and brand identity',
            'immediate_fix': 'Use consistent color palette throughout'
        },
        {
            'title': 'Poor text hierarchy',
            'type': 'Design',
            'severity': 'Orange',
            'step_name': 'Dismiss Copilot Dialog',
            'description': 'Text elements lack clear hierarchy',
            'impact': 'Makes content difficult to scan and understand',
            'immediate_fix': 'Improve text hierarchy with proper sizing and weight'
        },
        {
            'title': 'Missing help text',
            'type': 'Interaction',
            'severity': 'Yellow',
            'step_name': 'Dismiss Copilot Dialog',
            'description': 'No contextual help for AI features',
            'impact': 'Users may not understand how to use AI features',
            'immediate_fix': 'Add contextual help and tooltips'
        },
        
        # Screenshot 3: excel_final_state_1755521895.png (8 bugs)
        {
            'title': 'Inconsistent save button styling',
            'type': 'Design',
            'severity': 'Orange',
            'step_name': 'Save Workbook',
            'description': 'Save button doesn\'t match other primary actions',
            'impact': 'Reduces visual consistency and user confidence',
            'immediate_fix': 'Standardize save button styling with other primary actions'
        },
        {
            'title': 'Poor visual feedback for save action',
            'type': 'Interaction',
            'severity': 'Orange',
            'step_name': 'Save Workbook',
            'description': 'No clear indication when save is successful',
            'impact': 'Users may not know if their work was saved',
            'immediate_fix': 'Add clear success indicators for save actions'
        },
        {
            'title': 'Missing auto-save indicators',
            'type': 'Interaction',
            'severity': 'Yellow',
            'step_name': 'Save Workbook',
            'description': 'No visual indication of auto-save status',
            'impact': 'Users may not know if their work is being saved automatically',
            'immediate_fix': 'Add auto-save status indicators'
        },
        {
            'title': 'Inconsistent file naming display',
            'type': 'Visual',
            'severity': 'Yellow',
            'step_name': 'Save Workbook',
            'description': 'File name display doesn\'t follow consistent formatting',
            'impact': 'Makes it difficult to identify files quickly',
            'immediate_fix': 'Standardize file name display formatting'
        },
        {
            'title': 'Poor error handling for save failures',
            'type': 'Interaction',
            'severity': 'Red',
            'step_name': 'Save Workbook',
            'description': 'Save errors lack clear user guidance',
            'impact': 'Users don\'t know how to resolve save issues',
            'immediate_fix': 'Add clear error messages and recovery options'
        },
        {
            'title': 'Missing save confirmation dialog',
            'type': 'Interaction',
            'severity': 'Yellow',
            'step_name': 'Save Workbook',
            'description': 'No confirmation when overwriting existing files',
            'impact': 'Users may accidentally overwrite important files',
            'immediate_fix': 'Add confirmation dialogs for destructive actions'
        },
        {
            'title': 'Inconsistent save location display',
            'type': 'Visual',
            'severity': 'Yellow',
            'step_name': 'Save Workbook',
            'description': 'Save location information is not clearly displayed',
            'impact': 'Users may not know where their files are saved',
            'immediate_fix': 'Add clear save location indicators'
        },
        {
            'title': 'Poor keyboard navigation for save',
            'type': 'Accessibility',
            'severity': 'Orange',
            'step_name': 'Save Workbook',
            'description': 'Save functionality lacks proper keyboard support',
            'impact': 'Keyboard users can\'t efficiently save their work',
            'immediate_fix': 'Add keyboard shortcuts and navigation for save'
        }
    ]
    
    # Steps data
    steps_data = [
        {
            'step_name': 'Navigate to Excel',
            'description': 'User navigates to Excel web app and sees initial interface',
            'screenshot_path': 'screenshots/excel_web/excel_initial_state_1756061972.png',
            'scenario_description': 'Excel Document Creation with Copilot',
            'persona_type': 'Power User'
        },
        {
            'step_name': 'Dismiss Copilot Dialog',
            'description': 'User dismisses the Copilot dialog with suggestions',
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
    
    print(f"📊 INPUT:")
    print(f"   Raw bugs: {len(full_bugs)}")
    print(f"   Steps: {len(steps_data)}")
    print(f"   Screenshots: {len([s for s in steps_data if s.get('screenshot_path')])}")
    print()
    
    # Run consolidation
    consolidated_bugs = await analyzer.consolidate_bugs(full_bugs, steps_data)
    
    print(f"\n📈 RESULTS:")
    print("=" * 60)
    print(f"🎯 Consolidation achieved: {len(full_bugs)} → {len(consolidated_bugs)} bugs")
    print(f"📉 Reduction: {((len(full_bugs) - len(consolidated_bugs)) / len(full_bugs) * 100):.1f}%")
    
    if consolidated_bugs:
        print(f"\n🐛 CONSOLIDATED BUGS:")
        for i, bug in enumerate(consolidated_bugs, 1):
            print(f"\n--- Bug {i} ---")
            print(f"Title: {bug.get('title')}")
            print(f"Type: {bug.get('type')}")
            print(f"Severity: {bug.get('severity')}")
            print(f"Affected Steps: {bug.get('affected_steps')}")
            print(f"Screenshots: {len(bug.get('screenshot_paths', []))} files")
            print(f"Impact: {bug.get('impact', 'N/A')}")
            print(f"Fix: {bug.get('immediate_fix', 'N/A')}")
            
            # Show consolidation note
            consolidation_note = bug.get('consolidation_note', '')
            if consolidation_note:
                print(f"Note: {consolidation_note}")
    
    print(f"\n✅ CONSOLIDATION TEST COMPLETE!")

if __name__ == "__main__":
    asyncio.run(test_full_consolidation())

