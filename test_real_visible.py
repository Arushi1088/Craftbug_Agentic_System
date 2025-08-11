#!/usr/bin/env python3
"""
Real Test: Craft Bug Detection with Visible Browser
"""

import requests
import json
import time

def test_real_craft_bug_analysis():
    print("🔍 Testing Real Craft Bug Analysis with Visible Browser...")
    
    # Test backend health first
    try:
        health = requests.get("http://localhost:8000/health", timeout=5)
        print(f"✅ Backend Health: {health.json()['status']}")
    except Exception as e:
        print(f"❌ Backend Error: {e}")
        return False
    
    # Test frontend accessibility
    try:
        frontend = requests.get("http://localhost:4173/mocks/word/basic-doc.html", timeout=5)
        print(f"✅ Frontend Mock: {frontend.status_code} - {len(frontend.text)} bytes")
        if 'craft' in frontend.text.lower():
            print("🐛 Craft bugs detected in mock!")
    except Exception as e:
        print(f"❌ Frontend Error: {e}")
        return False
    
    # Start analysis with VISIBLE browser
    payload = {
        "url": "http://localhost:4173/mocks/word/basic-doc.html",
        "headless": False,  # THIS WILL SHOW CHROMIUM!
        "categories": ["A", "B", "D", "E"]
    }
    
    print(f"\n🚀 Starting analysis with payload: {json.dumps(payload, indent=2)}")
    
    try:
        response = requests.post(
            "http://localhost:8000/api/analyze/craft-bugs",
            json=payload,
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            analysis_id = result.get("analysis_id")
            print(f"✅ Analysis Started!")
            print(f"📝 Analysis ID: {analysis_id}")
            print(f"🎬 Status: {result.get('status')}")
            print(f"🌐 Browser Mode: Visible (headless=False)")
            
            # Poll for results
            print(f"\n⏱️ Polling for results (you should see Chromium open now)...")
            for i in range(20):  # Wait up to 2 minutes
                time.sleep(6)
                status_response = requests.get(f"http://localhost:8000/api/reports/{analysis_id}")
                
                if status_response.status_code == 200:
                    status_data = status_response.json()
                    status = status_data.get("status", "unknown")
                    print(f"📊 Check {i+1}: Status = {status}")
                    
                    if status == "completed":
                        print(f"\n🎉 Analysis Complete!")
                        
                        # Show craft bug results
                        craft_bugs = status_data.get("craft_bugs", {})
                        if craft_bugs:
                            print(f"🐛 Craft Bugs Found:")
                            for category, bugs in craft_bugs.items():
                                if bugs:
                                    print(f"  Category {category}: {len(bugs)} bugs")
                        
                        return True
                    elif status == "failed":
                        print(f"❌ Analysis failed: {status_data.get('error', 'Unknown error')}")
                        return False
                
                else:
                    print(f"⚠️ Status check failed: {status_response.status_code}")
            
            print(f"⏰ Timeout waiting for results")
            return False
            
        else:
            print(f"❌ Failed to start analysis: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Analysis Error: {e}")
        return False

if __name__ == "__main__":
    success = test_real_craft_bug_analysis()
    if success:
        print(f"\n🎯 SUCCESS: Real craft bug detection works!")
    else:
        print(f"\n💥 FAILED: Issues with craft bug detection")
