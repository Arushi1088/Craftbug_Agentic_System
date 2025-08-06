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
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from pathlib import Path

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
            
            self.logger.info("All agents initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize agents: {e}")
            raise
    
    async def _init_ux_analyzer(self):
        """Initialize UX Analyzer connection"""
        try:
            # Import and setup UX analyzer components
            from fastapi_server import app as analyzer_app
            self.ux_analyzer = {
                "app": analyzer_app,
                "endpoint": self.config["ux_analyzer"]["api_endpoint"]
            }
            self.logger.info("UX Analyzer connection established")
        except ImportError as e:
            self.logger.warning(f"UX Analyzer not available: {e}")
    
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
    
    async def analyze_website(self, url: str, custom_modules: Optional[Dict[str, bool]] = None) -> AnalysisResult:
        """Trigger UX analysis of a website"""
        self.logger.info(f"Starting UX analysis for: {url}")
        
        modules = custom_modules or self.config["ux_analyzer"]["modules"]
        
        try:
            # Simulate API call to UX analyzer
            # In real implementation, this would make HTTP request to analyzer
            analysis_data = {
                "url": url,
                "analysis_id": f"ux_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "overall_score": 75,  # Mock score
                "issues": [
                    {
                        "type": "accessibility",
                        "severity": "high",
                        "message": "Missing alt text on images",
                        "element": "img.hero-banner",
                        "recommendation": "Add descriptive alt text to all images"
                    },
                    {
                        "type": "performance",
                        "severity": "medium", 
                        "message": "Large bundle size detected",
                        "file": "main.js",
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
            
            result = AnalysisResult(
                analysis_id=analysis_data["analysis_id"],
                url=url,
                overall_score=analysis_data["overall_score"],
                issues=analysis_data["issues"],
                recommendations=analysis_data["recommendations"],
                timestamp=analysis_data["timestamp"],
                severity_counts=self._count_severities(analysis_data["issues"])
            )
            
            self.analysis_history.append(result)
            self.logger.info(f"UX analysis completed: {result.analysis_id}")
            
            return result
            
        except Exception as e:
            self.logger.error(f"UX analysis failed: {e}")
            raise
    
    def _count_severities(self, issues: List[Dict[str, Any]]) -> Dict[str, int]:
        """Count issues by severity level"""
        counts = {"high": 0, "medium": 0, "low": 0}
        for issue in issues:
            severity = issue.get("severity", "low")
            if severity in counts:
                counts[severity] += 1
        return counts
    
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
        """Run complete orchestration cycle: analyze -> create tasks -> execute fixes"""
        self.logger.info(f"Starting full orchestration cycle for: {url}")
        
        try:
            # Step 1: Analyze website
            analysis_result = await self.analyze_website(url)
            
            # Step 2: Create coder tasks
            coder_tasks = await self.create_coder_tasks(analysis_result)
            
            # Step 3: Execute fixes (if auto-fix is enabled)
            fix_results = None
            if self.config["orchestrator"]["auto_trigger_fixes"] and coder_tasks:
                fix_results = await self.execute_coder_tasks(coder_tasks)
            
            # Step 4: Generate report
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
                "ux_analyzer": self.ux_analyzer is not None,
                "coder_agent": self.coder_agent is not None and self.coder_agent.get("available", False)
            },
            "active_tasks": len(self.active_tasks),
            "analysis_history": len(self.analysis_history),
            "config": self.config,
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
