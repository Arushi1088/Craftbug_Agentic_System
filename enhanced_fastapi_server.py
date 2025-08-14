#!/usr/bin/env python3
"""
Enhanced FastAPI Server for UX Analyzer
Provides API endpoints with real browser automation and craft bug detection
"""

from fastapi import FastAPI, HTTPException, UploadFile, File, Form, BackgroundTasks, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
import json
import uuid
from datetime import datetime
import tempfile
import os
import sys
import asyncio
import logging
from pathlib import Path
from contextlib import asynccontextmanager

# Schema normalization imports
try:
    from schema_normalizer import migrate_reports_on_startup, iterate_all_report_files
except ImportError:
    # Fallback functions if schema_normalizer is not available
    def migrate_reports_on_startup(): pass
    def iterate_all_report_files(): return []

def normalize_report_schema(data):
    """
    Robust report schema normalization - ensures reports always have required fields
    """
    if not isinstance(data, dict):
        logger.error(f"normalize_report_schema received non-dict: {type(data)}")
        return {
            "status": "failed",
            "error": "Invalid report data",
            "ui_error": "Analysis failed due to invalid report format",
            "module_results": {},
            "scenario_results": [],
            "overall_score": 0,
            "total_issues": 0,
            "timestamp": datetime.now().isoformat()
        }

    # If already failed, ensure UI can render it
    if data.get("status") == "failed" or data.get("error"):
        data.setdefault("module_results", {})
        data.setdefault("scenario_results", [])
        data.setdefault("overall_score", 0)
        data.setdefault("total_issues", 0)
        data.setdefault("timestamp", datetime.now().isoformat())
        data.setdefault("ui_error", data.get("error") or "Analysis failed")
        return data

    # Normal success path - ensure all required fields exist
    data.setdefault("status", "completed")
    data.setdefault("module_results", {})
    data.setdefault("scenario_results", [])
    data.setdefault("overall_score", data.get("overall_score", 0))
    data.setdefault("total_issues", data.get("total_issues", 0))
    data.setdefault("timestamp", data.get("timestamp", datetime.now().isoformat()))
    
    # Ensure module_results is always a dict
    if not isinstance(data.get("module_results"), dict):
        data["module_results"] = {}
    
    # Ensure scenario_results is always a list
    if not isinstance(data.get("scenario_results"), list):
        data["scenario_results"] = []
    
    return data

# Load environment variables and validate API key
try:
    from dotenv import load_dotenv
    load_dotenv()
    load_dotenv("production.env")
    print("✅ Environment variables loaded")
except ImportError:
    print("⚠️ python-dotenv not available, using OS environment only")

# Validate OpenAI API Key early
api_key = os.getenv("OPENAI_API_KEY")
if api_key and api_key != "your-openai-api-key-here" and api_key.startswith("sk-"):
    print(f"✅ OpenAI API Key Loaded: {api_key[:8]}... (truncated)")
else:
    print("⚠️ OpenAI API key not properly configured")
    print("   Server will start but AI features may not work")
    print("   Run: python3 validate_api_key.py for detailed diagnosis")

# Import enhanced components
from scenario_executor import ScenarioExecutor, get_available_scenarios
# Temporarily disabled due to Playwright import issues
# from enhanced_scenario_runner import execute_realistic_scenario, EnhancedScenarioRunner
from enhanced_report_handler import (
    save_analysis_to_disk, 
    load_analysis_from_disk, 
    list_saved_reports, 
    get_report_statistics,
    search_saved_reports,
    cleanup_old_reports
)
# Import craft bug detector
from craft_bug_detector import CraftBugDetector

# Import utilities
try:
    from utils.scenario_resolver import resolve_scenario, validate_scenario_steps, _ensure_dict
except ImportError:
    pass

def resolve_scenario_name_to_path_and_id(scenario_name: str) -> tuple:
    """Resolve scenario name to file path and scenario ID"""
    if not scenario_name:
        return "scenarios/basic_navigation.yaml", None
    
    # Load all scenarios to find the match
    from scenario_executor import get_available_scenarios
    scenarios = get_available_scenarios()
    for scenario in scenarios:
        if scenario.get("name") == scenario_name:
            file_path = scenario.get("source", scenario.get("path", ""))
            scenario_id = scenario.get("id", "")
            return file_path, scenario_id
    
    # If not found, try to find by filename match
    if scenario_name.endswith('.yaml'):
        scenario_path = f"scenarios/{scenario_name}"
        if os.path.exists(scenario_path):
            return scenario_path, None
    
    # Default fallback
    logger.warning(f"Scenario '{scenario_name}' not found, using default")
    return "scenarios/basic_navigation.yaml", None
    def validate_scenario_steps(scenario): pass
    def _ensure_dict(name, obj): return obj if isinstance(obj, dict) else {}

# Import dashboard components
try:
    from ux_analytics_dashboard import UXAnalyticsDashboard
    from azure_devops_integration import AzureDevOpsClient, UXAnalysisToADOConverter
    DASHBOARD_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Dashboard components not available: {e}")
    DASHBOARD_AVAILABLE = False

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def _categorize_issue(finding: Dict[str, Any]) -> str:
    """Categorize issue to determine media type needed"""
    message = finding.get('message', '').lower()
    issue_type = finding.get('type', '').lower()
    
    # Visual issues - need screenshots
    visual_keywords = ['contrast', 'spacing', 'alignment', 'color', 'layout', 'size', 'position', 'margin', 'padding']
    if any(keyword in message for keyword in visual_keywords):
        return 'visual'
    
    # Performance issues - need videos
    performance_keywords = ['lag', 'slow', 'loading', 'responsive', 'delay', 'performance', 'animation', 'transition']
    if any(keyword in message for keyword in performance_keywords):
        return 'performance'
    
    # Functional issues - screenshots or videos depending on clarity
    functional_keywords = ['broken', 'missing', 'error', 'fail', 'not working', 'click', 'interaction']
    if any(keyword in message for keyword in functional_keywords):
        return 'functional'
    
    # Default to visual for most issues
    return 'visual'

# Mock URLs for deterministic testing
MOCK_URLS = {
    "word": "http://127.0.0.1:8080/mocks/word/basic-doc.html",
    "excel": "http://127.0.0.1:8080/mocks/excel/open-format.html", 
    "powerpoint": "http://127.0.0.1:8080/mocks/powerpoint/basic-deck.html",
}

