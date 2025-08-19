#!/usr/bin/env python3
"""
Enhanced Excel Web Automation with proper shadow DOM handling
Based on Office 365 Excel Web structure
"""

import asyncio
import time
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException, NoSuchElementException

class EnhancedExcelWebNavigator:
    """Enhanced Excel Web Navigator with proper Office 365 handling"""
    
    def __init__(self):
        self.driver = None
        self.wait = None
        self.current_frame = None
        
    async def initialize(self):
        """Initialize the browser with enhanced settings"""
        try:
            chrome_options = Options()
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-blink-features=AutomationControlled")
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            
            # Enhanced settings for Office 365
            chrome_options.add_argument("--disable-web-security")
            chrome_options.add_argument("--allow-running-insecure-content")
            chrome_options.add_argument("--disable-features=VizDisplayCompositor")
            
            self.driver = webdriver.Chrome(options=chrome_options)
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            self.wait = WebDriverWait(self.driver, 30)
            
            print("✅ Enhanced Excel Web Navigator initialized")
            return True
            
        except Exception as e:
            print(f"❌ Failed to initialize: {e}")
            return False
    
    def find_element_in_shadow_dom(self, shadow_host_selector, element_selector):
        """Find element within shadow DOM"""
        try:
            # Find shadow host
            shadow_host = self.driver.find_element("css selector", shadow_host_selector)
            
            # Get shadow root
            shadow_root = self.driver.execute_script("return arguments[0].shadowRoot", shadow_host)
            
            # Find element within shadow root
            element = shadow_root.find_element("css selector", element_selector)
            return element
            
        except Exception as e:
            print(f"❌ Shadow DOM element not found: {e}")
            return None
    
    def wait_for_excel_interface(self, timeout=60):
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
                    "[role='gridcell']"
                ]
                
                total_elements = 0
                for selector in excel_indicators:
                    elements = self.driver.find_elements("css selector", selector)
                    total_elements += len(elements)
                
                if total_elements > 10:  # Excel should have many elements
                    print(f"✅ Excel interface loaded with {total_elements} elements")
                    return True
                
                # Also check for any elements at all
                all_elements = self.driver.find_elements("css selector", "*")
                if len(all_elements) > 50:  # Should have many elements
                    print(f"✅ Interface loaded with {len(all_elements)} total elements")
                    return True
                
                await asyncio.sleep(2)
                
            except Exception as e:
                print(f"⚠️  Error checking Excel interface: {e}")
                await asyncio.sleep(2)
        
        print("⚠️  Excel interface may not be fully loaded")
        return False
    
    def switch_to_excel_iframe(self):
        """Switch to the correct Excel iframe"""
        try:
            # Wait for iframes to load
            self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "iframe")))
            
            # Find all iframes
            iframes = self.driver.find_elements("css selector", "iframe")
            print(f"📋 Found {len(iframes)} iframes")
            
            # Look for Excel iframe
            for i, iframe in enumerate(iframes):
                try:
                    src = iframe.get_attribute("src")
                    print(f"  Iframe {i}: {src}")
                    
                    # Office 365 Excel iframe patterns
                    if any(pattern in src.lower() for pattern in [
                        "excel", "office", "webshell", "officeapps", "excel.office.com"
                    ]):
                        self.driver.switch_to.frame(iframe)
                        self.current_frame = i
                        print(f"✅ Switched to Excel iframe {i}")
                        
                        # Wait for iframe content to load
                        await asyncio.sleep(3)
                        return True
                        
                except Exception as e:
                    print(f"  ❌ Error with iframe {i}: {e}")
                    continue
            
            print("⚠️  No Excel iframe found")
            return False
            
        except Exception as e:
            print(f"❌ Failed to switch to iframe: {e}")
            return False
    
    def find_excel_cells(self):
        """Find Excel cells using multiple strategies"""
        cell_selectors = [
            # Office 365 specific selectors
            "[data-testid*='cell']",
            "[class*='cell']",
            "[role='gridcell']",
            "td[data-testid]",
            "td[class*='cell']",
            
            # Shadow DOM selectors
            "[data-testid*='grid'] [data-testid*='cell']",
            "[class*='grid'] [class*='cell']",
            
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
    
    def click_cell(self, cell_index=0):
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
    
    def save_workbook(self):
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
        if self.driver:
            self.driver.quit()
            print("✅ Browser closed")

# Export the enhanced navigator
async def get_enhanced_excel_navigator():
    """Get an enhanced Excel Web navigator"""
    navigator = EnhancedExcelWebNavigator()
    return navigator

