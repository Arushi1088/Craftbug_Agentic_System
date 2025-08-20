#!/usr/bin/env python3
"""
Test Enhanced Excel Scenario
============================

Test the complete Excel scenario with our enhanced analyzer to see
how well it detects Craft bugs with all the new capabilities.
"""

import asyncio
import json
from datetime import datetime
from ai_driven_analyzer import AIDrivenAnalyzer
from excel_scenario_telemetry import ExcelScenarioTelemetry

async def test_enhanced_excel_scenario():
    """Test the enhanced Excel scenario with comprehensive analysis"""
    
    print("🚀 Testing Enhanced Excel Scenario with Comprehensive Analysis")
    print("=" * 70)
    
    # Initialize the enhanced analyzer
    analyzer = AIDrivenAnalyzer()
    
    # Initialize scenario telemetry
    telemetry = ExcelScenarioTelemetry()
    
    print("\n📊 Enhanced Analyzer Capabilities:")
    print("   ✅ Computer Vision Analysis")
    print("   ✅ Performance Monitoring")
    print("   ✅ Accessibility Compliance (Separate)")
    print("   ✅ Cross-Surface Validation")
    print("   ✅ Predictive ML Detection")
    print("   ✅ Persona-Specific Analysis")
    print("   ✅ 53 Craft Bug Examples")
    print("   ✅ Real Figma Design System")
    
    print(f"\n📝 Enhanced Prompt Length: {len(analyzer.enhanced_prompt)} characters")
    
    # Create sample telemetry data for testing
    sample_telemetry = {
        'scenario_name': 'excel_document_creation',
        'start_time': datetime.now().isoformat(),
        'steps': [
            {
                'step_name': 'Navigate to Excel Web',
                'description': 'Step 1: Navigate to Excel Web - Ensure we\'re on Excel Web with authentication - User navigated to Excel Web interface, authentication required',
                'start_time': datetime.now().isoformat(),
                'end_time': datetime.now().isoformat(),
                'duration_ms': 6000,  # Slow authentication
                'success': True,
                'timing': 6.0,
                'surface_level': 'L1',
                'interaction_type': 'page_load'
            },
            {
                'step_name': 'Click New Workbook',
                'description': 'Step 2: Click New Workbook - Click the \'Blank workbook\' text to create a new workbook - User clicked \'Blank workbook\' to create new Excel document',
                'start_time': datetime.now().isoformat(),
                'end_time': datetime.now().isoformat(),
                'duration_ms': 4000,  # Slow workbook creation
                'success': True,
                'timing': 4.0,
                'surface_level': 'L1',
                'interaction_type': 'button_click'
            },
            {
                'step_name': 'Wait for Excel to Launch in New Window',
                'description': 'Step 3: Wait for Excel to Launch in New Window - Wait for Excel to launch in new window after clicking \'Blank workbook\' - System waited for Excel to launch in new window/iframe',
                'start_time': datetime.now().isoformat(),
                'end_time': datetime.now().isoformat(),
                'duration_ms': 10000,  # Very slow launch
                'success': True,
                'timing': 10.0,
                'surface_level': 'L1',
                'interaction_type': 'page_load'
            },
            {
                'step_name': 'Dismiss Copilot Dialog',
                'description': 'Step 4: Dismiss Copilot Dialog - Dismiss the \'Start with Copilot\' dialog that appears when creating a new workbook - Unwanted Copilot dialog appeared, user had to dismiss it manually',
                'start_time': datetime.now().isoformat(),
                'end_time': datetime.now().isoformat(),
                'duration_ms': 3000,  # Slow dialog dismissal
                'success': True,
                'timing': 3.0,
                'dialog_detected': True,
                'dialog_type': 'copilot',
                'surface_level': 'L2',
                'interaction_type': 'dialog_dismiss'
            },
            {
                'step_name': 'Enter Sample Data',
                'description': 'Step 6: Enter Sample Data - Enter sample data in cells using canvas approach - User entered sample data in Excel cells',
                'start_time': datetime.now().isoformat(),
                'end_time': datetime.now().isoformat(),
                'duration_ms': 6000,  # Slow data entry
                'success': True,
                'timing': 6.0,
                'surface_level': 'L1',
                'interaction_type': 'text_input'
            },
            {
                'step_name': 'Click Save Button',
                'description': 'Step 8: Click Save Button - Click the save button to save the workbook - User clicked save button, save dialog appeared',
                'start_time': datetime.now().isoformat(),
                'end_time': datetime.now().isoformat(),
                'duration_ms': 4000,  # Slow save
                'success': True,
                'timing': 4.0,
                'surface_level': 'L1',
                'interaction_type': 'file_save'
            }
        ],
        'total_duration_ms': 33000,
        'success_rate': 100,
        'error_count': 0
    }
    
    print(f"\n🔍 Analyzing {len(sample_telemetry['steps'])} interaction steps...")
    
    # Analyze the scenario with enhanced capabilities
    analysis_results = await analyzer.analyze_scenario_with_enhanced_data(sample_telemetry)
    
    print("\n📊 Analysis Results:")
    print("=" * 50)
    
    # Display Craft bug summary
    craft_bugs = analysis_results.get('enhanced_craft_bugs', [])
    print(f"\n🐛 Craft Bugs Detected: {len(craft_bugs)}")
    
    if craft_bugs:
        print("\n🔍 Detailed Craft Bug Analysis:")
        for i, bug in enumerate(craft_bugs[:10], 1):  # Show first 10
            print(f"\n  {i}. {bug.get('title', 'Unknown Bug')}")
            print(f"     Type: {bug.get('craft_bug_type', 'Unknown')}")
            print(f"     Severity: {bug.get('severity', 'Unknown')}")
            print(f"     Surface: {bug.get('surface_level', 'Unknown')}")
            print(f"     Confidence: {bug.get('confidence', 'Unknown')}")
            print(f"     Impact: {bug.get('user_impact', 'Unknown')}")
            
            # Show persona impact if available
            persona_impact = bug.get('persona_impact', {})
            if persona_impact:
                print(f"     Persona Impact:")
                for persona, impact in persona_impact.items():
                    print(f"       - {persona}: {impact}")
    
    # Display performance analysis
    performance_score = analysis_results.get('overall_compliance_score', 0)
    print(f"\n⚡ Performance Analysis:")
    print(f"   Overall Compliance Score: {performance_score:.1f}/100")
    
    # Display surface level analysis
    surface_distribution = analysis_results.get('surface_level_distribution', {})
    if surface_distribution:
        print(f"\n📐 Surface Level Distribution:")
        for level, count in surface_distribution.items():
            print(f"   {level}: {count} interactions")
    
    # Display UX law violations
    ux_violations = analysis_results.get('ux_law_violations', [])
    print(f"\n📋 UX Law Violations: {len(ux_violations)}")
    for violation in ux_violations[:5]:  # Show first 5
        print(f"   - {violation}")
    
    # Display enhanced analysis summary
    enhanced_analysis = analysis_results.get('enhanced_analysis', {})
    if enhanced_analysis:
        print(f"\n🔬 Enhanced Analysis Summary:")
        
        # Design compliance
        design_compliance = enhanced_analysis.get('design_compliance', {})
        if design_compliance:
            score = design_compliance.get('score', 0)
            print(f"   Design Compliance: {score}/100")
        
        # Surface analysis
        surface_analysis = enhanced_analysis.get('surface_analysis', {})
        if surface_analysis:
            detected_level = surface_analysis.get('detected_level', 'Unknown')
            print(f"   Surface Level: {detected_level}")
        
        # UX law compliance
        ux_compliance = enhanced_analysis.get('ux_law_compliance', {})
        if ux_compliance:
            violations = ux_compliance.get('violations', [])
            print(f"   UX Law Violations: {len(violations)}")
    
    # Display recommendations
    recommendations = analysis_results.get('recommendations', [])
    if recommendations:
        print(f"\n💡 Recommendations:")
        for rec in recommendations[:5]:  # Show first 5
            print(f"   - {rec}")
    
    # Save detailed results
    results_file = f"test_results_enhanced_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(results_file, 'w') as f:
        json.dump(analysis_results, f, indent=2, default=str)
    
    print(f"\n💾 Detailed results saved to: {results_file}")
    
    # Summary
    print(f"\n🎯 Test Summary:")
    print(f"   ✅ Enhanced analyzer successfully processed scenario")
    print(f"   🐛 Detected {len(craft_bugs)} Craft bugs")
    print(f"   ⚡ Performance score: {performance_score:.1f}/100")
    print(f"   📋 UX law violations: {len(ux_violations)}")
    print(f"   🔬 Enhanced analysis capabilities: Active")
    
    return analysis_results

if __name__ == "__main__":
    asyncio.run(test_enhanced_excel_scenario())
