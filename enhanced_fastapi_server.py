#!/usr/bin/env python3
"""
Enhanced FastAPI Server for UX Analyzer
Provides API endpoints with real browser automation and craft bug detection
"""

from fastapi import FastAPI, HTTPException, UploadFile, File, Form, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
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

# Import enhanced components
from scenario_executor import ScenarioExecutor, get_available_scenarios
from enhanced_scenario_runner import execute_realistic_scenario, EnhancedScenarioRunner
from enhanced_report_handler import (
    save_analysis_to_disk, 
    load_analysis_from_disk, 
    list_saved_reports, 
    get_report_statistics,
    search_saved_reports,
    cleanup_old_reports
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import orchestrator routes if available
try:
    sys.path.append('/Users/arushitandon/Desktop/analyzer/orchestrator')
    from routes import router as orchestrator_router
except ImportError as e:
    print(f"Warning: Could not import orchestrator routes: {e}")
    orchestrator_router = None

app = FastAPI(title="Enhanced UX Analyzer API", version="2.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001", "http://localhost:3002"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
        logger.error(f"❌ Realistic analysis failed: {analysis_id}: {e}")
        
        error_result = {
            "analysis_id": analysis_id,
            "status": "failed",
            "error": str(e),
            "timestamp": datetime.now().isoformat(),
            "type": "error_report"
        }
        
        # Save error to disk too
        try:
            save_analysis_to_disk(analysis_id, error_result)
        except:
            pass
        
        ANALYSIS_CACHE[analysis_id] = {
            "status": "failed",
            "result": error_result,
            "error": str(e),
            "completed_at": datetime.now()
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
                report = scenario_executor.execute_url_scenario(
                    url=request.url,
                    scenario_path=request.scenario_path,
                    modules=request.modules
                )
            else:
                report = generate_mock_report(analysis_id, request.dict())
            
            # Save to disk
            file_path = save_analysis_to_disk(analysis_id, report)
            report["file_path"] = file_path
            
            # Cache result
            ANALYSIS_CACHE[analysis_id] = {
                "status": "completed",
                "result": report,
                "completed_at": datetime.now(),
                "file_path": file_path
            }
            
        except Exception as e:
            ANALYSIS_CACHE[analysis_id] = {
                "status": "failed",
                "error": str(e),
                "completed_at": datetime.now()
            }
        
        message = f"Enhanced mock analysis completed for {request.url}"
    
    logger.info(f"🎯 Started enhanced analysis {analysis_id} for {request.url}")
    
    return AnalysisResponse(
        analysis_id=analysis_id,
        status="processing" if request.execution_mode == "realistic" else "completed",
        message=message,
        execution_mode=request.execution_mode
    )

# Legacy endpoints for backwards compatibility
@app.post("/api/analyze", response_model=AnalysisResponse)
async def analyze_url(request: AnalysisRequest):
    """Legacy analyze endpoint for backwards compatibility"""
    if not request.url:
        raise HTTPException(status_code=400, detail="URL is required")
    
    analysis_id = str(uuid.uuid4())[:8]
    
    # Generate mock report
    report_data = generate_mock_report(analysis_id, request.dict())
    MOCK_REPORTS[analysis_id] = report_data
    
    # Also save to disk for consistency
    save_analysis_to_disk(analysis_id, report_data)
    
    return AnalysisResponse(
        analysis_id=analysis_id,
        status="completed",
        message=f"Analysis completed for {request.url}"
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
        
        # Save to both memory and disk
        MOCK_REPORTS[analysis_id] = report_data
        save_analysis_to_disk(analysis_id, report_data)
        
        return AnalysisResponse(
            analysis_id=analysis_id,
            status="completed",
            message=f"URL + Scenario analysis completed for {request.url}"
        )
        
    except Exception as e:
        logger.error(f"Scenario analysis failed: {e}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

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
        
        # Save to both memory and disk
        MOCK_REPORTS[analysis_id] = report_data
        save_analysis_to_disk(analysis_id, report_data)
        
        return AnalysisResponse(
            analysis_id=analysis_id,
            status="completed",
            message=f"Mock app + Scenario analysis completed for {request.app_path}"
        )
        
    except Exception as e:
        logger.error(f"Mock scenario analysis failed: {e}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

# Enhanced Report Endpoints

@app.get("/api/reports/{report_id}")
async def get_report(report_id: str):
    """Get analysis report with enhanced disk/cache lookup"""
    
    # Check analysis cache first (for active/recent analyses)
    if report_id in ANALYSIS_CACHE:
        cached = ANALYSIS_CACHE[report_id]
        if cached["status"] == "completed":
            return cached["result"]
        elif cached["status"] == "failed":
            raise HTTPException(status_code=500, detail=cached.get("error", "Analysis failed"))
        else:
            # Still processing
            return {
                "analysis_id": report_id,
                "status": cached["status"],
                "message": "Analysis still in progress",
                "started_at": cached.get("started_at", "").isoformat() if hasattr(cached.get("started_at", ""), "isoformat") else str(cached.get("started_at", ""))
            }
    
    # Check legacy mock reports
    if report_id in MOCK_REPORTS:
        return MOCK_REPORTS[report_id]
    
    # Load from disk
    report = load_analysis_from_disk(report_id)
    if report:
        return report
    
    raise HTTPException(status_code=404, detail="Report not found")

@app.get("/api/reports")
async def list_reports(
    limit: int = 50,
    offset: int = 0,
    analysis_type: Optional[str] = None,
    min_score: Optional[int] = None,
    has_craft_bugs: Optional[bool] = None
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
    
    return {
        "reports": result.get("reports", []),
        "pagination": result.get("pagination", {}),
        "statistics": result.get("statistics", {}),
        "filters_applied": filters
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

@app.get("/api/scenarios")
async def get_scenarios():
    """Get available scenarios"""
    try:
        scenarios = get_available_scenarios()
        return {"scenarios": scenarios}
    except Exception as e:
        logger.error(f"Error loading scenarios: {e}")
        return {"scenarios": []}

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
    
    if report_id in ANALYSIS_CACHE and ANALYSIS_CACHE[report_id]["status"] == "completed":
        report = ANALYSIS_CACHE[report_id]["result"]
    elif report_id in MOCK_REPORTS:
        report = MOCK_REPORTS[report_id]
    else:
        report = load_analysis_from_disk(report_id)
    
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    
    if format == "html":
        # Return a simple HTML version
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Enhanced UX Analysis Report</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; line-height: 1.6; }}
                .header {{ background: #f8f9fa; padding: 20px; border-radius: 8px; margin-bottom: 20px; }}
                .score {{ font-size: 32px; font-weight: bold; color: #2563eb; }}
                .craft-bugs {{ background: #fff3cd; padding: 15px; border-radius: 8px; margin: 15px 0; }}
                .module {{ margin: 20px 0; padding: 15px; border: 1px solid #e5e7eb; border-radius: 8px; }}
                .steps {{ margin: 10px 0; }}
                .step {{ padding: 8px; margin: 5px 0; background: #f8f9fa; border-radius: 4px; }}
                .success {{ border-left: 4px solid #10b981; }}
                .warning {{ border-left: 4px solid #f59e0b; }}
                .error {{ border-left: 4px solid #ef4444; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>Enhanced UX Analysis Report</h1>
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
            {"".join([f'<div class="module"><h3>{module.title()}</h3><p>Score: {data.get("score", 0)}/100</p></div>' for module, data in report.get('modules', {}).items()])}
            
            <h2>🎯 Scenario Steps</h2>
            <div class="steps">
                {"".join([f'<div class="step {step.get("status", "")}">{step.get("action", "Unknown")} - {step.get("status", "Unknown")} ({step.get("duration_ms", 0)}ms)</div>' for step in report.get('steps', [])])}
            </div>
        </body>
        </html>
        """
        return HTMLResponse(content=html_content)
    else:
        return JSONResponse(content=report)

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting Enhanced UX Analyzer FastAPI Server...")
    uvicorn.run(app, host="127.0.0.1", port=8000, reload=True)