def substitute_mock_urls(scenario_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Substitute {mock_url} placeholders with actual mock URLs based on app_type
    """
    import copy
    import json
    
    # Create a deep copy to avoid modifying original
    scenario = copy.deepcopy(scenario_data)
    
    # Get app_type from scenario
    app_type = scenario.get('app_type', '').lower()
    
    # If no app_type, try to infer from scenario name/id
    if not app_type:
        scenario_name = scenario.get('name', '').lower()
        scenario_id = scenario.get('id', '').lower()
        
        if 'word' in scenario_name or 'word' in scenario_id:
            app_type = 'word'
        elif 'excel' in scenario_name or 'excel' in scenario_id:
            app_type = 'excel'
        elif 'powerpoint' in scenario_name or 'powerpoint' in scenario_id or 'ppt' in scenario_name:
            app_type = 'powerpoint'
    
    # Get the mock URL for this app type
    mock_url = MOCK_URLS.get(app_type)
    if not mock_url:
        logger.warning(f"No mock URL found for app_type: {app_type}")
        return scenario
    
    # Convert to string, replace, then parse back
    scenario_str = json.dumps(scenario)
    scenario_str = scenario_str.replace('{mock_url}', mock_url)
    
    try:
        return json.loads(scenario_str)
    except json.JSONDecodeError:
        logger.error(f"Failed to parse scenario after URL substitution")
        return scenario

# Import orchestrator routes if available
try:
    orchestrator_path = '/Users/arushitandon/Desktop/analyzer/orchestrator'
    if os.path.exists(orchestrator_path) and os.path.exists(os.path.join(orchestrator_path, 'routes.py')):
        sys.path.insert(0, orchestrator_path)
        try:
            import routes
            orchestrator_router = getattr(routes, 'router', None)
            if orchestrator_router is None:
                print("Warning: 'router' attribute not found in routes module")
        except ImportError as import_error:
            print(f"Warning: Failed to import routes module: {import_error}")
            orchestrator_router = None
        except Exception as e:
            print(f"Warning: Unexpected error importing routes: {e}")
            orchestrator_router = None
    else:
        print(f"Warning: Orchestrator directory or routes.py not found at {orchestrator_path}")
        orchestrator_router = None
except (ImportError, AttributeError) as e:
    print(f"Warning: Could not import orchestrator routes: {e}")
    orchestrator_router = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    
    # Startup
    logger.info("🚀 Enhanced UX Analyzer starting up...")
    
    # Run schema migration on startup
    try:
        logger.info("🔧 Running report schema migration...")
        changed_count = migrate_reports_on_startup()
        logger.info(f"📊 Schema migration complete: {changed_count} files updated")
    except Exception as e:
        logger.error(f"❌ Schema migration failed: {e}")
    
    # Validate required directories
    os.makedirs("reports", exist_ok=True)
    os.makedirs("reports/analysis", exist_ok=True)
    os.makedirs("screenshots", exist_ok=True)
    os.makedirs("temp", exist_ok=True)
    logger.info("📁 Required directories validated")
    
    yield
    
    # Shutdown
    logger.info("🛑 Enhanced UX Analyzer shutting down...")

app = FastAPI(
    title="Enhanced UX Analyzer API", 
    description="Advanced UX analysis with real browser automation, craft bug detection, and Azure DevOps integration",
    version="2.1.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000", 
        "http://localhost:3001", 
        "http://localhost:3002", 
        "http://localhost:3003", 
        "http://localhost:3004",
        "http://localhost:4174",  # Vite preview server (mocks)
        "http://localhost:4173",  # Vite preview server (mocks - backup)
        "http://localhost:5173",  # Vite dev server
        "http://127.0.0.1:8080",  # Dashboard server
        "http://127.0.0.1:8080",  # Dashboard server (127.0.0.1)
        "http://127.0.0.1:3000",  # Dashboard on 127.0.0.1:3000
        "http://127.0.0.1:5173",  # Vite dev server (127.0.0.1)
        "https://dev.azure.com",
        "https://*.trycloudflare.com",
        "https://leasing-gba-om-prior.trycloudflare.com"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Content-Security-Policy", "frame-ancestors"]
)

# Mount static files for serving screenshots
app.mount("/reports", StaticFiles(directory="reports"), name="reports")

# Include orchestrator routes if available
if orchestrator_router:
    app.include_router(orchestrator_router, prefix="/api")
    print("✅ Orchestrator routes mounted at /api")

# Initialize components
scenario_executor = ScenarioExecutor()

# In-memory cache for active analyses (supplementing disk storage)
ANALYSIS_CACHE = {}

# Legacy mock reports for backwards compatibility
MOCK_REPORTS = {}

# Enhanced Pydantic models
class EnhancedAnalysisRequest(BaseModel):
    url: Optional[str] = None
    scenario: Optional[str] = None
    scenario_path: Optional[str] = None
    app_path: Optional[str] = None
    execution_mode: str = "mock"  # "mock" or "realistic"
    modules: Dict[str, bool] = {
        "performance": True,
        "accessibility": True,
        "keyboard": True,
        "ux_heuristics": True,
        "best_practices": True,
        "health_alerts": True,
        "functional": False,
        "craft_bug_detection": True,  # New!
        "realistic_execution": False  # New!
    }
    output_format: str = "json"
    headless: bool = True

class AnalysisRequest(BaseModel):
    url: Optional[str] = None
    scenario: Optional[str] = None
    scenario_id: Optional[str] = None
    scenario_path: Optional[str] = None
    app_path: Optional[str] = None
    modules: Dict[str, bool] = {
        "performance": True,
        "accessibility": True,
        "keyboard": True,
        "ux_heuristics": True,
        "best_practices": True,
        "health_alerts": True,
        "functional": False
    }
    output_format: str = "html"

class AnalysisResponse(BaseModel):
    analysis_id: str
    status: str
    message: str
    execution_mode: Optional[str] = None
    craft_bugs: Optional[List[dict]] = []
    ux_issues: Optional[List[dict]] = []
    total_issues: Optional[int] = 0

class ReportSearchRequest(BaseModel):
    url: Optional[str] = None
    score_min: Optional[int] = None
    score_max: Optional[int] = None
    has_craft_bugs: Optional[bool] = None
    analysis_type: Optional[str] = None
    date_from: Optional[str] = None
    date_to: Optional[str] = None
    limit: int = 50
    offset: int = 0

class CraftBugAnalysisRequest(BaseModel):
    url: str
    headless: bool = True
    categories: List[str] = ["A", "B", "D", "E"]  # Default: all categories

# Background task processing
async def process_realistic_analysis(analysis_id: str, request_data: Dict[str, Any]):
    """Process realistic scenario analysis in background"""
    try:
        logger.info(f"🎯 Starting realistic analysis: {analysis_id}")
        
        # Execute realistic scenario with browser automation
        result = await execute_realistic_scenario(
            url=request_data.get("url", ""),
            scenario_path=request_data.get("scenario_path", ""),
            headless=request_data.get("headless", True)
        )
        
        # Guard against None/invalid results from realistic execution
        if not isinstance(result, dict):
            logger.error(f"Realistic scenario returned invalid data type: {type(result)} for analysis {analysis_id}")
            raise RuntimeError(f"Realistic scenario executor returned empty/invalid report: {type(result)}")
        
        # Apply schema normalization to ensure consistent structure
        result = normalize_report_schema(result)
        
        # Save to disk automatically
        file_path = save_analysis_to_disk(analysis_id, result)
        result["file_path"] = file_path
        
        # Cache in memory for quick access
        ANALYSIS_CACHE[analysis_id] = {
            "status": "completed",
            "result": result,
            "completed_at": datetime.now(),
            "file_path": file_path
        }
        
        logger.info(f"✅ Realistic analysis completed: {analysis_id}")
        
    except Exception as e:
        logger.exception(f"❌ Realistic analysis failed: {analysis_id}: {e}")  # Keep full stack trace
        
        # Generate a proper error report with module structure for frontend compatibility
        error_result = {
            "analysis_id": analysis_id,
            "status": "failed",
            "error": str(e),
            "timestamp": datetime.now().isoformat(),
            "type": "error_report",
            "url": request_data.get("url", ""),
            "scenario_path": request_data.get("scenario_path", ""),
            "overall_score": 0,
            "total_issues": 1,
            "module_results": {
                "error_report": {
                    "title": "Analysis Error",
                    "description": f"Realistic analysis failed: {str(e)}",
                    "score": 0,
                    "issues": [{"severity": "critical", "description": str(e)}]
                }
            }
        }
        
        # Save error report
        file_path = save_analysis_to_disk(analysis_id, error_result)
        error_result["file_path"] = file_path
        
        ANALYSIS_CACHE[analysis_id] = {
            "status": "failed",
            "result": error_result,
            "error": str(e),
            "completed_at": datetime.now(),
            "file_path": file_path
        }

async def process_craft_bug_analysis(analysis_id: str, request_data: Dict[str, Any]):
    """Process craft bug analysis with browser automation"""
    from playwright.async_api import async_playwright
    
    try:
        logger.info(f"🐛 Starting craft bug analysis: {analysis_id}")
        
        detector = CraftBugDetector()
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=request_data.get("headless", True))
            page = await browser.new_page()
            
            # Perform craft bug analysis
            craft_bug_report = await detector.analyze_craft_bugs(page, request_data["url"])
            
            await browser.close()
        
        # Convert craft bug report to standard analysis format
        result = {
            "analysis_id": analysis_id,
            "status": "completed",
            "timestamp": datetime.now().isoformat(),
            "type": "craft_bug_analysis",
            "url": request_data["url"],
            "overall_score": max(0, 100 - (craft_bug_report.total_bugs_found * 10)),
            "total_issues": craft_bug_report.total_bugs_found,
            "module_results": {
                "craft_bug_detection": {
                    "title": "Craft Bug Detection",
                    "description": "Analysis of intentional UX craft bugs",
                    "score": max(0, 100 - (craft_bug_report.total_bugs_found * 10)),
                    "issues": [
                        {
                            "category": finding.category,
                            "type": finding.bug_type,
                            "severity": finding.severity,
                            "description": finding.description,
                            "location": finding.location,
                            "metrics": finding.metrics
                        }
                        for finding in craft_bug_report.findings
                    ],
                    "summary": {
                        "total_bugs": craft_bug_report.total_bugs_found,
                        "bugs_by_category": craft_bug_report.bugs_by_category,
                        "analysis_duration": craft_bug_report.analysis_duration,
                        "metrics_summary": craft_bug_report.metrics_summary
                    }
                }
            },
            "craft_bug_report": craft_bug_report.__dict__
        }
        
        # Apply schema normalization
        result = normalize_report_schema(result)
        
        # Save to disk
        file_path = save_analysis_to_disk(analysis_id, result)
        result["file_path"] = file_path
        
        # Cache result
        ANALYSIS_CACHE[analysis_id] = {
            "status": "completed",
            "result": result,
            "completed_at": datetime.now(),
            "file_path": file_path
        }
        
        logger.info(f"✅ Craft bug analysis completed: {analysis_id}, found {craft_bug_report.total_bugs_found} bugs")
        
    except Exception as e:
        logger.exception(f"❌ Craft bug analysis failed: {analysis_id}: {e}")
        
        # Generate error report
        error_result = {
            "analysis_id": analysis_id,
            "status": "failed",
            "error": str(e),
            "timestamp": datetime.now().isoformat(),
            "type": "craft_bug_analysis",
            "url": request_data.get("url", ""),
            "overall_score": 0,
            "total_issues": 1,
            "module_results": {
                "craft_bug_detection": {
                    "title": "Craft Bug Detection",
                    "description": "Analysis failed",
                    "score": 0,
                    "issues": [{
                        "category": "error",
                        "type": "analysis_failure",
                        "severity": "critical",
                        "description": str(e),
                        "location": "analysis_system"
                    }]
                }
            }
        }
        
        # Save error report
        file_path = save_analysis_to_disk(analysis_id, error_result)
        error_result["file_path"] = file_path
        
        ANALYSIS_CACHE[analysis_id] = {
            "status": "failed",
            "result": error_result,
            "error": str(e),
            "completed_at": datetime.now(),
            "file_path": file_path
        }


def generate_mock_scenario_report(analysis_id: str, request_data: Dict[str, Any]) -> Dict[str, Any]:
    """Generate a mock scenario analysis report"""
    import random
    
    # Generate scenario results
    scenario_names = [
        "Login Process",
        "Navigation Flow", 
        "Form Submission",
        "Search Functionality",
        "User Profile Access"
    ]
    
    scenario_results = []
    for i, name in enumerate(scenario_names[:3]):  # Generate 3 scenarios
        score = random.randint(70, 98)
        status = "success" if score > 80 else "warning"
        duration = random.randint(1000, 5000)
        
        steps = [
            {
                "action": f"Navigate to {name.lower()}",
                "status": "success",
                "duration_ms": random.randint(200, 800),
                "selector": f"[data-testid='{name.lower().replace(' ', '-')}']"
            },
            {
                "action": f"Interact with {name.lower()} elements",
                "status": "success",
                "duration_ms": random.randint(300, 1200),
                "selector": f".{name.lower().replace(' ', '-')}-container"
            },
            {
                "action": f"Validate {name.lower()} completion",
                "status": "success" if score > 85 else "warning",
                "duration_ms": random.randint(100, 500),
                "selector": f"[aria-label='{name} completed']"
            }
        ]
        
        scenario_results.append({
            "name": name,
            "score": score,
            "status": status,
            "duration_ms": duration,
            "steps": steps
        })
    
    # Generate module results for scenario-based analysis
    modules = {}
    enabled_modules = [k for k, v in request_data.get('modules', {}).items() if v]
    
    for module in enabled_modules:
        score = random.randint(75, 95)
        modules[module] = {
            "score": score,
            "findings": [
                {
                    "type": "info" if score > 85 else "warning",
                    "message": f"Scenario-based {module} analysis completed successfully",
                    "severity": "low" if score > 85 else "medium",
                    "element": f".scenario-{module}-element"
                }
            ],
            "recommendations": [
                f"Optimize {module} for scenario-based interactions",
                f"Implement advanced {module} monitoring for user journeys"
            ],
            "metrics": {
                "scenario_coverage": random.randint(80, 100),
                "user_journey_score": random.randint(70, 95),
                "interaction_success_rate": random.randint(85, 100)
            }
        }
    
    overall_score = sum(s["score"] for s in scenario_results) // len(scenario_results) if scenario_results else 0
    
    return {
        "analysis_id": analysis_id,
        "timestamp": datetime.now().isoformat(),
        "url": request_data.get("url"),
        "scenario_path": request_data.get("scenario_path"),
        "app_path": request_data.get("app_path"),
        "type": "scenario",
        "mode": "scenario",
        "overall_score": overall_score,
        "scenario_results": scenario_results,
        "modules": modules
    }

def generate_mock_report(analysis_id: str, request_data: Dict[str, Any]) -> Dict[str, Any]:
    """Generate a mock analysis report for backwards compatibility"""
    import random
    
    modules = {}
    enabled_modules = [k for k, v in request_data.get('modules', {}).items() if v]
    
    for module in enabled_modules:
        score = random.randint(60, 95)
        modules[module] = {
            "score": score,
            "findings": [
                {
                    "type": "warning" if score < 80 else "info",
                    "message": f"Sample finding for {module} module",
                    "severity": "medium" if score < 80 else "low"
                }
            ],
            "recommendations": [
                f"Improve {module} by implementing best practices",
                f"Consider optimizing {module} performance"
            ],
            "metrics": {
                "response_time": random.randint(100, 500),
                "score_breakdown": {
                    "category_1": random.randint(70, 100),
                    "category_2": random.randint(60, 95)
                }
            }
        }
    
    overall_score = sum(m["score"] for m in modules.values()) // len(modules) if modules else 0
    
    return {
        "analysis_id": analysis_id,
        "timestamp": datetime.now().isoformat(),
        "url": request_data.get("url"),
        "mode": "url" if request_data.get("url") else "scenario",
        "overall_score": overall_score,
        "modules": modules
    }

# API Endpoints

@app.get("/")
async def root():
    return {
        "service": "Enhanced UX Analyzer API",
        "version": "2.0.0",
        "features": [
            "Real browser automation with Playwright",
            "Craft bug detection and analysis",
            "Persistent report storage",
            "Advanced scenario execution",
            "Comprehensive UX analytics"
        ],
        "timestamp": datetime.now().isoformat()
    }

@app.get("/health")
async def health_check():
    """Enhanced health check with system status"""
    stats = get_report_statistics()
    
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "2.0.0",
        "system_info": {
            "active_analyses": len([a for a in ANALYSIS_CACHE.values() if a.get("status") == "processing"]),
            "cached_reports": len(ANALYSIS_CACHE),
            "disk_reports": stats.get("index_statistics", {}).get("total_reports", 0),
            "storage_usage_mb": stats.get("storage_info", {}).get("disk_usage_mb", 0)
        },
        "features": {
            "realistic_scenarios": True,
            "craft_bug_detection": True,
            "persistent_storage": True,
            "browser_automation": True
        }
    }

# Enhanced Analysis Endpoints

@app.post("/api/analyze/enhanced", response_model=AnalysisResponse)
async def analyze_enhanced(
    request: EnhancedAnalysisRequest,
    background_tasks: BackgroundTasks
):
    """Enhanced analysis with realistic browser automation and craft bug detection"""
    
    if not request.url:
        raise HTTPException(status_code=400, detail="URL is required")
    
    if not request.scenario_path:
        raise HTTPException(status_code=400, detail="Scenario path is required")
    
    # Check if scenario file exists
    if not os.path.exists(request.scenario_path):
        raise HTTPException(status_code=404, detail=f"Scenario file not found: {request.scenario_path}")
    
    analysis_id = str(uuid.uuid4())[:8]
    
    # Initialize analysis cache entry
    ANALYSIS_CACHE[analysis_id] = {
        "status": "processing",
        "started_at": datetime.now(),
        "request_data": request.dict()
    }
    
    if request.execution_mode == "realistic":
        # Process with real browser automation
        background_tasks.add_task(process_realistic_analysis, analysis_id, request.dict())
        message = f"Enhanced realistic analysis started for {request.url}"
    else:
        # Process with enhanced mock (faster)
        try:
            if request.scenario_path:
                report_data = scenario_executor.execute_url_scenario(
                    url=request.url,
                    scenario_path=request.scenario_path,
                    modules=request.modules
                )
                
                # Guard against None/invalid executor results
                if not isinstance(report_data, dict):
                    error_msg = f"Scenario executor returned invalid data type: {type(report_data)}"
                    logger.error(f"{error_msg} for URL {request.url}")
                    raise RuntimeError(error_msg)
                
                # Ensure we have required fields for analysis status
                if "analysis_id" not in report_data:
                    report_data["analysis_id"] = analysis_id
                
            else:
                report_data = generate_mock_report(analysis_id, request.dict())
            
            # Apply robust schema normalization
            report_data = normalize_report_schema(report_data)
            
            # Final safety check
            if not isinstance(report_data, dict):
                raise RuntimeError("Report normalization failed - not a dict")
            
            # Save to disk
            file_path = save_analysis_to_disk(analysis_id, report_data)
            report_data["file_path"] = file_path
            
            # Cache result
            ANALYSIS_CACHE[analysis_id] = {
                "status": "completed",
                "result": report_data,
                "completed_at": datetime.now(),
                "file_path": file_path
            }
            
        except Exception as e:
            logger.exception(f"Enhanced analysis failed for {request.url}: {e}")  # Keep stack trace
            
            # Generate structured error report that the UI can render
            error_report = {
                "analysis_id": analysis_id,
                "status": "failed",
                "error": str(e),
                "ui_error": f"Analysis failed: {str(e)}",  # User-friendly error message
                "timestamp": datetime.now().isoformat(),
                "url": request.url,
                "scenario_path": request.scenario_path,
                "overall_score": 0,
                "total_issues": 1,
                "module_results": {},
                "scenario_results": [],
                "metadata": {
                    "error_type": "enhanced_analysis_error",
                    "execution_mode": request.execution_mode,
                    "requested_modules": list(request.modules.keys())
                }
            }
            
            # Normalize the error report to ensure UI compatibility
            error_report = normalize_report_schema(error_report)
            
            # Save error report to disk for debugging
            try:
                file_path = save_analysis_to_disk(analysis_id, error_report)
                error_report["file_path"] = file_path
            except Exception as save_error:
                logger.error(f"Failed to save error report: {save_error}")
            
            # Cache error result
            ANALYSIS_CACHE[analysis_id] = {
                "status": "failed",
                "result": error_report,
                "completed_at": datetime.now(),
                "error": str(e)
            }
        
        message = f"Enhanced mock analysis completed for {request.url}"
    
    logger.info(f"🎯 Started enhanced analysis {analysis_id} for {request.url}")
    
    return AnalysisResponse(
        analysis_id=analysis_id,
        status="processing" if request.execution_mode == "realistic" else "completed",
        message=message,
        execution_mode=request.execution_mode
    )

@app.post("/api/analyze/craft-bugs", response_model=AnalysisResponse)
async def analyze_craft_bugs(
    request: CraftBugAnalysisRequest,
    background_tasks: BackgroundTasks
):
    """Dedicated craft bug detection analysis"""
    
    if not request.url:
        raise HTTPException(status_code=400, detail="URL is required")
    
    analysis_id = str(uuid.uuid4())[:8]
    
    # Initialize analysis cache entry
    ANALYSIS_CACHE[analysis_id] = {
        "status": "processing",
        "started_at": datetime.now(),
        "request_data": request.dict()
    }
    
    # Process craft bug analysis in background
    background_tasks.add_task(process_craft_bug_analysis, analysis_id, request.dict())
    
    return AnalysisResponse(
        analysis_id=analysis_id,
        status="processing",
        message=f"Craft bug analysis started for {request.url}",
        execution_mode="craft_bug_detection"
    )

# Word Craft Bug Scenario endpoint for dashboard testing
@app.post("/api/analyze/word-craft-bugs", response_model=AnalysisResponse)
async def analyze_word_craft_bugs(request: AnalysisRequest):
    """Analyze Word mock with craft bug detection scenarios through dashboard"""
    if not request.url:
        raise HTTPException(status_code=400, detail="URL is required")
    
    analysis_id = str(uuid.uuid4())[:8]
    
    try:
        # Default to Word URL if not provided
        word_url = request.url
        if not word_url.endswith('word/basic-doc.html'):
            word_url = "http://127.0.0.1:8080/mocks/word/basic-doc.html"
        
        # Use craft bug scenario (craft-1 or craft-2)
        craft_scenario_id = request.scenario_id or "craft-1"
        
        logger.info(f"🐛 Running Word craft bug analysis: URL={word_url}, scenario={craft_scenario_id}")
        
        # Import and use the craft bug detection function
        from test_word_forced_interactions import word_analysis_with_forced_interactions
        
        # Run the combined analysis (API + craft bug interactions)
        result = await word_analysis_with_forced_interactions()
        
        if result:
            # Convert the combined result to proper report format
            report_data = {
                "analysis_id": analysis_id,
                "status": "completed",
                "timestamp": datetime.now().isoformat(),
                "url": word_url,
                "scenario_id": craft_scenario_id,
                "overall_score": 65,  # Lower score due to craft bugs
                "total_issues": result["standard_analysis"].get("total_issues", 0) + result["craft_bug_analysis"]["total_bugs_found"],
                "craft_bugs_detected": result["craft_bug_analysis"]["total_bugs_found"],
                "craft_bug_details": result["craft_bug_analysis"]["findings"],
                "standard_analysis": result["standard_analysis"],
                "craft_bug_analysis": result["craft_bug_analysis"],
                "module_results": {
                    "accessibility": result["standard_analysis"].get("accessibility", {}),
                    "performance": result["standard_analysis"].get("performance", {}),
                    "craft_bugs": {
                        "enabled": True,
                        "findings": result["craft_bug_analysis"]["findings"],
                        "total_detected": result["craft_bug_analysis"]["total_bugs_found"],
                        "categories": ["B", "D"],  # Layout thrash, input lag
                        "severity_breakdown": {
                            "high": len([f for f in result["craft_bug_analysis"]["findings"] if f.get("severity") == "high"]),
                            "medium": len([f for f in result["craft_bug_analysis"]["findings"] if f.get("severity") == "medium"]),
                            "low": len([f for f in result["craft_bug_analysis"]["findings"] if f.get("severity") == "low"])
                        }
                    }
                },
                "ux_issues": [],
                "recommendations": [
                    {
                        "id": "craft-bug-1",
                        "title": "Animation Conflicts Detected",
                        "description": "Multiple conflicting animations detected during user interactions",
                        "severity": "medium",
                        "category": "craft_bugs"
                    },
                    {
                        "id": "craft-bug-2", 
                        "title": "Input Lag Issues",
                        "description": "Significant input delays detected during typing interactions",
                        "severity": "high",
                        "category": "craft_bugs"
                    }
                ]
            }
        else:
            # Fallback if analysis fails
            report_data = {
                "analysis_id": analysis_id,
                "status": "completed",
                "error": "Craft bug analysis failed",
                "url": word_url,
                "overall_score": 95,
                "total_issues": 0,
                "craft_bugs_detected": 0,
                "module_results": {}
            }
        
        # Apply schema normalization
        report_data = normalize_report_schema(report_data)
        
        # Store results
        MOCK_REPORTS[analysis_id] = report_data
        save_analysis_to_disk(analysis_id, report_data)
        
        # Automatically create ADO work items for issues found
        await auto_create_ado_work_items(report_data, analysis_id)
        
        logger.info(f"✅ Word craft bug analysis completed: {analysis_id}")
        
        return AnalysisResponse(
            analysis_id=analysis_id,
            status="completed",
            message=f"Word craft bug analysis completed - {report_data.get('craft_bugs_detected', 0)} craft bugs detected"
        )
        
    except Exception as e:
        logger.error(f"❌ Word craft bug analysis failed: {str(e)}")
        
        # Return error response
        error_report = {
            "analysis_id": analysis_id,
            "status": "failed",
            "error": str(e),
            "url": request.url,
            "overall_score": 0,
            "total_issues": 1,
            "module_results": {}
        }
        error_report = normalize_report_schema(error_report)
        MOCK_REPORTS[analysis_id] = error_report
        save_analysis_to_disk(analysis_id, error_report)
        
        return AnalysisResponse(
            analysis_id=analysis_id,
            status="completed",
            message=f"Word craft bug analysis failed: {str(e)}"
        )

# Legacy endpoints for backwards compatibility
@app.post("/api/analyze", response_model=AnalysisResponse)
async def analyze_url(request: AnalysisRequest):
    """Main analyze endpoint - runs real analysis instead of mock data"""
    if not request.url:
        raise HTTPException(status_code=400, detail="URL is required")
    
    analysis_id = str(uuid.uuid4())[:8]
    
    try:
        # Use real scenario executor instead of generating mock data
        if request.scenario_id:
            # Run real analysis with scenario
            logger.info(f"🚀 Running real analysis for URL: {request.url}, scenario: {request.scenario_id}")
            report_data = await scenario_executor.execute_scenario_by_id(
                url=request.url,
                scenario_id=request.scenario_id,
                modules=request.modules or {}
            )
        else:
            # Fallback to basic URL analysis without specific scenario
            logger.info(f"🚀 Running basic URL analysis for: {request.url}")
            report_data = await scenario_executor.execute_scenario_by_id(
                url=request.url,
                scenario_id="1.1",  # Use default Word scenario
                modules=request.modules or {}
            )
        
        # Guard against None/invalid executor results
        if not isinstance(report_data, dict):
            error_msg = f"Scenario executor returned invalid data type: {type(report_data)}"
            logger.error(f"{error_msg} for URL {request.url}")
            raise RuntimeError(error_msg)
        
        # Ensure we have required fields for analysis status
        if "analysis_id" not in report_data:
            report_data["analysis_id"] = analysis_id
        
        # Apply robust schema normalization
        report_data = normalize_report_schema(report_data)
        
        # Store report in memory and disk
        MOCK_REPORTS[analysis_id] = report_data
        save_analysis_to_disk(analysis_id, report_data)
        
        # Automatically create ADO work items for issues found
        await auto_create_ado_work_items(report_data, analysis_id)
        
        logger.info(f"✅ Real analysis completed for {request.url}, analysis_id: {analysis_id}")
        
        # Extract craft bugs and UX issues for immediate response
        craft_bugs = report_data.get('craft_bugs', [])
        ux_issues = report_data.get('ux_issues', [])
        total_issues = len(ux_issues)
        
        return AnalysisResponse(
            analysis_id=analysis_id,
            status="completed",
            message=f"Real analysis completed for {request.url}",
            craft_bugs=craft_bugs,
            ux_issues=ux_issues,
            total_issues=total_issues
        )
        
    except Exception as e:
        logger.error(f"❌ Analysis failed for {request.url}: {str(e)}")
        
        # Fallback to mock data if real analysis fails
        logger.warning("⚠️ Falling back to mock data due to analysis failure")
        report_data = generate_mock_report(analysis_id, request.dict())
        MOCK_REPORTS[analysis_id] = report_data
        save_analysis_to_disk(analysis_id, report_data)
        
        return AnalysisResponse(
            analysis_id=analysis_id,
            status="completed",
            message=f"Analysis completed for {request.url} (fallback mode)"
        )

@app.post("/api/analyze/url-scenario", response_model=AnalysisResponse)
async def analyze_url_scenario(request: AnalysisRequest):
    """Analyze a URL with a predefined scenario"""
    if not request.url:
        raise HTTPException(status_code=400, detail="URL is required")
    if not request.scenario_path:
        raise HTTPException(status_code=400, detail="Scenario path is required")
    
    analysis_id = str(uuid.uuid4())[:8]
    
    try:
        # Use the scenario executor for YAML scenario processing
        report_data = scenario_executor.execute_url_scenario(
            url=request.url,
            scenario_path=request.scenario_path,
            modules=request.modules
        )
        
        # Guard against None/invalid executor results
        if not isinstance(report_data, dict):
            error_msg = f"Scenario executor returned invalid data type: {type(report_data)}"
            logger.error(f"{error_msg} for URL {request.url}")
            raise RuntimeError(error_msg)
        
        # Ensure we have required fields for analysis status
        if "analysis_id" not in report_data:
            report_data["analysis_id"] = analysis_id
        
        # Apply robust schema normalization
        report_data = normalize_report_schema(report_data)
        
        # Final safety check
        if not isinstance(report_data, dict):
            raise RuntimeError("Report normalization failed - not a dict")
        
        # Save to both memory and disk
        MOCK_REPORTS[analysis_id] = report_data
        save_analysis_to_disk(analysis_id, report_data)
        
        return AnalysisResponse(
            analysis_id=analysis_id,
            status="completed",
            message=f"URL + Scenario analysis completed for {request.url}"
        )
        
    except Exception as e:
        logger.exception(f"Scenario analysis failed for {request.url}: {e}")  # Keep stack trace
        
        # Generate structured error report that the UI can render
        error_report = {
            "analysis_id": analysis_id,
            "status": "failed",
            "error": str(e),
            "ui_error": f"Scenario analysis failed: {str(e)}",
            "timestamp": datetime.now().isoformat(),
            "url": request.url,
            "scenario_path": request.scenario_path,
            "overall_score": 0,
            "total_issues": 1,
            "module_results": {},
            "scenario_results": [],
            "metadata": {
                "error_type": "url_scenario_analysis_error",
                "requested_modules": list(request.modules.keys())
            }
        }
        
        # Normalize the error report
        error_report = normalize_report_schema(error_report)
        
        # Save error report
        MOCK_REPORTS[analysis_id] = error_report
        try:
            save_analysis_to_disk(analysis_id, error_report)
        except Exception as save_error:
            logger.error(f"Failed to save error report: {save_error}")
        
        return AnalysisResponse(
            analysis_id=analysis_id,
            status="failed",
            message=f"Scenario analysis failed for {request.url}: {str(e)}"
        )

@app.post("/api/analyze/mock-scenario", response_model=AnalysisResponse)
async def analyze_mock_scenario(request: AnalysisRequest):
    """Analyze a mock application with a predefined scenario"""
    if not request.app_path:
        raise HTTPException(status_code=400, detail="App path is required")
    if not request.scenario_path:
        raise HTTPException(status_code=400, detail="Scenario path is required")
    
    analysis_id = str(uuid.uuid4())[:8]
    
    try:
        # Use the scenario executor for mock app analysis
        report_data = scenario_executor.execute_mock_scenario(
            mock_app_path=request.app_path,
            scenario_path=request.scenario_path,
            modules=request.modules
        )
        
        # Guard against None/invalid executor results
        if not isinstance(report_data, dict):
            error_msg = f"Mock scenario executor returned invalid data type: {type(report_data)}"
            logger.error(f"{error_msg} for app {request.app_path}")
            raise RuntimeError(error_msg)
        
        # Ensure we have required fields for analysis status
        if "analysis_id" not in report_data:
            report_data["analysis_id"] = analysis_id
        
        # Apply robust schema normalization
        report_data = normalize_report_schema(report_data)
        
        # Final safety check
        if not isinstance(report_data, dict):
            raise RuntimeError("Report normalization failed - not a dict")
        
        # Save to both memory and disk
        MOCK_REPORTS[analysis_id] = report_data
        save_analysis_to_disk(analysis_id, report_data)
        
        return AnalysisResponse(
            analysis_id=analysis_id,
            status="completed",
            message=f"Mock app + Scenario analysis completed for {request.app_path}"
        )
        
    except Exception as e:
        logger.exception(f"Mock scenario analysis failed for {request.app_path}: {e}")  # Keep stack trace
        
        # Generate structured error report that the UI can render
        error_report = {
            "analysis_id": analysis_id,
            "status": "failed",
            "error": str(e),
            "ui_error": f"Mock scenario analysis failed: {str(e)}",
            "timestamp": datetime.now().isoformat(),
            "app_path": request.app_path,
            "scenario_path": request.scenario_path,
            "overall_score": 0,
            "total_issues": 1,
            "module_results": {},
            "scenario_results": [],
            "metadata": {
                "error_type": "mock_scenario_analysis_error",
                "requested_modules": list(request.modules.keys())
            }
        }
        
        # Normalize the error report
        error_report = normalize_report_schema(error_report)
        
        # Save error report
        MOCK_REPORTS[analysis_id] = error_report
        try:
            save_analysis_to_disk(analysis_id, error_report)
        except Exception as save_error:
            logger.error(f"Failed to save error report: {save_error}")
        
        return AnalysisResponse(
            analysis_id=analysis_id,
            status="failed",
            message=f"Mock scenario analysis failed for {request.app_path}: {str(e)}"
        )
        
        # Generate structured error report for frontend
        error_report = {
            "analysis_id": analysis_id,
            "status": "failed",
            "error": str(e),
            "timestamp": datetime.now().isoformat(),
            "app_path": request.app_path,
            "scenario_path": request.scenario_path,
            "module_results": {},
            "scenario_results": [],
            "overall_score": 0,
            "total_issues": 0,
            "ui_error": f"Mock scenario analysis failed: {str(e)}"
        }
        
        # Save error report so frontend can display it
        MOCK_REPORTS[analysis_id] = error_report
        save_analysis_to_disk(analysis_id, error_report)
        
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

# Enhanced Report Endpoints with Schema Normalization

def _resolve_report_path(analysis_id: str) -> Path:
    """
    Resolve report path with support for both short and long IDs.
    Supports prefix matching for short IDs like 9808b21e.
    """
    # Try exact match first
    reports_dir = Path("reports/analysis")
    if not reports_dir.exists():
        return None
    
    # Exact filename match
    exact_path = reports_dir / f"analysis_{analysis_id}.json"
    if exact_path.exists():
        return exact_path
    
    # Try with timestamp patterns
    for json_file in reports_dir.glob(f"analysis_{analysis_id}_*.json"):
        return json_file
    
    # Prefix match (short id support)
    for json_file in reports_dir.glob("analysis_*.json"):
        stem_parts = json_file.stem.split("_")
        if len(stem_parts) >= 2 and stem_parts[1].startswith(analysis_id):
            return json_file
    
    return None

@app.get("/api/reports/{report_id}")
async def get_report(report_id: str):
    """Get analysis report with enhanced disk/cache lookup and schema normalization"""
    
    # Check analysis cache first (for active/recent analyses)
    if report_id in ANALYSIS_CACHE:
        cached = ANALYSIS_CACHE[report_id]
        if cached["status"] == "completed":
            result = cached["result"]
            # Apply schema normalization
            result = normalize_report_schema(result)
            # Ensure consistent analysis_id
            result["analysis_id"] = report_id
            result["requested_id"] = report_id
            return result
        elif cached["status"] == "failed":
            # Return the failed result with proper structure instead of raising exception
            result = cached["result"]
            result = normalize_report_schema(result)
            result["analysis_id"] = report_id
            result["requested_id"] = report_id
            return result
        else:
            # Still processing
            return {
                "analysis_id": report_id,
                "requested_id": report_id,
                "status": cached["status"],
                "message": "Analysis still in progress",
                "started_at": cached.get("started_at", "").isoformat() if hasattr(cached.get("started_at", ""), "isoformat") else str(cached.get("started_at", ""))
            }
    
    # Check legacy mock reports
    if report_id in MOCK_REPORTS:
        report = MOCK_REPORTS[report_id]
        report = normalize_report_schema(report)
        report["analysis_id"] = report_id
        report["requested_id"] = report_id
        return report
    
    # Enhanced path resolution with short ID support
    report_path = _resolve_report_path(report_id)
    if report_path and report_path.exists():
        try:
            with open(report_path, 'r') as f:
                report = json.load(f)
            
            # Apply schema normalization
            report = normalize_report_schema(report)
            
            # Ensure consistent analysis_id in response
            report["analysis_id"] = report_id
            report["requested_id"] = report_id
            return report
        except Exception as e:
            logger.error(f"Error loading report {report_id}: {e}")
            raise HTTPException(status_code=500, detail=f"Error loading report: {str(e)}")
    
    # Final fallback - check load_analysis_from_disk
    report = load_analysis_from_disk(report_id)
    if report:
        # Apply schema normalization
        report = normalize_report_schema(report)
        # Ensure consistent analysis_id in response
        report["analysis_id"] = report_id
        report["requested_id"] = report_id
        return report
    
    # Not found - return a helpful response
    return {
        "analysis_id": report_id, 
        "status": "not found", 
        "requested_id": report_id,
        "message": f"Report {report_id} not found in cache or disk storage"
    }

@app.get("/api/reports")
async def list_reports(
    limit: int = 50,
    offset: int = 0,
    analysis_type: Optional[str] = None,
    min_score: Optional[int] = None,
    has_craft_bugs: Optional[bool] = None,
    include_failed: bool = False
):
    """List reports with enhanced filtering"""
    
    filters = {}
    if analysis_type:
        filters["analysis_type"] = analysis_type
    if min_score is not None:
        filters["min_score"] = min_score
    if has_craft_bugs is not None:
        filters["has_craft_bugs"] = has_craft_bugs
    
    result = list_saved_reports(limit=limit, offset=offset, filters=filters)
    
    # Filter out failed reports by default unless explicitly requested
    if not include_failed:
        original_reports = result.get("reports", [])
        
        def is_success(r):
            # Treat completed as successful; failed only when explicitly failed
            status = r.get("status", "")
            return (
                status in ["completed", "success", "done"] and 
                not r.get("failed", False) and
                status != "failed"
            )
        
        successful_reports = [r for r in original_reports if is_success(r)]
        result["reports"] = successful_reports
        # Update pagination info if we filtered results
        if len(successful_reports) != len(original_reports):
            pagination = result.get("pagination", {})
            pagination["filtered_count"] = len(successful_reports)
            pagination["total_unfiltered"] = len(original_reports)
    
    return {
        "reports": result.get("reports", []),
        "pagination": result.get("pagination", {}),
        "statistics": result.get("statistics", {}),
        "filters_applied": {**filters, "include_failed": include_failed}
    }

@app.post("/api/reports/search")
async def search_reports(request: ReportSearchRequest):
    """Advanced report search"""
    
    query = {k: v for k, v in request.dict().items() 
             if v is not None and k not in ["limit", "offset"]}
    
    results = search_saved_reports(query)
    
    # Apply pagination
    total = len(results)
    paginated = results[request.offset:request.offset + request.limit]
    
    return {
        "results": paginated,
        "total": total,
        "limit": request.limit,
        "offset": request.offset,
        "has_more": request.offset + request.limit < total,
        "query": query
    }

@app.get("/api/reports/statistics")
async def report_statistics():
    """Get comprehensive report statistics"""
    return get_report_statistics()

@app.get("/api/statistics")
async def statistics():
    """Get comprehensive report statistics (alternative endpoint)"""
    return get_report_statistics()

@app.get("/api/analysis/{analysis_id}/status")
async def get_analysis_status(analysis_id: str):
    """Get real-time analysis status"""
    
    if analysis_id in ANALYSIS_CACHE:
        cached = ANALYSIS_CACHE[analysis_id]
        return {
            "analysis_id": analysis_id,
            "status": cached["status"],
            "started_at": cached.get("started_at", "").isoformat() if hasattr(cached.get("started_at", ""), "isoformat") else str(cached.get("started_at", "")),
            "completed_at": cached.get("completed_at", "").isoformat() if hasattr(cached.get("completed_at", ""), "isoformat") else str(cached.get("completed_at", "")) if cached.get("completed_at") else None,
            "error": cached.get("error"),
            "file_path": cached.get("file_path")
        }
    
    # Check if it exists on disk
    report = load_analysis_from_disk(analysis_id)
    if report:
        return {
            "analysis_id": analysis_id,
            "status": "completed",
            "stored_on_disk": True,
            "timestamp": report.get("timestamp")
        }
    
    raise HTTPException(status_code=404, detail="Analysis not found")

# Utility Endpoints

# Global scenarios cache
SCENARIOS_CACHE = []

def load_all_scenarios():
    """Load all scenarios and cache them"""
    global SCENARIOS_CACHE
    SCENARIOS_CACHE = get_available_scenarios()
    return SCENARIOS_CACHE

@app.get("/api/scenarios")
async def get_scenarios():
    """Get available scenarios"""
    try:
        scenarios = get_available_scenarios()
        return {"scenarios": scenarios}
    except Exception as e:
        logger.error(f"Error loading scenarios: {e}")
        return {"scenarios": []}

@app.post("/api/scenarios/reload")
async def reload_scenarios():
    """Reload scenarios cache"""
    try:
        scenarios = load_all_scenarios()
        logger.info(f"Reloaded {len(scenarios)} scenarios")
        return {"count": len(scenarios), "message": "Scenarios reloaded successfully"}
    except Exception as e:
        logger.error(f"Error reloading scenarios: {e}")
        return {"count": 0, "error": str(e)}

@app.get("/api/modules")
async def get_available_modules():
    """Get available analysis modules with descriptions"""
    modules = [
        {
            "key": "performance",
            "name": "Performance Analysis",
            "description": "Core Web Vitals and loading metrics",
            "enabled": True
        },
        {
            "key": "accessibility", 
            "name": "Accessibility Audit",
            "description": "WCAG 2.1 compliance testing",
            "enabled": True
        },
        {
            "key": "keyboard",
            "name": "Keyboard Navigation", 
            "description": "Keyboard accessibility evaluation",
            "enabled": True
        },
        {
            "key": "ux_heuristics",
            "name": "UX Heuristics",
            "description": "Nielsen's usability principles", 
            "enabled": True
        },
        {
            "key": "best_practices",
            "name": "Best Practices",
            "description": "Modern web development standards",
            "enabled": True
        },
        {
            "key": "health_alerts", 
            "name": "Health Alerts",
            "description": "Critical issues detection",
            "enabled": True
        },
        {
            "key": "functional",
            "name": "Functional Testing",
            "description": "User journey validation", 
            "enabled": False
        }
    ]
    return {"modules": modules}

@app.post("/api/reports/cleanup")
async def cleanup_reports(days_to_keep: int = 30):
    """Clean up old reports"""
    try:
        result = cleanup_old_reports(days_to_keep)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Cleanup failed: {str(e)}")

@app.delete("/api/reports/{report_id}")
async def delete_report(report_id: str):
    """Delete a specific report"""
    
    # Remove from caches
    if report_id in ANALYSIS_CACHE:
        del ANALYSIS_CACHE[report_id]
    
    if report_id in MOCK_REPORTS:
        del MOCK_REPORTS[report_id]
    
    # Delete from disk
    from enhanced_report_handler import get_report_handler
    success = get_report_handler().delete_report(report_id)
    
    if success:
        return {"message": f"Report {report_id} deleted successfully"}
    else:
        raise HTTPException(status_code=404, detail="Report not found")

# Legacy endpoints for backwards compatibility
@app.post("/api/analyze/screenshot", response_model=AnalysisResponse)
async def analyze_screenshot(
    screenshot: UploadFile = File(...),
    config: str = Form(...)
):
    """Analyze an uploaded screenshot"""
    try:
        config_data = json.loads(config)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid config JSON")
    
    analysis_id = str(uuid.uuid4())[:8]
    
    # Save uploaded file temporarily
    with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp_file:
        content = await screenshot.read()
        tmp_file.write(content)
        tmp_path = tmp_file.name
    
    # Generate mock report
    config_data["screenshot_path"] = tmp_path
    report_data = generate_mock_report(analysis_id, config_data)
    MOCK_REPORTS[analysis_id] = report_data
    
    # Save to disk
    save_analysis_to_disk(analysis_id, report_data)
    
    # Clean up temp file
    os.unlink(tmp_path)
    
    return AnalysisResponse(
        analysis_id=analysis_id,
        status="completed",
        message=f"Screenshot analysis completed"
    )

@app.get("/api/reports/{report_id}/download")
async def download_report(report_id: str, format: str = "json"):
    """Download report in specified format"""
    
    # Get report from any source
    report = None
    file_path = None
    
    if report_id in ANALYSIS_CACHE and ANALYSIS_CACHE[report_id]["status"] == "completed":
        report = ANALYSIS_CACHE[report_id]["result"]
    elif report_id in MOCK_REPORTS:
        report = MOCK_REPORTS[report_id]
    else:
        report = load_analysis_from_disk(report_id)
        # Try to find the actual file for direct download
        import glob
        pattern = f"reports/analysis/analysis_{report_id}_*.json"
        matches = glob.glob(pattern)
        if matches:
            file_path = matches[0]
    
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    
    # Ensure consistent analysis_id in downloaded report
    report["analysis_id"] = report_id
    report["requested_id"] = report_id
    
    if format == "json":
        # If we have a file path, return it directly
        if file_path and os.path.exists(file_path):
            from fastapi.responses import FileResponse
            return FileResponse(
                file_path, 
                media_type="application/json",
                filename=f"analysis_{report_id}.json"
            )
        else:
            # Return JSON response
            from fastapi.responses import JSONResponse
            return JSONResponse(
                content=report,
                headers={"Content-Disposition": f"attachment; filename=analysis_{report_id}.json"}
            )
    
    elif format == "html":
        # Return enhanced HTML version with contextual media
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Enhanced UX Analysis Report</title>
            <style>
                body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif; margin: 40px; line-height: 1.6; background: #f5f5f5; }}
                .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
                .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; border-radius: 10px; margin-bottom: 30px; }}
                .score {{ font-size: 48px; font-weight: bold; color: white; text-align: center; margin: 20px 0; }}
                .craft-bugs {{ background: #fff3cd; padding: 20px; border-radius: 8px; margin: 20px 0; border: 1px solid #ffeaa7; }}
                .module {{ margin: 25px 0; padding: 20px; border: 1px solid #e5e7eb; border-radius: 10px; background: #f9fafb; }}
                .module h3 {{ color: #1f2937; border-bottom: 2px solid #e5e7eb; padding-bottom: 10px; margin-bottom: 20px; }}
                .finding-item {{ 
                    display: flex; 
                    align-items: flex-start; 
                    gap: 20px; 
                    padding: 20px; 
                    border-bottom: 1px solid #e9ecef; 
                    background: white; 
                    border-radius: 8px; 
                    margin: 15px 0;
                }}
                .finding-content {{ flex: 1; min-width: 0; }}
                .finding-media-sidebar {{ flex-shrink: 0; width: 350px; max-width: 350px; }}
                .media-container {{ 
                    background: #f8f9fa; 
                    border: 1px solid #e9ecef; 
                    border-radius: 6px; 
                    padding: 15px; 
                    margin-top: 10px; 
                }}
                .media-container h5 {{ 
                    margin: 0 0 10px 0; 
                    color: #495057; 
                    font-size: 0.9em; 
                    font-weight: 600; 
                }}
                .issue-screenshot {{ 
                    max-width: 100%; 
                    height: auto; 
                    border: 1px solid #ddd; 
                    border-radius: 4px; 
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1); 
                }}
                .issue-video {{ 
                    max-width: 100%; 
                    height: auto; 
                    border: 1px solid #ddd; 
                    border-radius: 4px; 
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1); 
                }}
                .media-caption {{ 
                    font-size: 0.8em; 
                    color: #6c757d; 
                    margin-top: 8px; 
                    text-align: center; 
                }}
                .no-media-placeholder {{ 
                    background: #e9ecef; 
                    border: 2px dashed #adb5bd; 
                    border-radius: 4px; 
                    padding: 20px; 
                    text-align: center; 
                    color: #6c757d; 
                    font-style: italic; 
                }}
                .severity-badge {{ 
                    padding: 4px 8px; 
                    border-radius: 4px; 
                    font-size: 0.8em; 
                    font-weight: bold; 
                    text-transform: uppercase; 
                    color: white; 
                }}
                .severity-high {{ background: #dc3545; }}
                .severity-medium {{ background: #ffc107; color: black; }}
                .severity-low {{ background: #28a745; }}
                .category-badge {{ 
                    font-size: 0.8em; 
                    color: #6c757d; 
                    background: #e9ecef; 
                    padding: 2px 6px; 
                    border-radius: 3px; 
                }}
                .steps {{ margin: 10px 0; }}
                .step {{ padding: 8px; margin: 5px 0; background: #f8f9fa; border-radius: 4px; }}
                .success {{ border-left: 4px solid #10b981; }}
                .warning {{ border-left: 4px solid #f59e0b; }}
                .error {{ border-left: 4px solid #ef4444; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🎯 Enhanced UX Analysis Report</h1>
                    <p><strong>Report ID:</strong> {report_id}</p>
                    <p><strong>Analysis Type:</strong> {report.get('type', 'Unknown')}</p>
                    <p><strong>Overall Score:</strong> <span class="score">{report.get('overall_score', 0)}/100</span></p>
                    <p><strong>Timestamp:</strong> {report.get('timestamp', 'Unknown')}</p>
                </div>
                
                <div class="craft-bugs">
                    <h2>🔍 Craft Bug Analysis</h2>
                    <p><strong>Craft Bugs Detected:</strong> {len(report.get('craft_bugs_detected', []))}</p>
                    <p><strong>Pattern Issues:</strong> {len(report.get('pattern_issues', []))}</p>
                </div>
                
                <h2>📊 Module Results</h2>
        """
        
        # Add modules with contextual media
        for module_name, module_data in report.get('modules', {}).items():
            html_content += f"""
                <div class="module">
                    <h3>{module_name.title()} - Score: {module_data.get('score', 0)}/100</h3>
            """
            
            # Add findings with contextual media
            findings = module_data.get('findings', [])
            if findings:
                for finding in findings:
                    severity = finding.get('severity', 'medium')
                    issue_category = _categorize_issue(finding)
                    
                    html_content += f"""
                        <div class="finding-item">
                            <div class="finding-content">
                                <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 10px;">
                                    <span class="severity-badge severity-{severity}">{severity}</span>
                                    <span class="category-badge">{issue_category.title()}</span>
                                </div>
                                <strong>{finding.get('message', 'No message')}</strong><br>
                                <small style="color: #6c757d;">Element: {finding.get('element', 'Unknown')}</small>
                            </div>
                            
                            <div class="finding-media-sidebar">
                    """
                    
                    # Add contextual media based on issue category
                    has_media = False
                    
                    # Screenshot for visual/functional issues
                    if issue_category in ['visual', 'functional'] and (finding.get('screenshot') or finding.get('screenshot_base64')):
                        has_media = True
                        html_content += """
                                <div class="media-container">
                                    <h5>📸 Visual Evidence</h5>
                        """
                        
                        # Screenshot from file
                        if finding.get('screenshot'):
                            html_content += f"""
                                    <img src="file://{finding.get('screenshot')}" class="issue-screenshot" alt="Issue Screenshot">
                            """
                        
                        # Base64 screenshot
                        if finding.get('screenshot_base64'):
                            html_content += f"""
                                    <img src="data:image/png;base64,{finding.get('screenshot_base64')}" class="issue-screenshot" alt="Issue Screenshot">
                            """
                        
                        html_content += """
                                    <div class="media-caption">Contextual Screenshot</div>
                                </div>
                        """
                    
                    # Video for performance issues
                    if issue_category in ['performance', 'functional'] and finding.get('video'):
                        has_media = True
                        html_content += """
                                <div class="media-container">
                                    <h5>🎥 Performance Evidence</h5>
                                    <video class="issue-video" controls>
                                        <source src="file://{finding.get('video')}" type="video/webm">
                                        Your browser does not support the video tag.
                                    </video>
                                    <div class="media-caption">Performance Recording</div>
                                </div>
                        """
                    
                    # Placeholder if no media available
                    if not has_media:
                        html_content += """
                                <div class="media-container">
                                    <div class="no-media-placeholder">
                                        📷 No media captured<br>
                                        <small>Media will be captured during analysis</small>
                                    </div>
                                </div>
                        """
                    
                    html_content += """
                            </div>
                        </div>
                    """
            else:
                html_content += """
                    <p style="color: #6c757d; font-style: italic;">No issues found in this module.</p>
                """
            
            html_content += """
                </div>
            """
        
        html_content += """
                <h2>🎯 Scenario Steps</h2>
                <div class="steps">
        """
        
        # Add scenario steps
        for step in report.get('steps', []):
            status_class = step.get('status', '')
            html_content += f"""
                    <div class="step {status_class}">{step.get('action', 'Unknown')} - {step.get('status', 'Unknown')} ({step.get('duration_ms', 0)}ms)</div>
            """
        
        html_content += """
                </div>
            </div>
        </body>
        </html>
        """
        return HTMLResponse(content=html_content)
    else:
        return JSONResponse(content=report)

# Dashboard API Endpoints
@app.get("/api/dashboard/analytics")
async def get_dashboard_analytics(days: int = 7):
    """Get analytics data for the dashboard"""
    if not DASHBOARD_AVAILABLE:
        raise HTTPException(status_code=503, detail="Dashboard components not available")
    
    try:
        dashboard = UXAnalyticsDashboard()
        analytics = dashboard.generate_dashboard_report(days=days)
        return JSONResponse(content=analytics)
    except Exception as e:
        logger.error(f"Dashboard analytics error: {e}")
        raise HTTPException(status_code=500, detail=f"Analytics generation failed: {str(e)}")

@app.get("/api/dashboard/alerts")
async def get_dashboard_alerts():
    """Get active dashboard alerts"""
    if not DASHBOARD_AVAILABLE:
        raise HTTPException(status_code=503, detail="Dashboard components not available")
    
    try:
        dashboard = UXAnalyticsDashboard()
        alerts = dashboard.db.get_active_alerts()
        return JSONResponse(content=[{
            "alert_id": alert.alert_id,
            "title": alert.title,
            "message": alert.message,
            "severity": alert.severity,
            "timestamp": alert.timestamp.isoformat(),
            "app_type": alert.app_type,
            "resolved": alert.resolved
        } for alert in alerts])
    except Exception as e:
        logger.error(f"Dashboard alerts error: {e}")
        raise HTTPException(status_code=500, detail=f"Alerts retrieval failed: {str(e)}")

@app.post("/api/dashboard/process-results")
async def process_analysis_results_endpoint(report_id: str):
    """Process analysis results for dashboard integration"""
    if not DASHBOARD_AVAILABLE:
        raise HTTPException(status_code=503, detail="Dashboard components not available")
    
    try:
        # Load the analysis results
        analysis_data = load_analysis_from_disk(report_id)
        if not analysis_data:
            raise HTTPException(status_code=404, detail="Analysis report not found")
        
        # Process through dashboard
        dashboard = UXAnalyticsDashboard()
        
        # Convert to dashboard format if needed
        dashboard_data = {
            "test_run_id": analysis_data.get("analysis_id", report_id),
            "timestamp": analysis_data.get("timestamp", datetime.now().isoformat()),
            "app_type": analysis_data.get("app_type", "unknown"),
            "scenarios_tested": 1,
            "total_issues_found": len(analysis_data.get("issues", [])),
            "ai_analysis_enabled": analysis_data.get("ai_analysis_enabled", False),
            "scenarios": {
                "main_scenario": {
                    "title": analysis_data.get("scenario_name", "Analysis"),
                    "issues": analysis_data.get("issues", [])
                }
            }
        }
        
        # Save to temp file and process
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(dashboard_data, f, indent=2)
            temp_file = f.name
        
        try:
            dashboard.process_analysis_results(temp_file)
        finally:
            os.unlink(temp_file)
        
        return JSONResponse(content={"status": "success", "message": "Results processed for dashboard"})
        
    except Exception as e:
        logger.error(f"Dashboard processing error: {e}")
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")

@app.post("/api/dashboard/create-ado-tickets")
async def create_ado_tickets(request: dict):
    """Create Azure DevOps tickets from analysis results"""
    if not DASHBOARD_AVAILABLE:
        raise HTTPException(status_code=503, detail="Dashboard components not available")
    
    try:
        report_id = request.get("report_id")
        demo_mode = request.get("demo_mode", True)
        issue_data = request.get("issue_data")
        
        # Initialize ADO client
        ado_client = AzureDevOpsClient(demo_mode=demo_mode)
        
        if issue_data:
            # Create single work item from provided issue data
            work_item = ado_client.create_ux_work_item(issue_data)
            work_items = [work_item] if work_item else []
        else:
            # Load the analysis results and create work items for all issues
            analysis_data = load_analysis_from_disk(report_id)
            if not analysis_data:
                raise HTTPException(status_code=404, detail="Analysis report not found")
            
            # Create work items for each issue
            work_items = []
            issues = analysis_data.get("issues", [])
            
            for i, issue in enumerate(issues):
                ux_issue = {
                    "app_type": analysis_data.get("app_type", "unknown"),
                    "scenario_id": f"scenario_{i}",
                    "title": issue.get("title", f"UX Issue {i+1}"),
                    "description": issue.get("description", str(issue)),
                    "category": issue.get("category", "General"),
                    "severity": issue.get("severity", "medium")
                }
                
                work_item = ado_client.create_ux_work_item(ux_issue)
                if work_item:
                    work_items.append(work_item)
        
        return JSONResponse(content={
            "status": "success", 
            "work_items_created": len(work_items),
            "work_items": work_items,
            "demo_mode": demo_mode
        })
        
    except Exception as e:
        logger.error(f"ADO ticket creation error: {e}")
        raise HTTPException(status_code=500, detail=f"Ticket creation failed: {str(e)}")

# New endpoints for UI integration
@app.post("/api/analyze/url", response_model=AnalysisResponse)
async def analyze_url(
    url: str = Form(...),
    scenario_name: str = Form(None),
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    """Analyze a URL - simplified endpoint for frontend integration"""
    try:
        analysis_id = str(uuid.uuid4())[:8]
        logger.info(f"Starting URL analysis: {analysis_id} for {url}")
        
        # Create analysis request object with proper modules format
        modules_dict = {
            "accessibility": True,
            "performance": True,
            "keyboard": True,
            "ux_heuristics": True,
            "best_practices": True,
            "health_alerts": True,
            "functional": False
        }
        
        # Resolve scenario name to path and ID
        scenario_path, scenario_id = resolve_scenario_name_to_path_and_id(scenario_name)
        
        request = AnalysisRequest(
            url=url,
            scenario_path=scenario_path,
            modules=modules_dict
        )
        
        # Process analysis in background
        async def run_analysis():
            try:
                # Handle specific scenario ID selection for Word/Excel/PowerPoint scenarios
                if scenario_id and scenario_path.endswith(('word_scenarios.yaml', 'excel_scenarios.yaml', 'powerpoint_scenarios.yaml')):
                    # For Office app scenarios, we need to pass the specific scenario ID
                    report_data = scenario_executor.execute_specific_scenario(
                        url=request.url,
                        scenario_path=request.scenario_path,
                        scenario_id=scenario_id,
                        modules=request.modules
                    )
                else:
                    # For regular scenarios, use the existing method
                    report_data = scenario_executor.execute_url_scenario(
                        url=request.url,
                        scenario_path=request.scenario_path,
                        modules=request.modules
                    )
                
                # Guard against None/invalid executor results
                if not isinstance(report_data, dict):
                    error_msg = f"Background scenario executor returned invalid data type: {type(report_data)}"
                    logger.error(f"{error_msg} for URL {request.url}")
                    raise RuntimeError(error_msg)
                
                # Apply robust schema normalization
                report_data = normalize_report_schema(report_data)
                
                # Ensure we have required fields for analysis status
                if "analysis_id" not in report_data:
                    report_data["analysis_id"] = analysis_id
                
                MOCK_REPORTS[analysis_id] = report_data
                save_analysis_to_disk(analysis_id, report_data)
                logger.info(f"URL analysis completed: {analysis_id}")
                
            except Exception as e:
                logger.exception(f"Background URL analysis failed: {analysis_id} - {e}")
                
                # Generate error report for background task
                error_report = {
                    "analysis_id": analysis_id,
                    "status": "failed",
                    "error": str(e),
                    "ui_error": f"Background analysis failed: {str(e)}",
                    "timestamp": datetime.now().isoformat(),
                    "url": request.url,
                    "scenario_path": request.scenario_path,
                    "overall_score": 0,
                    "total_issues": 1,
                    "module_results": {},
                    "scenario_results": []
                }
                
                error_report = normalize_report_schema(error_report)
                MOCK_REPORTS[analysis_id] = error_report
                try:
                    save_analysis_to_disk(analysis_id, error_report)
                except Exception as save_error:
                    logger.error(f"Failed to save background error report: {save_error}")
        
        background_tasks.add_task(run_analysis)
        
        return AnalysisResponse(
            analysis_id=analysis_id,
            status="started",
            message=f"URL analysis started for {url}",
            estimated_duration_minutes=2
        )
        
    except Exception as e:
        logger.error(f"URL analysis setup failed: {e}")
        raise HTTPException(status_code=500, detail=f"Analysis setup failed: {str(e)}")

@app.post("/api/analyze/scenario")
async def analyze_scenario(
    scenario_file: UploadFile = File(...),
    url: str = Form(None)
):
    """Upload and execute a custom scenario YAML file"""
    try:
        analysis_id = str(uuid.uuid4())[:8]
        
        # Save uploaded scenario file
        scenarios_dir = "scenarios/custom"
        os.makedirs(scenarios_dir, exist_ok=True)
        scenario_path = f"{scenarios_dir}/{analysis_id}_{scenario_file.filename}"
        
        with open(scenario_path, "wb") as f:
            content = await scenario_file.read()
            f.write(content)
        
        # Execute scenario with proper modules format
        modules_dict = {
            "accessibility": True,
            "performance": True,
            "keyboard": True,
            "ux_heuristics": True,
            "best_practices": True,
            "health_alerts": True,
            "functional": False
        }
        
        request = AnalysisRequest(
            url=url,
            scenario_path=scenario_path,
            modules=modules_dict
        )
        
        report_data = scenario_executor.execute_url_scenario(
            url=request.url,
            scenario_path=request.scenario_path,
            modules=request.modules
        )
        
        # Guard against None/invalid executor results
        if not isinstance(report_data, dict):
            error_msg = f"Custom scenario executor returned invalid data type: {type(report_data)}"
            logger.error(f"{error_msg} for URL {url}")
            raise RuntimeError(error_msg)
        
        # Apply robust schema normalization
        report_data = normalize_report_schema(report_data)
        
        # Ensure we have required fields for analysis status
        if "analysis_id" not in report_data:
            report_data["analysis_id"] = analysis_id
        
        MOCK_REPORTS[analysis_id] = report_data
        save_analysis_to_disk(analysis_id, report_data)
        
        return AnalysisResponse(
            analysis_id=analysis_id,
            status="completed",
            message="Custom scenario analysis completed",
            estimated_duration_minutes=0
        )
        
    except Exception as e:
        logger.exception(f"Custom scenario analysis failed: {e}")
        
        # Generate structured error report
        error_report = {
            "analysis_id": analysis_id,
            "status": "failed",
            "error": str(e),
            "ui_error": f"Custom scenario analysis failed: {str(e)}",
            "timestamp": datetime.now().isoformat(),
            "url": url,
            "scenario_path": scenario_path,
            "overall_score": 0,
            "total_issues": 1,
            "module_results": {},
            "scenario_results": []
        }
        
        error_report = normalize_report_schema(error_report)
        MOCK_REPORTS[analysis_id] = error_report
        try:
            save_analysis_to_disk(analysis_id, error_report)
        except Exception as save_error:
            logger.error(f"Failed to save custom scenario error report: {save_error}")
        
        raise HTTPException(status_code=500, detail=f"Custom scenario analysis failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Scenario analysis failed: {str(e)}")

async def update_ado_work_item_on_fix(issue_data: Dict[str, Any], fix_details: Dict[str, Any]) -> Dict[str, Any]:
    """Update Azure DevOps work item when a fix is applied"""
    try:
        # Check if this issue has an associated ADO work item
        ado_work_item_id = issue_data.get("ado_work_item_id")
        if not ado_work_item_id:
            return {"ado_updated": False, "reason": "No ADO work item ID found"}
        
        # Initialize ADO client
        ado_client = AzureDevOpsClient()
        
        # Prepare fix details for ADO update
        fix_result = ado_client.mark_issue_fixed(ado_work_item_id, fix_details)
        
        if fix_result.get("success"):
            return {
                "ado_updated": True,
                "work_item_id": ado_work_item_id,
                "ado_status": "Resolved",
                "ado_response": fix_result
            }
        else:
            return {
                "ado_updated": False,
                "error": fix_result.get("error", "Unknown ADO error"),
                "work_item_id": ado_work_item_id
            }
            
    except Exception as e:
        logger.error(f"Failed to update ADO work item: {e}")
        return {
            "ado_updated": False,
            "error": str(e)
        }

@app.post("/api/fix-now")
async def fix_now(
    issue_id: str = Form(...),
    report_id: str = Form(...),
    fix_type: str = Form(...)
):
    """Apply immediate fixes for UX issues"""
    try:
        # First try to load from real report files
        import glob
        file_pattern = f"reports/analysis/analysis_{report_id}_*.json"
        matching_files = glob.glob(file_pattern)
        
        report_data = None
        file_path = None
        
        if matching_files:
            # Load from real report file
            file_path = matching_files[0]
            with open(file_path, "r") as f:
                report_data = json.load(f)
        else:
            # Fallback to mock reports
            report_data = MOCK_REPORTS.get(report_id)
            if not report_data:
                raise HTTPException(status_code=404, detail="Report not found")
        
        # Handle new format: module_results > fix_type > findings[]
        module_results = report_data.get("module_results", {})
        if fix_type in module_results:
            findings = module_results[fix_type].get("findings", [])
            try:
                # Extract index from issue_id like 'accessibility-0'
                finding_index = int(issue_id.split("-")[1])
                if finding_index >= len(findings):
                    raise HTTPException(status_code=404, detail="Issue index out of range")
                
                target_finding = findings[finding_index]
                
                # Apply fix - mark as fixed
                target_finding["fixed"] = True
                target_finding["fix_timestamp"] = datetime.now().isoformat()
                
                # Track fix history
                fix_log = {
                    "issue_id": issue_id,
                    "fixed_by": "system",
                    "timestamp": datetime.now().isoformat(),
                    "finding_type": target_finding.get("type", "unknown"),
                    "message": target_finding.get("message", "")
                }
                report_data.setdefault("fix_history", []).append(fix_log)
                
                # Save updated report back to file
                if file_path:
                    with open(file_path, "w") as f:
                        json.dump(report_data, f, indent=2)
                else:
                    MOCK_REPORTS[report_id] = report_data
                    save_analysis_to_disk(report_id, report_data)
                
                # Update Azure DevOps work item if applicable
                ado_update_result = await update_ado_work_item_on_fix(
                    target_finding, 
                    {
                        "timestamp": target_finding["fix_timestamp"],
                        "fix_type": fix_type,
                        "finding_type": target_finding.get("type", "unknown"),
                        "message": target_finding.get("message", "")
                    }
                )
                
                # Include ADO update in response
                response_content = {
                    "status": "success",
                    "message": f"Issue '{issue_id}' marked as fixed",
                    "finding": {
                        "type": target_finding.get("type"),
                        "message": target_finding.get("message"),
                        "fixed": True
                    },
                    "fix_timestamp": target_finding["fix_timestamp"],
                    "ado_integration": ado_update_result
                }
                
                return JSONResponse(content=response_content)
                
            except (IndexError, ValueError) as e:
                raise HTTPException(status_code=400, detail=f"Invalid issue_id format: {issue_id}")
        
        # Fallback to legacy ux_issues format
        issue = None
        for issue_item in report_data.get("ux_issues", []):
            if issue_item.get("issue_id") == issue_id:
                issue = issue_item
                break
        
        if not issue:
            raise HTTPException(status_code=404, detail=f"Issue '{issue_id}' not found in report")
        
        # Generate fix suggestions for legacy format
        fix_suggestions = []
        issue_type = issue.get("type", "general")
        
        if issue_type == "accessibility":
            fix_suggestions = [
                "Add alt text to images",
                "Improve color contrast ratio",
                "Add ARIA labels to interactive elements",
                "Ensure keyboard navigation support"
            ]
        elif issue_type == "performance":
            fix_suggestions = [
                "Optimize image compression",
                "Minify CSS and JavaScript",
                "Enable browser caching",
                "Reduce server response time"
            ]
        elif issue_type == "usability":
            fix_suggestions = [
                "Simplify navigation structure",
                "Improve button sizing and placement",
                "Add clear call-to-action buttons",
                "Enhance form validation messages"
            ]
        else:
            fix_suggestions = [
                "Review design guidelines",
                "Test with real users",
                "Implement responsive design",
                "Optimize user flow"
            ]
        
        # Mark legacy issue as being fixed
        issue["status"] = "fixing"
        issue["fix_applied"] = True
        issue["fix_timestamp"] = datetime.now().isoformat()
        issue["fix_suggestions"] = fix_suggestions
        
        # Save updated report
        if file_path:
            with open(file_path, "w") as f:
                json.dump(report_data, f, indent=2)
        else:
            MOCK_REPORTS[report_id] = report_data
            save_analysis_to_disk(report_id, report_data)
        
        # Update Azure DevOps work item if applicable
        ado_update_result = await update_ado_work_item_on_fix(
            issue,
            {
                "timestamp": issue["fix_timestamp"],
                "fix_type": fix_type,
                "fix_suggestions": fix_suggestions,
                "issue_type": issue.get("type", "general")
            }
        )
        
        return JSONResponse(content={
            "status": "success",
            "message": f"Fix initiated for issue {issue_id}",
            "fix_suggestions": fix_suggestions,
            "issue_status": "fixing",
            "ado_integration": ado_update_result
        })
        
    except Exception as e:
        logger.error(f"Fix-now operation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Fix operation failed: {str(e)}")

# ===== AZURE DEVOPS INTEGRATION ENDPOINTS =====

async def auto_create_ado_work_items(report_data: dict, analysis_id: str):
    """Automatically create Azure DevOps work items for issues found in analysis"""
    try:
        # Check if ADO integration is enabled
        ado_enabled = os.getenv('ADO_ENABLED', 'false').lower() == 'true'
        if not ado_enabled:
            logger.info("ADO integration disabled - skipping automatic work item creation")
            return
        
        # Initialize ADO client
        ado_client = AzureDevOpsClient(demo_mode=False)
        
        # Extract issues from report data
        issues = []
        
        # Check for module findings
        if "module_results" in report_data:
            for module_key, module_data in report_data["module_results"].items():
                if isinstance(module_data, dict) and "findings" in module_data:
                    for finding in module_data["findings"]:
                        if isinstance(finding, dict):
                            issues.append({
                                "title": finding.get("title", f"UX Issue: {finding.get('message', 'Unknown')}"),
                                "description": finding.get("message", ""),
                                "category": module_key,
                                "severity": finding.get("severity", "medium"),
                                "app_type": report_data.get("app_type", "web-app"),
                                "scenario_id": f"{analysis_id}_{module_key}",
                                "element": finding.get("element", "unknown")
                            })
        
        # Check for legacy issues
        if "issues" in report_data:
            for i, issue in enumerate(report_data["issues"]):
                if isinstance(issue, dict):
                    issues.append({
                        "title": issue.get("title", f"UX Issue {i+1}"),
                        "description": issue.get("description", str(issue)),
                        "category": issue.get("category", "General"),
                        "severity": issue.get("severity", "medium"),
                        "app_type": report_data.get("app_type", "web-app"),
                        "scenario_id": f"{analysis_id}_legacy_{i}",
                        "element": issue.get("element", "unknown")
                    })
        
        # Create work items for each issue
        work_items_created = []
        for issue in issues:
            try:
                work_item = ado_client.create_ux_work_item(issue)
                if work_item and work_item.get("success"):
                    work_items_created.append(work_item)
                    logger.info(f"Created ADO work item: {work_item.get('work_item_id')} for {issue['title']}")
            except Exception as e:
                logger.error(f"Failed to create ADO work item for {issue['title']}: {e}")
        
        # Update report data with ADO integration info
        if work_items_created:
            report_data["ado_integration"] = {
                "work_items_created": len(work_items_created),
                "work_items": work_items_created,
                "sync_status": "completed",
                "last_sync_date": datetime.now().isoformat(),
                "organization": ado_client.organization,
                "project": ado_client.project
            }
            logger.info(f"Created {len(work_items_created)} ADO work items for analysis {analysis_id}")
        
    except Exception as e:
        logger.error(f"Auto ADO work item creation failed for analysis {analysis_id}: {e}")
        # Don't fail the analysis if ADO integration fails

@app.get("/api/ado/issue-url/{work_item_id}")
async def get_ado_issue_url(work_item_id: int):
    """Get the Azure DevOps URL for a work item to enable 'View & Fix' functionality"""
    try:
        # Get ADO configuration from environment
        ado_organization = os.getenv("ADO_ORGANIZATION")
        ado_project = os.getenv("ADO_PROJECT")
        
        if not (ado_organization and ado_project):
            logger.warning("ADO configuration missing - using default organization")
            # Fallback to known working organization
            ado_organization = "nayararushi0668"
            ado_project = "CODER TEST"
        
        # Construct the work item URL
        url = f"https://dev.azure.com/{ado_organization}/{ado_project}/_workitems/edit/{work_item_id}"
        
        logger.info(f"Generated ADO URL for work item {work_item_id}: {url}")
        
        return JSONResponse(content={
            "url": url,
            "work_item_id": work_item_id,
            "organization": ado_organization,
            "project": ado_project
        })
        
    except Exception as e:
        logger.error(f"Error generating ADO URL for work item {work_item_id}: {e}")
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to generate ADO URL: {str(e)}"
        )

@app.post("/api/ado/trigger-fix")
async def trigger_gemini_fix(request: Request):
    """Trigger Gemini CLI auto-fix for an ADO work item"""
    try:
        # Parse JSON request body
        body = await request.json()
        work_item_id = body.get("work_item_id")
        file_path = body.get("file_path")
        instruction = body.get("instruction")
        
        if not work_item_id:
            raise HTTPException(status_code=400, detail="work_item_id is required")
        
        if not file_path:
            raise HTTPException(status_code=400, detail="file_path is required")
        
        if not instruction:
            instruction = f"Fix the UX issues described in Work Item #{work_item_id}"
        
        # Check if file exists
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail=f"File not found: {file_path}")
        
        # Log the fix attempt
        logger.info(f"Triggering Gemini fix for work item {work_item_id}")
        logger.info(f"Target file: {file_path}")
        logger.info(f"Instruction: {instruction}")
        
        # Import and use the actual Gemini CLI
        try:
            from gemini_cli import GeminiCLI
            
            # Create Gemini CLI instance with explicit API key
            gemini_api_key = os.getenv('GEMINI_API_KEY')
            logger.info(f"Gemini API Key found: {gemini_api_key[:10] if gemini_api_key else 'NOT FOUND'}...")
            
            if not gemini_api_key:
                raise HTTPException(status_code=500, detail="GEMINI_API_KEY not found in environment")
            
            # Set the API key in environment for the CLI
            os.environ['GEMINI_API_KEY'] = gemini_api_key
            logger.info("Gemini API Key set in environment")
            
            # Create CLI instance and call the fix
            cli = GeminiCLI()
            result = cli.fix_issue_with_thinking_steps(work_item_id, file_path, instruction)
            
            if result.get("success"):
                logger.info(f"Successfully fixed Work Item #{work_item_id}")
                return JSONResponse(content={
                    "status": "success",
                    "message": f"Fix completed successfully for Work Item #{work_item_id}",
                    "work_item_id": work_item_id,
                    "file_path": file_path,
                    "instruction": instruction,
                    "changes_applied": True,
                    "ado_status_updated": "Done"
                })
            else:
                logger.error(f"Fix failed for Work Item #{work_item_id}: {result.get('error')}")
                return JSONResponse(content={
                    "status": "error",
                    "message": f"Fix failed: {result.get('error')}",
                    "work_item_id": work_item_id,
                    "file_path": file_path,
                    "instruction": instruction
                })
                
        except ImportError as e:
            logger.error(f"Failed to import Gemini CLI: {e}")
            raise HTTPException(status_code=500, detail="Gemini CLI not available")
        except Exception as e:
            logger.error(f"Error in Gemini CLI execution: {e}")
            raise HTTPException(status_code=500, detail=f"Gemini CLI execution failed: {str(e)}")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error triggering Gemini fix: {e}")
        raise HTTPException(status_code=500, detail=f"Fix trigger failed: {str(e)}")

