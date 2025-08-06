#!/usr/bin/env python3
"""
Manual test script to simulate /fix-now comment trigger
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from comment_trigger import CommentTriggerListener

def test_trigger():
    """Test the comment trigger system manually"""
    print("🧪 Testing Comment Trigger System...")
    
    listener = CommentTriggerListener()
    
    # Get active work items
    work_items = listener.get_active_work_items()
    print(f"📋 Found {len(work_items)} active work items: {work_items[:5]}")
    
    if work_items:
        # Test with the first work item
        test_work_item = work_items[0]
        print(f"🎯 Testing with work item #{test_work_item}")
        
        # Manually trigger the fix
        print("🚨 Manually triggering fix (simulating /fix-now comment)...")
        listener.trigger_orchestrator_fix(test_work_item)
        
        print("✅ Test completed!")
    else:
        print("❌ No active work items found to test with")

if __name__ == "__main__":
    test_trigger()
