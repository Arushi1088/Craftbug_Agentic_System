"""
Test Craft Bug Detection with Local File
"""
import requests
import json
import time

def test_craft_bug_local():
    """Test craft bug detection with a file:// URL"""
    
    # Use file path directly
    file_path = "file:///Users/arushitandon/Desktop/analyzer/web-ui/public/mocks/word/basic-doc.html"
    
    # API endpoint
    api_endpoint = "http://localhost:8000/api/analyze/craft-bugs"
    
    # Request payload
    payload = {
        "url": file_path,
        "headless": True,
        "categories": ["A", "B", "D", "E"]
    }
    
    print("🐛 Testing Craft Bug Detection with Local File")
    print(f"Target: {file_path}")
    print(f"API: {api_endpoint}")
    print("-" * 60)
    
    try:
        response = requests.post(
            api_endpoint,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        print(f"Response Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            analysis_id = result.get('analysis_id')
            print(f"✅ Analysis started: {analysis_id}")
            
            # Wait and check results
            for i in range(15):  # Wait longer for file analysis
                time.sleep(2)
                status_response = requests.get(f"http://localhost:8000/api/reports/{analysis_id}")
                if status_response.status_code == 200:
                    data = status_response.json()
                    status = data.get('status')
                    print(f"  Check {i+1}: {status}")
                    
                    if status == 'completed':
                        print("\n🎉 Analysis completed!")
                        
                        # Show craft bug results
                        craft_bugs = data.get('module_results', {}).get('craft_bug_detection', {})
                        if craft_bugs:
                            issues = craft_bugs.get('issues', [])
                            summary = craft_bugs.get('summary', {})
                            
                            print(f"📊 CRAFT BUG RESULTS:")
                            print(f"Total Bugs Found: {summary.get('total_bugs', 0)}")
                            print(f"Analysis Duration: {summary.get('analysis_duration', 0):.2f}s")
                            
                            if issues:
                                print(f"\n🐛 DETECTED CRAFT BUGS:")
                                for i, issue in enumerate(issues, 1):
                                    print(f"{i}. [{issue.get('category')}] {issue.get('type')}")
                                    print(f"   Severity: {issue.get('severity')}")
                                    print(f"   Description: {issue.get('description')}")
                                    print()
                            else:
                                print("⚠️ No craft bugs detected (might be a detection issue)")
                        break
                    elif status == 'failed':
                        print(f"❌ Analysis failed: {data.get('error')}")
                        break
                        
        else:
            print(f"❌ API Error: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_craft_bug_local()
