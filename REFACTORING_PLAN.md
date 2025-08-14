# 🏗️ **Craftbug Agentic System - Comprehensive Refactoring Plan**

## 📊 **Codebase Analysis Summary**

### **Current State:**
- **Total Files**: 150+ files across multiple directories
- **Main Components**: FastAPI backend, React frontend, Playwright automation, Azure DevOps integration
- **Code Duplication**: Multiple working/backup files, redundant test scripts
- **Architecture**: Monolithic FastAPI server (3542 lines), scattered utilities
- **Testing**: 50+ test files with overlapping functionality

---

## 🎯 **Refactoring Objectives**

### **Primary Goals:**
1. **Reduce Code Duplication** - Eliminate redundant files and functions
2. **Improve Architecture** - Implement proper separation of concerns
3. **Enhance Maintainability** - Create modular, testable components
4. **Standardize Patterns** - Consistent error handling, logging, and API design
5. **Optimize Performance** - Reduce bundle sizes and improve response times

---

## 📋 **Phase 1: Code Cleanup & File Organization**

### **Task 1.1: Remove Duplicate/Backup Files**
- [ ] **Delete redundant files:**
  - `enhanced_fastapi_server_working.py` (93KB, 2452 lines)
  - `scenario_executor_working.py` (80KB, 1758 lines)
  - `web-ui-backup/` directory
  - `enhanced_reports_backup/` directory
  - `temp/` directory contents
  - `screenshots/` directory contents

- [ ] **Consolidate test files:**
  - Merge `test_*.py` files with similar functionality
  - Create unified test suites by category
  - Remove duplicate test scenarios

### **Task 1.2: File Structure Reorganization**
```
craftbug_agentic_system/
├── src/
│   ├── api/                    # FastAPI application
│   │   ├── __init__.py
│   │   ├── main.py            # Main FastAPI app
│   │   ├── routes/            # API route modules
│   │   │   ├── analysis.py
│   │   │   ├── reports.py
│   │   │   ├── scenarios.py
│   │   │   ├── ado.py
│   │   │   └── git.py
│   │   ├── models/            # Pydantic models
│   │   │   ├── analysis.py
│   │   │   ├── reports.py
│   │   │   └── scenarios.py
│   │   └── middleware/        # Custom middleware
│   ├── core/                  # Core business logic
│   │   ├── analysis/          # Analysis engines
│   │   │   ├── executor.py
│   │   │   ├── detector.py
│   │   │   └── reporter.py
│   │   ├── automation/        # Browser automation
│   │   │   ├── playwright.py
│   │   │   └── scenarios.py
│   │   └── integrations/      # External integrations
│   │       ├── azure_devops.py
│   │       ├── gemini.py
│   │       └── git.py
│   ├── utils/                 # Shared utilities
│   │   ├── config.py
│   │   ├── logging.py
│   │   └── helpers.py
│   └── web/                   # Frontend application
│       ├── src/
│       ├── public/
│       └── package.json
├── tests/                     # Comprehensive test suite
│   ├── unit/
│   ├── integration/
│   └── e2e/
├── scenarios/                 # YAML scenario definitions
├── docs/                      # Documentation
└── scripts/                   # Utility scripts
```

---

## 🔧 **Phase 2: Architecture Refactoring**

### **Task 2.1: FastAPI Application Restructuring**

#### **Current Issues:**
- Monolithic `enhanced_fastapi_server.py` (3542 lines)
- Mixed concerns (API routes, business logic, HTML generation)
- Inline HTML/CSS/JavaScript in Python code
- Hardcoded configurations

#### **Refactoring Actions:**
- [ ] **Extract API Routes:**
  ```python
  # src/api/routes/analysis.py
  from fastapi import APIRouter, HTTPException
  from src.core.analysis import AnalysisService
  from src.models.analysis import AnalysisRequest, AnalysisResponse
  
  router = APIRouter(prefix="/api/analysis", tags=["analysis"])
  
  @router.post("/", response_model=AnalysisResponse)
  async def analyze_url(request: AnalysisRequest):
      service = AnalysisService()
      return await service.analyze(request)
  ```

- [ ] **Create Service Layer:**
  ```python
  # src/core/analysis/service.py
  class AnalysisService:
      def __init__(self):
          self.executor = ScenarioExecutor()
          self.detector = CraftBugDetector()
          self.reporter = ReportGenerator()
      
      async def analyze(self, request: AnalysisRequest) -> AnalysisResponse:
          # Business logic here
          pass
  ```

- [ ] **Extract Models:**
  ```python
  # src/models/analysis.py
  from pydantic import BaseModel
  from typing import Optional, Dict, Any
  
  class AnalysisRequest(BaseModel):
      url: str
      scenario_id: Optional[str] = None
      modules: Dict[str, bool] = {}
  
  class AnalysisResponse(BaseModel):
      analysis_id: str
      status: str
      message: str
      craft_bugs: List[Dict] = []
      ux_issues: List[Dict] = []
      total_issues: int = 0
  ```

