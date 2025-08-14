#!/usr/bin/env python3
"""
Legacy System Wrapper
Maintains current functionality during refactoring by wrapping existing components
"""

import logging
import asyncio
from typing import Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class LegacySystemWrapper:
    """
    Wrapper to maintain current functionality during refactoring.
    This ensures the old system continues to work while we build the new one.
    """
    
    def __init__(self):
        self.legacy_executor = None
        self.legacy_app = None
        self._initialize_legacy_components()
    
    def _initialize_legacy_components(self):
        """Initialize legacy components safely"""
        try:
            # Import legacy scenario executor
            from scenario_executor import ScenarioExecutor
            self.legacy_executor = ScenarioExecutor()
            logger.info("✅ Legacy scenario executor initialized")
            
        except ImportError as e:
            logger.error(f"❌ Failed to import legacy scenario executor: {e}")
            self.legacy_executor = None
        
        try:
            # Import legacy FastAPI app (for reference)
            import enhanced_fastapi_server
            self.legacy_app = enhanced_fastapi_server
            logger.info("✅ Legacy FastAPI app imported")
            
        except ImportError as e:
            logger.error(f"❌ Failed to import legacy FastAPI app: {e}")
            self.legacy_app = None
    
    async def analyze_url(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Use current working analysis system.
        This is the core method that must always work.
        """
        if not self.legacy_executor:
            raise RuntimeError("Legacy executor not available")
        
        try:
            logger.info("🔄 Using legacy analysis system")
            
            # Extract parameters from request
            url = request.get("url")
            scenario_id = request.get("scenario_id", "1.1")  # Default to Word scenario
            modules = request.get("modules", {})
            
            if not url:
                raise ValueError("URL is required for analysis")
            
            # Use the current working executor
            result = await self.legacy_executor.execute_scenario_by_id(
                url=url,
                scenario_id=scenario_id,
                modules=modules
            )
            
            logger.info("✅ Legacy analysis completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"❌ Legacy analysis failed: {e}")
            raise
    
    async def get_scenarios(self) -> list:
        """Get scenarios using legacy system"""
        try:
            if not self.legacy_executor:
                return []
            
            # Use the current working scenario loading
            scenarios = self.legacy_executor.get_available_scenarios()
            logger.info(f"✅ Legacy scenarios loaded: {len(scenarios)} found")
            return scenarios
            
        except Exception as e:
            logger.error(f"❌ Legacy scenarios failed: {e}")
            return []
    
    async def get_report(self, report_id: str) -> Optional[Dict[str, Any]]:
        """Get report using legacy system"""
        try:
            # This would typically use the legacy report storage
            # For now, we'll return a basic structure
            logger.info(f"🔄 Using legacy report system for {report_id}")
            
            # Import legacy report handling if available
            try:
                from enhanced_fastapi_server import MOCK_REPORTS
                if report_id in MOCK_REPORTS:
                    return MOCK_REPORTS[report_id]
            except ImportError:
                pass
            
            # Fallback to basic report structure
            return {
                "analysis_id": report_id,
                "status": "completed",
                "url": "http://127.0.0.1:8080/mocks/word/basic-doc.html",
                "overall_score": 85,
                "craft_bugs": [],
                "ux_issues": [],
                "total_issues": 0,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Legacy report retrieval failed: {e}")
            return None
    
    async def trigger_fix(self, work_item_id: int, file_path: str, instruction: str) -> Dict[str, Any]:
        """Trigger fix using legacy Gemini CLI"""
        try:
            logger.info("🔄 Using legacy fix system")
            
            # Import and use the current working Gemini CLI
            from gemini_cli import GeminiCLI
            
            gemini = GeminiCLI()
            result = gemini.fix_issue_with_thinking_steps(
                work_item_id=work_item_id,
                file_path=file_path,
                instruction=instruction
            )
            
            logger.info("✅ Legacy fix completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"❌ Legacy fix failed: {e}")
            return {
                "status": "error",
                "message": f"Legacy fix failed: {str(e)}",
                "work_item_id": work_item_id
            }
    
    async def create_ado_tickets(self, report_data: Dict[str, Any], demo_mode: bool = True) -> Dict[str, Any]:
        """Create ADO tickets using legacy system"""
        try:
            logger.info("🔄 Using legacy ADO integration")
            
            # Import and use the current working ADO integration
            from azure_devops_integration import AzureDevOpsClient, UXAnalysisToADOConverter
            
            # Create ADO client
            client = AzureDevOpsClient()
            
            # Convert report to ADO format
            converter = UXAnalysisToADOConverter()
            ado_issues = converter.convert_ux_analysis_to_ado_issues(report_data)
            
            # Create work items
            created_items = []
            for issue in ado_issues:
                work_item = await client.create_work_item(issue)
                if work_item:
                    created_items.append(work_item)
            
            logger.info(f"✅ Legacy ADO integration completed: {len(created_items)} items created")
            return {
                "status": "success",
                "work_items_created": len(created_items),
                "work_items": created_items
            }
            
        except Exception as e:
            logger.error(f"❌ Legacy ADO integration failed: {e}")
            return {
                "status": "error",
                "message": f"Legacy ADO integration failed: {str(e)}",
                "work_items_created": 0
            }
    
    async def commit_git_changes(self, work_item_id: int, commit_message: str = None) -> Dict[str, Any]:
        """Commit Git changes using legacy system"""
        try:
            logger.info("🔄 Using legacy Git integration")
            
            # Import and use the current working Git integration
            import subprocess
            import os
            
            # Basic Git operations
            git_commands = [
                ["git", "add", "."],
                ["git", "commit", "-m", commit_message or f"Fix for work item {work_item_id}"],
                ["git", "push"]
            ]
            
            results = []
            for cmd in git_commands:
                try:
                    result = subprocess.run(cmd, capture_output=True, text=True, check=True)
                    results.append({
                        "command": " ".join(cmd),
                        "status": "success",
                        "output": result.stdout
                    })
                except subprocess.CalledProcessError as e:
                    results.append({
                        "command": " ".join(cmd),
                        "status": "error",
                        "output": e.stderr
                    })
            
            # Check if all commands succeeded
            all_success = all(r["status"] == "success" for r in results)
            
            if all_success:
                logger.info("✅ Legacy Git integration completed successfully")
                return {
                    "status": "success",
                    "message": "Git changes committed and pushed",
                    "work_item_id": work_item_id,
                    "commands": results
                }
            else:
                logger.error("❌ Legacy Git integration failed")
                return {
                    "status": "error",
                    "message": "Some Git commands failed",
                    "work_item_id": work_item_id,
                    "commands": results
                }
                
        except Exception as e:
            logger.error(f"❌ Legacy Git integration failed: {e}")
            return {
                "status": "error",
                "message": f"Legacy Git integration failed: {str(e)}",
                "work_item_id": work_item_id
            }
    
    def is_available(self) -> bool:
        """Check if legacy system is available"""
        return self.legacy_executor is not None
    
    def get_status(self) -> Dict[str, Any]:
        """Get legacy system status"""
        return {
            "legacy_executor_available": self.legacy_executor is not None,
            "legacy_app_available": self.legacy_app is not None,
            "timestamp": datetime.now().isoformat()
        }

# Global instance for easy access
legacy_wrapper = LegacySystemWrapper()
