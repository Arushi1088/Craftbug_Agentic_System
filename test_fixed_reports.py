#!/usr/bin/env python3
"""
Test script to verify the fixed reports work correctly
"""

import requests
import json

def test_fixed_report():
    """Test accessing a fixed failed report"""
    try:
        # First start the server (we'll need to do this manually)
        print("🔍 Testing fixed report access...")
        
        # Test the health endpoint first
        try:
            health_response = requests.get("http://localhost:8000/health", timeout=5)
            if health_response.status_code == 200:
                print("✅ Server is running")
            else:
                print("❌ Server health check failed")
                return
        except:
            print("❌ Server not accessible - please start enhanced_fastapi_server.py")
            return
        
        # Test accessing the fixed report
        report_id = "3a044ae2"
        response = requests.get(f"http://localhost:8000/api/reports/{report_id}", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Report retrieved successfully!")
            print(f"   Analysis ID: {data.get('analysis_id')}")
            print(f"   Status: {data.get('status')}")
            print(f"   Module Results: {list(data.get('module_results', {}).keys())}")
            
            if 'module_results' in data and 'error_report' in data['module_results']:
                error_module = data['module_results']['error_report']
                print(f"   Error Module Title: {error_module.get('title')}")
                print(f"   Error Findings: {len(error_module.get('findings', []))}")
                print("✅ Error report has proper module structure!")
            else:
                print("❌ Module results not found or improperly structured")
                
        else:
            print(f"❌ Failed to retrieve report: {response.status_code}")
            print(f"   Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Test failed: {e}")

def test_report_list():
    """Test the reports list endpoint"""
    try:
        response = requests.get("http://localhost:8000/api/reports", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Reports list retrieved: {len(data.get('reports', []))} reports")
        else:
            print(f"❌ Reports list failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Reports list test failed: {e}")

if __name__ == "__main__":
    test_fixed_report()
    test_report_list()
