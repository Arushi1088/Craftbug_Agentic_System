"""
Test Craft Bug Detection API Integration
"""
import requests
import json
import time

def test_craft_bug_api():
    """Test the craft bug detection API endpoint"""
    
    # Test URL - use our enhanced Word mock
    test_url = "http://localhost:4173/mocks/word/basic-doc.html"
    
    # API endpoint
    api_endpoint = "http://localhost:8000/api/analyze/craft-bugs"
    
    # Request payload
    payload = {
        "url": test_url,
        "headless": True,
        "categories": ["A", "B", "D", "E"]
    }
    
    print("🐛 Testing Craft Bug Detection API")
    print(f"Target URL: {test_url}")
    print(f"API Endpoint: {api_endpoint}")
    print("-" * 50)
    
    try:
        # Make API request
        print("📡 Sending API request...")
        response = requests.post(
            api_endpoint,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        print(f"Response Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Analysis started successfully!")
            print(f"Analysis ID: {result.get('analysis_id')}")
            print(f"Status: {result.get('status')}")
            
            # If analysis is processing, wait for completion
            if result.get('status') == 'processing':
                analysis_id = result.get('analysis_id')
                print(f"⏳ Waiting for analysis to complete...")
                
                # Poll for results
                for i in range(10):  # Max 30 seconds wait
                    time.sleep(3)
                    status_response = requests.get(f"http://localhost:8000/api/reports/{analysis_id}")
                    if status_response.status_code == 200:
                        status_data = status_response.json()
                        if status_data.get('status') == 'completed':
                            print("✅ Analysis completed!")
                            
                            # Check craft bug results
                            craft_bugs = status_data.get('module_results', {}).get('craft_bug_detection', {})
                            if craft_bugs:
                                issues = craft_bugs.get('issues', [])
                                print(f"🐛 Found {len(issues)} craft bugs:")
                                for issue in issues[:3]:  # Show first 3
                                    print(f"  - [{issue.get('category')}] {issue.get('type')}: {issue.get('description')}")
                            break
                    print(f"  Status check {i+1}/10...")
                
        else:
            print(f"❌ API request failed: {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Network error: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

if __name__ == "__main__":
    test_craft_bug_api()
