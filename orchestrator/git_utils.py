#!/usr/bin/env python3
"""
Git utilities for automated commits and pushes after Gemini fixes
Part of STEP 4: Automated Git workflow integration
"""

import os
import subprocess
import logging
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)


class GitHandler:
    """Handles Git operations for automated commits and pushes"""
    
    def __init__(self, base_path: str = None):
        """
        Initialize Git handler
        
        Args:
            base_path: Base path of the repository (defaults to current directory)
        """
        self.base_path = base_path or os.getcwd()
        self.repo_name = "BUGFIX"  # Repository name
        self.default_branch = "orchestrator"
        
    def is_git_repo(self) -> bool:
        """Check if current directory is a Git repository"""
        try:
            result = subprocess.run(
                ["git", "rev-parse", "--git-dir"],
                cwd=self.base_path,
                capture_output=True,
                text=True,
                check=True
            )
            return True
        except subprocess.CalledProcessError:
            return False
    
    def get_current_branch(self) -> Optional[str]:
        """Get the current Git branch name"""
        try:
            result = subprocess.run(
                ["git", "branch", "--show-current"],
                cwd=self.base_path,
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to get current branch: {e}")
            return None
    
    def check_git_status(self) -> Dict[str, Any]:
        """Check Git repository status"""
        try:
            # Check for uncommitted changes
            result = subprocess.run(
                ["git", "status", "--porcelain"],
                cwd=self.base_path,
                capture_output=True,
                text=True,
                check=True
            )
            
            uncommitted_changes = result.stdout.strip().split('\n') if result.stdout.strip() else []
            
            # Check if branch exists on remote
            try:
                subprocess.run(
                    ["git", "rev-parse", "--verify", f"origin/{self.default_branch}"],
                    cwd=self.base_path,
                    capture_output=True,
                    check=True
                )
                remote_exists = True
            except subprocess.CalledProcessError:
                remote_exists = False
            
            return {
                "is_git_repo": True,
                "current_branch": self.get_current_branch(),
                "uncommitted_changes": uncommitted_changes,
                "remote_exists": remote_exists,
                "clean": len(uncommitted_changes) == 0
            }
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to check Git status: {e}")
            return {
                "is_git_repo": False,
                "error": str(e)
            }
    
    def commit_and_push_fix(self, issue: Dict[str, Any], fixed_files: list = None) -> bool:
        """
        Commits Gemini-applied fixes and pushes to the remote GitHub repository.
        
        Args:
            issue: Dictionary containing issue information
            fixed_files: List of files that were fixed (optional)
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Validate Git repository
            if not self.is_git_repo():
                logger.error("Not a Git repository")
                return False
            
            # Determine files to commit
            files_to_commit = []
            
            if fixed_files:
                # Use provided file list
                files_to_commit = fixed_files
            elif "file" in issue:
                # Construct file path from issue
                frontend_paths = ["web-ui", "frontend", "src"]
                file_found = False
                
                for base_dir in frontend_paths:
                    file_path = os.path.join(base_dir, issue["file"])
                    full_path = os.path.join(self.base_path, file_path)
                    
                    if os.path.exists(full_path):
                        files_to_commit.append(file_path)
                        file_found = True
                        break
                
                if not file_found:
                    logger.warning(f"Could not find file to commit: {issue.get('file', 'unknown')}")
                    # Add all modified files instead
                    status = self.check_git_status()
                    if status.get("uncommitted_changes"):
                        files_to_commit = [change[3:] for change in status["uncommitted_changes"] if change.startswith(" M ")]
            
            if not files_to_commit:
                logger.warning("No files to commit")
                return False
            
            # Create commit message
            issue_summary = issue.get("message", issue.get("type", "Unknown issue"))[:60]
            commit_msg = f"[AUTO-FIX] Gemini fix for: {issue_summary}"
            
            if "severity" in issue:
                commit_msg += f" ({issue['severity']} severity)"
            
            # Add files to staging
            logger.info(f"Adding files to Git staging: {files_to_commit}")
            for file_path in files_to_commit:
                try:
                    subprocess.run(
                        ["git", "add", file_path],
                        cwd=self.base_path,
                        check=True,
                        capture_output=True
                    )
                    logger.info(f"✅ Added to staging: {file_path}")
                except subprocess.CalledProcessError as e:
                    logger.warning(f"Failed to add {file_path}: {e}")
                    # Continue with other files
            
            # Check if there's anything to commit
            result = subprocess.run(
                ["git", "diff", "--cached", "--name-only"],
                cwd=self.base_path,
                capture_output=True,
                text=True,
                check=True
            )
            
            if not result.stdout.strip():
                logger.warning("No staged changes to commit")
                return False
            
            # Commit changes
            logger.info(f"Committing with message: {commit_msg}")
            subprocess.run(
                ["git", "commit", "-m", commit_msg],
                cwd=self.base_path,
                check=True,
                capture_output=True
            )
            logger.info("✅ Changes committed successfully")
            
            # Push to remote
            current_branch = self.get_current_branch() or self.default_branch
            logger.info(f"Pushing to origin/{current_branch}")
            
            try:
                subprocess.run(
                    ["git", "push", "origin", current_branch],
                    cwd=self.base_path,
                    check=True,
                    capture_output=True
                )
                logger.info(f"✅ Changes pushed to origin/{current_branch}")
                
                print(f"✅ Fix committed and pushed: {', '.join(files_to_commit)}")
                print(f"📝 Commit message: {commit_msg}")
                print(f"🌟 Branch: {current_branch}")
                
                return True
                
            except subprocess.CalledProcessError as e:
                logger.error(f"Failed to push to remote: {e}")
                print(f"⚠️  Changes committed locally but push failed: {e}")
                return False
                
        except subprocess.CalledProcessError as e:
            logger.error(f"Git commit failed: {e}")
            print(f"❌ Git commit/push failed: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error in Git operations: {e}")
            print(f"❌ Unexpected Git error: {e}")
            return False
    
    def create_pull_request_info(self, issue: Dict[str, Any]) -> Dict[str, str]:
        """
        Generate information for creating a pull request
        
        Args:
            issue: Dictionary containing issue information
            
        Returns:
            dict: PR information including title, description, etc.
        """
        issue_type = issue.get("type", "unknown")
        severity = issue.get("severity", "medium")
        message = issue.get("message", "Automated fix applied")
        
        pr_title = f"🤖 Auto-fix: {message}"
        pr_description = f"""
## 🤖 Automated Fix Applied

**Issue Type:** {issue_type.title()}
**Severity:** {severity.title()}
**Description:** {message}

### Changes Made
- Applied Gemini AI fix for {issue_type} issue
- Files modified: {issue.get('file', 'Multiple files')}

### Recommendation
{issue.get('recommendation', 'No specific recommendation provided')}

---
*This fix was automatically applied by the Gemini CLI integration system.*
*Please review the changes before merging.*
"""
        
        return {
            "title": pr_title,
            "description": pr_description,
            "branch": self.get_current_branch() or self.default_branch,
            "base": "main"
        }


# Convenience function for backward compatibility
def commit_and_push_fix(issue: Dict[str, Any], fixed_files: list = None) -> bool:
    """
    Convenience function for committing and pushing fixes
    
    Args:
        issue: Dictionary containing issue information
        fixed_files: List of files that were fixed (optional)
        
    Returns:
        bool: True if successful, False otherwise
    """
    handler = GitHandler()
    return handler.commit_and_push_fix(issue, fixed_files)


def get_git_status() -> Dict[str, Any]:
    """Get current Git repository status"""
    handler = GitHandler()
    return handler.check_git_status()
