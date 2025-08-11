# 🎯 DASHBOARD TESTING GUIDE

## ✅ System Status
- ✅ Backend API: http://localhost:8000 (Running)
- ✅ Dashboard: http://localhost:8080 (Open in VS Code)
- ✅ Chromium Browser: Ready for automation
- ✅ Craft Bug Detection: Enabled

## 🧪 Test Word Scenarios

### Available Word Mock URLs:
1. **Basic Document (with craft bugs)**: `http://localhost:8080/mocks/word/basic-doc.html`
2. **Clean Document (no bugs)**: `http://localhost:8080/mocks/word/basic-doc-clean.html`

### Available Scenario IDs:
- `1.1` - Basic Document Navigation
- `1.2` - Comment Resolution Workflow  
- `1.3` - Document Formatting Tasks
- `1.4` - Collaborative Review Process
- `1.5` - Interactive Craft Bug Testing (triggers animations & input lag)

## 🎮 How to Test:

### Option 1: Use the Dashboard (Recommended)
1. Dashboard is open at: http://localhost:8080
2. Enter URL: `http://localhost:8080/mocks/word/basic-doc.html`
3. Select Scenario: `1.1` or `1.5` (for craft bugs)
4. Enable modules: Performance, Accessibility, UX Heuristics
5. Click "Analyze" and watch Chromium open!

### Option 2: Direct API Testing
```bash
curl -X POST "http://localhost:8000/api/analyze" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "http://localhost:8080/mocks/word/basic-doc.html",
    "scenario_id": "1.5", 
    "modules": {
      "performance": true,
      "accessibility": true, 
      "ux_heuristics": true
    }
  }'
```

## 🐛 Expected Craft Bugs to Find:
- **Animation Conflicts**: CSS animations that conflict (medium severity)
- **Input Lag**: Delayed response on interactive elements
- **Layout Thrash**: Excessive layout recalculations
- **Missing Hover States**: Buttons without proper feedback

## 📊 What You'll See:
1. **Chromium browser opens** (visible window)
2. **Real automation** clicking through Word interface
3. **Craft bug metrics** collected during interactions
4. **Detailed report** with detected issues
5. **Performance metrics** from real browser execution

## 🔍 Test Analysis ID: `55deceac`
You can view this test report at: http://localhost:8000/api/reports/55deceac

Ready to test! 🚀