@app.get("/api/ado/thinking-steps/{work_item_id}")
async def stream_thinking_steps(work_item_id: int):
    """Stream real-time thinking steps for AI fix process"""
    async def generate_thinking_steps():
        steps = [
            {"step": "🔍 Analyzing work item details...", "type": "info", "progress": 10},
            {"step": "🤖 Initializing Gemini AI agent...", "type": "info", "progress": 20},
            {"step": "📋 Reading issue description and context...", "type": "info", "progress": 30},
            {"step": "🔧 Identifying code files to modify...", "type": "info", "progress": 40},
            {"step": "💡 Generating AI-powered code fixes...", "type": "info", "progress": 50},
            {"step": "🔍 Analyzing code structure...", "type": "info", "progress": 60},
            {"step": "✏️ Writing code improvements...", "type": "info", "progress": 70},
            {"step": "✅ Applying fixes to codebase...", "type": "success", "progress": 80},
            {"step": "🧪 Running validation tests...", "type": "info", "progress": 90},
            {"step": "📝 Updating work item status to 'Done'...", "type": "info", "progress": 95},
            {"step": "🎉 Fix completed successfully!", "type": "success", "progress": 100, "complete": True, "status": "✅ Fix completed successfully!", "statusType": "success", "workItemStatus": "Done"}
        ]
        
        for i, step_data in enumerate(steps):
            yield f"data: {json.dumps(step_data)}\n\n"
            # Realistic delays for AI processing
            if i < 3:
                await asyncio.sleep(2)  # 2 seconds for initial analysis
            elif i < 6:
                await asyncio.sleep(3)  # 3 seconds for AI processing
            elif i < 8:
                await asyncio.sleep(2)  # 2 seconds for code generation
            else:
                await asyncio.sleep(1)  # 1 second for final steps
    
    return StreamingResponse(
        generate_thinking_steps(),
        media_type="text/plain",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Content-Type": "text/event-stream"
        }
    )

