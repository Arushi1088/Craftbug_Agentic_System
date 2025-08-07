#!/usr/bin/env python3
"""
Test script to verify screenshot functionality
"""

import asyncio
import json
from enhanced_scenario_runner import execute_realistic_scenario

async def test_screenshot_capture():
    """Test screenshot capture with a simple scenario"""
    
    print("🧪 Testing Step 4: Screenshot Capture")
    print("=" * 50)
    
    # Test with a real URL and the basic navigation scenario
    try:
        result = await execute_realistic_scenario(
            url="https://example.com",
            scenario_path="scenarios/basic_navigation.yaml",
            headless=True
        )
        
        print(f"✅ Scenario executed: {result.get('status', 'unknown')}")
        print(f"📊 Overall score: {result.get('overall_score', 'N/A')}")
        print(f"📸 Has screenshots: {result.get('has_screenshots', False)}")
        
        steps = result.get('steps', [])
        print(f"🎯 Total steps: {len(steps)}")
        
        screenshot_count = 0
        for i, step in enumerate(steps):
            if step.get('screenshot'):
                screenshot_count += 1
                print(f"   Step {i+1}: {step.get('action')} - 📸 {step.get('screenshot')}")
            else:
                print(f"   Step {i+1}: {step.get('action')} - ❌ No screenshot")
        
        print(f"📸 Screenshots captured: {screenshot_count}/{len(steps)}")
        
        # Save result to a test report for frontend viewing
        test_report = {
            "analysis_id": result.get('analysis_id', 'test12345'),
            "timestamp": result.get('timestamp', '2025-08-07T19:30:00.000Z'),
            "type": "url_scenario",
            "url": "https://example.com",
            "scenario_file": "basic_navigation.yaml",
            "overall_score": result.get('overall_score', 85),
            "has_screenshots": result.get('has_screenshots', False),
            "scenario_results": [{
                "name": "Screenshot Test Scenario",
                "score": result.get('overall_score', 85),
                "status": result.get('status', 'completed'),
                "duration_ms": result.get('total_duration_ms', 5000),
                "steps": steps
            }],
            "module_results": {
                "performance": {
                    "score": 85,
                    "threshold_met": True,
                    "analytics_enabled": False,
                    "findings": [],
                    "recommendations": ["Test screenshot capture functionality"]
                }
            }
        }
        
        # Save to a test report file
        with open('reports/analysis/screenshot_test_report.json', 'w') as f:
            json.dump(test_report, f, indent=2)
        
        print(f"✅ Test report saved: screenshot_test_report.json")
        
        return result
        
    except Exception as e:
        print(f"❌ Error during screenshot test: {e}")
        return None

if __name__ == "__main__":
    asyncio.run(test_screenshot_capture())
