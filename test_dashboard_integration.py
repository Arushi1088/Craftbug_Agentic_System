#!/usr/bin/env python3
"""
Test Dashboard Integration with FinalCraftBugAnalyzer
"""

import asyncio
from enhanced_ux_analyzer import EnhancedUXAnalyzer

async def test_dashboard_integration():
    """Test that the dashboard is using the FinalCraftBugAnalyzer"""
    
    print("🎯 Testing Dashboard Integration with FinalCraftBugAnalyzer")
    
    # Sample telemetry data
    telemetry_data = {
        'scenario_name': 'Excel Document Creation with Copilot',
        'steps': [
            {
                'name': 'Navigate to Excel',
                'description': 'User navigates to Excel web app',
                'screenshot_path': 'screenshots/excel_web/excel_initial_state_1756061972.png',
                'timing': 2.5,
                'success': True
            },
            {
                'name': 'Dismiss Copilot Dialog',
                'description': 'User dismisses the Copilot dialog',
                'screenshot_path': 'screenshots/excel_web/excel_copilot_dialog_1756061967.png',
                'timing': 1.8,
                'success': True
            },
            {
                'name': 'Save Workbook',
                'description': 'User saves the workbook',
                'screenshot_path': 'screenshots/excel_web/excel_final_state_1755521895.png',
                'timing': 3.2,
                'success': True
            }
        ],
        'success_rate': 100
    }
    
    # Initialize the enhanced analyzer (same as dashboard)
    analyzer = EnhancedUXAnalyzer()
    
    print("🚀 Running analysis with FinalCraftBugAnalyzer...")
    
    # Run the analysis
    result = await analyzer.analyze_scenario_with_enhanced_data(telemetry_data)
    
    print(f"\n📊 Analysis Results:")
    print(f"   Total bugs found: {result.get('total_llm_bugs', 0)}")
    print(f"   LLM bugs: {len(result.get('llm_generated_bugs', []))}")
    print(f"   Enhanced bugs: {len(result.get('enhanced_craft_bugs', []))}")
    
    if result.get('llm_generated_bugs'):
        print(f"\n🔍 Sample Bugs:")
        for i, bug in enumerate(result['llm_generated_bugs'][:3], 1):
            print(f"   Bug {i}: {bug.get('title', 'Unknown')}")
            print(f"      Type: {bug.get('type', 'Unknown')}")
            print(f"      Severity: {bug.get('severity', 'Unknown')}")
            if 'confidence' in bug:
                print(f"      Confidence: {bug.get('confidence', 'Unknown')}")
            print()
    
    print("✅ Dashboard integration test complete!")
    print("🌐 You can now test the dashboard at: http://127.0.0.1:8081/")

if __name__ == "__main__":
    asyncio.run(test_dashboard_integration())

