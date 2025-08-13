# 🚀 Craftbug Agentic System - Complete End-to-End Documentation

## 📋 Table of Contents
1. [System Overview](#system-overview)
2. [Architecture](#architecture)
3. [Technology Stack](#technology-stack)
4. [Core Components](#core-components)
5. [User Journey](#user-journey)
6. [Agent System](#agent-system)
7. [Visual vs Code Components](#visual-vs-code-components)
8. [Implementation Details](#implementation-details)
9. [API Endpoints](#api-endpoints)
10. [Deployment](#deployment)
11. [Getting Started](#getting-started)

---

## 🎯 System Overview

The **Craftbug Agentic System** is an AI-powered UX analysis and automated code fixing platform that detects UI/UX issues in web applications and automatically fixes them using AI agents.

### Key Features:
- **Real-time UX Analysis**: Automated detection of accessibility, performance, and usability issues
- **AI-Powered Code Fixes**: Automated code generation and fixes using Gemini AI
- **Visual Media Capture**: Screenshots and videos for issue documentation
- **Azure DevOps Integration**: Seamless ticket management and workflow
- **Real-time Agent Thinking**: Live display of AI reasoning process
- **Git Integration**: Automated code commits and version control

---

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Backend       │    │   External      │
│   (React/TS)    │◄──►│   (FastAPI)     │◄──►│   Services      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
│                        │                        │
├─ Dashboard UI          ├─ Analysis Engine       ├─ Gemini AI
├─ Report Viewer         ├─ Agent Orchestrator    ├─ Azure DevOps
├─ Media Gallery         ├─ Media Capture         ├─ Git Repository
└─ Fix Interface         └─ Report Generator      └─ Browser Automation
```

### Architecture Layers:

1. **Presentation Layer**: React TypeScript frontend
2. **API Layer**: FastAPI REST endpoints
3. **Business Logic Layer**: Analysis engines and agents
4. **Data Layer**: JSON reports, media files, database
5. **Integration Layer**: External APIs (Gemini, ADO, Git)

---

## 🛠️ Technology Stack

### Frontend
- **Framework**: React 18 + TypeScript
- **Styling**: Tailwind CSS
- **Build Tool**: Vite
- **State Management**: React Hooks + Context
- **Charts**: Plotly.js
- **Icons**: Lucide React

### Backend
- **Framework**: FastAPI (Python 3.11)
- **Async Support**: asyncio, aiofiles
- **Browser Automation**: Playwright
- **AI Integration**: Google Gemini API
- **HTTP Client**: httpx
- **File Handling**: pathlib, shutil

### External Services
- **AI Model**: Gemini 1.5 Pro
- **Version Control**: Git
- **Project Management**: Azure DevOps
- **Media Storage**: Local filesystem
- **Real-time Communication**: Server-Sent Events (SSE)

---

## 🔧 Core Components

### 1. Analysis Engine (`enhanced_fastapi_server.py`)
```python
# Main analysis orchestrator
class EnhancedUXAnalyzer:
    - Real browser automation
    - Screenshot/video capture
    - Issue detection algorithms
    - Report generation
```

### 2. AI Agent System (`gemini_cli.py`)
```python
# AI-powered code fixing
class GeminiAgent:
    - Code analysis
    - Fix generation
    - ADO integration
    - Real-time thinking steps
```

### 3. Report Generator (`enhanced_report_generator.py`)
```python
# Enhanced reporting with media
class EnhancedReportGenerator:
    - Contextual media association
    - HTML report generation
    - Media capture and storage
    - Issue categorization
```

### 4. Frontend Dashboard (`web-ui/src/`)
```typescript
// React components
- DashboardPage: Main analytics view
- ReportPage: Detailed report viewer
- AnalysisPage: Analysis configuration
- Media components: Screenshot/video display
```

---

## 🎯 User Journey

### 1. **Analysis Initiation** (Visual Interface)
```
User → Dashboard → Configure Analysis → Start Analysis
```
- **Visual**: Analysis configuration form
- **Code**: FastAPI endpoint `/api/analyze`

### 2. **Real-time Analysis** (Background Process)
```
Browser Automation → Issue Detection → Media Capture → Report Generation
```
- **Code**: Playwright automation, analysis algorithms
- **Visual**: Progress indicators, real-time logs

### 3. **Report Review** (Visual Interface)
```
Report Dashboard → Issue Details → Media Gallery → Fix Decisions
```
- **Visual**: Interactive report viewer with side-by-side media
- **Code**: Report data processing, media serving

### 4. **AI Fix Generation** (Hybrid)
```
User Request → AI Analysis → Code Generation → ADO Integration
```
- **Visual**: Fix interface with real-time thinking display
- **Code**: Gemini API integration, code generation

### 5. **Git Integration** (Code Backend)
```
Code Changes → Git Commit → Push → Status Update
```
- **Code**: Git automation, branch management
- **Visual**: Status indicators, approval workflow

---

## 🤖 Agent System

### 1. **Analysis Agent** (Automated)
```python
# Detects UX issues automatically
- Accessibility violations
- Performance bottlenecks
- Visual inconsistencies
- Craft bug detection
```

### 2. **Fix Agent** (AI-Powered)
```python
# Generates code fixes using Gemini
- Code analysis
- Fix generation
- Context understanding
- Real-time reasoning
```

### 3. **Integration Agent** (Automated)
```python
# Manages external integrations
- Azure DevOps ticket creation
- Git commit/push operations
- Status synchronization
```

### 4. **Media Agent** (Automated)
```python
# Handles media capture and processing
- Screenshot capture
- Video recording
- Media association
- Storage management
```

---

## 🎨 Visual vs Code Components

### **Visual Components** (User Interface)
1. **Dashboard** (`DashboardPage.tsx`)
   - Analytics overview
   - Report summaries
   - Performance metrics

2. **Report Viewer** (`ReportPage.tsx`)
   - Issue listings
   - Media gallery
   - Side-by-side layout

3. **Analysis Configuration** (`AnalysisPage.tsx`)
   - URL input
   - Scenario selection
   - Analysis settings

4. **Fix Interface** (`fix-with-agent` screen)
   - Real-time thinking display
   - Fix approval workflow
   - Status indicators

### **Code Components** (Backend Logic)
1. **Analysis Engine** (`enhanced_fastapi_server.py`)
   - Browser automation
   - Issue detection algorithms
   - Report generation

2. **AI Agent** (`gemini_cli.py`)
   - Code analysis
   - Fix generation
   - ADO integration

3. **Media Processing** (`enhanced_report_generator.py`)
   - Screenshot capture
   - Video recording
   - Media association

4. **Git Operations** (`enhanced_fastapi_server.py`)
   - Commit automation
   - Branch management
   - Push operations

---

## 🔍 Implementation Details

### 1. **Real-time Analysis Flow**
```python
# enhanced_fastapi_server.py
@app.post("/api/analyze")
async def analyze_url():
    1. Initialize browser automation
    2. Execute scenario steps
    3. Capture screenshots/videos
    4. Run issue detection algorithms
    5. Generate enhanced report
    6. Create ADO tickets
    7. Return analysis results
```

### 2. **AI Fix Generation**
```python
# gemini_cli.py
def fix_issue_with_thinking_steps():
    1. Analyze issue context
    2. Generate thinking steps
    3. Create code fixes
    4. Update ADO ticket
    5. Stream real-time updates
```

### 3. **Media Capture System**
```python
# enhanced_report_generator.py
async def capture_issue_specific_media():
    1. Categorize issue type
    2. Capture appropriate media
    3. Associate with findings
    4. Store with metadata
```

### 4. **Frontend State Management**
```typescript
// React hooks for state management
const [reports, setReports] = useState<Report[]>([]);
const [currentReport, setCurrentReport] = useState<Report | null>(null);
const [analysisStatus, setAnalysisStatus] = useState<string>('idle');
```

---

## 🌐 API Endpoints

### Analysis Endpoints
```python
POST /api/analyze          # Start analysis
GET  /api/reports/{id}     # Get report data
GET  /api/scenarios        # List available scenarios
```

### Media Endpoints
```python
GET  /enhanced/{filepath}  # Serve media files
GET  /api/reports/{id}/download  # Download reports
```

### Fix Endpoints
```python
POST /api/ado/trigger-fix  # Start AI fix
GET  /api/ado/thinking-steps/{id}  # SSE stream
GET  /api/git/approve-commit  # Git approval interface
POST /api/git/commit-changes  # Execute git operations
```

### Frontend Routes
```typescript
/                    # Dashboard
/analyze            # Analysis configuration
/reports/{id}       # Report viewer
/fix-with-agent     # AI fix interface
```

---

## 🚀 Getting Started

### Prerequisites
- Python 3.11+
- Node.js 16+
- Git
- Google Gemini API Key
- Azure DevOps Personal Access Token

### Installation Steps

#### 1. Clone the Repository
```bash
git clone <repository-url>
cd Craftbug_Agentic_System
```

#### 2. Backend Setup
```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your API keys
```

#### 3. Frontend Setup
```bash
cd web-ui
npm install
```

#### 4. Environment Configuration
```bash
# Required environment variables
GEMINI_API_KEY=your_gemini_api_key
AZURE_DEVOPS_ORG=your_organization
AZURE_DEVOPS_PROJECT=your_project
AZURE_DEVOPS_PAT=your_personal_access_token
```

#### 5. Start the Application
```bash
# Terminal 1: Start backend
python enhanced_fastapi_server.py

# Terminal 2: Start frontend
cd web-ui
npm run dev
```

#### 6. Access the Application
- Frontend: http://localhost:8080
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

---

## 📊 System Metrics

### Performance Indicators
- **Analysis Time**: 30-60 seconds per analysis
- **Media Capture**: 10-20 screenshots per analysis
- **Issue Detection**: 5-15 issues per analysis
- **AI Fix Time**: 10-30 seconds per fix

### Scalability
- **Concurrent Analyses**: Limited by browser instances
- **Media Storage**: Local filesystem (scalable to cloud)
- **AI Processing**: Rate-limited by Gemini API
- **Git Operations**: Sequential for safety

---

## 🔮 Future Enhancements

### Planned Features
1. **Multi-language Support**: Support for different programming languages
2. **Cloud Integration**: AWS/Azure media storage
3. **Advanced Analytics**: Machine learning for issue prediction
4. **Team Collaboration**: Multi-user support
5. **Custom Scenarios**: User-defined analysis scenarios

### Technical Improvements
1. **Microservices**: Split into smaller services
2. **Event-driven**: Implement message queues
3. **Caching**: Add Redis for performance
4. **Testing**: Comprehensive test suite
5. **CI/CD**: Automated deployment pipeline

---

## 📁 Project Structure

```
Craftbug_Agentic_System/
├── enhanced_fastapi_server.py      # Main backend server
├── gemini_cli.py                   # AI agent implementation
├── enhanced_report_generator.py    # Report generation
├── requirements.txt                # Python dependencies
├── web-ui/                         # React frontend
│   ├── src/
│   │   ├── pages/                  # Main page components
│   │   ├── components/             # Reusable components
│   │   ├── hooks/                  # Custom React hooks
│   │   └── services/               # API services
│   ├── package.json
│   └── vite.config.ts
├── reports/                        # Generated reports
│   └── enhanced/                   # Enhanced reports with media
├── scenarios/                      # Analysis scenarios
└── docs/                          # Documentation
```

---

## 🤝 Contributing

### Development Workflow
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

### Code Standards
- Python: PEP 8 compliance
- TypeScript: ESLint configuration
- React: Functional components with hooks
- API: RESTful design principles

---

## 📞 Support

### Documentation
- [API Documentation](http://localhost:8000/docs)
- [Frontend Documentation](./web-ui/README.md)
- [Deployment Guide](./docs/DEPLOYMENT.md)

### Issues
- Report bugs via GitHub Issues
- Feature requests welcome
- Security issues: Please email directly

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

**Craftbug Agentic System** - AI-Powered UX Analysis & Automated Code Fixing Platform

*Built with ❤️ using React, FastAPI, and Gemini AI*
