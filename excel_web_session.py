"""
Excel Web Session Management Module
Handles session persistence, validation, and management
"""

import asyncio
import json
import time
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from pathlib import Path
from playwright.async_api import Page
from excel_web_config import get_excel_web_config


class ExcelWebSession:
    """Represents an Excel Web session"""
    
    def __init__(self):
        self.session_id: str = ""
        self.created_at: datetime = datetime.now()
        self.last_used: datetime = datetime.now()
        self.is_valid: bool = False
        self.cookies: Dict[str, Any] = {}
        self.local_storage: Dict[str, Any] = {}
        self.session_data: Dict[str, Any] = {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert session to dictionary for storage"""
        return {
            "session_id": self.session_id,
            "created_at": self.created_at.isoformat(),
            "last_used": self.last_used.isoformat(),
            "is_valid": self.is_valid,
            "cookies": self.cookies,
            "local_storage": self.local_storage,
            "session_data": self.session_data
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ExcelWebSession':
        """Create session from dictionary"""
        session = cls()
        session.session_id = data.get("session_id", "")
        session.created_at = datetime.fromisoformat(data.get("created_at", datetime.now().isoformat()))
        session.last_used = datetime.fromisoformat(data.get("last_used", datetime.now().isoformat()))
        session.is_valid = data.get("is_valid", False)
        session.cookies = data.get("cookies", {})
        session.local_storage = data.get("local_storage", {})
        session.session_data = data.get("session_data", {})
        return session


class SessionManager:
    """Manages Excel Web sessions"""
    
    def __init__(self):
        self.config = get_excel_web_config()
        self.sessions_dir = Path("sessions/excel_web")
        self.sessions_dir.mkdir(parents=True, exist_ok=True)
        self.current_session: Optional[ExcelWebSession] = None
    
    def generate_session_id(self) -> str:
        """Generate a unique session ID"""
        timestamp = int(time.time() * 1000)
        return f"excel_web_session_{timestamp}"
    
    async def create_session(self, page: Page) -> ExcelWebSession:
        """Create a new session from browser page"""
        session = ExcelWebSession()
        session.session_id = self.generate_session_id()
        session.created_at = datetime.now()
        session.last_used = datetime.now()
        session.is_valid = True
        
        # Capture cookies
        try:
            cookies = await page.context.cookies()
            session.cookies = {cookie["name"]: cookie for cookie in cookies}
        except Exception as e:
            print(f"⚠️  Failed to capture cookies: {e}")
        
        # Capture local storage
        try:
            local_storage = await page.evaluate("() => Object.entries(localStorage)")
            session.local_storage = dict(local_storage)
        except Exception as e:
            print(f"⚠️  Failed to capture local storage: {e}")
        
        # Capture session storage
        try:
            session_storage = await page.evaluate("() => Object.entries(sessionStorage)")
            session.session_data = dict(session_storage)
        except Exception as e:
            print(f"⚠️  Failed to capture session storage: {e}")
        
        self.current_session = session
        await self.save_session(session)
        
        print(f"✅ Created new session: {session.session_id}")
        return session
    
    async def save_session(self, session: ExcelWebSession):
        """Save session to file"""
        try:
            session_file = self.sessions_dir / f"{session.session_id}.json"
            with open(session_file, 'w') as f:
                json.dump(session.to_dict(), f, indent=2)
        except Exception as e:
            print(f"❌ Failed to save session: {e}")
    
    async def load_session(self, session_id: str) -> Optional[ExcelWebSession]:
        """Load session from file"""
        try:
            session_file = self.sessions_dir / f"{session_id}.json"
            if not session_file.exists():
                return None
            
            with open(session_file, 'r') as f:
                data = json.load(f)
            
            session = ExcelWebSession.from_dict(data)
            return session
        except Exception as e:
            print(f"❌ Failed to load session: {e}")
            return None
    
    async def restore_session(self, page: Page, session: ExcelWebSession) -> bool:
        """Restore session to browser page"""
        try:
            # Restore cookies
            if session.cookies:
                cookies = list(session.cookies.values())
                await page.context.add_cookies(cookies)
                print("✅ Restored cookies")
            
            # Restore local storage
            if session.local_storage:
                for key, value in session.local_storage.items():
                    await page.evaluate(f"localStorage.setItem('{key}', '{value}')")
                print("✅ Restored local storage")
            
            # Restore session storage
            if session.session_data:
                for key, value in session.session_data.items():
                    await page.evaluate(f"sessionStorage.setItem('{key}', '{value}')")
                print("✅ Restored session storage")
            
            return True
        except Exception as e:
            print(f"❌ Failed to restore session: {e}")
            return False
    
    def is_session_valid(self, session: ExcelWebSession) -> bool:
        """Check if session is still valid"""
        if not session.is_valid:
            return False
        
        # Check session timeout
        timeout_delta = timedelta(minutes=self.config.session_timeout_minutes)
        if datetime.now() - session.last_used > timeout_delta:
            print(f"⚠️  Session expired: {session.session_id}")
            session.is_valid = False
            return False
        
        return True
    
    async def update_session_usage(self, session: ExcelWebSession):
        """Update session last used timestamp"""
        session.last_used = datetime.now()
        await self.save_session(session)
    
    async def invalidate_session(self, session: ExcelWebSession):
        """Invalidate a session"""
        session.is_valid = False
        await self.save_session(session)
        
        # Remove session file
        try:
            session_file = self.sessions_dir / f"{session.session_id}.json"
            if session_file.exists():
                session_file.unlink()
        except Exception as e:
            print(f"⚠️  Failed to remove session file: {e}")
        
        print(f"✅ Invalidated session: {session.session_id}")
    
    async def cleanup_expired_sessions(self):
        """Clean up expired sessions"""
        try:
            for session_file in self.sessions_dir.glob("*.json"):
                session = await self.load_session(session_file.stem)
                if session and not self.is_session_valid(session):
                    await self.invalidate_session(session)
        except Exception as e:
            print(f"⚠️  Failed to cleanup sessions: {e}")
    
    async def get_valid_session(self) -> Optional[ExcelWebSession]:
        """Get a valid session if available"""
        if self.current_session and self.is_session_valid(self.current_session):
            await self.update_session_usage(self.current_session)
            return self.current_session
        
        # Try to find any valid session
        try:
            for session_file in self.sessions_dir.glob("*.json"):
                session = await self.load_session(session_file.stem)
                if session and self.is_session_valid(session):
                    self.current_session = session
                    await self.update_session_usage(session)
                    return session
        except Exception as e:
            print(f"⚠️  Failed to find valid session: {e}")
        
        return None


# Global session manager
session_manager = SessionManager()


async def get_session_manager() -> SessionManager:
    """Get the global session manager"""
    return session_manager
