import os
import subprocess
from typing import Dict, Any, Optional
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
GEMINI_CLI_PATH = os.getenv("GEMINI_CLI_PATH", "gemini")  # fallback if path isn't set
FRONTEND_PATH = os.getenv("FRONTEND_PATH", "../frontend")  # relative path to source files

# Setup logging
logger = logging.getLogger('gemini_handler')

class GeminiHandler:
    """
    Handler for Gemini CLI integration to automatically fix bugs
    """
    
    def __init__(self, gemini_cli_path: Optional[str] = None, frontend_path: Optional[str] = None):
        self.gemini_cli_path = gemini_cli_path or GEMINI_CLI_PATH
        self.frontend_path = frontend_path or FRONTEND_PATH
        self.logger = logger
        
        # Ensure frontend path is absolute
        if not os.path.isabs(self.frontend_path):
            self.frontend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), self.frontend_path))
    
    def fix_bug_with_gemini(self, issue: Dict[str, Any]) -> bool:
        """
        Calls Gemini CLI to fix the bug in the specified file.
        
        Args:
            issue: Dictionary containing bug details with keys:
                   - file: relative path to file
                   - message: issue description
                   - severity: issue severity
                   - type: issue type
                   - recommendation: fix recommendation
        
        Returns:
            bool: True if fix was successful, False otherwise
        """
        try:
            # Get current Git branch
            current_branch = self._get_current_branch()
            
            # Determine file path
            file_path = self._get_file_path(issue)
            if not file_path:
                self.logger.error(f"Could not determine file path for issue: {issue}")
                return False
            
            # Create fix prompt
            prompt = self._create_fix_prompt(issue)
            
            self.logger.info(f"Attempting Gemini fix for {file_path}")
            self.logger.info(f"Fix prompt: {prompt}")
            
            # Execute Gemini CLI command
            result = subprocess.run(
                [
                    self.gemini_cli_path,
                    "patch",
                    "--instruction", prompt,
                    "--repo-path", self.frontend_path,
                    "--branch", current_branch
                ],
                check=True,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )

            self.logger.info("✅ Gemini Fix Applied Successfully")
            self.logger.info(f"Gemini output: {result.stdout}")
            
            # Validate the fix
            if self._validate_fix(file_path, issue):
                return True
            else:
                self.logger.warning("Fix applied but validation failed")
                return False

        except subprocess.CalledProcessError as e:
            self.logger.error("❌ Gemini Fix Failed")
            self.logger.error(f"Error: {e.stderr}")
            self.logger.error(f"Return code: {e.returncode}")
            return False
        
        except subprocess.TimeoutExpired:
            self.logger.error("❌ Gemini Fix Timed Out")
            return False
        
        except FileNotFoundError:
            self.logger.error(f"❌ Gemini CLI not found at: {self.gemini_cli_path}")
            self.logger.error("Please install Gemini CLI or update GEMINI_CLI_PATH in .env")
            return False
        
        except Exception as e:
            self.logger.error(f"❌ Unexpected error during Gemini fix: {e}")
            return False
    
    def _get_file_path(self, issue: Dict[str, Any]) -> Optional[str]:
        """
        Determine the full file path for the issue
        """
        # Try to get file from issue
        file_name = issue.get("file", "")
        
        if not file_name:
            # Try to infer from issue type and element
            issue_type = issue.get("type", "")
            element = issue.get("element", "")
            
            if issue_type == "accessibility" or "html" in issue_type.lower():
                file_name = "index.html"
            elif issue_type == "performance" or "js" in issue_type.lower():
                file_name = "main.js"
            elif "css" in issue_type.lower() or "style" in issue_type.lower():
                file_name = "style.css"
            else:
                # Default fallback
                file_name = "index.html"
        
        # Create full path
        if file_name:
            full_path = os.path.join(self.frontend_path, file_name)
            
            # Check if file exists, if not try to find similar files
            if not os.path.exists(full_path):
                self.logger.warning(f"File not found: {full_path}, attempting to find alternative")
                full_path = self._find_similar_file(file_name)
            
            return full_path
        
        return None
    
    def _find_similar_file(self, file_name: str) -> Optional[str]:
        """
        Try to find a similar file if the exact file doesn't exist
        """
        if not os.path.exists(self.frontend_path):
            self.logger.error(f"Frontend path does not exist: {self.frontend_path}")
            return None
        
        # Get file extension
        _, ext = os.path.splitext(file_name)
        
        # Search for files with same extension
        for root, dirs, files in os.walk(self.frontend_path):
            for file in files:
                if file.endswith(ext):
                    full_path = os.path.join(root, file)
                    self.logger.info(f"Found alternative file: {full_path}")
                    return full_path
        
        # If no exact extension match, try common web files
        common_files = ["index.html", "main.js", "app.js", "style.css", "main.css"]
        for common_file in common_files:
            full_path = os.path.join(self.frontend_path, common_file)
            if os.path.exists(full_path):
                self.logger.info(f"Using fallback file: {full_path}")
                return full_path
        
        return None
    
    def _create_fix_prompt(self, issue: Dict[str, Any]) -> str:
        """
        Create a detailed prompt for Gemini to fix the issue
        """
        issue_type = issue.get("type", "unknown")
        message = issue.get("message", "")
        severity = issue.get("severity", "medium")
        recommendation = issue.get("recommendation", "")
        element = issue.get("element", "")
        
        prompt_parts = [
            f"Fix {severity} severity {issue_type} issue: {message}"
        ]
        
        if element:
            prompt_parts.append(f"The issue is related to element: {element}")
        
        if recommendation:
            prompt_parts.append(f"Recommended solution: {recommendation}")
        
        # Add specific instructions based on issue type
        if issue_type == "accessibility":
            prompt_parts.append("Ensure the fix improves accessibility and follows WCAG guidelines.")
        elif issue_type == "performance":
            prompt_parts.append("Optimize for better performance without breaking functionality.")
        elif issue_type == "ux_heuristics":
            prompt_parts.append("Improve user experience following established UX principles.")
        
        prompt_parts.append("Make minimal changes and preserve existing functionality.")
        
        return " ".join(prompt_parts)
    
    def _validate_fix(self, file_path: str, issue: Dict[str, Any]) -> bool:
        """
        Basic validation to check if the fix was applied
        """
        try:
            # Check if file still exists and is readable
            if not os.path.exists(file_path):
                return False
            
            # Basic file integrity check
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # File should not be empty
            if not content.strip():
                return False
            
            # For specific issue types, do basic validation
            issue_type = issue.get("type", "")
            
            if issue_type == "accessibility" and "alt" in issue.get("message", "").lower():
                # Check if alt attributes were added
                return "alt=" in content
            
            if issue_type == "performance" and "bundle" in issue.get("message", "").lower():
                # Basic check for performance optimizations
                return True  # Assume fix is valid for now
            
            return True
            
        except Exception as e:
            self.logger.error(f"Validation failed: {e}")
            return False
    
    def _get_current_branch(self) -> str:
        """
        Get the current Git branch name
        
        Returns:
            str: Current branch name, defaults to 'main' if unable to determine
        """
        try:
            result = subprocess.run(
                ["git", "branch", "--show-current"],
                check=True,
                capture_output=True,
                text=True,
                cwd=self.frontend_path
            )
            branch = result.stdout.strip()
            if branch:
                self.logger.info(f"Using Git branch: {branch}")
                return branch
            else:
                self.logger.warning("Could not determine current branch, defaulting to 'main'")
                return "main"
        except Exception as e:
            self.logger.warning(f"Failed to get current branch: {e}, defaulting to 'main'")
            return "main"
    
    def test_gemini_cli(self) -> bool:
        """
        Test if Gemini CLI is available and working
        """
        try:
            result = subprocess.run(
                [self.gemini_cli_path, "--help"],
                check=True,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            self.logger.info("✅ Gemini CLI is available")
            return True
            
        except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
            self.logger.error(f"❌ Gemini CLI not available at: {self.gemini_cli_path}")
            return False
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get status information about the Gemini handler
        """
        return {
            "gemini_cli_path": self.gemini_cli_path,
            "frontend_path": self.frontend_path,
            "cli_available": self.test_gemini_cli(),
            "frontend_path_exists": os.path.exists(self.frontend_path)
        }

# Convenience function for direct usage
def fix_bug_with_gemini(issue: Dict[str, Any]) -> bool:
    """
    Convenience function to fix a bug using Gemini CLI
    
    Args:
        issue: Dictionary containing bug details
    
    Returns:
        bool: True if fix was successful, False otherwise
    """
    handler = GeminiHandler()
    return handler.fix_bug_with_gemini(issue)
