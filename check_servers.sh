#!/bin/bash

echo "🔍 Checking UX Analyzer System Status..."
echo "============================================"

# Function to check if a URL is responding
check_url() {
    local url=$1
    local name=$2
    local response=$(curl -s -w "%{http_code}" -o /dev/null "$url" 2>/dev/null)
    
    if [ "$response" = "200" ]; then
        echo "✅ $name: Running (HTTP $response)"
        return 0
    else
        echo "❌ $name: Not responding (HTTP $response)"
        return 1
    fi
}

# Check Backend API
check_url "http://127.0.0.1:8000/" "Backend API (127.0.0.1:8000)"

# Check Frontend Dashboard  
check_url "http://127.0.0.1:8080/" "Dashboard (127.0.0.1:8080)"

# Check Mock Apps
check_url "http://localhost:4174/" "Mock Apps (localhost:4174)"

echo ""
echo "🧪 Testing API Functionality..."

# Test scenarios endpoint
scenarios=$(curl -s "http://127.0.0.1:8000/api/scenarios" 2>/dev/null | jq -r '.scenarios | length' 2>/dev/null)
if [ "$scenarios" ] && [ "$scenarios" -gt 0 ]; then
    echo "✅ Scenarios API: $scenarios scenarios available"
else
    echo "❌ Scenarios API: Not working"
fi

# Test existing report
report_status=$(curl -s "http://127.0.0.1:8000/api/reports/67a67490" 2>/dev/null | jq -r '.status' 2>/dev/null)
if [ "$report_status" = "completed" ]; then
    echo "✅ Reports API: Working (test report accessible)"
else
    echo "❌ Reports API: Issue with test report"
fi

echo ""
echo "🔗 Quick Access Links:"
echo "   Dashboard: http://127.0.0.1:8080/"
echo "   Working Report: http://127.0.0.1:8080/reports/67a67490"
echo "   New Report: http://127.0.0.1:8080/reports/3fa3cabb"
echo "   API Status: http://127.0.0.1:8000/"
