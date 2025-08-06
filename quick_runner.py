#!/usr/bin/env python3
"""
🎯 Quick Test Runner - Handles paths automatically
Run this from any directory
"""

import os
import sys
import subprocess

def run_test():
    # Set the correct working directory
    project_dir = "/Users/arushitandon/Desktop/UIUX analyzer/ux-analyzer"
    
    print(f"🎯 QUICK TEST RUNNER")
    print(f"📁 Working directory: {project_dir}")
    
    if not os.path.exists(project_dir):
        print(f"❌ Project directory not found: {project_dir}")
        return False
    
    # Change to the correct directory
    os.chdir(project_dir)
    print(f"✅ Changed to project directory")
    
    # Run the fresh test
    try:
        print(f"🚀 Running fresh_test.py...")
        result = subprocess.run([sys.executable, "fresh_test.py"], 
                              capture_output=False, 
                              text=True)
        return result.returncode == 0
    except Exception as e:
        print(f"❌ Error running test: {e}")
        return False

if __name__ == "__main__":
    success = run_test()
    if success:
        print(f"\n✅ Test completed successfully!")
    else:
        print(f"\n❌ Test had issues")
