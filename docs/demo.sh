#!/usr/bin/env bash
# UX Analyzer Demo Script
# Demonstrates all major functionality of the UX Analyzer system

echo "🎯 UX ANALYZER DEMO SCRIPT"
echo "========================================="
echo ""

# Ensure we're in the right directory
cd "$(dirname "$0")/.."

echo "📁 Current directory: $(pwd)"
echo ""

echo "=== CLI URL Analysis (JSON + HTML) ==="
echo "🔍 Analyzing example.com with JSON and HTML outputs..."
python3 bin/ux-analyze url-scenario https://example.com scenarios/office_tests.yaml --json_out --output_dir demos/

echo ""
echo "=== CLI Mock App Analysis ==="
echo "🔍 Analyzing mock Office app with scenario testing..."
python3 bin/ux-analyze mock-scenario mock-apps/office.json scenarios/office_tests.yaml --output_dir demos/

echo ""
echo "=== Scenario Validation ==="
echo "🔍 Validating YAML scenario files..."
python3 bin/ux-analyze validate scenarios/office_tests.yaml

echo ""
echo "=== List Available Scenarios ==="
echo "📋 Available YAML scenarios:"
python3 bin/ux-analyze list-scenarios

echo ""
echo "=== Golden File Testing ==="
echo "🧪 Running comprehensive test suite..."
python3 -m pytest tests/test_golden.py -v --tb=short

echo ""
echo "=== API Server Demo ==="
echo "🚀 Starting FastAPI server for API testing..."
echo "   Visit http://localhost:8000/docs for API documentation"
echo "   Use Ctrl+C to stop the server"
echo ""

# Start the production server
python3 production_server.py
