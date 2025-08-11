# Robust Scenario Pipeline Fixes - Implementation Summary

## 🚀 Overview
Fixed the `'NoneType' object has no attribute 'get'` error by implementing comprehensive error handling and scenario resolution throughout the analysis pipeline.

## 🔧 Key Fixes Implemented

### 1. Bulletproof Scenario Resolution (`utils/scenario_resolver.py`)
- **New utility**: `resolve_scenario()` handles all YAML formats:
  - Direct `{steps: [...]}` format
  - `{scenarios: [{id: "1.1", steps:[...]}]}` format  
  - Legacy `{tests: {Name: {scenarios:[{steps:[...]}]}}}` format
- **Guard functions**: `_ensure_dict()` and `validate_scenario_steps()` prevent None/invalid objects
- **Clear error messages**: File not found, invalid format, missing steps all have specific errors

### 2. Robust Error Handling in ScenarioExecutor (`scenario_executor.py`)
- **Never returns None**: All methods now return structured dict reports
- **Error reports**: Generate UI-compatible error reports with required fields:
  ```python
  {
    "analysis_id": "...",
    "status": "failed", 
    "error": "detailed error message",
    "ui_error": "user-friendly message",
    "module_results": {},
    "scenario_results": [],
    "overall_score": 0,
    "total_issues": 1
  }
  ```
- **New methods**: `_generate_error_report()`, `_generate_scenario_report_from_steps()`

### 3. Enhanced FastAPI Server Guards (`enhanced_fastapi_server.py`)
- **Updated normalize_report_schema()**: Robust schema normalization that handles:
  - None/invalid inputs → structured error reports
  - Failed reports → ensure UI compatibility  
  - Success reports → add missing required fields
- **Executor call guards**: All `scenario_executor.execute_*()` calls now:
  - Check return type is dict
  - Apply schema normalization
  - Generate structured error reports on failure
  - Save error reports to disk for debugging

### 4. Comprehensive Error Coverage
Updated all endpoints that call scenario executor:
- `/api/analyze/enhanced`
- `/api/analyze/url-scenario` 
- `/api/analyze/mock-scenario`
- Background analysis tasks
- Custom scenario endpoints

## 🧪 Testing & Validation

### Test Suite (`test_robust_fixes.py`)
- ✅ Scenario resolver handles all formats
- ✅ FileNotFoundError for missing files
- ✅ RuntimeError for None objects
- ✅ Executor returns structured error reports
- ✅ Schema normalization works correctly

### End-to-End Test (`test_end_to_end.py`)
- ✅ Real API calls with known-good scenarios
- ✅ Report retrieval and validation
- ✅ Error handling verification

## 🎯 Before vs After

### Before (Error-Prone)
```python
# Scenario executor could return None
report_data = scenario_executor.execute_url_scenario(...)
# Later code assumes dict
score = report_data.get("overall_score")  # 💥 AttributeError if None
```

### After (Bulletproof)
```python
# Scenario executor always returns dict
report_data = scenario_executor.execute_url_scenario(...)
# Guard against invalid types
if not isinstance(report_data, dict):
    raise RuntimeError("Invalid executor response")
# Apply schema normalization  
report_data = normalize_report_schema(report_data)
# Now safe to use
score = report_data.get("overall_score", 0)  # ✅ Always works
```

## 📋 Recommended Quick Test

1. **Start the server**:
   ```bash
   python3 enhanced_fastapi_server.py
   ```

2. **Test with a known scenario**:
   ```bash
   curl -X POST 'http://localhost:8000/api/analyze/url-scenario' \
     -H 'Content-Type: application/json' \
     -d '{
       "url": "http://localhost:3001/mocks/word/basic-doc.html",
       "scenario_path": "scenarios/word_scenarios.yaml", 
       "modules": {"performance":true,"accessibility":true}
     }'
   ```

3. **Check the report**:
   ```bash
   curl http://localhost:8000/api/reports/<analysis_id>
   ```

The UI should now show proper red "Analysis Failed" banners for any errors instead of blank pages.

## 🔍 Debugging Failed Analyses

If analyses still fail:

1. **Check server logs** for the exact error and stack trace
2. **Verify scenario file format** using `utils/scenario_resolver.py`
3. **Test scenario file directly**:
   ```python
   from utils.scenario_resolver import resolve_scenario
   scenario = resolve_scenario("path/to/scenario.yaml")
   print(json.dumps(scenario, indent=2))
   ```
4. **Check mock URL substitution** - ensure `{mock_url}` placeholders are replaced
5. **Verify browser/Playwright installation** if using realistic mode

The robust pipeline now provides clear error messages at each step to help identify the exact failure point.
