# 🤖 Coder Agent Integration Guide

## Overview
The Coder Agent Integration provides AI-powered automated code fixes for UX issues detected in mock applications. It integrates seamlessly with Azure DevOps (ADO) workflow and includes both real AI-powered fixes and simulation mode.

## 🎯 Features Implemented

### 1. **Enhanced Gemini CLI Agent** (`gemini_cli.py`)
- **AI-Powered Fixes**: Uses Google's Gemini AI to analyze and fix UX issues
- **Simulation Mode**: Fallback when AI is not available
- **ADO Integration**: Automatically updates work item status after fixes
- **Smart File Detection**: Automatically finds target files based on app type
- **Backup System**: Creates backups before applying fixes

### 2. **Fix with Agent Button** (Frontend)
- **Two-Button Workflow**:
  - **"Fix Now"**: Creates ADO work item and opens it
  - **"Fix with Agent"**: Triggers AI-powered code fix
- **Real-time Status**: Shows loading states and completion feedback
- **Error Handling**: Graceful error handling with user feedback

### 3. **Backend Integration** (`enhanced_fastapi_server.py`)
- **Enhanced `/api/ado/trigger-fix` endpoint**: Now uses real Gemini AI
- **Work Item Integration**: Fetches issue details from ADO
- **Comprehensive Logging**: Detailed logs for debugging

## 🚀 Setup Instructions

### 1. **Set Up Gemini API Token**
```bash
# Run the setup script
./set-gemini-token.sh

# Or manually set the environment variable
export GEMINI_TOKEN='your-gemini-api-token'
```

### 2. **Install Dependencies**
```bash
pip install google-generativeai
```

### 3. **Configure ADO Integration** (if not already done)
```bash
./set-ado-pat.sh
```

## 🔧 How It Works

### **Complete Workflow:**

1. **Issue Detection**: UX Analyzer detects issues in mock apps
2. **Report Generation**: Issues are documented with screenshots/videos
3. **Fix Now Button**: Creates ADO work item and opens it
4. **Fix with Agent Button**: 
   - Fetches work item details from ADO
   - Analyzes the issue using Gemini AI
   - Applies fixes to mock app files
   - Updates ADO work item status to "Resolved"
   - Provides feedback to user

### **AI Fix Process:**

#### **Real AI Mode** (when `GEMINI_TOKEN` is set):
1. **Analysis**: Gemini AI analyzes the current HTML/CSS/JS code
2. **Fix Generation**: AI generates improved code based on UX best practices
3. **Application**: Fixes are applied to the target file
4. **Backup**: Original file is backed up before changes

#### **Simulation Mode** (when `GEMINI_TOKEN` is not set):
1. **Predefined Fixes**: Applies common UX improvements
2. **Accessibility**: Adds ARIA labels and roles
3. **Visual Design**: Enhances styling and layout
4. **Interaction**: Improves user feedback and interactions

## 📁 File Structure

```
Craftbug_Agentic_System/
├── gemini_cli.py                    # Enhanced Gemini CLI Agent
├── gemini_cli_original.py           # Original coder agent files
├── coder_agent_server.py            # Coder agent server
├── set-gemini-token.sh              # Gemini token setup script
├── web-ui/
│   └── public/
│       └── mocks/                   # Target files for fixes
│           ├── word/
│           ├── excel/
│           └── powerpoint/
└── enhanced_fastapi_server.py       # Backend with agent integration
```

## 🎮 Usage

### **For Users:**

1. **Run Analysis**: Use the UX Analyzer to detect issues
2. **View Report**: Check the generated report with issues
3. **Click "Fix Now"**: Creates ADO work item and opens it
4. **Click "Fix with Agent"**: Triggers AI-powered fix
5. **Check Results**: View the fixed mock app

### **For Developers:**

1. **Set Environment Variables**:
   ```bash
   export GEMINI_TOKEN='your-token'
   export ADO_PAT='your-ado-pat'
   export ADO_ORGANIZATION='nayararushi0668'
   export ADO_PROJECT='CODER TEST'
   ```

2. **Test the Integration**:
   ```bash
   # Test Gemini CLI directly
   python gemini_cli.py 55  # Replace with actual work item ID
   ```

3. **Monitor Logs**: Check server logs for detailed information

## 🔍 Supported Fix Types

### **Accessibility Issues:**
- ARIA labels and roles
- Keyboard navigation
- Screen reader compatibility

### **Visual Design Issues:**
- Improved styling and layout
- Better color contrast
- Responsive design

### **Interaction Issues:**
- Enhanced user feedback
- Better button states
- Improved form handling

### **Performance Issues:**
- Optimized code structure
- Better resource loading
- Improved responsiveness

## 🛠️ Configuration Options

### **Environment Variables:**
- `GEMINI_TOKEN`: Google Gemini API token
- `ADO_PAT`: Azure DevOps Personal Access Token
- `ADO_ORGANIZATION`: ADO organization name
- `ADO_PROJECT`: ADO project name

### **File Mapping:**
- **Word**: `web-ui/public/mocks/word/`
- **Excel**: `web-ui/public/mocks/excel/`
- **PowerPoint**: `web-ui/public/mocks/powerpoint/`

## 🚨 Error Handling

### **Common Issues:**

1. **Gemini Token Not Set**:
   - System falls back to simulation mode
   - No real AI fixes applied
   - Predefined improvements still work

2. **ADO Integration Issues**:
   - Work item creation may fail
   - Status updates may not work
   - Fixes still apply to local files

3. **File Not Found**:
   - System logs the error
   - User gets feedback
   - No changes applied

## 📊 Monitoring and Logging

### **Server Logs:**
- Detailed fix process logging
- AI response tracking
- Error reporting
- Performance metrics

### **User Feedback:**
- Success/failure alerts
- Fix method indication
- Progress indicators
- Error messages

## 🔄 Future Enhancements

### **Planned Features:**
1. **Git Integration**: Automatic commits and pushes
2. **User Approval**: Approval workflow before changes
3. **Multiple File Support**: Fix multiple files at once
4. **Advanced AI Models**: Support for other AI providers
5. **Fix History**: Track all applied fixes
6. **Rollback System**: Easy undo for applied fixes

### **Integration Points:**
1. **GitHub Actions**: Automated CI/CD integration
2. **Slack/Teams**: Notifications for fix completion
3. **Jira**: Alternative issue tracking
4. **Custom Webhooks**: Extensible notification system

## 🎯 Success Metrics

### **Key Performance Indicators:**
- Fix success rate
- Time to fix completion
- User satisfaction
- ADO work item resolution rate
- Code quality improvements

### **Quality Assurance:**
- Automated testing of fixes
- Code review integration
- Performance impact assessment
- Accessibility compliance checking

---

## 🚀 Quick Start

1. **Set up tokens**: `./set-gemini-token.sh` and `./set-ado-pat.sh`
2. **Start servers**: `python enhanced_fastapi_server.py`
3. **Run analysis**: Use the web UI to analyze mock apps
4. **Apply fixes**: Use "Fix with Agent" buttons
5. **Monitor results**: Check mock apps and ADO work items

The Coder Agent Integration is now ready for production use! 🎉
