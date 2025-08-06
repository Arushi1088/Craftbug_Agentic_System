#!/usr/bin/env python3
"""
Test Runner for Buggy E-Commerce Application
This script will demonstrate the bugs before AI fixes them
"""

import subprocess
import time
import requests
import threading
import sys

def run_app():
    """Run the buggy application"""
    try:
        subprocess.run([sys.executable, 'buggy_ecommerce_app.py'], check=True)
    except KeyboardInterrupt:
        print("\n🛑 Application stopped")
    except Exception as e:
        print(f"❌ Application error: {e}")

def test_endpoints():
    """Test various endpoints to trigger bugs"""
    base_url = "http://localhost:5001"
    
    # Wait for server to start
    time.sleep(3)
    
    print("🧪 Testing application endpoints...")
    
    test_cases = [
        {"url": f"{base_url}/", "description": "Home page (should work initially)"},
        {"url": f"{base_url}/products", "description": "Products page (may have SQL issues)"},
        {"url": f"{base_url}/product/1", "description": "Product detail (likely to crash)"},
        {"url": f"{base_url}/cart", "description": "Cart view (NoneType errors expected)"},
        {"url": f"{base_url}/admin", "description": "Admin panel (division by zero)"},
    ]
    
    for test in test_cases:
        try:
            print(f"\n📍 Testing: {test['description']}")
            response = requests.get(test['url'], timeout=5)
            if response.status_code == 200:
                print(f"✅ Status: {response.status_code}")
                if "Error" in response.text:
                    print("⚠️ Page loaded but contains error messages")
            else:
                print(f"❌ Status: {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"💥 Request failed: {e}")
        except Exception as e:
            print(f"🐛 Unexpected error: {e}")
    
    print("\n🎯 Test Results Summary:")
    print("The application likely shows multiple errors due to intentional bugs.")
    print("This is expected behavior for AI agent testing!")

if __name__ == '__main__':
    print("🚀 Starting Buggy E-Commerce Application Test")
    print("This will run the application and test for bugs...")
    
    # Start the Flask app in a separate thread
    app_thread = threading.Thread(target=run_app, daemon=True)
    app_thread.start()
    
    # Run tests
    test_endpoints()
    
    print("\n💡 To manually test the application:")
    print("1. Keep this script running")
    print("2. Open http://localhost:5001 in your browser")
    print("3. Navigate through the pages to see the bugs")
    print("4. Press Ctrl+C to stop")
    
    try:
        # Keep the main thread alive
        app_thread.join()
    except KeyboardInterrupt:
        print("\n👋 Test session ended")
