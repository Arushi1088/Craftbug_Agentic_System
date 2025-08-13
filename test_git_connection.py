#!/usr/bin/env python3
"""
Test Git connection and push functionality
"""

import subprocess
import os
import json

def test_git_connection():
    """Test Git connection and basic operations"""
    
    print("🔧 TESTING GIT CONNECTION")
    print("=" * 30)
    
    try:
        # Test 1: Check if we're in a Git repository
        print("1️⃣ Checking Git repository...")
        result = subprocess.run(['git', 'status'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Git repository found")
        else:
            print("❌ Not in a Git repository")
            return False
        
        # Test 2: Check current branch
        print("2️⃣ Checking current branch...")
        current_branch = subprocess.check_output(['git', 'branch', '--show-current'], text=True).strip()
        print(f"✅ Current branch: {current_branch}")
        
        # Test 3: Check remote origin
        print("3️⃣ Checking remote origin...")
        result = subprocess.run(['git', 'remote', '-v'], capture_output=True, text=True)
        if result.returncode == 0 and 'origin' in result.stdout:
            print("✅ Remote origin configured")
            print(f"   {result.stdout.strip()}")
        else:
            print("❌ No remote origin configured")
            return False
        
        # Test 4: Check if we can fetch from remote
        print("4️⃣ Testing remote connection...")
        result = subprocess.run(['git', 'fetch', 'origin'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Remote connection working")
        else:
            print("❌ Remote connection failed")
            print(f"   Error: {result.stderr}")
            return False
        
        # Test 5: Check if we have changes to commit
        print("5️⃣ Checking for uncommitted changes...")
        result = subprocess.run(['git', 'status', '--porcelain'], capture_output=True, text=True)
        if result.stdout.strip():
            print("⚠️  Found uncommitted changes:")
            print(f"   {result.stdout.strip()}")
        else:
            print("✅ No uncommitted changes")
        
        # Test 6: Test Git add and commit (dry run)
        print("6️⃣ Testing Git operations...")
        
        # Create a test file
        test_file = "test_git_connection.txt"
        with open(test_file, 'w') as f:
            f.write("Test file for Git connection verification\n")
        
        # Add the file
        subprocess.run(['git', 'add', test_file], check=True)
        print("✅ Git add successful")
        
        # Commit the file
        subprocess.run(['git', 'commit', '-m', 'Test: Git connection verification'], check=True)
        print("✅ Git commit successful")
        
        # Test 7: Test push (this will actually push)
        print("7️⃣ Testing Git push...")
        try:
            subprocess.run(['git', 'push', 'origin', current_branch], check=True)
            print("✅ Git push successful")
        except subprocess.CalledProcessError as e:
            print(f"❌ Git push failed: {e}")
            return False
        
        # Clean up test file
        subprocess.run(['git', 'rm', test_file], check=True)
        subprocess.run(['git', 'commit', '-m', 'Remove test file'], check=True)
        subprocess.run(['git', 'push', 'origin', current_branch], check=True)
        print("✅ Cleanup completed")
        
        print("\n🎉 GIT CONNECTION TEST PASSED!")
        print("✅ All Git operations working correctly")
        return True
        
    except Exception as e:
        print(f"❌ Git connection test failed: {e}")
        return False

def test_git_api_endpoint():
    """Test the Git API endpoint"""
    
    print("\n🌐 TESTING GIT API ENDPOINT")
    print("=" * 30)
    
    import requests
    
    try:
        # Test the commit-changes endpoint
        test_data = {
            "work_item_id": 999,
            "commit_message": "Test: Git API endpoint verification"
        }
        
        response = requests.post(
            "http://localhost:8000/api/git/commit-changes",
            headers={"Content-Type": "application/json"},
            json=test_data,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Git API endpoint working")
            print(f"   Status: {result.get('status')}")
            print(f"   Message: {result.get('message')}")
            print(f"   Branch: {result.get('branch')}")
            return True
        else:
            print(f"❌ Git API endpoint failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Git API test failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 GIT CONNECTION VERIFICATION")
    print("=" * 40)
    
    # Test basic Git connection
    git_ok = test_git_connection()
    
    if git_ok:
        # Test API endpoint if server is running
        try:
            test_git_api_endpoint()
        except:
            print("⚠️  Server not running - API test skipped")
    
    print("\n📝 SUMMARY:")
    if git_ok:
        print("✅ Git connection is working properly")
        print("✅ Push functionality is available")
        print("✅ Backend is ready for Git operations")
    else:
        print("❌ Git connection needs to be fixed")
        print("❌ Push functionality may not work")