### **Task 2.2: Configuration Management**
- [ ] **Create centralized config:**
  ```python
  # src/utils/config.py
  from pydantic_settings import BaseSettings
  
  class Settings(BaseSettings):
      # API Configuration
      api_host: str = "127.0.0.1"
      api_port: int = 8000
      
      # External Services
      gemini_api_key: str
      ado_organization: str
      ado_project: str
      ado_pat: str
      
      # File Paths
      scenarios_dir: str = "scenarios"
      reports_dir: str = "reports"
      
      class Config:
          env_file = ".env"
  ```

### **Task 2.3: Error Handling & Logging**
- [ ] **Implement consistent error handling:**
  ```python
  # src/utils/exceptions.py
  class CraftbugException(Exception):
      def __init__(self, message: str, error_code: str = None):
          self.message = message
          self.error_code = error_code
          super().__init__(self.message)
  
  class AnalysisError(CraftbugException):
      pass
  
  class IntegrationError(CraftbugException):
      pass
  ```

- [ ] **Standardize logging:**
  ```python
  # src/utils/logging.py
  import logging
  from typing import Optional
  
  def setup_logging(level: str = "INFO", log_file: Optional[str] = None):
      logging.basicConfig(
          level=getattr(logging, level.upper()),
          format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
          handlers=[
              logging.StreamHandler(),
              logging.FileHandler(log_file) if log_file else logging.NullHandler()
          ]
      )
  ```

---

## 🧪 **Phase 3: Testing Infrastructure**

### **Task 3.1: Test Suite Consolidation**
- [ ] **Create unified test structure:**
  ```
  tests/
  ├── unit/
  │   ├── test_analysis_service.py
  │   ├── test_scenario_executor.py
  │   └── test_craft_bug_detector.py
  ├── integration/
  │   ├── test_api_endpoints.py
  │   ├── test_azure_devops_integration.py
  │   └── test_gemini_integration.py
  └── e2e/
      ├── test_complete_workflow.py
      └── test_ui_interactions.py
  ```

- [ ] **Implement test fixtures:**
  ```python
  # tests/conftest.py
  import pytest
  from fastapi.testclient import TestClient
  from src.api.main import app
  
  @pytest.fixture
  def client():
      return TestClient(app)
  
  @pytest.fixture
  def mock_scenario():
      return {
          "id": "test-1",
          "name": "Test Scenario",
          "steps": [
              {"action": "navigate", "url": "http://test.com"},
              {"action": "click", "selector": "button"}
          ]
      }
  ```

### **Task 3.2: Test Data Management**
- [ ] **Create test data factories:**
  ```python
  # tests/factories.py
  from factory import Factory, Faker
  from src.models.analysis import AnalysisRequest
  
  class AnalysisRequestFactory(Factory):
      class Meta:
          model = AnalysisRequest
      
      url = Faker('url')
      scenario_id = Faker('word')
      modules = {'performance': True, 'accessibility': True}
  ```

---

## 🔄 **Phase 4: Frontend Refactoring**

### **Task 4.1: React Component Organization**
- [ ] **Restructure React components:**
  ```
  src/web/src/
  ├── components/
  │   ├── common/              # Reusable components
  │   │   ├── Button.tsx
  │   │   ├── Modal.tsx
  │   │   └── Loading.tsx
  │   ├── analysis/            # Analysis-specific components
  │   │   ├── AnalysisForm.tsx
  │   │   ├── ResultsView.tsx
  │   │   └── FixAgent.tsx
  │   └── dashboard/           # Dashboard components
  │       ├── Summary.tsx
  │       └── Charts.tsx
  ├── hooks/                   # Custom React hooks
  ├── services/                # API service layer
  ├── types/                   # TypeScript type definitions
  └── utils/                   # Frontend utilities
  ```

### **Task 4.2: State Management**
- [ ] **Implement proper state management:**
  ```typescript
  // src/web/src/store/analysis.ts
  import { create } from 'zustand'
  
  interface AnalysisState {
    currentAnalysis: Analysis | null
    isRunning: boolean
    results: AnalysisResult[]
    startAnalysis: (request: AnalysisRequest) => Promise<void>
    clearResults: () => void
  }
  
  export const useAnalysisStore = create<AnalysisState>((set, get) => ({
    currentAnalysis: null,
    isRunning: false,
    results: [],
    startAnalysis: async (request) => {
      set({ isRunning: true })
      // Implementation
    },
    clearResults: () => set({ results: [] })
  }))
  ```

---

## 🔌 **Phase 5: Integration Refactoring**

