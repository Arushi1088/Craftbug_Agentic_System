#!/usr/bin/env python3
"""
Azure DevOps Comment Trigger for Orchestrator Agent
Monitors work items for /fix-now comments and triggers automated fixes
"""

import time
import requests
import logging
import os
import base64
from typing import List, Dict, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
POLL_INTERVAL_SECONDS = 15  # Poll every 15 seconds
ADO_ORG = os.getenv("ADO_ORG")
ADO_PROJECT = os.getenv("ADO_PROJECT")
ADO_TOKEN = os.getenv("ADO_TOKEN")

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('comment_trigger')

class CommentTriggerListener:
    """Monitors ADO work items for /fix-now comments and triggers fixes"""
    
    def __init__(self):
        self.ado_org = ADO_ORG
        self.ado_project = ADO_PROJECT
        self.ado_token = ADO_TOKEN
        self.ado_encoded = base64.b64encode(f":{self.ado_token}".encode()).decode()
        self.already_triggered = set()
        
        # Validate configuration
        if not all([self.ado_org, self.ado_project, self.ado_token]):
            raise ValueError("Missing ADO configuration. Please set ADO_ORG, ADO_PROJECT, and ADO_TOKEN")
    
    def get_work_item_comments(self, work_item_id: int) -> List[Dict[str, Any]]:
        """Get comments for a specific work item"""
        try:
            # Use the work item history API instead of comments API
            url = f"https://dev.azure.com/{self.ado_org}/{self.ado_project}/_apis/wit/workItems/{work_item_id}/revisions?api-version=7.0"
            headers = {
                "Authorization": f"Basic {self.ado_encoded}",
                "Content-Type": "application/json"
            }
            
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                revisions = response.json().get("value", [])
                # Extract comments from revisions
                comments = []
                for revision in revisions:
                    fields = revision.get("fields", {})
                    history = fields.get("System.History", "")
                    if history and history.strip():
                        comments.append({"text": history})
                return comments
            else:
                logger.error(f"Failed to get comments for work item {work_item_id}: {response.status_code}")
                return []
        except Exception as e:
            logger.error(f"Error getting comments for work item {work_item_id}: {e}")
            return []
    
    def find_fix_trigger_comment(self, work_item_id: int) -> bool:
        """Check if work item has a /fix-now comment"""
        comments = self.get_work_item_comments(work_item_id)
        for comment in reversed(comments):  # Check latest comments first
            text = comment.get("text", "").strip().lower()
            if "/fix-now" in text:
                logger.info(f"Found /fix-now trigger in work item #{work_item_id}")
                return True
        return False
    
    def get_active_work_items(self) -> List[int]:
        """Get all active (non-closed) work items"""
        try:
            url = f"https://dev.azure.com/{self.ado_org}/{self.ado_project}/_apis/wit/wiql?api-version=7.0"
            headers = {
                "Authorization": f"Basic {self.ado_encoded}",
                "Content-Type": "application/json"
            }
            
            query = {
                "query": "SELECT [System.Id] FROM WorkItems WHERE [System.WorkItemType] = 'Task' AND [System.State] <> 'Closed' AND [System.State] <> 'Done'"
            }
            
            response = requests.post(url, json=query, headers=headers)
            if response.status_code == 200:
                work_items = response.json().get("workItems", [])
                return [item["id"] for item in work_items]
            else:
                logger.error(f"Failed to get work items: {response.status_code}")
                return []
        except Exception as e:
            logger.error(f"Error getting active work items: {e}")
            return []
    
    def trigger_orchestrator_fix(self, work_item_id: int):
        """Trigger the orchestrator to fix the work item"""
        try:
            logger.info(f"🚨 Triggering orchestrator fix for Work Item #{work_item_id}")
            
            # Import here to avoid circular imports
            from main import trigger_fix_for_work_item
            
            # Trigger the fix
            success = trigger_fix_for_work_item(work_item_id)
            
            if success:
                logger.info(f"✅ Successfully triggered fix for Work Item #{work_item_id}")
                self.already_triggered.add(work_item_id)
            else:
                logger.error(f"❌ Failed to trigger fix for Work Item #{work_item_id}")
                
        except Exception as e:
            logger.error(f"Error triggering fix for work item {work_item_id}: {e}")
    
    def main_loop(self):
        """Main monitoring loop"""
        logger.info("🔁 Starting comment trigger listener...")
        logger.info(f"📊 Monitoring ADO: {self.ado_org}/{self.ado_project}")
        logger.info(f"⏰ Poll interval: {POLL_INTERVAL_SECONDS} seconds")
        
        while True:
            try:
                work_items = self.get_active_work_items()
                logger.info(f"📋 Checking {len(work_items)} active work items...")
                
                for work_item_id in work_items:
                    if work_item_id in self.already_triggered:
                        continue
                        
                    if self.find_fix_trigger_comment(work_item_id):
                        self.trigger_orchestrator_fix(work_item_id)
                
                time.sleep(POLL_INTERVAL_SECONDS)
                
            except KeyboardInterrupt:
                logger.info("🛑 Comment trigger listener stopped by user")
                break
            except Exception as e:
                logger.error(f"Error in main loop: {e}")
                time.sleep(POLL_INTERVAL_SECONDS)

def main():
    """Entry point for the comment trigger listener"""
    listener = CommentTriggerListener()
    listener.main_loop()

if __name__ == "__main__":
    main()
