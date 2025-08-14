#!/usr/bin/env python3
"""
Main FastAPI Application for Craftbug Agentic System
New modular FastAPI app with legacy fallback capability
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
import uvicorn
from contextlib import asynccontextmanager

from src.api.routes import analysis, ado, git, dashboard
from src.utils.feature_flags import FeatureFlags
from src.utils.monitoring import system_monitor, initialize_monitoring

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    logger.info("🚀 Starting new Craftbug API server")
    
    # Initialize monitoring
    await initialize_monitoring()
    logger.info("✅ Monitoring initialized")
    
    # Load feature flags
    FeatureFlags.load_from_env()
    logger.info("✅ Feature flags loaded")
    
    yield
    
    # Shutdown
    logger.info("🛑 Shutting down new Craftbug API server")

# Create FastAPI app
app = FastAPI(
    title="Craftbug Agentic System - New API",
    description="New modular API with legacy fallback capability",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080", "http://127.0.0.1:8080"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(analysis.router)
app.include_router(ado.router)
app.include_router(git.router)
app.include_router(dashboard.router)

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Craftbug Agentic System - New API",
        "version": "1.0.0",
        "status": "running",
        "feature_flags": FeatureFlags.get_current_state()
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Run health checks
        health_results = await system_monitor.run_health_checks()
        
        return {
            "status": "healthy",
            "service": "new_craftbug_api",
            "health_checks": health_results,
            "feature_flags": FeatureFlags.get_current_state()
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=500, detail="Health check failed")

@app.get("/api/status")
async def api_status():
    """API status endpoint"""
    return {
        "api": "new_craftbug_api",
        "version": "1.0.0",
        "status": "running",
        "feature_flags": FeatureFlags.get_current_state(),
        "monitoring": system_monitor.get_status()
    }

# Legacy compatibility endpoints
@app.get("/api/scenarios")
async def get_scenarios_legacy():
    """Legacy scenarios endpoint for backward compatibility"""
    try:
        scenarios = await analysis.analysis_service.get_scenarios()
        return scenarios
    except Exception as e:
        logger.error(f"Legacy scenarios failed: {e}")
        return []

@app.get("/api/reports/{analysis_id}")
async def get_report_legacy(analysis_id: str):
    """Legacy report endpoint for backward compatibility"""
    try:
        report = await analysis.analysis_service.get_report(analysis_id)
        if not report:
            raise HTTPException(status_code=404, detail="Report not found")
        return report
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Legacy report failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/analyze")
async def analyze_legacy(request: analysis.AnalysisRequest):
    """Legacy analyze endpoint for backward compatibility"""
    try:
        result = await analysis.analysis_service.analyze(request)
        return result
    except Exception as e:
        logger.error(f"Legacy analyze failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler"""
    logger.error(f"Global exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": str(exc),
            "service": "new_craftbug_api"
        }
    )

if __name__ == "__main__":
    # Run the new API server on a different port
    uvicorn.run(
        "src.api.main:app",
        host="127.0.0.1",
        port=8001,  # Different port from legacy system
        reload=True,
        log_level="info"
    )
