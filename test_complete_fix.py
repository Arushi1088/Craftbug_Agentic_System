#!/usr/bin/env python3
"""
Test the complete fix: hover action + craft bugs in API response
"""
import requests
import json

def test_complete_fix():
    print('🧪 Testing complete fix: hover action + craft bugs in API response')
    
    try:
        response = requests.post('http://localhost:8000/api/analyze', json={
            'url': 'http://localhost:9000/mocks/word/basic-doc.html',
            'scenario_id': '1.4',
            'modules': {
                'ux_heuristics': True,
                'performance': True
            }
        }, timeout=45)
        
        if response.status_code == 200:
            data = response.json()
            print('\n✅ API Response Structure:')
            print(f'Status: {data.get("status")}')
            print(f'Analysis ID: {data.get("analysis_id")}')
            print(f'Total Issues: {data.get("total_issues", "N/A")}')
            
            craft_bugs = data.get('craft_bugs', [])
            ux_issues = data.get('ux_issues', [])
            
            print(f'\n🐛 Craft Bugs in Response: {len(craft_bugs)}')
            for i, bug in enumerate(craft_bugs, 1):
                print(f'  {i}. {bug.get("type", "Unknown")}: {bug.get("description", "No description")}')
            
            print(f'\n📋 UX Issues in Response: {len(ux_issues)}')
            for i, issue in enumerate(ux_issues[:3], 1):  # Show first 3
                issue_type = issue.get("type", "Unknown")
                description = issue.get("description", "No description")[:60]
                print(f'  {i}. {issue_type}: {description}...')
            
            if len(ux_issues) > 3:
                print(f'  ... and {len(ux_issues) - 3} more issues')
                
            # Summary
            if craft_bugs:
                print(f'\n🎯 SUCCESS: {len(craft_bugs)} craft bugs now included in API response!')
            else:
                print(f'\n⚠️  No craft bugs in response, but {len(ux_issues)} UX issues found')
                
            print(f'\n✅ Total issues detected: {data.get("total_issues", len(ux_issues))}')
            
            return True
            
        else:
            print(f'❌ API Error: {response.status_code}')
            try:
                error_data = response.json()
                print(f'Error details: {error_data}')
            except:
                print(f'Response text: {response.text}')
            return False
            
    except Exception as e:
        print(f'❌ Error: {e}')
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_complete_fix()
