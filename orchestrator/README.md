# 🎯 Orchestrator Agent

The Orchestrator Agent is a multi-agent coordination system that bridges the **UX Analyzer** and **Coder Agent** to create an automated bug detection and fixing pipeline.

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   UX Analyzer   │    │  Orchestrator   │    │   Coder Agent   │
│                 │    │     Agent       │    │                 │
│ • Performance   │◄──►│                 │◄──►│ • Gemini AI     │
│ • Accessibility │    │ • Coordination  │    │ • Azure DevOps  │
│ • UX Heuristics │    │ • Task Creation │    │ • Auto Fixes    │
│ • Best Practices│    │ • Monitoring    │    │ • Code Analysis │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## ✨ Key Features

### 🔄 **Full Automation Pipeline**
- **Analyze** → **Detect Issues** → **Create Tasks** → **Auto-Fix** → **Report**

### 🎛️ **Intelligent Orchestration**
- **Severity-based filtering**: Only create tasks for high/medium priority issues
- **Concurrent task execution**: Process multiple fixes simultaneously
- **Smart file identification**: Automatically determine which files need fixing
- **Context preservation**: Pass analysis context to coder agent for better fixes

### 📊 **Comprehensive Monitoring**
- **Real-time status tracking**
- **Analysis history management**
- **Task execution monitoring**
- **Performance metrics**

### 🔧 **Flexible Configuration**
- **Environment-based config**: Use `.env` or `config.json`
- **Module selection**: Choose which UX analysis modules to run
- **Auto-fix control**: Enable/disable automatic code fixes
- **Threshold settings**: Configure issue severity thresholds

## 🚀 Quick Start

### 1. **Setup Environment**
```bash
# Copy environment template
cp .env.example .env

# Edit with your credentials
nano .env
```

### 2. **Install Dependencies**
```bash
pip install -r requirements.txt
```

### 3. **Configure Agents**
Edit `config.json` or set environment variables:

```json
{
  "ux_analyzer": {
    "api_endpoint": "http://localhost:8000"
  },
  "coder_agent": {
    "azure_devops_org": "your-org",
    "gemini_api_key": "your-key"
  },
  "orchestrator": {
    "auto_trigger_fixes": false,
    "severity_threshold": "medium"
  }
}
```

### 4. **Run Orchestrator**
```bash
python main.py
```

## 📋 Usage Examples

### **Basic Website Analysis**
```python
from orchestrator.main import OrchestratorAgent

orchestrator = OrchestratorAgent()
await orchestrator.initialize_agents()

# Run full analysis cycle
result = await orchestrator.orchestrate_full_cycle("https://your-website.com")
print(result)
```

### **Custom Module Analysis**
```python
# Analyze only accessibility and performance
custom_modules = {
    "accessibility": True,
    "performance": True,
    "ux_heuristics": False
}

result = await orchestrator.analyze_website(
    "https://your-website.com", 
    custom_modules=custom_modules
)
```

### **Manual Task Creation**
```python
# Get analysis results
analysis = await orchestrator.analyze_website("https://your-website.com")

# Create tasks without auto-execution
tasks = await orchestrator.create_coder_tasks(analysis)

# Review tasks manually, then execute
if input("Execute fixes? (y/n): ").lower() == 'y':
    results = await orchestrator.execute_coder_tasks(tasks)
```

## 🔗 Integration Points

### **UX Analyzer Integration**
- **API Endpoint**: `http://localhost:8000/api/analyze`
- **Supported Formats**: URL analysis, screenshot analysis, scenario testing
- **Data Flow**: Analysis results → Issue extraction → Task creation

### **Coder Agent Integration**
- **Path**: `../coder_agent/`
- **Components**: Gemini AI, Azure DevOps tools, GitHub integration
- **Data Flow**: Task specification → Code analysis → Automated fixes

## 📁 Project Structure

```
orchestrator/
├── main.py              # Main orchestrator logic
├── config.json          # Configuration file
├── .env.example         # Environment template
├── requirements.txt     # Python dependencies
├── README.md           # This file
├── logs/               # Orchestrator logs
└── tests/              # Unit tests
```

## 🔧 Configuration Options

### **Environment Variables**
| Variable | Description | Default |
|----------|-------------|---------|
| `UX_ANALYZER_API_ENDPOINT` | UX Analyzer API URL | `http://localhost:8000` |
| `AZURE_DEVOPS_ORG` | Azure DevOps organization | None |
| `GEMINI_API_KEY` | Google Gemini API key | None |
| `ORCHESTRATOR_AUTO_TRIGGER_FIXES` | Auto-execute fixes | `false` |
| `ORCHESTRATOR_SEVERITY_THRESHOLD` | Minimum severity for tasks | `medium` |

### **Severity Levels**
- **`high`**: Critical issues that break functionality
- **`medium`**: Important issues affecting UX
- **`low`**: Minor improvements and optimizations

### **Auto-Fix Safety**
- **Manual Approval**: Require human review before fixes
- **File Size Limits**: Prevent modification of large files
- **Domain Restrictions**: Only analyze allowed domains

## 📊 Monitoring & Reporting

### **Status Endpoint**
```python
status = orchestrator.get_status()
# Returns: agent availability, active tasks, history count
```

### **Analysis History**
- **Persistent storage**: SQLite database for analysis history
- **Metrics tracking**: Success rates, execution times, issue trends
- **Report generation**: JSON, HTML, and dashboard formats

### **Logging**
- **Structured logging**: JSON format for easy parsing
- **Log rotation**: Automatic cleanup of old log files
- **Multiple levels**: DEBUG, INFO, WARNING, ERROR

## 🔒 Security & Safety

### **Auto-Fix Controls**
- **Dry run mode**: Preview changes without execution
- **File whitelist**: Only modify approved file types
- **Rollback capability**: Undo changes if issues detected

### **API Security**
- **Rate limiting**: Prevent API abuse
- **Domain validation**: Restrict analysis to approved domains
- **Token management**: Secure credential handling

## 🧪 Testing

```bash
# Run unit tests
pytest tests/

# Run with coverage
pytest --cov=orchestrator tests/

# Test specific component
pytest tests/test_orchestrator.py::test_full_cycle
```

## 🚀 Deployment

### **Production Setup**
1. **Environment**: Use production `.env` file
2. **Database**: Configure persistent database (PostgreSQL recommended)
3. **Monitoring**: Set up log aggregation and alerting
4. **Scaling**: Use Redis/Celery for distributed task processing

### **Docker Deployment**
```dockerfile
FROM python:3.11-slim
COPY orchestrator/ /app/orchestrator/
WORKDIR /app/orchestrator
RUN pip install -r requirements.txt
CMD ["python", "main.py"]
```

## 🤝 Contributing

1. **Fork** the repository
2. **Create** feature branch: `git checkout -b feature/awesome-feature`
3. **Commit** changes: `git commit -m 'Add awesome feature'`
4. **Push** to branch: `git push origin feature/awesome-feature`
5. **Submit** pull request

## 📝 License

This project is part of the Craftbug Agentic System and follows the same licensing terms.

---

## 🎯 Next Steps

- [ ] Implement real UX Analyzer API integration
- [ ] Add Coder Agent execution interface
- [ ] Create web dashboard for monitoring
- [ ] Add support for custom analysis rules
- [ ] Implement notification integrations
- [ ] Add performance metrics collection

**Happy Orchestrating! 🎼**