### **Task 5.1: Azure DevOps Integration**
- [ ] **Refactor ADO integration:**
  ```python
  # src/core/integrations/azure_devops.py
  from abc import ABC, abstractmethod
  from typing import Dict, Any
  
  class WorkItemProvider(ABC):
      @abstractmethod
      async def create_work_item(self, data: Dict[str, Any]) -> Dict[str, Any]:
          pass
      
      @abstractmethod
      async def update_work_item(self, id: int, data: Dict[str, Any]) -> Dict[str, Any]:
          pass
  
  class AzureDevOpsProvider(WorkItemProvider):
      def __init__(self, organization: str, project: str, pat: str):
          self.client = AzureDevOpsClient(organization, project, pat)
      
      async def create_work_item(self, data: Dict[str, Any]) -> Dict[str, Any]:
          return await self.client.create_work_item(data)
  ```

### **Task 5.2: Gemini Integration**
- [ ] **Refactor Gemini CLI:**
  ```python
  # src/core/integrations/gemini.py
  class GeminiService:
      def __init__(self, api_key: str):
          self.client = genai.Client(api_key=api_key)
      
      async def generate_fix(self, code: str, issue: str) -> str:
          prompt = self._build_fix_prompt(code, issue)
          response = await self.client.models.generate_content(prompt)
          return response.text
      
      def _build_fix_prompt(self, code: str, issue: str) -> str:
          return f"""
          Fix the following issue in the code:
          
          Issue: {issue}
          
          Code:
          {code}
          
          Provide only the fixed code without explanations.
          """
  ```

---

## 📊 **Phase 6: Performance Optimization**

### **Task 6.1: Database Integration**
- [ ] **Implement proper data persistence:**
  ```python
  # src/core/database/models.py
  from sqlalchemy import Column, Integer, String, DateTime, JSON
  from sqlalchemy.ext.declarative import declarative_base
  
  Base = declarative_base()
  
  class Analysis(Base):
      __tablename__ = "analyses"
      
      id = Column(Integer, primary_key=True)
      analysis_id = Column(String, unique=True, index=True)
      url = Column(String)
      status = Column(String)
      results = Column(JSON)
      created_at = Column(DateTime)
  ```

### **Task 6.2: Caching Strategy**
- [ ] **Implement Redis caching:**
  ```python
  # src/utils/cache.py
  import redis
  import json
  from typing import Optional, Any
  
  class CacheManager:
      def __init__(self, redis_url: str):
          self.redis = redis.from_url(redis_url)
      
      async def get(self, key: str) -> Optional[Any]:
          data = self.redis.get(key)
          return json.loads(data) if data else None
      
      async def set(self, key: str, value: Any, ttl: int = 3600):
          self.redis.setex(key, ttl, json.dumps(value))
  ```

---

## 🚀 **Phase 7: Deployment & CI/CD**

### **Task 7.1: Docker Configuration**
- [ ] **Create multi-stage Dockerfile:**
  ```dockerfile
  # Dockerfile
  FROM python:3.11-slim as backend
  WORKDIR /app
  COPY requirements.txt .
  RUN pip install -r requirements.txt
  COPY src/ ./src/
  CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
  
  FROM node:18-alpine as frontend
  WORKDIR /app
  COPY src/web/package*.json ./
  RUN npm ci --only=production
  COPY src/web/ ./
  RUN npm run build
  
  FROM nginx:alpine
  COPY --from=frontend /app/dist /usr/share/nginx/html
  COPY nginx.conf /etc/nginx/nginx.conf
  ```

### **Task 7.2: GitHub Actions Workflow**
- [ ] **Create CI/CD pipeline:**
  ```yaml
  # .github/workflows/ci.yml
  name: CI/CD Pipeline
  
  on: [push, pull_request]
  
  jobs:
    test:
      runs-on: ubuntu-latest
      steps:
        - uses: actions/checkout@v3
        - name: Set up Python
          uses: actions/setup-python@v4
          with:
            python-version: '3.11'
        - name: Install dependencies
          run: |
            pip install -r requirements.txt
            pip install pytest pytest-asyncio
        - name: Run tests
          run: pytest tests/
  
    build:
      needs: test
      runs-on: ubuntu-latest
      steps:
        - uses: actions/checkout@v3
        - name: Build Docker image
          run: docker build -t craftbug-agentic-system .
  ```

---

## 📈 **Phase 8: Monitoring & Observability**

