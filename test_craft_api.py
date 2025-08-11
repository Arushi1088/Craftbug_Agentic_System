"""
Test script for craft bug detection API endpoint
"""
import requests
import json
import time

def test_craft_bug_api():
    """Test the new craft bug analysis endpoint"""
    
    # API endpoint
    base_url = "http://127.0.0.1:8000"
    endpoint = f"{base_url}/api/analyze/craft-bugs"
    
    # Test data
    test_request = {
        "url": "http://127.0.0.1:9000/mocks/word/basic-doc.html",
        "headless": True,
        "categories": ["A", "B", "D", "E"]
    }
    
    print(f"🧪 Testing Craft Bug API: {endpoint}")
    print(f"📋 Request data: {json.dumps(test_request, indent=2)}")
    
    try:
        # Start analysis
        response = requests.post(endpoint, json=test_request)
        
        if response.status_code == 200:
            result = response.json()
            analysis_id = result.get("analysis_id")
            print(f"✅ Analysis started successfully!")
            print(f"📊 Analysis ID: {analysis_id}")
            print(f"📊 Status: {result.get('status')}")
            print(f"📊 Message: {result.get('message')}")
            
            # Poll for results
            status_endpoint = f"{base_url}/api/analysis/{analysis_id}/status"
            
            print(f"\n⏳ Polling for results...")
            max_attempts = 30
            for attempt in range(max_attempts):
                time.sleep(2)
                
                status_response = requests.get(status_endpoint)
                if status_response.status_code == 200:
                    status_data = status_response.json()
                    status = status_data.get("status")
                    
                    print(f"  Attempt {attempt + 1}: {status}")
                    
                    if status == "completed":
                        print(f"\n🎉 Analysis completed!")
                        
                        # Get full results
                        results_endpoint = f"{base_url}/api/analysis/{analysis_id}"
                        results_response = requests.get(results_endpoint)
                        
                        if results_response.status_code == 200:
                            results = results_response.json()
                            print(f"\n📊 CRAFT BUG ANALYSIS RESULTS:")
                            print(f"{'='*50}")
                            print(f"Overall Score: {results.get('overall_score', 'N/A')}")
                            print(f"Total Issues: {results.get('total_issues', 'N/A')}")
                            
                            module_results = results.get('module_results', {})
                            craft_bug_module = module_results.get('craft_bug_detection', {})
                            
                            if craft_bug_module:
                                summary = craft_bug_module.get('summary', {})
                                print(f"\nCraft Bug Summary:")
                                print(f"  Total Bugs: {summary.get('total_bugs', 0)}")
                                print(f"  Bugs by Category: {summary.get('bugs_by_category', {})}")
                                print(f"  Analysis Duration: {summary.get('analysis_duration', 0):.2f}s")
                                
                                issues = craft_bug_module.get('issues', [])
                                if issues:
                                    print(f"\n🔍 Issues Found:")
                                    for i, issue in enumerate(issues, 1):
                                        print(f"  {i}. [{issue.get('category')}] {issue.get('type')}")
                                        print(f"     Severity: {issue.get('severity')}")
                                        print(f"     Description: {issue.get('description')}")
                                else:
                                    print(f"\n✅ No craft bugs detected!")
                        break
                    elif status == "failed":
                        print(f"\n❌ Analysis failed!")
                        error = status_data.get("error", "Unknown error")
                        print(f"Error: {error}")
                        break
            else:
                print(f"\n⏰ Timeout waiting for results")
        else:
            print(f"❌ API request failed: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error testing API: {e}")

if __name__ == "__main__":
    print("🐛 Testing Craft Bug Detection API")
    test_craft_bug_api()
