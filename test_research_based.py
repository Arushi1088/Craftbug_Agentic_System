#!/usr/bin/env python3
"""
Test script for research-based Excel Web navigator
"""

import asyncio
from excel_web_research_based import get_research_based_navigator
import time

async def test_research_based_navigator():
    """Test the research-based Excel Web navigator"""
    
    print("🧪 Testing Research-based Excel Web Navigator...")
    
    # Get navigator
    navigator = await get_research_based_navigator()
    
    try:
        # Initialize
        if not await navigator.initialize():
            print("❌ Failed to initialize navigator")
            return
        
        # Navigate and create workbook
        if not await navigator.navigate_to_excel_and_create_workbook():
            print("❌ Failed to navigate and create workbook")
            return
        
        print("✅ Successfully navigated to Excel and created workbook")
        
        # Take a screenshot
        screenshot_path = f"screenshots/excel_web/research_based_test_{int(time.time())}.png"
        navigator.driver.save_screenshot(screenshot_path)
        print(f"📸 Screenshot saved: {screenshot_path}")
        
        # Try to find cells
        cells = navigator.find_excel_cells()
        if cells:
            print(f"✅ Found {len(cells)} cells")
            
            # Try to click a cell
            if await navigator.click_cell(0):
                print("✅ Successfully clicked cell")
                
                # Try to enter data
                if navigator.enter_data_in_cell("Test Data"):
                    print("✅ Successfully entered data")
                else:
                    print("❌ Failed to enter data")
            else:
                print("❌ Failed to click cell")
        else:
            print("❌ No cells found")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Close browser
        try:
            navigator.close()
            print("✅ Browser closed")
        except:
            pass

if __name__ == "__main__":
    asyncio.run(test_research_based_navigator())

