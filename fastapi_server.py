#!/usr/bin/env python3
"""
FastAPI Server for UX Analyzer
Provides API endpoints for the React web UI
"""

from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
import json
import uuid
from datetime import datetime
import tempfile
import os

# Import the existing UX analyzer components
import sys
sys.path.append('/Users/arushitandon/Desktop/UIUX analyzer/ux-analyzer')

try:
    from agent.agent import Agent
    from computers.default.local_playwright import LocalPlaywrightBrowser
except ImportError as e:
    print(f"Warning: Could not import UX analyzer components: {e}")
    Agent = None
    LocalPlaywrightBrowser = None

app = FastAPI(title="UX Analyzer API", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models for request/response
class AnalysisRequest(BaseModel):
    url: Optional[str] = None
    scenario: Optional[str] = None
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

# Mock report data for demonstration
MOCK_REPORTS = {}

def generate_mock_report(analysis_id: str, request_data: Dict[str, Any]) -> Dict[str, Any]:
    """Generate a mock analysis report"""
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

@app.get("/")
async def root():
    return {"message": "UX Analyzer API", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.post("/api/analyze", response_model=AnalysisResponse)
async def analyze_url(request: AnalysisRequest):
    """Analyze a URL with specified modules"""
    if not request.url:
        raise HTTPException(status_code=400, detail="URL is required")
    
    analysis_id = str(uuid.uuid4())[:8]
    
    # Generate mock report
    report_data = generate_mock_report(analysis_id, request.dict())
    MOCK_REPORTS[analysis_id] = report_data
    
    return AnalysisResponse(
        analysis_id=analysis_id,
        status="completed",
        message=f"Analysis completed for {request.url}"
    )

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
    
    # Clean up temp file
    os.unlink(tmp_path)
    
    return AnalysisResponse(
        analysis_id=analysis_id,
        status="completed",
        message=f"Screenshot analysis completed"
    )

@app.post("/api/analyze/scenario", response_model=AnalysisResponse)
async def analyze_scenario(request: AnalysisRequest):
    """Analyze a user scenario"""
    if not request.scenario:
        raise HTTPException(status_code=400, detail="Scenario is required")
    
    analysis_id = str(uuid.uuid4())[:8]
    
    # Generate mock report
    report_data = generate_mock_report(analysis_id, request.dict())
    MOCK_REPORTS[analysis_id] = report_data
    
    return AnalysisResponse(
        analysis_id=analysis_id,
        status="completed",
        message=f"Scenario analysis completed"
    )

@app.post("/api/analyze/mock-app", response_model=AnalysisResponse)
async def analyze_mock_app(request: AnalysisRequest):
    """Analyze a mock application"""
    if not request.app_path:
        raise HTTPException(status_code=400, detail="App path is required")
    
    analysis_id = str(uuid.uuid4())[:8]
    
    # Generate mock report
    report_data = generate_mock_report(analysis_id, request.dict())
    MOCK_REPORTS[analysis_id] = report_data
    
    return AnalysisResponse(
        analysis_id=analysis_id,
        status="completed",
        message=f"Mock app analysis completed for {request.app_path}"
    )

@app.get("/api/reports/{report_id}")
async def get_report(report_id: str):
    """Get analysis report by ID"""
    if report_id not in MOCK_REPORTS:
        raise HTTPException(status_code=404, detail="Report not found")
    
    return MOCK_REPORTS[report_id]

@app.get("/api/reports/{report_id}/download")
async def download_report(report_id: str, format: str = "json"):
    """Download report in specified format"""
    if report_id not in MOCK_REPORTS:
        raise HTTPException(status_code=404, detail="Report not found")
    
    report = MOCK_REPORTS[report_id]
    
    if format == "html":
        # Return a simple HTML version
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>UX Analysis Report</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; }}
                .score {{ font-size: 24px; font-weight: bold; color: #2563eb; }}
                .module {{ margin: 20px 0; padding: 15px; border: 1px solid #e5e7eb; border-radius: 8px; }}
            </style>
        </head>
        <body>
            <h1>UX Analysis Report</h1>
            <p><strong>Report ID:</strong> {report_id}</p>
            <p><strong>Overall Score:</strong> <span class="score">{report['overall_score']}/100</span></p>
            <h2>Module Results</h2>
            {"".join([f'<div class="module"><h3>{module.title()}</h3><p>Score: {data["score"]}/100</p></div>' for module, data in report['modules'].items()])}
        </body>
        </html>
        """
        return HTMLResponse(content=html_content)
    else:
        return JSONResponse(content=report)

@app.get("/docs")
async def get_docs():
    """API documentation endpoint"""
    return {"message": "Visit /docs for interactive API documentation"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000, reload=True)
