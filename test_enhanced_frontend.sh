#!/bin/bash

# Test script for enhanced frontend analytics display
# This script helps debug the report display issue

echo "🔍 Testing Enhanced Frontend Analytics Display"
echo "=============================================="

cd /Users/arushitandon/Desktop/analyzer

# Start the frontend dev server if not already running
echo "📊 Starting frontend dev server..."
cd web-ui

# Check if npm is available and install dependencies if needed
if command -v npm &> /dev/null; then
    if [ ! -d "node_modules" ]; then
        echo "📦 Installing dependencies..."
        npm install
    fi
    
    echo "🚀 Starting development server..."
    echo "ℹ️  This will open the frontend with enhanced debugging capabilities"
    echo "ℹ️  Navigate to /report/sample to see the enhanced sample report"
    echo "ℹ️  Debug controls will be visible in development mode"
    echo ""
    echo "Expected features:"
    echo "  ✅ Enhanced sample report with 7 analytics modules"
    echo "  ✅ Debug controls panel (development mode only)"
    echo "  ✅ Module breakdown with findings and scores"
    echo "  ✅ ADO integration metadata display"
    echo "  ✅ Proper module icons and names"
    echo ""
    echo "Press Ctrl+C to stop the server"
    echo ""
    
    npm run dev
else
    echo "❌ npm not found. Please install Node.js and npm first."
    echo "   You can install from: https://nodejs.org/"
    exit 1
fi