### **Task 8.1: Application Monitoring**
- [ ] **Implement structured logging:**
  ```python
  # src/utils/logging.py
  import structlog
  
  def setup_structured_logging():
      structlog.configure(
          processors=[
              structlog.stdlib.filter_by_level,
              structlog.stdlib.add_logger_name,
              structlog.stdlib.add_log_level,
              structlog.stdlib.PositionalArgumentsFormatter(),
              structlog.processors.TimeStamper(fmt="iso"),
              structlog.processors.StackInfoRenderer(),
              structlog.processors.format_exc_info,
              structlog.processors.UnicodeDecoder(),
              structlog.processors.JSONRenderer()
          ],
          context_class=dict,
          logger_factory=structlog.stdlib.LoggerFactory(),
          wrapper_class=structlog.stdlib.BoundLogger,
          cache_logger_on_first_use=True,
      )
  ```

### **Task 8.2: Health Checks**
- [ ] **Implement comprehensive health checks:**
  ```python
  # src/api/routes/health.py
  from fastapi import APIRouter
  from src.core.health import HealthChecker
  
  router = APIRouter(prefix="/health", tags=["health"])
  
  @router.get("/")
  async def health_check():
      checker = HealthChecker()
      return await checker.check_all()
  
  @router.get("/ready")
  async def readiness_check():
      checker = HealthChecker()
      return await checker.check_readiness()
  ```

---

## 📋 **Implementation Timeline**

### **Week 1-2: Foundation**
- [ ] Complete Phase 1 (Code Cleanup)
- [ ] Set up new project structure
- [ ] Create basic configuration management

### **Week 3-4: Core Refactoring**
- [ ] Complete Phase 2 (Architecture)
- [ ] Implement service layer
- [ ] Extract API routes

### **Week 5-6: Testing & Frontend**
- [ ] Complete Phase 3 (Testing)
- [ ] Complete Phase 4 (Frontend)
- [ ] Implement comprehensive test suite

### **Week 7-8: Integrations & Performance**
- [ ] Complete Phase 5 (Integrations)
- [ ] Complete Phase 6 (Performance)
- [ ] Implement caching and database

### **Week 9-10: Deployment & Monitoring**
- [ ] Complete Phase 7 (Deployment)
- [ ] Complete Phase 8 (Monitoring)
- [ ] Final testing and documentation

---

## 🎯 **Success Metrics**

### **Code Quality:**
- [ ] **Reduced file count**: From 150+ to <50 core files
- [ ] **Reduced complexity**: Average cyclomatic complexity <10
- [ ] **Improved test coverage**: >90% coverage
- [ ] **Eliminated duplication**: 0 duplicate functions

### **Performance:**
- [ ] **Faster startup**: <5 seconds
- [ ] **Reduced memory usage**: <500MB baseline
- [ ] **Improved response times**: <2 seconds for analysis
- [ ] **Better caching**: 80% cache hit rate

### **Maintainability:**
- [ ] **Modular architecture**: Clear separation of concerns
- [ ] **Consistent patterns**: Standardized error handling
- [ ] **Comprehensive documentation**: All APIs documented
- [ ] **Easy deployment**: One-command deployment

---

## 🚨 **Risk Mitigation**

### **High-Risk Areas:**
1. **Breaking Changes**: Implement feature flags for gradual migration
2. **Data Loss**: Comprehensive backup strategy before refactoring
3. **Integration Failures**: Extensive integration testing
4. **Performance Regression**: Continuous performance monitoring

### **Mitigation Strategies:**
- [ ] **Feature Flags**: Use feature flags for gradual rollout
- [ ] **Backup Strategy**: Complete system backup before refactoring
- [ ] **Rollback Plan**: Maintain ability to rollback to previous version
- [ ] **Monitoring**: Real-time monitoring during refactoring

---

## 📚 **Documentation Requirements**

### **Technical Documentation:**
- [ ] **API Documentation**: OpenAPI/Swagger specs
- [ ] **Architecture Diagrams**: System design documentation
- [ ] **Deployment Guide**: Step-by-step deployment instructions
- [ ] **Troubleshooting Guide**: Common issues and solutions

### **User Documentation:**
- [ ] **User Manual**: End-user documentation
- [ ] **Developer Guide**: Integration and extension guide
- [ ] **Admin Guide**: System administration guide
- [ ] **Migration Guide**: Guide for existing users

---

## ✅ **Completion Checklist**

### **Pre-Refactoring:**
- [ ] Complete codebase analysis
- [ ] Create comprehensive test suite
- [ ] Set up development environment
- [ ] Create backup of current system

### **During Refactoring:**
- [ ] Maintain functionality throughout process
- [ ] Run tests after each phase
- [ ] Update documentation continuously
- [ ] Monitor performance metrics

### **Post-Refactoring:**
- [ ] Complete end-to-end testing
- [ ] Performance validation
- [ ] Security audit
- [ ] User acceptance testing
- [ ] Production deployment
- [ ] Monitoring setup

---

**🎉 This refactoring plan will transform the Craftbug Agentic System into a maintainable, scalable, and performant application ready for production use!**