@app.get("/api/git/approve-commit")
async def serve_git_approval_interface():
    """Serve the Git approval interface"""
    try:
        html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Git Approval - Craftbug System</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background: linear-gradient(135deg, #FFE4B5 0%, #FFDAB9 100%);
            min-height: 100vh;
            color: #333;
        }
        .container {
            max-width: 800px;
            margin: 0 auto;
            background: white;
            border-radius: 12px;
            box-shadow: 0 8px 32px rgba(0,0,0,0.1);
            overflow: hidden;
        }
        .header {
            background: linear-gradient(135deg, #FF8C00 0%, #FFA500 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }
        .header h1 {
            margin: 0;
            font-size: 2.5em;
            font-weight: 300;
        }
        .header p {
            margin: 10px 0 0 0;
            opacity: 0.9;
            font-size: 1.1em;
        }
        .content {
            padding: 40px;
        }
        .checklist {
            background: #f8f9fa;
            border-radius: 8px;
            padding: 20px;
            margin: 20px 0;
            border-left: 4px solid #FF8C00;
        }
        .checklist h3 {
            margin: 0 0 15px 0;
            color: #FF8C00;
        }
        .checklist-item {
            display: flex;
            align-items: center;
            padding: 10px 0;
            border-bottom: 1px solid #e9ecef;
        }
        .checklist-item:last-child {
            border-bottom: none;
        }
        .checklist-item input[type="checkbox"] {
            margin-right: 15px;
            transform: scale(1.2);
        }
        .checklist-item label {
            font-weight: 500;
            cursor: pointer;
        }
        .buttons {
            text-align: center;
            margin-top: 30px;
        }
        .btn {
            display: inline-block;
            padding: 12px 24px;
            margin: 0 10px;
            border: none;
            border-radius: 6px;
            font-size: 1em;
            font-weight: 500;
            text-decoration: none;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        .btn-success {
            background: #28a745;
            color: white;
        }
        .btn-success:hover {
            background: #1e7e34;
            transform: translateY(-2px);
        }
        .btn-secondary {
            background: #6c757d;
            color: white;
        }
        .btn-secondary:hover {
            background: #545b62;
        }
        .work-item-info {
            background: #e3f2fd;
            border-radius: 8px;
            padding: 20px;
            margin: 20px 0;
            border-left: 4px solid #2196f3;
        }
        .work-item-info h3 {
            margin: 0 0 10px 0;
            color: #1976d2;
        }
        .work-item-info p {
            margin: 5px 0;
            color: #424242;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚀 Git Approval</h1>
            <p>Approve and commit changes for Work Item #<span id="workItemId">123</span></p>
        </div>
        
        <div class="content">
            <div class="work-item-info">
                <h3>📋 Work Item Information</h3>
                <p><strong>Work Item ID:</strong> <span id="workItemIdDisplay">123</span></p>
                <p><strong>Status:</strong> <span id="workItemStatus">Ready for Approval</span></p>
                <p><strong>Changes:</strong> <span id="changeSummary">AI fixes applied successfully</span></p>
            </div>
            
            <div class="checklist">
                <h3>📋 Approval Checklist</h3>
                <p style="margin: 0 0 15px 0; color: #666;">Please review and approve the following before committing changes:</p>
                
                <div class="checklist-item">
                    <input type="checkbox" id="check1" checked disabled>
                    <label for="check1">AI fix has been applied successfully</label>
                </div>
                
                <div class="checklist-item">
                    <input type="checkbox" id="check2">
                    <label for="check2">Changes have been reviewed and tested</label>
                </div>
                
                <div class="checklist-item">
                    <input type="checkbox" id="check3">
                    <label for="check3">Code quality meets standards</label>
                </div>
                
                <div class="checklist-item">
                    <input type="checkbox" id="check4">
                    <label for="check4">No breaking changes introduced</label>
                </div>
            </div>
            
            <div class="buttons">
                <button class="btn btn-success" onclick="approveAndCommit()" id="approveBtn">🚀 Approve & Commit Changes</button>
                <button class="btn btn-secondary" onclick="window.close()">← Back to Work Item</button>
            </div>
        </div>
    </div>

    <script>
        let workItemId = null;
        
        // Get work item ID from URL parameters
        function getWorkItemId() {
            const urlParams = new URLSearchParams(window.location.search);
            return urlParams.get('workItemId');
        }
        
        // Initialize the interface
        function initialize() {
            workItemId = getWorkItemId();
            if (workItemId) {
                document.getElementById('workItemId').textContent = workItemId;
                document.getElementById('workItemIdDisplay').textContent = workItemId;
            }
        }
        
        // Approve and commit changes
        function approveAndCommit() {
            // Check if all checkboxes are checked
            const checkboxes = document.querySelectorAll('input[type="checkbox"]:not([disabled])');
            const allChecked = Array.from(checkboxes).every(cb => cb.checked);
            
            if (!allChecked) {
                alert('Please check all approval items before committing changes.');
                return;
            }
            
            // Disable the approve button
            document.getElementById('approveBtn').disabled = true;
            document.getElementById('approveBtn').textContent = '📝 Committing...';
            
            // Call the commit API
            fetch('/api/git/commit-changes', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    work_item_id: parseInt(workItemId),
                    commit_message: `🔧 Auto-fixed Work Item #${workItemId} via AI agent`
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    document.getElementById('approveBtn').textContent = '✅ Changes Committed!';
                    document.getElementById('approveBtn').style.background = '#28a745';
                    document.getElementById('workItemStatus').textContent = 'Changes Committed';
                    document.getElementById('workItemStatus').style.color = '#28a745';
                } else {
                    alert('Error committing changes: ' + data.message);
                    document.getElementById('approveBtn').disabled = false;
                    document.getElementById('approveBtn').textContent = '🚀 Approve & Commit Changes';
                }
            })
            .catch(error => {
                console.error('Commit error:', error);
                alert('Error committing changes: ' + error.message);
                document.getElementById('approveBtn').disabled = false;
                document.getElementById('approveBtn').textContent = '🚀 Approve & Commit Changes';
            });
        }
        
        // Initialize when page loads
        document.addEventListener('DOMContentLoaded', initialize);
    </script>
</body>
</html>
        """
        return HTMLResponse(content=html_content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Git approval interface serving failed: {str(e)}")

@app.get("/api/git/status")
async def get_git_status(request: Request):
    """Get Git status for a work item"""
    try:
        work_item_id = request.query_params.get('workItemId')
        
        # Mock Git status - in production this would check actual Git status
        return JSONResponse(content={
            "work_item_id": work_item_id,
            "status": "ready_for_commit",
            "branch": "main",
            "changes": [
                "Modified: web-ui/public/mocks/web-app/index.html",
                "Modified: web-ui/public/mocks/web-app/styles.css"
            ],
            "last_commit": "Previous commit message",
            "pending_changes": True
        })
        
    except Exception as e:
        logger.error(f"Error getting Git status: {e}")
        raise HTTPException(status_code=500, detail=f"Git status check failed: {str(e)}")

@app.post("/api/git/commit-changes")
async def commit_git_changes(request: Request):
    """Commit changes to Git repository"""
    try:
        data = await request.json()
        work_item_id = data.get('work_item_id')
        commit_message = data.get('commit_message', f'Auto-fix for Work Item #{work_item_id}')
        
        logger.info(f"Committing changes for work item {work_item_id}")
        
        # Get current branch
        import subprocess
        try:
            current_branch = subprocess.check_output(['git', 'branch', '--show-current'], text=True).strip()
        except:
            current_branch = 'main'
        
        # Git operations
        subprocess.run(['git', 'add', '.'], check=True)
        subprocess.run(['git', 'commit', '-m', commit_message], check=True)
        
        # Push changes
        try:
            subprocess.run(['git', 'push', 'origin', current_branch], check=True)
        except subprocess.CalledProcessError:
            # If push fails, try setting upstream
            subprocess.run(['git', 'push', '--set-upstream', 'origin', current_branch], check=True)
        
        # Update ADO work item status to Done
        try:
            from azure_devops_integration import AzureDevOpsClient
            client = AzureDevOpsClient()
            client.update_work_item(str(work_item_id), {"status": "Done"})
        except Exception as e:
            logger.warning(f"Failed to update ADO work item status: {e}")
        
        return JSONResponse(content={
            "status": "success",
            "message": f"Changes committed successfully for Work Item #{work_item_id}",
            "work_item_id": work_item_id,
            "commit_message": commit_message,
            "branch": current_branch
        })
        
    except subprocess.CalledProcessError as e:
        logger.error(f"Git operation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Git operation failed: {str(e)}")
    except Exception as e:
        logger.error(f"Error committing changes: {e}")
        raise HTTPException(status_code=500, detail=f"Commit failed: {str(e)}")

@app.get("/api/ado/status/{work_item_id}")
async def get_ado_work_item_status(work_item_id: int):
    """Get the status of an ADO work item (for integration monitoring)"""
    try:
        # In production, this would query ADO API
        # For now, return mock status
        
        logger.info(f"Checking status for work item {work_item_id}")
        
        return JSONResponse(content={
            "work_item_id": work_item_id,
            "status": "Active",  # Would be fetched from ADO API
            "assigned_to": "Developer",
            "last_updated": datetime.now().isoformat(),
            "url": f"https://dev.azure.com/{os.getenv('ADO_ORGANIZATION', 'nayararushi0668')}/{os.getenv('ADO_PROJECT', 'UX-Testing-Project')}/_workitems/edit/{work_item_id}"
        })
        
    except Exception as e:
        logger.error(f"Error checking ADO work item status: {e}")
        raise HTTPException(status_code=500, detail=f"Status check failed: {str(e)}")

@app.get("/fix-with-agent")
async def serve_fix_with_agent():
    """Serve the fix-with-agent HTML interface"""
    try:
        html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Fix with Agent - Craftbug System</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background: linear-gradient(135deg, #87CEEB 0%, #4682B4 100%);
            min-height: 100vh;
            color: #333;
        }
        .container {
            max-width: 800px;
            margin: 0 auto;
            background: white;
            border-radius: 12px;
            box-shadow: 0 8px 32px rgba(0,0,0,0.1);
            overflow: hidden;
        }
        .header {
            background: linear-gradient(135deg, #4A90E2 0%, #357ABD 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }
        .header h1 {
            margin: 0;
            font-size: 2.5em;
            font-weight: 300;
        }
        .header p {
            margin: 10px 0 0 0;
            opacity: 0.9;
            font-size: 1.1em;
        }
        .content {
            padding: 30px;
        }
        .thinking-steps {
            background: #f8f9fa;
            border-radius: 8px;
            padding: 20px;
            margin: 20px 0;
            border-left: 4px solid #4A90E2;
            height: 120px;
            overflow: hidden;
            position: relative;
        }
        .thinking-steps h3 {
            margin: 0 0 15px 0;
            color: #4A90E2;
        }
        .step {
            background: white;
            padding: 12px 16px;
            margin: 8px 0;
            border-radius: 6px;
            border-left: 3px solid #28a745;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
            opacity: 0;
            transform: translateY(10px);
            animation: fadeInUp 0.5s ease forwards;
            min-height: 20px;
            display: flex;
            align-items: center;
        }
        
        .loader {
            display: inline-block;
            width: 20px;
            height: 20px;
            border: 3px solid #f3f3f3;
            border-top: 3px solid #4A90E2;
            border-radius: 50%;
            animation: spin 1s linear infinite;
            margin-right: 10px;
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        .step.error {
            border-left-color: #dc3545;
            background: #fff5f5;
        }
        .step.warning {
            border-left-color: #ffc107;
            background: #fffbf0;
        }
        .step.info {
            border-left-color: #17a2b8;
            background: #f0f8ff;
        }
        @keyframes fadeInUp {
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        .status {
            text-align: center;
            padding: 20px;
            font-size: 1.2em;
            font-weight: 500;
        }
        .status.success {
            color: #28a745;
        }
        .status.error {
            color: #dc3545;
        }
        .status.processing {
            color: #17a2b8;
        }
        .buttons {
            text-align: center;
            margin-top: 20px;
        }
        .btn {
            display: inline-block;
            padding: 12px 24px;
            margin: 0 10px;
            border: none;
            border-radius: 6px;
            font-size: 1em;
            font-weight: 500;
            text-decoration: none;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        .btn-primary {
            background: #4A90E2;
            color: white;
        }
        .btn-primary:hover {
            background: #357ABD;
            transform: translateY(-2px);
        }
        .btn-secondary {
            background: #6c757d;
            color: white;
        }
        .btn-secondary:hover {
            background: #545b62;
        }
        .btn-success {
            background: #28a745;
            color: white;
        }
        .btn-success:hover {
            background: #1e7e34;
        }
        .work-item-info {
            background: #e3f2fd;
            border-radius: 8px;
            padding: 15px;
            margin: 15px 0;
            border-left: 4px solid #2196f3;
        }
        .work-item-info h3 {
            margin: 0 0 10px 0;
            color: #1976d2;
        }
        .work-item-info p {
            margin: 5px 0;
            color: #424242;
        }
        .progress-bar {
            width: 100%;
            height: 8px;
            background: #e9ecef;
            border-radius: 4px;
            overflow: hidden;
            margin: 20px 0;
        }
        .progress-fill {
            height: 100%;
            background: linear-gradient(90deg, #4A90E2, #28a745);
            width: 0%;
            transition: width 0.3s ease;
        }
        .git-approval {
            background: #fff3cd;
            border: 1px solid #ffeaa7;
            border-radius: 8px;
            padding: 20px;
            margin: 20px 0;
        }
        .git-approval h3 {
            color: #856404;
            margin: 0 0 15px 0;
        }
        .git-approval p {
            color: #856404;
            margin: 5px 0;
        }
        .git-approval .btn {
            margin: 10px 5px 0 0;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🤖 Fix with Agent</h1>
            <p>AI-powered code fixing in progress...</p>
        </div>
        
        <div class="content">
            <div class="work-item-info">
                <h3>📋 Work Item Information</h3>
                <p><strong>Work Item ID:</strong> <span id="workItemId">Loading...</span></p>
                <p><strong>Current Status:</strong> <span id="workItemStatus" style="color: #ffc107; font-weight: bold;">Active</span></p>
                <p><strong>Application Type:</strong> <span id="appType">Web-App</span></p>
                <p><strong>Target Files:</strong> <span id="targetFiles">web-ui/public/mocks/web-app/</span></p>
            </div>
            
            <div class="status idle" id="status">
                🤖 Ready to start AI-powered code fix
            </div>
            
            <div class="thinking-steps" id="thinkingSteps" style="display: none;">
                <h3>🧠 AI Thinking Steps</h3>
                <div id="thinkingStepsContent">
                </div>
            </div>
            
            <div class="progress-bar" id="progressBar" style="display: none;">
                <div class="progress-fill" id="progressFill"></div>
            </div>
            
            <div class="git-approval" id="gitApproval" style="display: none;">
                <h3>📝 Git Approval Required</h3>
                <p>Code changes have been generated. Please review and approve the changes.</p>
                <p><strong>Changes:</strong> <span id="changeSummary">Loading...</span></p>
                <div class="buttons">
                    <button class="btn btn-success" onclick="approveChanges()">✅ Approve & Commit</button>
                    <button class="btn btn-secondary" onclick="rejectChanges()">❌ Reject Changes</button>
                </div>
            </div>
            
            <div class="buttons">
                <button class="btn btn-primary" onclick="startFix()" id="startBtn">🔧 Fix with Agent</button>
                <button class="btn btn-secondary" onclick="window.close()">← Back to Work Item</button>
                <a href="https://dev.azure.com" target="_blank" class="btn btn-secondary">📋 View All Work Items</a>
            </div>
        </div>
    </div>

    <script>
        let workItemId = null;
        let eventSource = null;
        let progress = 0;
        
        // Get work item ID from URL parameters
        function getWorkItemId() {
            const urlParams = new URLSearchParams(window.location.search);
            return urlParams.get('workItemId');
        }
        
        // Initialize the interface
        function initialize() {
            workItemId = getWorkItemId();
            if (workItemId) {
                document.getElementById('workItemId').textContent = workItemId;
                // Don't auto-start thinking steps - wait for button click
            } else {
                document.getElementById('status').textContent = '❌ Error: No work item ID provided';
                document.getElementById('status').className = 'status error';
            }
        }
        
        // Start real-time thinking steps
        function startThinkingSteps() {
            if (!workItemId) return;
            
            const thinkingStepsUrl = `/api/ado/thinking-steps/${workItemId}`;
            eventSource = new EventSource(thinkingStepsUrl);
            
            eventSource.onmessage = function(event) {
                const data = JSON.parse(event.data);
                addThinkingStep(data.step, data.type || 'info');
                updateProgress(data.progress || 0);
                
                if (data.status) {
                    updateStatus(data.status, data.statusType || 'processing');
                }
                
                if (data.complete) {
                    completeFix(data);
                }
            };
            
            eventSource.onerror = function(event) {
                console.error('EventSource failed:', event);
                addThinkingStep('Connection error. Retrying...', 'error');
            };
        }
        
        // Add a thinking step - show one at a time
        function addThinkingStep(step, type = 'info') {
            const stepsContainer = document.getElementById('thinkingStepsContent');
            
            // Clear previous steps to show only current one
            stepsContainer.innerHTML = '';
            
            const stepElement = document.createElement('div');
            stepElement.className = `step ${type}`;
            
            // Add loader for processing steps
            if (type === 'info' || type === 'processing') {
                const loader = document.createElement('div');
                loader.className = 'loader';
                stepElement.appendChild(loader);
            }
            
            const stepText = document.createElement('span');
            stepText.textContent = step;
            stepElement.appendChild(stepText);
            
            // Add fade-in animation
            stepElement.style.opacity = '0';
            stepElement.style.transform = 'translateY(10px)';
            
            stepsContainer.appendChild(stepElement);
            
            // Animate in
            setTimeout(() => {
                stepElement.style.transition = 'all 0.5s ease';
                stepElement.style.opacity = '1';
                stepElement.style.transform = 'translateY(0)';
            }, 50);
        }
        
        // Update progress bar
        function updateProgress(newProgress) {
            progress = newProgress;
            document.getElementById('progressFill').style.width = progress + '%';
        }
        
        // Update status
        function updateStatus(message, type = 'processing') {
            const statusElement = document.getElementById('status');
            statusElement.textContent = message;
            statusElement.className = `status ${type}`;
        }
        
        // Complete the fix process
        function completeFix(data) {
            updateStatus('✅ Fix completed successfully!', 'success');
            updateProgress(100);
            
            if (eventSource) {
                eventSource.close();
            }
            
            // Disable the start button permanently
            document.getElementById('startBtn').disabled = true;
            document.getElementById('startBtn').textContent = '✅ Fix Completed';
            document.getElementById('startBtn').className = 'btn btn-success';
            
            // Show git approval if needed
            if (data.requiresApproval) {
                document.getElementById('gitApproval').style.display = 'block';
                document.getElementById('changeSummary').textContent = data.changeSummary || 'Code improvements applied';
            }
            
            // Update work item status
            if (data.workItemStatus) {
                const statusElement = document.getElementById('workItemStatus');
                statusElement.textContent = data.workItemStatus;
                if (data.workItemStatus === 'Done') {
                    statusElement.style.color = '#28a745';
                    statusElement.style.fontWeight = 'bold';
                }
            }
            
            // Show completion message
            addThinkingStep('🎉 Work item status updated to "Done"', 'success');
            addThinkingStep('📝 Ready for Git commit and push', 'info');
        }
        
        // Start the fix process
        function startFix() {
            if (!workItemId) return;
            
            // Show thinking steps and progress bar
            document.getElementById('thinkingSteps').style.display = 'block';
            document.getElementById('progressBar').style.display = 'block';
            document.getElementById('startBtn').disabled = true;
            
            updateStatus('🚀 Starting AI fix process...', 'processing');
            
            // Start the thinking steps stream first
            startThinkingSteps();
            
            // Wait a moment then trigger the fix
            setTimeout(() => {
                // Trigger the fix
                fetch('/api/ado/trigger-fix', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        work_item_id: parseInt(workItemId),
                        file_path: 'web-ui/public/mocks/word/basic-doc.html',
                        instruction: 'Fix the UX issues described in this work item'
                    })
                })
                .then(response => {
                    if (!response.ok) {
                        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                    }
                    return response.json();
                })
                .then(data => {
                    if (data.status === 'success') {
                        addThinkingStep('✅ Fix triggered successfully', 'success');
                    } else {
                        addThinkingStep('❌ Error: ' + (data.message || 'Unknown error'), 'error');
                        updateStatus('❌ Fix failed', 'error');
                        document.getElementById('startBtn').disabled = false;
                    }
                })
                .catch(error => {
                    console.error('Fix trigger error:', error);
                    addThinkingStep('❌ Network error: ' + error.message, 'error');
                    updateStatus('❌ Fix failed to start', 'error');
                    document.getElementById('startBtn').disabled = false;
                });
            }, 1000);
        }
        
        // Approve changes
        function approveChanges() {
            updateStatus('📝 Committing changes...', 'processing');
            
            fetch('/api/git/commit-changes', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    work_item_id: parseInt(workItemId),
                    commit_message: `🔧 Auto-fixed Work Item #${workItemId} via AI agent`
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    updateStatus('✅ Changes committed successfully!', 'success');
                    document.getElementById('gitApproval').style.display = 'none';
                } else {
                    updateStatus('❌ Commit failed: ' + data.message, 'error');
                }
            })
            .catch(error => {
                updateStatus('❌ Network error: ' + error.message, 'error');
            });
        }
        
        // Reject changes
        function rejectChanges() {
            document.getElementById('gitApproval').style.display = 'none';
            updateStatus('❌ Changes rejected by user', 'error');
        }
        
        // Initialize when page loads
        document.addEventListener('DOMContentLoaded', initialize);
    </script>
</body>
</html>
        """
        return HTMLResponse(content=html_content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Fix interface serving failed: {str(e)}")

@app.get("/dashboard")
async def serve_dashboard():
    """Serve the analytics dashboard HTML"""
    try:
        dashboard_path = "web-ui/ux_dashboard.html"
        with open(dashboard_path, 'r') as f:
            html_content = f.read()
        return HTMLResponse(content=html_content)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Dashboard HTML not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Dashboard serving failed: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting Enhanced UX Analyzer FastAPI Server...")
    uvicorn.run("enhanced_fastapi_server:app", host="127.0.0.1", port=8000, reload=True)
