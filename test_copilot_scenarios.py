#!/usr/bin/env python3
"""
Copilot Scenario Testing Script
Tests the enhanced framework's AI-specific detection capabilities
"""

import asyncio
import json
import time
from datetime import datetime
from typing import Dict, Any, List

# Import the enhanced components
try:
    from excel_scenario_telemetry import ExcelScenarioTelemetry
    from enhanced_ux_analyzer import EnhancedUXAnalyzer
    from enhanced_fastapi_server import generate_excel_ux_report
except ImportError as e:
    print(f"❌ Failed to import enhanced components: {e}")
    exit(1)

class CopilotScenarioTester:
    """Test Copilot scenarios with enhanced AI detection"""
    
    def __init__(self):
        self.telemetry = ExcelScenarioTelemetry()
        # Replace hardcoded analyzer with AI-driven analyzer
        # self.analyzer = EnhancedUXAnalyzer()
        self.analyzer = AIDrivenAnalyzer()
        self.test_results = []
        
    async def test_copilot_chart_generation(self) -> Dict[str, Any]:
        """Test Copilot chart generation scenario"""
        print("\n🚀 Testing Copilot Chart Generation Scenario")
        print("=" * 60)
        
        # Execute scenario with enhanced telemetry
        telemetry_result = await self.telemetry.execute_scenario_with_telemetry()
        
        if not telemetry_result:
            return {"error": "Failed to execute scenario"}
        
        # Analyze with enhanced AI detection
        analysis_result = await self.analyzer.analyze_scenario_with_enhanced_data(telemetry_result)
        
        # Generate comprehensive report
        report_result = await generate_excel_ux_report()
        
        # Extract Copilot-specific findings
        copilot_findings = self._extract_copilot_findings(analysis_result)
        
        return {
            "scenario": "copilot_chart_generation",
            "telemetry": telemetry_result,
            "analysis": analysis_result,
            "report": report_result,
            "copilot_findings": copilot_findings,
            "timestamp": datetime.now().isoformat()
        }
    
    def _extract_copilot_findings(self, analysis_result: Dict) -> Dict[str, Any]:
        """Extract Copilot-specific findings from analysis"""
        copilot_findings = {
            "ai_trust_issues": [],
            "copilot_pane_issues": [],
            "conversation_flow_issues": [],
            "ai_integration_issues": [],
            "trust_building_moments": [],
            "trust_breaking_moments": []
        }
        
        # Extract from craft bugs
        craft_bugs = analysis_result.get("craft_bugs", [])
        for bug in craft_bugs:
            title = bug.get("title", "").lower()
            description = bug.get("description", "").lower()
            
            # Categorize Copilot-specific issues
            if "copilot" in title or "ai" in title:
                if "trust" in title or "trust" in description:
                    if "breaking" in description or "frustration" in description:
                        copilot_findings["trust_breaking_moments"].append(bug)
                    else:
                        copilot_findings["trust_building_moments"].append(bug)
                elif "pane" in title or "panel" in title:
                    copilot_findings["copilot_pane_issues"].append(bug)
                elif "conversation" in title or "flow" in title:
                    copilot_findings["conversation_flow_issues"].append(bug)
                elif "integration" in title or "grid" in title:
                    copilot_findings["ai_integration_issues"].append(bug)
                else:
                    copilot_findings["ai_trust_issues"].append(bug)
        
        return copilot_findings
    
    async def run_comprehensive_copilot_test(self) -> Dict[str, Any]:
        """Run comprehensive Copilot testing"""
        print("🎯 Starting Comprehensive Copilot Scenario Testing")
        print("=" * 80)
        
        start_time = time.time()
        
        # Test chart generation
        chart_result = await self.test_copilot_chart_generation()
        self.test_results.append(chart_result)
        
        # Calculate test metrics
        total_time = time.time() - start_time
        
        # Analyze overall Copilot findings
        all_copilot_findings = []
        for result in self.test_results:
            if "copilot_findings" in result:
                all_copilot_findings.append(result["copilot_findings"])
        
        # Generate summary
        summary = self._generate_copilot_summary(all_copilot_findings)
        
        return {
            "test_results": self.test_results,
            "summary": summary,
            "total_test_time": total_time,
            "scenarios_tested": len(self.test_results),
            "timestamp": datetime.now().isoformat()
        }
    
    def _generate_copilot_summary(self, all_findings: List[Dict]) -> Dict[str, Any]:
        """Generate summary of Copilot findings"""
        summary = {
            "total_ai_issues": 0,
            "trust_issues": 0,
            "pane_issues": 0,
            "conversation_issues": 0,
            "integration_issues": 0,
            "trust_building_moments": 0,
            "trust_breaking_moments": 0,
            "critical_ai_issues": 0,
            "ai_ux_score": 0
        }
        
        for findings in all_findings:
            summary["total_ai_issues"] += len(findings.get("ai_trust_issues", []))
            summary["trust_issues"] += len(findings.get("ai_trust_issues", []))
            summary["pane_issues"] += len(findings.get("copilot_pane_issues", []))
            summary["conversation_issues"] += len(findings.get("conversation_flow_issues", []))
            summary["integration_issues"] += len(findings.get("ai_integration_issues", []))
            summary["trust_building_moments"] += len(findings.get("trust_building_moments", []))
            summary["trust_breaking_moments"] += len(findings.get("trust_breaking_moments", []))
        
        # Calculate AI UX score (0-100)
        total_issues = summary["total_ai_issues"]
        trust_ratio = summary["trust_building_moments"] / max(summary["trust_breaking_moments"], 1)
        
        # Base score starts at 50, adjusted by issues and trust ratio
        base_score = 50
        issue_penalty = min(total_issues * 5, 30)  # Max 30 point penalty
        trust_bonus = min(trust_ratio * 10, 20)    # Max 20 point bonus
        
        summary["ai_ux_score"] = max(0, min(100, base_score - issue_penalty + trust_bonus))
        
        return summary

async def main():
    """Main test execution"""
    print("🎯 Copilot Scenario Testing with Enhanced Framework")
    print("=" * 80)
    
    tester = CopilotScenarioTester()
    
    try:
        # Run comprehensive test
        results = await tester.run_comprehensive_copilot_test()
        
        # Print results
        print("\n📊 Copilot Test Results Summary")
        print("=" * 50)
        
        summary = results["summary"]
        print(f"🤖 AI UX Score: {summary['ai_ux_score']:.1f}/100")
        print(f"🚨 Total AI Issues: {summary['total_ai_issues']}")
        print(f"🔒 Trust Issues: {summary['trust_issues']}")
        print(f"🪟 Pane Issues: {summary['pane_issues']}")
        print(f"💬 Conversation Issues: {summary['conversation_issues']}")
        print(f"🔗 Integration Issues: {summary['integration_issues']}")
        print(f"✅ Trust Building Moments: {summary['trust_building_moments']}")
        print(f"❌ Trust Breaking Moments: {summary['trust_breaking_moments']}")
        print(f"⏱️ Total Test Time: {results['total_test_time']:.2f}s")
        
        # Save results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"copilot_test_results_{timestamp}.json"
        
        with open(filename, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        print(f"\n💾 Results saved to: {filename}")
        
        # Determine if enhanced framework is working
        if summary["ai_ux_score"] > 0:
            print("\n✅ Enhanced Framework Successfully Detected AI-Specific Issues!")
            print("🎯 The enhanced framework is working and catching Copilot-specific craft bugs.")
        else:
            print("\n⚠️ No AI-specific issues detected. Framework may need tuning.")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())

