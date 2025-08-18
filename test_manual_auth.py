"""
Test script for Excel Web manual authentication
"""

import asyncio
import sys
from excel_web_manual_auth import get_manual_auth


async def test_manual_authentication():
    """Test the Excel Web manual authentication flow"""
    manual_auth = await get_manual_auth()
    
    try:
        print("🧪 Testing Excel Web Manual Authentication...")
        
        # Check for existing session first
        existing_session = await manual_auth.verify_existing_session()
        if existing_session:
            print("✅ Found existing valid session!")
            return True
        
        # Perform manual authentication
        session = await manual_auth.perform_manual_authentication(timeout_minutes=5)
        
        if session:
            print("✅ Manual authentication test passed!")
            print(f"📋 Session ID: {session.session_id}")
            return True
        else:
            print("❌ Manual authentication test failed")
            return False
            
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        return False


async def main():
    """Main test function"""
    print("🚀 Starting Excel Web Manual Authentication Test")
    print("=" * 60)
    
    success = await test_manual_authentication()
    
    print("=" * 60)
    if success:
        print("🎉 Manual authentication test passed!")
        print("✅ You can now use Excel Web automation!")
        sys.exit(0)
    else:
        print("💥 Manual authentication test failed!")
        print("❌ Please try again or check your credentials")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
