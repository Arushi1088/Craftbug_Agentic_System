#!/usr/bin/env python3
"""
Final Comprehensive Excel Web Solution
Combines authentication with proper Office 365 Excel iframe detection
"""

import asyncio
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from excel_web_selenium_only import get_selenium_navigator

class FinalExcelWebNavigator:
    """Final Excel Web Navigator with authentication and proper iframe handling"""
    
    def __init__(self):
        self.navigator = None
        self.driver = None
        
    async def initialize(self):
        """Initialize using the existing authenticated navigator"""
        try:
            # Use the existing navigator that handles authentication
            self.navigator = await get_selenium_navigator()
            
            if not await self.navigator.initialize():
                print("❌ Failed to initialize navigator")
                return False
            
            if not await self.navigator.ensure_authenticated():
                print("❌ Failed to authenticate")
                return False
            
            self.driver = self.navigator.driver
            print("✅ Final Excel Web Navigator initialized with authentication")
            return True
            
        except Exception as e:
            print(f"❌ Failed to initialize: {e}")
            return False
    
    async def navigate_and_create_workbook(self):
        """Navigate to Excel and create workbook with proper iframe handling"""
        try:
            # Navigate to Excel Web using existing method
            await self.navigator.navigate_to_excel_web()
            print("✅ Navigated to Excel Web")
            
            # Wait for page to load
            await asyncio.sleep(5)
            
            # Click "Blank workbook" - this triggers Excel app loading
            try:
                blank_workbook = self.driver.find_element("xpath", "//span[contains(text(), 'Blank workbook')]")
                blank_workbook.click()
                print("✅ Clicked 'Blank workbook'")
            except Exception as e:
                print(f"❌ Failed to click 'Blank workbook': {e}")
                return False
            
            # Wait for Excel app to start loading
            await asyncio.sleep(10)
            
            # Now wait for the Excel iframe to appear
            excel_iframe = await self.wait_for_excel_iframe()
            if not excel_iframe:
                print("❌ Excel iframe never appeared")
                return False
            
            # Switch to Excel iframe
            self.driver.switch_to.frame(excel_iframe)
            print("✅ Switched to Excel iframe")
            
            # Wait for Excel interface to fully load
            await self.wait_for_excel_interface()
            
            return True
            
        except Exception as e:
            print(f"❌ Failed to navigate and create workbook: {e}")
            return False
    
    async def wait_for_excel_iframe(self, timeout=60):
        """Wait for the Excel iframe to appear after clicking 'Blank workbook'"""
        print("⏳ Waiting for Excel iframe to appear...")
        
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                # Find all iframes
                iframes = self.driver.find_elements("css selector", "iframe")
                print(f"📋 Found {len(iframes)} iframes")
                
                for i, iframe in enumerate(iframes):
                    try:
                        src = iframe.get_attribute("src")
                        print(f"  Iframe {i}: {src}")
                        
                        # Look for Excel iframe patterns
                        if src and any(pattern in src.lower() for pattern in [
                            "excel.office.com",
                            "excel.officeapps.live.com",
                            "webshell.suite.office.com/excel",
                            "officeapps.live.com/excel",
                            "excel.officeapps.live.com/we/weframe.aspx",
                            "excel.officeapps.live.com/we/weframe"
                        ]):
                            print(f"✅ Found Excel iframe at index {i}: {src}")
                            return iframe
                    except:
                        continue
                
                await asyncio.sleep(3)
                
            except Exception as e:
                print(f"⚠️  Error checking for Excel iframe: {e}")
                await asyncio.sleep(3)
        
        print("❌ Excel iframe not found within timeout")
        return None
    
    async def wait_for_excel_interface(self, timeout=60):
        """Wait for Excel interface to fully load"""
        print("⏳ Waiting for Excel interface to load...")
        
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                # Check for Excel-specific elements
                excel_indicators = [
                    "[data-testid*='excel']",
                    "[class*='excel']",
                    "[data-testid*='grid']",
                    "[class*='grid']",
                    "[data-testid*='cell']",
                    "[class*='cell']",
                    "[role='grid']",
                    "[role='gridcell']",
                    "[data-testid*='worksheet']",
                    "[class*='worksheet']"
                ]
                
                total_elements = 0
                for selector in excel_indicators:
                    elements = self.driver.find_elements("css selector", selector)
                    total_elements += len(elements)
                
                # Also check for any elements at all
                all_elements = self.driver.find_elements("css selector", "*")
                
                print(f"📊 Excel elements: {total_elements}, Total elements: {len(all_elements)}")
                
                if total_elements > 10 or len(all_elements) > 100:
                    print(f"✅ Excel interface loaded with {total_elements} Excel elements and {len(all_elements)} total elements")
                    return True
                
                await asyncio.sleep(3)
                
            except Exception as e:
                print(f"⚠️  Error checking Excel interface: {e}")
                await asyncio.sleep(3)
        
        print("⚠️  Excel interface may not be fully loaded")
        return False
    
    def find_excel_cells(self):
        """Find Excel cells using Office 365 specific selectors"""
        cell_selectors = [
            # Office 365 Excel specific
            "[data-testid*='cell']",
            "[class*='cell']",
            "[role='gridcell']",
            "td[data-testid]",
            "td[class*='cell']",
            
            # Grid-based selectors
            "[data-testid*='grid'] [data-testid*='cell']",
            "[class*='grid'] [class*='cell']",
            
            # Worksheet selectors
            "[data-testid*='worksheet'] [data-testid*='cell']",
            "[class*='worksheet'] [class*='cell']",
            
            # Generic table cells
            "td",
            "th"
        ]
        
        for selector in cell_selectors:
            try:
                cells = self.driver.find_elements("css selector", selector)
                if cells:
                    print(f"✅ Found {len(cells)} cells with selector: {selector}")
                    return cells
            except Exception as e:
                continue
        
        print("❌ No cells found with any selector")
        return []
    
    async def click_cell(self, cell_index=0):
        """Click on a specific cell"""
        cells = self.find_excel_cells()
        
        if not cells:
            print("❌ No cells available to click")
            return False
        
        try:
            # Click on the first cell
            cell = cells[cell_index]
            cell.click()
            print(f"✅ Clicked cell {cell_index}")
            
            # Wait for cell to be selected
            await asyncio.sleep(1)
            return True
            
        except Exception as e:
            print(f"❌ Failed to click cell: {e}")
            return False
    
    def enter_data_in_cell(self, data):
        """Enter data in the currently selected cell"""
        try:
            # Try multiple strategies for data entry
            
            # Strategy 1: Direct input
            actions = ActionChains(self.driver)
            actions.send_keys(data)
            actions.perform()
            print(f"✅ Entered data: {data}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to enter data: {e}")
            return False
    
    async def save_workbook(self):
        """Save the workbook using Office 365 shortcuts"""
        try:
            # Use Office 365 save shortcut
            actions = ActionChains(self.driver)
            actions.key_down(Keys.COMMAND).send_keys('s').key_up(Keys.COMMAND).perform()
            print("✅ Used Cmd+S to save")
            
            # Wait for save dialog or auto-save
            await asyncio.sleep(3)
            return True
            
        except Exception as e:
            print(f"❌ Failed to save: {e}")
            return False
    
    def close(self):
        """Close the browser"""
        if self.navigator:
            self.navigator.close()
            print("✅ Browser closed")

# Export the final navigator
async def get_final_excel_navigator():
    """Get the final Excel Web navigator"""
    navigator = FinalExcelWebNavigator()
    return navigator

