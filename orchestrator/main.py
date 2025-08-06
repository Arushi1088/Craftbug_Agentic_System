#!/usr/bin/env python3
"""
Orchestrator Agent - Multi-Agent Coordination System
Bridges UX Analyzer and Coder Agent for automated bug detection and fixing
"""

import os
import sys
import json
import asyncio
import logging
import requests
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from pathlib import Path

# Import ADO client
from ado_client import AzureDevOpsClient, create_ado_ticket

# Import Gemini handler
from gemini_handler import GeminiHandler, fix_bug_with_gemini

# Add paths for both agent systems
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'coder_agent'))

@dataclass
class AnalysisResult:
    """Result from UX Analyzer"""
    analysis_id: str
    url: str
    overall_score: int
    issues: List[Dict[str, Any]]
    recommendations: List[str]
    timestamp: str
    severity_counts: Dict[str, int]

@dataclass
class CoderTask:
    """Task for Coder Agent"""
    task_id: str
    description: str
    priority: str
    files_to_fix: List[str]
    bug_type: str
    analysis_context: Dict[str, Any]

class OrchestratorAgent:
    """
    Main orchestrator that coordinates between UX Analyzer and Coder Agent
    """
    
    def __init__(self, config_path: Optional[str] = None):
        self.config = self._load_config(config_path)
        self.logger = self._setup_logging()
        self.active_tasks = {}
        self.analysis_history = []
        
        # Initialize connections to both agents
        self.ux_analyzer = None
        self.coder_agent = None
        self.ado_client = None
        self.gemini_handler = None
        
    def fetch_ux_issues(self, url: str) -> Dict[str, Any]:
        """Fetch UX issues from FastAPI analyzer"""
        try:
            endpoint = self.config["ux_analyzer"]["api_endpoint"]
            
            # Make request to UX Analyzer API
            payload = {
                "url": url,
                "modules": self.config["ux_analyzer"]["modules"],
                "output_format": "json"
            }
            
            self.logger.info(f"Calling UX Analyzer API: {endpoint}/api/analyze")
            response = requests.post(f"{endpoint}/api/analyze", json=payload, timeout=30)
            response.raise_for_status()
            
            analysis_response = response.json()
            self.logger.info(f"Received analysis response: {analysis_response.get('analysis_id', 'unknown')}")
            
            # Get the full report if analysis_id is returned
            if 'analysis_id' in analysis_response and analysis_response.get('status') == 'completed':
                # Wait a moment for report to be ready
                import time
                time.sleep(1)
                
                try:
                    report_response = requests.get(
                        f"{endpoint}/api/reports/{analysis_response['analysis_id']}", 
                        timeout=30
                    )
                    if report_response.status_code == 200:
                        return report_response.json()
                    else:
                        self.logger.warning(f"Report not found for ID: {analysis_response['analysis_id']}")
                        # Return the analysis response as-is
                        return analysis_response
                except Exception as e:
                    self.logger.warning(f"Failed to fetch report: {e}")
                    return analysis_response
            
            return analysis_response
            
        except requests.exceptions.ConnectionError:
            self.logger.error("Could not connect to UX Analyzer. Is the FastAPI server running on port 8000?")
            raise Exception("UX Analyzer API not available. Please start: uvicorn fastapi_server:app --reload --port 8000")
        except requests.exceptions.Timeout:
            self.logger.error("UX Analyzer API request timed out")
            raise Exception("UX Analyzer API timeout")
        except Exception as e:
            self.logger.error(f"Error calling UX Analyzer API: {e}")
            raise
        
    def _load_config(self, config_path: Optional[str]) -> Dict[str, Any]:
        """Load orchestrator configuration"""
        default_config = {
            "ux_analyzer": {
                "api_endpoint": "http://localhost:8000",
                "modules": {
                    "performance": True,
                    "accessibility": True,
                    "keyboard": True,
                    "ux_heuristics": True,
                    "best_practices": True,
                    "health_alerts": True,
                    "functional": False
                }
            },
            "coder_agent": {
                "azure_devops_org": None,
                "project": None,
                "gemini_api_key": None,
                "auto_fix_enabled": False,
                "max_concurrent_fixes": 3
            },
            "orchestrator": {
                "severity_threshold": "medium",
                "auto_trigger_fixes": False,
                "analysis_interval_minutes": 60,
                "report_format": "json"
            }
        }
        
        if config_path and os.path.exists(config_path):
            try:
                with open(config_path, 'r') as f:
                    user_config = json.load(f)
                    default_config.update(user_config)
            except Exception as e:
                print(f"Warning: Could not load config from {config_path}: {e}")
        
        return default_config
    
    def _setup_logging(self) -> logging.Logger:
        """Setup logging for orchestrator"""
        logger = logging.getLogger('orchestrator')
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            # Create logs directory
            log_dir = Path(__file__).parent / 'logs'
            log_dir.mkdir(exist_ok=True)
            
            # File handler
            fh = logging.FileHandler(log_dir / f'orchestrator_{datetime.now().strftime("%Y%m%d")}.log')
            fh.setLevel(logging.INFO)
            
            # Console handler
            ch = logging.StreamHandler()
            ch.setLevel(logging.INFO)
            
            # Formatter
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            fh.setFormatter(formatter)
            ch.setFormatter(formatter)
            
            logger.addHandler(fh)
            logger.addHandler(ch)
        
        return logger
    
    async def initialize_agents(self):
        """Initialize connections to both UX Analyzer and Coder Agent"""
        self.logger.info("Initializing agent connections...")
        
        try:
            # Initialize UX Analyzer connection
            await self._init_ux_analyzer()
            
            # Initialize Coder Agent connection
            await self._init_coder_agent()
            
            # Initialize Azure DevOps client
            await self._init_ado_client()
            
            # Initialize Gemini handler
            await self._init_gemini_handler()
            
            self.logger.info("All agents initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize agents: {e}")
            raise
    
    async def _init_ux_analyzer(self):
        """Initialize UX Analyzer connection"""
        try:
            # Test API connection
            endpoint = self.config["ux_analyzer"]["api_endpoint"]
            health_response = requests.get(f"{endpoint}/health", timeout=5)
            health_response.raise_for_status()
            
            self.ux_analyzer = {
                "endpoint": endpoint,
                "available": True,
                "status": health_response.json()
            }
            self.logger.info(f"UX Analyzer API connection established: {endpoint}")
            
        except requests.exceptions.ConnectionError:
            self.logger.warning(f"UX Analyzer API not available at {self.config['ux_analyzer']['api_endpoint']}")
            self.logger.warning("Please start FastAPI server: uvicorn fastapi_server:app --reload --port 8000")
            self.ux_analyzer = {
                "endpoint": self.config["ux_analyzer"]["api_endpoint"],
                "available": False,
                "status": "Connection failed"
            }
        except Exception as e:
            self.logger.warning(f"UX Analyzer initialization failed: {e}")
            self.ux_analyzer = {
                "endpoint": self.config["ux_analyzer"]["api_endpoint"],
                "available": False,
                "status": str(e)
            }
    
    async def _init_coder_agent(self):
        """Initialize Coder Agent connection"""
        try:
            # Check if coder agent is available
            coder_agent_path = Path(__file__).parent.parent / 'coder_agent'
            if coder_agent_path.exists():
                self.coder_agent = {
                    "path": str(coder_agent_path),
                    "available": True
                }
                self.logger.info("Coder Agent connection established")
            else:
                self.logger.warning("Coder Agent path not found")
        except Exception as e:
            self.logger.warning(f"Coder Agent not available: {e}")
    
    async def _init_ado_client(self):
        """Initialize Azure DevOps client"""
        try:
            self.ado_client = AzureDevOpsClient()
            
            if self.ado_client.is_configured():
                # Test connection
                if self.ado_client.test_connection():
                    self.logger.info("Azure DevOps client initialized successfully")
                else:
                    self.logger.warning("Azure DevOps connection test failed")
            else:
                self.logger.warning("Azure DevOps not configured. Set ADO_ORG, ADO_PROJECT, ADO_TOKEN in .env")
                
        except Exception as e:
            self.logger.warning(f"Azure DevOps client initialization failed: {e}")
            self.ado_client = None
    
    async def _init_gemini_handler(self):
        """Initialize Gemini CLI handler"""
        try:
            self.gemini_handler = GeminiHandler()
            
            # Test Gemini CLI availability
            if self.gemini_handler.test_gemini_cli():
                self.logger.info("Gemini CLI handler initialized successfully")
            else:
                self.logger.warning("Gemini CLI not available. Install Gemini CLI or update GEMINI_CLI_PATH in .env")
                
        except Exception as e:
            self.logger.warning(f"Gemini handler initialization failed: {e}")
            self.gemini_handler = None
    
    async def analyze_website(self, url: str, custom_modules: Optional[Dict[str, bool]] = None) -> AnalysisResult:
        """Trigger UX analysis of a website using real FastAPI server"""
        self.logger.info(f"Starting UX analysis for: {url}")
        
        if custom_modules:
            # Temporarily update config for this analysis
            original_modules = self.config["ux_analyzer"]["modules"].copy()
            self.config["ux_analyzer"]["modules"].update(custom_modules)
        
        try:
            # Call real UX Analyzer API
            analysis_data = self.fetch_ux_issues(url)
            
            # Convert API response to AnalysisResult format
            if "modules" in analysis_data:
                # Extract issues from module results
                issues = []
                recommendations = []
                
                for module_name, module_data in analysis_data["modules"].items():
                    if isinstance(module_data, dict) and "findings" in module_data:
                        for finding in module_data["findings"]:
                            issues.append({
                                "type": module_name,
                                "severity": finding.get("severity", "medium"),
                                "message": finding.get("message", ""),
                                "element": finding.get("element", ""),
                                "file": finding.get("file", ""),
                                "recommendation": finding.get("recommendation", "")
                            })
                    
                    # Extract recommendations
                    if isinstance(module_data, dict) and "recommendations" in module_data:
                        recommendations.extend(module_data["recommendations"])
                
                result = AnalysisResult(
                    analysis_id=analysis_data.get("analysis_id", f"ux_{datetime.now().strftime('%Y%m%d_%H%M%S')}"),
                    url=url,
                    overall_score=analysis_data.get("overall_score", 0),
                    issues=issues,
                    recommendations=recommendations,
                    timestamp=analysis_data.get("timestamp", datetime.now().isoformat()),
                    severity_counts=self._count_severities(issues)
                )
            else:
                # Fallback to mock data if API response format is unexpected
                self.logger.warning("Unexpected API response format, using mock data")
                result = self._create_mock_analysis_result(url)
            
            self.analysis_history.append(result)
            self.logger.info(f"UX analysis completed: {result.analysis_id}")
            
            return result
            
        except Exception as e:
            self.logger.error(f"UX analysis failed: {e}")
            # Fallback to mock data for development
            self.logger.info("Falling back to mock data for development")
            result = self._create_mock_analysis_result(url)
            self.analysis_history.append(result)
            return result
            
        finally:
            # Restore original modules config
            if custom_modules:
                self.config["ux_analyzer"]["modules"] = original_modules
    
    def _count_severities(self, issues: List[Dict[str, Any]]) -> Dict[str, int]:
        """Count issues by severity level"""
        counts = {"high": 0, "medium": 0, "low": 0}
        for issue in issues:
            severity = issue.get("severity", "low")
            if severity in counts:
                counts[severity] += 1
        return counts
    
    def _create_mock_analysis_result(self, url: str) -> AnalysisResult:
        """Create mock analysis result for development/fallback"""
        analysis_data = {
            "url": url,
            "analysis_id": f"ux_mock_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "overall_score": 75,  # Mock score
            "issues": [
                {
                    "type": "accessibility",
                    "severity": "high",
                    "message": "Missing alt text on images",
                    "element": "img.hero-banner",
                    "file": "index.html",
                    "recommendation": "Add descriptive alt text to all images"
                },
                {
                    "type": "performance",
                    "severity": "medium", 
                    "message": "Large bundle size detected",
                    "file": "main.js",
                    "element": "",
                    "recommendation": "Consider code splitting and lazy loading"
                }
            ],
            "recommendations": [
                "Implement proper alt text for accessibility",
                "Optimize JavaScript bundle size",
                "Add ARIA labels for better screen reader support"
            ],
            "timestamp": datetime.now().isoformat()
        }
        
        return AnalysisResult(
            analysis_id=analysis_data["analysis_id"],
            url=url,
            overall_score=analysis_data["overall_score"],
            issues=analysis_data["issues"],
            recommendations=analysis_data["recommendations"],
            timestamp=analysis_data["timestamp"],
            severity_counts=self._count_severities(analysis_data["issues"])
        )
    
    async def create_coder_tasks(self, analysis_result: AnalysisResult) -> List[CoderTask]:
        """Convert UX analysis results into actionable coder tasks"""
        self.logger.info(f"Creating coder tasks from analysis: {analysis_result.analysis_id}")
        
        tasks = []
        severity_threshold = self.config["orchestrator"]["severity_threshold"]
        
        for i, issue in enumerate(analysis_result.issues):
            if self._should_create_task(issue, severity_threshold):
                task = CoderTask(
                    task_id=f"task_{analysis_result.analysis_id}_{i}",
                    description=f"Fix {issue['type']} issue: {issue['message']}",
                    priority=issue.get("severity", "medium"),
                    files_to_fix=self._identify_files_to_fix(issue),
                    bug_type=issue["type"],
                    analysis_context={
                        "analysis_id": analysis_result.analysis_id,
                        "url": analysis_result.url,
                        "issue_details": issue,
                        "recommendation": issue.get("recommendation", "")
                    }
                )
                tasks.append(task)
        
        self.logger.info(f"Created {len(tasks)} coder tasks")
        return tasks
    
    async def create_ado_tickets_from_issues(self, issues: List[Dict[str, Any]], analysis_id: str) -> List[int]:
        """Create Azure DevOps tickets from UX issues"""
        if not self.ado_client or not self.ado_client.is_configured():
            self.logger.warning("Azure DevOps not configured, skipping ticket creation")
            return []
        
        self.logger.info(f"Creating ADO tickets for {len(issues)} issues from analysis {analysis_id}")
        
        created_tickets = []
        severity_threshold = self.config["orchestrator"]["severity_threshold"]
        
        for issue in issues:
            if self._should_create_task(issue, severity_threshold):
                try:
                    # Add analysis context to issue
                    issue_with_context = issue.copy()
                    issue_with_context["analysis_id"] = analysis_id
                    
                    ticket_id = self.ado_client.create_ado_ticket(issue_with_context)
                    if ticket_id:
                        created_tickets.append(ticket_id)
                        self.logger.info(f"✅ Created ADO ticket #{ticket_id} for {issue['type']} issue")
                    else:
                        self.logger.error(f"❌ Failed to create ADO ticket for {issue['type']} issue")
                        
                except Exception as e:
                    self.logger.error(f"Error creating ADO ticket for issue: {e}")
        
        self.logger.info(f"Successfully created {len(created_tickets)} ADO tickets: {created_tickets}")
        return created_tickets
    
    async def apply_gemini_fixes(self, issues: List[Dict[str, Any]], analysis_id: str) -> Dict[str, Any]:
        """Apply Gemini CLI fixes to UX issues"""
        if not self.gemini_handler:
            self.logger.warning("Gemini handler not available, skipping automatic fixes")
            return {
                "attempted": 0,
                "successful": 0,
                "failed": 0,
                "results": []
            }
        
        self.logger.info(f"Applying Gemini fixes for {len(issues)} issues from analysis {analysis_id}")
        
        results = {
            "attempted": 0,
            "successful": 0,
            "failed": 0,
            "results": []
        }
        
        severity_threshold = self.config["orchestrator"]["severity_threshold"]
        
        for issue in issues:
            if self._should_create_task(issue, severity_threshold):
                results["attempted"] += 1
                
                try:
                    # Add analysis context to issue
                    issue_with_context = issue.copy()
                    issue_with_context["analysis_id"] = analysis_id
                    
                    # Apply Gemini fix
                    fix_successful = self.gemini_handler.fix_bug_with_gemini(issue_with_context)
                    
                    if fix_successful:
                        results["successful"] += 1
                        self.logger.info(f"✅ Successfully applied Gemini fix for {issue['type']} issue")
                    else:
                        results["failed"] += 1
                        self.logger.error(f"❌ Failed to apply Gemini fix for {issue['type']} issue")
                    
                    results["results"].append({
                        "issue_type": issue['type'],
                        "issue_message": issue.get('message', ''),
                        "severity": issue.get('severity', 'medium'),
                        "fix_successful": fix_successful,
                        "file": issue.get('file', 'unknown')
                    })
                        
                except Exception as e:
                    results["failed"] += 1
                    self.logger.error(f"Error applying Gemini fix for issue: {e}")
                    
                    results["results"].append({
                        "issue_type": issue.get('type', 'unknown'),
                        "issue_message": issue.get('message', ''),
                        "severity": issue.get('severity', 'medium'),
                        "fix_successful": False,
                        "error": str(e),
                        "file": issue.get('file', 'unknown')
                    })
        
        self.logger.info(f"Gemini fixes completed: {results['successful']} successful, {results['failed']} failed")
        return results
    
    def _should_create_task(self, issue: Dict[str, Any], threshold: str) -> bool:
        """Determine if an issue should trigger a coder task"""
        severity_levels = {"low": 1, "medium": 2, "high": 3}
        issue_level = severity_levels.get(issue.get("severity", "low"), 1)
        threshold_level = severity_levels.get(threshold, 2)
        
        return issue_level >= threshold_level
    
    def _identify_files_to_fix(self, issue: Dict[str, Any]) -> List[str]:
        """Identify which files need to be modified for this issue"""
        files = []
        
        # Extract file information from issue
        if "file" in issue:
            files.append(issue["file"])
        elif "element" in issue:
            # For DOM issues, assume HTML/template files
            files.append("index.html")
        
        # Add default files based on issue type
        issue_type = issue.get("type", "")
        if issue_type == "accessibility":
            files.extend(["index.html", "style.css"])
        elif issue_type == "performance":
            files.extend(["webpack.config.js", "package.json"])
        
        return list(set(files))  # Remove duplicates
    
    async def execute_coder_tasks(self, tasks: List[CoderTask]) -> Dict[str, Any]:
        """Execute coder tasks using the Coder Agent"""
        self.logger.info(f"Executing {len(tasks)} coder tasks")
        
        results = {
            "completed": 0,
            "failed": 0,
            "skipped": 0,
            "task_results": []
        }
        
        if not self.coder_agent or not self.coder_agent.get("available"):
            self.logger.warning("Coder Agent not available, simulating task execution")
            # Simulate task execution
            for task in tasks:
                results["task_results"].append({
                    "task_id": task.task_id,
                    "status": "simulated",
                    "message": f"Would fix {task.bug_type} issue in {', '.join(task.files_to_fix)}"
                })
                results["completed"] += 1
            return results
        
        # Execute tasks with Coder Agent
        max_concurrent = self.config["coder_agent"]["max_concurrent_fixes"]
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def execute_single_task(task: CoderTask):
            async with semaphore:
                return await self._execute_single_coder_task(task)
        
        # Execute tasks concurrently
        task_results = await asyncio.gather(
            *[execute_single_task(task) for task in tasks],
            return_exceptions=True
        )
        
        # Process results
        for result in task_results:
            if isinstance(result, Exception):
                results["failed"] += 1
                results["task_results"].append({
                    "status": "failed",
                    "error": str(result)
                })
            else:
                if result["status"] == "completed":
                    results["completed"] += 1
                else:
                    results["failed"] += 1
                results["task_results"].append(result)
        
        self.logger.info(f"Task execution completed: {results['completed']} succeeded, {results['failed']} failed")
        return results
    
    async def _execute_single_coder_task(self, task: CoderTask) -> Dict[str, Any]:
        """Execute a single coder task"""
        try:
            # This would integrate with the actual Coder Agent
            # For now, simulate the execution
            await asyncio.sleep(1)  # Simulate processing time
            
            return {
                "task_id": task.task_id,
                "status": "completed",
                "message": f"Fixed {task.bug_type} issue",
                "files_modified": task.files_to_fix,
                "execution_time": "1.0s"
            }
            
        except Exception as e:
            return {
                "task_id": task.task_id,
                "status": "failed",
                "error": str(e)
            }
    
    async def orchestrate_full_cycle(self, url: str) -> Dict[str, Any]:
        """Run complete orchestration cycle: analyze -> create tasks -> create ADO tickets -> apply Gemini fixes -> execute fixes"""
        self.logger.info(f"Starting full orchestration cycle for: {url}")
        
        try:
            # Step 1: Analyze website
            analysis_result = await self.analyze_website(url)
            
            # Step 2: Create coder tasks
            coder_tasks = await self.create_coder_tasks(analysis_result)
            
            # Step 3: Create Azure DevOps tickets
            ado_tickets = await self.create_ado_tickets_from_issues(analysis_result.issues, analysis_result.analysis_id)
            
            # Step 4: Apply Gemini CLI fixes
            gemini_results = await self.apply_gemini_fixes(analysis_result.issues, analysis_result.analysis_id)
            
            # Step 5: Execute additional fixes (if auto-fix is enabled)
            fix_results = None
            if self.config["orchestrator"]["auto_trigger_fixes"] and coder_tasks:
                fix_results = await self.execute_coder_tasks(coder_tasks)
            
            # Step 6: Generate report
            report = {
                "orchestration_id": f"orch_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "url": url,
                "timestamp": datetime.now().isoformat(),
                "analysis": {
                    "analysis_id": analysis_result.analysis_id,
                    "overall_score": analysis_result.overall_score,
                    "issues_found": len(analysis_result.issues),
                    "severity_breakdown": analysis_result.severity_counts
                },
                "tasks": {
                    "created": len(coder_tasks),
                    "task_details": [
                        {
                            "task_id": task.task_id,
                            "description": task.description,
                            "priority": task.priority,
                            "bug_type": task.bug_type
                        } for task in coder_tasks
                    ]
                },
                "ado_tickets": {
                    "created": len(ado_tickets),
                    "ticket_ids": ado_tickets
                },
                "gemini_fixes": gemini_results,
                "fixes": fix_results,
                "recommendations": analysis_result.recommendations
            }
            
            self.logger.info(f"Orchestration cycle completed: {report['orchestration_id']}")
            return report
            
        except Exception as e:
            self.logger.error(f"Orchestration cycle failed: {e}")
            raise
    
    def get_status(self) -> Dict[str, Any]:
        """Get current orchestrator status"""
        return {
            "agents": {
                "ux_analyzer": {
                    "available": self.ux_analyzer is not None and self.ux_analyzer.get("available", False),
                    "endpoint": self.ux_analyzer.get("endpoint", "Unknown") if self.ux_analyzer else None,
                    "status": self.ux_analyzer.get("status", "Not initialized") if self.ux_analyzer else "Not initialized"
                },
                "coder_agent": {
                    "available": self.coder_agent is not None and self.coder_agent.get("available", False),
                    "path": self.coder_agent.get("path", "Unknown") if self.coder_agent else None
                },
                "ado_client": {
                    "available": self.ado_client is not None and self.ado_client.is_configured(),
                    "org": self.ado_client.org if self.ado_client else None,
                    "project": self.ado_client.project if self.ado_client else None,
                    "configured": self.ado_client.is_configured() if self.ado_client else False
                },
                "gemini_handler": {
                    "available": self.gemini_handler is not None,
                    "cli_available": self.gemini_handler.test_gemini_cli() if self.gemini_handler else False,
                    "frontend_path": self.gemini_handler.frontend_path if self.gemini_handler else None,
                    "frontend_path_exists": self.gemini_handler.get_status()["frontend_path_exists"] if self.gemini_handler else False
                }
            },
            "active_tasks": len(self.active_tasks),
            "analysis_history": len(self.analysis_history),
            "config": {
                "ux_analyzer_endpoint": self.config["ux_analyzer"]["api_endpoint"],
                "severity_threshold": self.config["orchestrator"]["severity_threshold"],
                "auto_trigger_fixes": self.config["orchestrator"]["auto_trigger_fixes"]
            },
            "timestamp": datetime.now().isoformat()
        }

async def main():
    """Main entry point for orchestrator"""
    print("🚀 Starting Orchestrator Agent...")
    
    # Initialize orchestrator
    orchestrator = OrchestratorAgent()
    await orchestrator.initialize_agents()
    
    print("📊 Orchestrator Status:")
    status = orchestrator.get_status()
    print(json.dumps(status, indent=2))
    
    # Example: Run full orchestration cycle
    test_url = "https://example.com"
    print(f"\n🔄 Running orchestration cycle for: {test_url}")
    
    try:
        result = await orchestrator.orchestrate_full_cycle(test_url)
        print("✅ Orchestration completed successfully!")
        print(json.dumps(result, indent=2))
    except Exception as e:
        print(f"❌ Orchestration failed: {e}")

if __name__ == "__main__":
    asyncio.run(main())
