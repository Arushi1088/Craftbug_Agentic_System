# 🚀 Craftbug Agentic System

AI-Powered UX Analysis & Automated Code Fixing Platform

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://python.org)
[![React](https://img.shields.io/badge/React-18+-blue.svg)](https://reactjs.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green.svg)](https://fastapi.tiangolo.com)
[![Gemini AI](https://img.shields.io/badge/Gemini-AI-orange.svg)](https://ai.google.dev/gemini)

## 🎯 Overview

The **Craftbug Agentic System** is a comprehensive platform that automatically detects UI/UX issues in web applications and fixes them using AI agents. It combines real-time analysis, visual media capture, and automated code generation to streamline the development workflow.

### ✨ Key Features

- 🔍 **Real-time UX Analysis**: Automated detection of accessibility, performance, and usability issues
- 🤖 **AI-Powered Code Fixes**: Automated code generation using Google Gemini AI
- 📸 **Visual Media Capture**: Screenshots and videos for issue documentation
- 🔗 **Azure DevOps Integration**: Seamless ticket management and workflow
- 🧠 **Real-time Agent Thinking**: Live display of AI reasoning process
- 📝 **Git Integration**: Automated code commits and version control

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

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Node.js 16+
- Git
- Google Gemini API Key
- Azure DevOps Personal Access Token

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd Craftbug_Agentic_System
   ```

2. **Backend Setup**
   ```bash
   # Create virtual environment
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   
   # Install dependencies
   pip install -r requirements.txt
   ```

3. **Frontend Setup**
   ```bash
   cd web-ui
   npm install
   ```

4. **Environment Configuration**
   ```bash
   # Set up environment variables
   export GEMINI_API_KEY="your_gemini_api_key"
   export AZURE_DEVOPS_ORG="your_organization"
   export AZURE_DEVOPS_PROJECT="your_project"
   export AZURE_DEVOPS_PAT="your_personal_access_token"
   ```

5. **Start the Application**
   ```bash
   # Terminal 1: Start backend
   python enhanced_fastapi_server.py
   
   # Terminal 2: Start frontend
   cd web-ui
   npm run dev
   ```

6. **Access the Application**
   - Frontend: http://localhost:8080
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

## 📖 Documentation

For complete documentation, see:
- [Complete System Documentation](./CRAFTBUG_SYSTEM_DOCUMENTATION.md)
- [API Documentation](http://localhost:8000/docs)
- [Deployment Guide](./docs/DEPLOYMENT.md)

## 🎯 User Journey

1. **Analysis Initiation**: Configure and start UX analysis
2. **Real-time Analysis**: Automated issue detection with media capture
3. **Report Review**: Interactive report viewer with side-by-side media
4. **AI Fix Generation**: AI-powered code fixes with real-time thinking
5. **Git Integration**: Automated code commits and version control

## 🤖 Agent System

- **Analysis Agent**: Automated UX issue detection
- **Fix Agent**: AI-powered code generation using Gemini
- **Integration Agent**: Azure DevOps and Git automation
- **Media Agent**: Screenshot and video capture

## 🛠️ Technology Stack

### Frontend
- React 18 + TypeScript
- Tailwind CSS
- Vite
- Plotly.js
- Lucide React

### Backend
- FastAPI (Python 3.11)
- Playwright (Browser Automation)
- Google Gemini API
- Azure DevOps API

### External Services
- Gemini 1.5 Pro (AI Model)
- Azure DevOps (Project Management)
- Git (Version Control)

## 📊 System Metrics

- **Analysis Time**: 30-60 seconds per analysis
- **Media Capture**: 10-20 screenshots per analysis
- **Issue Detection**: 5-15 issues per analysis
- **AI Fix Time**: 10-30 seconds per fix

## 🔮 Roadmap

### Planned Features
- Multi-language support
- Cloud integration (AWS/Azure)
- Advanced analytics with ML
- Team collaboration features
- Custom analysis scenarios

### Technical Improvements
- Microservices architecture
- Event-driven design
- Redis caching
- Comprehensive testing
- CI/CD pipeline

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📞 Support

- Report bugs via GitHub Issues
- Feature requests welcome
- Security issues: Please email directly

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

**Craftbug Agentic System** - AI-Powered UX Analysis & Automated Code Fixing Platform

*Built with ❤️ using React, FastAPI, and Gemini AI*
