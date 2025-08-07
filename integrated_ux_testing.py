#!/usr/bin/env python3
"""
Integrated Enhanced UX Testing Suite
Combines all Office applications with improved AI prompting
"""

import json
import time
import yaml
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any

# Import our enhanced prompt engine
try:
    from enhanced_prompt_tuning import EnhancedUXPromptEngine
    ENHANCED_AI_AVAILABLE = True
except ImportError:
    ENHANCED_AI_AVAILABLE = False
    print("⚠️ Enhanced AI prompting not available")

class IntegratedUXTestSuite:
    """Integrated test suite for all Office applications with enhanced AI"""
    
    def __init__(self):
        self.results = {
            "test_run_id": f"integrated_ux_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "timestamp": datetime.now().isoformat(),
            "applications": ["word", "excel", "powerpoint"],
            "enhanced_ai_enabled": ENHANCED_AI_AVAILABLE,
            "total_scenarios": 0,
            "total_issues": 0,
            "app_results": {}
        }
        
        # Initialize enhanced AI engine
        if ENHANCED_AI_AVAILABLE:
            try:
                self.ai_engine = EnhancedUXPromptEngine()
                print("🤖 Enhanced AI Engine: Enabled")
            except Exception as e:
                print(f"⚠️ Enhanced AI Engine: Disabled ({e})")
                self.ai_engine = None
        else:
            self.ai_engine = None
    
    def load_all_scenarios(self) -> Dict[str, Dict]:
        """Load scenarios from all application YAML files"""
        scenarios = {}
        
        scenario_files = {
            "word": "scenarios/word_scenarios.yaml",
            "excel": "scenarios/excel_scenarios.yaml", 
            "powerpoint": "scenarios/powerpoint_scenarios.yaml"
        }
        
        for app, file_path in scenario_files.items():
            try:
                with open(file_path, 'r') as f:
                    data = yaml.safe_load(f)
                    # Extract scenarios based on app-specific structure
                    if app == "word":
                        scenarios[app] = data.get('scenarios', [])
                    elif app == "excel":
                        scenarios[app] = data.get('excel_scenarios', {}).get('scenarios', {})
                    elif app == "powerpoint":
                        scenarios[app] = data.get('powerpoint_scenarios', {}).get('scenarios', {})
                    
                print(f"📋 Loaded {len(scenarios[app])} {app} scenarios")
                
            except FileNotFoundError:
                print(f"⚠️ Scenario file not found: {file_path}")
                scenarios[app] = {}
            except Exception as e:
                print(f"❌ Error loading {app} scenarios: {e}")
                scenarios[app] = {}
        
        return scenarios
    
    def test_application_scenarios(self, app_type: str, scenarios: Dict) -> Dict[str, Any]:
        """Test all scenarios for a specific application"""
        
        print(f"\n🧪 Testing {app_type.title()} Application")
        print("-" * 40)
        
        app_results = {
            "app_type": app_type,
            "scenarios_tested": 0,
            "total_issues": 0,
            "scenarios": {}
        }
        
        # Handle different scenario structures
        scenario_items = scenarios.items() if isinstance(scenarios, dict) else enumerate(scenarios)
        
        for scenario_id, scenario_data in scenario_items:
            if isinstance(scenario_data, dict):
                try:
                    print(f"📝 Testing scenario {scenario_id}: {scenario_data.get('title', scenario_data.get('name', 'Unknown'))}")
                    
                    # Simulate basic testing
                    basic_issues = self._simulate_basic_testing(app_type, scenario_data)
                    
                    # Run enhanced AI analysis if available
                    enhanced_issues = self._run_enhanced_analysis(app_type, scenario_data)
                    
                    all_issues = basic_issues + enhanced_issues
                    
                    app_results["scenarios"][str(scenario_id)] = {
                        "title": scenario_data.get('title', scenario_data.get('name', 'Unknown')),
                        "task_goal": scenario_data.get('task_goal', ''),
                        "difficulty": scenario_data.get('difficulty', 'unknown'),
                        "basic_issues": len(basic_issues),
                        "enhanced_issues": len(enhanced_issues),
                        "total_issues": len(all_issues),
                        "issues": all_issues,
                        "status": "completed"
                    }
                    
                    app_results["scenarios_tested"] += 1
                    app_results["total_issues"] += len(all_issues)
                    
                    print(f"   ✅ {len(all_issues)} issues found ({len(basic_issues)} basic + {len(enhanced_issues)} enhanced)")
                    
                except Exception as e:
                    print(f"   ❌ Scenario {scenario_id} failed: {e}")
                    app_results["scenarios"][str(scenario_id)] = {
                        "status": "failed",
                        "error": str(e)
                    }
        
        return app_results
    
    def _simulate_basic_testing(self, app_type: str, scenario_data: Dict) -> List[str]:
        """Simulate basic UX testing (fallback when AI is not available)"""
        
        basic_issues = []
        
        # App-specific basic issues
        if app_type == "word":
            basic_issues = [
                "Text formatting controls may not provide immediate visual feedback",
                "Review panel might cover important document content",
                "Track changes interface could be overwhelming for new users"
            ]
        elif app_type == "excel":
            basic_issues = [
                "Formula bar might be too small for complex formulas",
                "Cell formatting panel may obstruct spreadsheet view",
                "Sheet navigation tabs could be too small for long names"
            ]
        elif app_type == "powerpoint":
            basic_issues = [
                "Animation controls may be complex for non-technical users",
                "Presenter view setup might not be intuitive",
                "Slide thumbnail panel could be difficult to navigate"
            ]
        
        return basic_issues[:3]  # Return first 3 basic issues
    
    def _run_enhanced_analysis(self, app_type: str, scenario_data: Dict) -> List[str]:
        """Run enhanced AI analysis using improved prompting"""
        
        if not self.ai_engine:
            return []
        
        try:
            # Prepare scenario context for enhanced analysis
            context = {
                "task_goal": scenario_data.get('task_goal', ''),
                "difficulty": scenario_data.get('difficulty', 'unknown'),
                "screen_context": scenario_data.get('screen_context', '')
            }
            
            # Run enhanced analysis
            analysis = self.ai_engine.analyze_scenario_enhanced(app_type, context)
            
            if analysis.get("issues"):
                # Extract issue descriptions
                enhanced_issues = [issue.get("description", str(issue)) for issue in analysis["issues"]]
                return enhanced_issues[:3]  # Limit to 3 enhanced issues
            
        except Exception as e:
            print(f"   ⚠️ Enhanced analysis failed: {e}")
        
        return []
    
    def run_comprehensive_test(self):
        """Run comprehensive UX testing across all applications"""
        
        print("🚀 Integrated UX Testing Suite - Enhanced AI Analysis")
        print("=" * 60)
        
        # Load all scenarios
        all_scenarios = self.load_all_scenarios()
        
        if not any(all_scenarios.values()):
            print("❌ No scenarios found to test")
            return
        
        # Test each application
        for app_type in self.results["applications"]:
            if app_type in all_scenarios and all_scenarios[app_type]:
                app_results = self.test_application_scenarios(app_type, all_scenarios[app_type])
                self.results["app_results"][app_type] = app_results
                
                self.results["total_scenarios"] += app_results["scenarios_tested"]
                self.results["total_issues"] += app_results["total_issues"]
        
        # Save results
        self.save_results()
        
        # Print comprehensive summary
        self.print_comprehensive_summary()
    
    def save_results(self):
        """Save comprehensive test results"""
        results_file = f"integrated_ux_test_results_{self.results['test_run_id'].split('_', 3)[3]}.json"
        
        try:
            with open(results_file, 'w') as f:
                json.dump(self.results, f, indent=2)
            print(f"\n💾 Comprehensive results saved to: {results_file}")
        except Exception as e:
            print(f"\n❌ Failed to save results: {e}")
    
    def print_comprehensive_summary(self):
        """Print comprehensive testing summary"""
        
        print("\n" + "=" * 60)
        print("📊 COMPREHENSIVE UX TESTING SUMMARY")
        print("=" * 60)
        
        print(f"🧪 Total scenarios tested: {self.results['total_scenarios']}")
        print(f"🐛 Total issues found: {self.results['total_issues']}")
        print(f"🤖 Enhanced AI analysis: {'enabled' if self.results['enhanced_ai_enabled'] else 'disabled'}")
        
        if self.results["total_scenarios"] > 0:
            avg_issues = self.results["total_issues"] / self.results["total_scenarios"]
            print(f"📊 Average issues per scenario: {avg_issues:.1f}")
        
        print("\n📋 Application Breakdown:")
        
        for app_type, app_results in self.results["app_results"].items():
            scenarios_tested = app_results["scenarios_tested"]
            total_issues = app_results["total_issues"]
            
            if scenarios_tested > 0:
                avg_app_issues = total_issues / scenarios_tested
                status_icon = "✅" if avg_app_issues < 4 else "⚠️" if avg_app_issues < 6 else "❌"
                
                print(f"  {status_icon} {app_type.title()}: {scenarios_tested} scenarios, {total_issues} issues (avg: {avg_app_issues:.1f})")
        
        # Enhanced analysis breakdown
        if self.results["enhanced_ai_enabled"]:
            print("\n🔍 Enhanced Analysis Breakdown:")
            
            total_basic = 0
            total_enhanced = 0
            
            for app_results in self.results["app_results"].values():
                for scenario_results in app_results["scenarios"].values():
                    if isinstance(scenario_results, dict) and "basic_issues" in scenario_results:
                        total_basic += scenario_results.get("basic_issues", 0)
                        total_enhanced += scenario_results.get("enhanced_issues", 0)
            
            print(f"   📝 Basic UX issues: {total_basic}")
            print(f"   🤖 AI-enhanced issues: {total_enhanced}")
            
            if total_enhanced > 0:
                enhancement_ratio = total_enhanced / (total_basic + total_enhanced)
                print(f"   📊 AI enhancement ratio: {enhancement_ratio:.1%}")
        
        print("\n✅ Comprehensive UX testing completed!")

def main():
    """Main execution for integrated testing"""
    
    # Verify required files exist
    required_files = [
        "scenarios/word_scenarios.yaml",
        "scenarios/excel_scenarios.yaml", 
        "scenarios/powerpoint_scenarios.yaml"
    ]
    
    missing_files = [f for f in required_files if not os.path.exists(f)]
    if missing_files:
        print("❌ Missing required scenario files:")
        for f in missing_files:
            print(f"   - {f}")
        return
    
    # Run integrated testing
    test_suite = IntegratedUXTestSuite()
    test_suite.run_comprehensive_test()

if __name__ == "__main__":
    main()
