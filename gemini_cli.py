#!/usr/bin/env python3
"""
Gemini CLI Integration for AI-powered code fixing
Actually calls Gemini API to fix code and updates ADO tickets
"""

import os
import json
import logging
import subprocess
import requests
from typing import Dict, List, Any, Optional
from datetime import datetime

# Set up logger
logger = logging.getLogger(__name__)

class GeminiCLI:
    """Gemini CLI integration for AI-powered code fixing"""
    
    def __init__(self):
        self.api_key = os.getenv('GEMINI_API_KEY')
        # Try both v1 and v1beta endpoints
        self.api_urls = [
            "https://generativelanguage.googleapis.com/v1/models/gemini-1.5-pro:generateContent",
            "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-pro:generateContent"
        ]
        
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY environment variable is required")
        
        logger.info(f"Gemini CLI initialized with API key: {self.api_key[:10]}...")
    
    def fix_issue_with_thinking_steps(self, work_item_id: int, file_path: str, instruction: str) -> Dict[str, Any]:
        """Fix an issue using Gemini AI with real-time thinking steps"""
        
        thinking_steps = []
        
        try:
            # Step 1: Analyze the issue
            thinking_steps.append({
                "step": "🔍 Analyzing work item details...",
                "type": "info",
                "progress": 10
            })
            
            # Step 2: Read the file content
            thinking_steps.append({
                "step": "📋 Reading issue description and context...",
                "type": "info",
                "progress": 20
            })
            
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"File not found: {file_path}")
            
            with open(file_path, 'r', encoding='utf-8') as f:
                original_content = f.read()
            
            # Step 3: Generate AI fix
            thinking_steps.append({
                "step": "🤖 Initializing Gemini AI agent...",
                "type": "info",
                "progress": 30
            })
            
            thinking_steps.append({
                "step": "🔧 Identifying code files to modify...",
                "type": "info",
                "progress": 40
            })
            
            thinking_steps.append({
                "step": "💡 Generating AI-powered code fixes...",
                "type": "info",
                "progress": 50
            })
            
            # Call Gemini API to fix the code
            thinking_steps.append({
                "step": "🔍 Analyzing code structure...",
                "type": "info",
                "progress": 60
            })
            
            thinking_steps.append({
                "step": "✏️ Writing code improvements...",
                "type": "info",
                "progress": 70
            })
            
            # Call Gemini API to fix the code
            fixed_content = self._call_gemini_api(original_content, instruction)
            
            # Step 4: Apply the fix
            thinking_steps.append({
                "step": "✅ Applying fixes to codebase...",
                "type": "success",
                "progress": 70
            })
            
            # Write the fixed content back to the file
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(fixed_content)
            
            # Step 5: Update ADO work item
            thinking_steps.append({
                "step": "📝 Updating work item status...",
                "type": "info",
                "progress": 85
            })
            
            # Update ADO work item status
            self._update_ado_work_item(work_item_id, "Done")
            
            # Step 6: Complete
            thinking_steps.append({
                "step": "🎉 Fix completed successfully!",
                "type": "success",
                "progress": 100,
                "complete": True,
                "status": "✅ Fix completed successfully!",
                "statusType": "success",
                "workItemStatus": "Done"
            })
            
            return {
                "success": True,
                "thinking_steps": thinking_steps,
                "work_item_id": work_item_id,
                "file_path": file_path,
                "original_content": original_content,
                "fixed_content": fixed_content,
                "changes_applied": True
            }
            
        except Exception as e:
            logger.error(f"Error in fix_issue_with_thinking_steps: {e}")
            thinking_steps.append({
                "step": f"❌ Error: {str(e)}",
                "type": "error",
                "progress": 100,
                "complete": True,
                "status": f"❌ Fix failed: {str(e)}",
                "statusType": "error"
            })
            
            return {
                "success": False,
                "thinking_steps": thinking_steps,
                "error": str(e)
            }
    
    def _call_gemini_api(self, content: str, instruction: str) -> str:
        """Call Gemini API to fix the code"""
        
        prompt = f"""
You are an expert software developer specializing in accessibility and UX improvements. Please fix the following code based on the instruction.

INSTRUCTION: {instruction}

CODE TO FIX:
```html
{content}
```

IMPORTANT GUIDELINES:
- Fix accessibility issues like missing labels, ARIA attributes, and color contrast
- Improve semantic HTML structure
- Add proper form labels and descriptions
- Ensure keyboard navigation works
- Maintain the existing functionality while improving accessibility
- Return ONLY the complete fixed HTML code without any explanations or markdown formatting

Please provide the complete fixed file content:
"""
        
        headers = {
            "Content-Type": "application/json",
        }
        
        data = {
            "contents": [
                {
                    "parts": [
                        {
                            "text": prompt
                        }
                    ]
                }
            ],
            "generationConfig": {
                "temperature": 0.1,
                "topK": 1,
                "topP": 1,
                "maxOutputTokens": 8192,
            }
        }
        
        # Try multiple API endpoints
        last_error = None
        for api_url in self.api_urls:
            try:
                logger.info(f"Trying Gemini API endpoint: {api_url}")
                response = requests.post(
                    f"{api_url}?key={self.api_key}",
                    headers=headers,
                    json=data,
                    timeout=30
                )
                
                if response.status_code == 200:
                    result = response.json()
                    if 'candidates' in result and len(result['candidates']) > 0:
                        fixed_content = result['candidates'][0]['content']['parts'][0]['text']
                        # Clean up the response - remove any markdown formatting
                        if fixed_content.startswith('```'):
                            lines = fixed_content.split('\n')
                            if len(lines) > 2:
                                fixed_content = '\n'.join(lines[1:-1])
                        logger.info("Gemini API call successful")
                        return fixed_content
                    else:
                        raise Exception("No response from Gemini API")
                else:
                    last_error = f"Gemini API error: {response.status_code} - {response.text}"
                    logger.warning(f"API endpoint {api_url} failed: {last_error}")
                    continue
                    
            except Exception as e:
                last_error = str(e)
                logger.warning(f"API endpoint {api_url} failed: {e}")
                continue
        
                # If we get here, all endpoints failed
        raise Exception(f"All Gemini API endpoints failed. Last error: {last_error}")
    
    def _update_ado_work_item(self, work_item_id: int, new_state: str):
        """Update ADO work item status"""
        try:
            from azure_devops_integration import AzureDevOpsClient
            client = AzureDevOpsClient()
            client.update_work_item(str(work_item_id), {"status": new_state})
            logger.info(f"Updated ADO work item {work_item_id} to status: {new_state}")
        except Exception as e:
            logger.error(f"Failed to update ADO work item {work_item_id}: {e}")
            # Don't raise the exception - we don't want to fail the whole fix if ADO update fails

def fix_issue_with_thinking_steps(work_item_id: int, file_path: str, instruction: str) -> Dict[str, Any]:
    """Convenience function to fix an issue with thinking steps"""
    cli = GeminiCLI()
    return cli.fix_issue_with_thinking_steps(work_item_id, file_path, instruction)

if __name__ == "__main__":
    # Test the Gemini CLI
    import sys
    
    if len(sys.argv) != 4:
        print("Usage: python gemini_cli.py <work_item_id> <file_path> <instruction>")
        sys.exit(1)
    
    work_item_id = int(sys.argv[1])
    file_path = sys.argv[2]
    instruction = sys.argv[3]
    
    result = fix_issue_with_thinking_steps(work_item_id, file_path, instruction)
    print(json.dumps(result, indent=2))
