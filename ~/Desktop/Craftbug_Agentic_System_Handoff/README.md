# Craftbug Agentic System - Developer Handoff

## 🚀 Overview

This is a complete LLM-enhanced UX analysis system that automatically detects craft bugs in web applications using AI-powered screenshot analysis. The system integrates with Excel Web for automated testing and generates comprehensive bug reports.

## ✨ Key Features

- **AI-Powered Bug Detection**: Uses GPT-5-nano for cost-effective craft bug analysis
- **Screenshot Analysis**: Automatically captures and analyzes screenshots for each test step
- **Comprehensive Reports**: Generates detailed HTML reports with bug classifications
- **Cost Optimized**: Uses the cheapest available OpenAI model ($0.15/1M tokens)
- **Deduplication**: Prevents duplicate bug reports across analysis types
- **Expert Triaging**: Validates and prioritizes bugs based on impact

## 🏗️ Architecture

```
├── Backend (FastAPI)
│   ├── enhanced_fastapi_server.py    # Main API server
│   ├── llm_enhanced_analyzer.py      # Core LLM analysis engine
│   ├── enhanced_ux_analyzer.py       # UX analysis orchestration
│   └── excel_scenario_telemetry.py   # Screenshot collection
├── Frontend (React + Vite)
│   └── web-ui/                       # Dashboard interface
├── Scenarios
│   └── scenarios/                    # Test scenario definitions
└── Utilities
    ├── src/                          # Core utilities
    └── utils/                        # Helper functions
```

## 🛠️ Setup Instructions

### 1. Environment Setup

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Environment Variables

Create a `.env` file in the root directory:

```env
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-5-nano
OPENAI_TEMPERATURE=0.1
OPENAI_MAX_TOKENS=2000
```

### 3. Frontend Setup

```bash
cd web-ui
npm install
npm run dev
```

### 4. Backend Setup

```bash
# In the root directory
python3 enhanced_fastapi_server.py
```

## 🎯 Usage

### Starting the System

1. **Start Backend**: `python3 enhanced_fastapi_server.py`
2. **Start Frontend**: `cd web-ui && npm run dev`
3. **Access Dashboard**: Open http://127.0.0.1:8080

### Running Tests

```bash
# Test screenshot flow
python3 test_screenshot_flow.py

# Test LLM analysis
python3 simple_llm_test.py

# Test visual issues
python3 test_with_visual_issues.py
```

### API Endpoints

- `GET /health` - Health check
- `POST /api/excel-web/ux-report` - Generate Excel UX report
- `GET /reports/excel_ux/{filename}` - View generated reports

## 🔧 Configuration

### Model Selection

The system is configured to use `gpt-5-nano` for cost optimization. To change models:

1. Update `OPENAI_MODEL` in `.env`
2. Restart the server

Available models (from cheapest to most expensive):
- `gpt-5-nano`: $0.15/1M tokens (current)
- `gpt-5-mini`: $0.60/1M tokens
- `gpt-5`: $2.50/1M tokens
- `o3`: $5.00/1M tokens

### Analysis Types

The system performs three types of analysis per screenshot:

1. **Comprehensive Visual Analysis**: Detects visual bugs, alignment issues, color problems
2. **Performance Analysis**: Identifies visual quality issues
3. **Interaction Analysis**: Finds interaction design problems

## 📊 Output

### Bug Categories

- **Visual**: Alignment, colors, typography, spacing
- **Accessibility**: Contrast, readability, screen reader compatibility
- **Interaction Design**: Clickability, affordances, visual feedback
- **Layout**: Grid alignment, responsive design issues
- **Design System**: Fluent Design compliance violations

### Report Structure

Each bug report includes:
- Issue summary with severity (Red/Orange/Yellow)
- Location and context
- Visual analysis details
- Reproduction steps
- Persona impact assessment
- Developer action items

## 🐛 Troubleshooting

### Common Issues

1. **OpenAI Quota Exceeded**
   - Add billing to your OpenAI account
   - Check usage at https://platform.openai.com/usage

2. **Port Conflicts**
   - Backend: Kill existing process on port 8000
   - Frontend: Kill existing process on port 8080

3. **Screenshot Issues**
   - Ensure screenshots directory exists
   - Check file permissions

### Testing

```bash
# Test system health
curl http://127.0.0.1:8000/health

# Test screenshot flow
python3 test_screenshot_flow.py

# Check model availability
python3 -c "import openai; print(openai.Model.list())"
```

## 📁 File Structure

```
Craftbug_Agentic_System_Handoff/
├── README.md                          # This file
├── requirements.txt                   # Python dependencies
├── AI_MODEL_CONFIG.md                # Model configuration guide
├── enhanced_fastapi_server.py        # Main API server
├── llm_enhanced_analyzer.py          # Core LLM engine
├── enhanced_ux_analyzer.py           # UX analysis
├── excel_scenario_telemetry.py       # Telemetry collection
├── dynamic_ux_analyzer.py            # Dynamic analysis
├── test_screenshot_flow.py           # Screenshot testing
├── simple_llm_test.py                # LLM testing
├── test_with_visual_issues.py        # Visual testing
├── web-ui/                           # Frontend application
├── scenarios/                        # Test scenarios
├── src/                              # Core utilities
└── utils/                            # Helper functions
```

## 🚀 Deployment

### Production Setup

1. **Environment**: Use production-grade server
2. **Database**: Add persistent storage for reports
3. **Security**: Implement proper authentication
4. **Monitoring**: Add logging and error tracking
5. **Scaling**: Consider containerization with Docker

### Docker (Optional)

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["python3", "enhanced_fastapi_server.py"]
```

## 📞 Support

For issues or questions:
1. Check the troubleshooting section
2. Review the test files for examples
3. Check OpenAI API status
4. Verify environment variables

## 🔄 Updates

The system is designed to be easily updatable:
- Model changes: Update `.env` file
- Prompt changes: Modify `llm_enhanced_analyzer.py`
- UI changes: Modify `web-ui/` files
- Scenarios: Add to `scenarios/` directory

---

**System Status**: ✅ Fully functional and ready for production use
**Last Updated**: August 22, 2025
**Version**: 2.0.0
