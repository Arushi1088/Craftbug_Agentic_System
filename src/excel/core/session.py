"""
Unified Session Management for Excel Web

This module provides unified session management functionality, consolidating
session handling from multiple existing classes while maintaining backward compatibility.
"""

import json
import asyncio
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from pathlib import Path
from dataclasses import dataclass, asdict
from .config import get_config


@dataclass
class ExcelWebSession:
    """Excel Web session data"""
    session_id: str = ""
    created_at: datetime = None
    last_used: datetime = None
    is_valid: bool = True
    cookies: Dict[str, Any] = None
    local_storage: Dict[str, str] = None
    session_data: Dict[str, str] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.last_used is None:
            self.last_used = datetime.now()
        if self.cookies is None:
            self.cookies = {}
        if self.local_storage is None:
            self.local_storage = {}
        if self.session_data is None:
            self.session_data = {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert session to dictionary"""
        return {
            'session_id': self.session_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_used': self.last_used.isoformat() if self.last_used else None,
            'is_valid': self.is_valid,
            'cookies': self.cookies,
            'local_storage': self.local_storage,
            'session_data': self.session_data
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ExcelWebSession':
        """Create session from dictionary"""
        session = cls()
        session.session_id = data.get('session_id', '')
        session.created_at = datetime.fromisoformat(data['created_at']) if data.get('created_at') else None
        session.last_used = datetime.fromisoformat(data['last_used']) if data.get('last_used') else None
        session.is_valid = data.get('is_valid', True)
        session.cookies = data.get('cookies', {})
        session.local_storage = data.get('local_storage', {})
        session.session_data = data.get('session_data', {})
        return session


class SessionManager:
    """Unified session manager"""
    
    def __init__(self):
        self.config = get_config().get_excel_web_config()
        self.session_dir = Path(self.config.session_storage_path)
        self.session_dir.mkdir(parents=True, exist_ok=True)
        self.session_timeout = self.config.session_timeout
    
    async def create_session(self, browser_instance=None) -> ExcelWebSession:
        """Create a new session"""
        session = ExcelWebSession()
        session.session_id = f"session_{int(datetime.now().timestamp() * 1000)}"
        session.created_at = datetime.now()
        session.last_used = datetime.now()
        session.is_valid = True
        
        # Capture session data from browser if provided
        if browser_instance:
            await self._capture_session_data(session, browser_instance)
        
        # Save session
        await self.save_session(session)
        return session
    
    async def save_session(self, session: ExcelWebSession) -> bool:
        """Save session to file"""
        try:
            session.last_used = datetime.now()
            session_file = self.session_dir / f"{session.session_id}.json"
            
            with open(session_file, 'w') as f:
                json.dump(session.to_dict(), f, indent=2, default=str)
            
            print(f"✅ Session saved: {session.session_id}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to save session: {e}")
            return False
    
    async def load_session(self, session_id: str) -> Optional[ExcelWebSession]:
        """Load session from file"""
        try:
            session_file = self.session_dir / f"{session_id}.json"
            
            if not session_file.exists():
                return None
            
            with open(session_file, 'r') as f:
                data = json.load(f)
            
            session = ExcelWebSession.from_dict(data)
            return session
            
        except Exception as e:
            print(f"❌ Failed to load session {session_id}: {e}")
            return None
    
    async def get_valid_session(self) -> Optional[ExcelWebSession]:
        """Get a valid session"""
        try:
            # List all session files
            session_files = list(self.session_dir.glob("*.json"))
            
            if not session_files:
                return None
            
            # Sort by modification time (newest first)
            session_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
            
            for session_file in session_files:
                session_id = session_file.stem
                session = await self.load_session(session_id)
                
                if session and session.is_valid:
                    # Check if session is expired
                    if self._is_session_expired(session):
                        print(f"⚠️  Session {session_id} is expired")
                        await self.invalidate_session(session)
                        continue
                    
                    print(f"✅ Found valid session: {session_id}")
                    return session
            
            return None
            
        except Exception as e:
            print(f"❌ Error getting valid session: {e}")
            return None
    
    async def invalidate_session(self, session: ExcelWebSession) -> bool:
        """Invalidate a session"""
        try:
            session.is_valid = False
            await self.save_session(session)
            print(f"✅ Session {session.session_id} invalidated")
            return True
            
        except Exception as e:
            print(f"❌ Failed to invalidate session: {e}")
            return False
    
    async def cleanup_expired_sessions(self) -> int:
        """Clean up expired sessions"""
        try:
            cleaned_count = 0
            session_files = list(self.session_dir.glob("*.json"))
            
            for session_file in session_files:
                session_id = session_file.stem
                session = await self.load_session(session_id)
                
                if session and self._is_session_expired(session):
                    try:
                        session_file.unlink()
                        cleaned_count += 1
                        print(f"🗑️  Cleaned up expired session: {session_id}")
                    except Exception as e:
                        print(f"⚠️  Failed to delete expired session {session_id}: {e}")
            
            if cleaned_count > 0:
                print(f"✅ Cleaned up {cleaned_count} expired sessions")
            
            return cleaned_count
            
        except Exception as e:
            print(f"❌ Error cleaning up sessions: {e}")
            return 0
    
    def _is_session_expired(self, session: ExcelWebSession) -> bool:
        """Check if session is expired"""
        if not session.last_used:
            return True
        
        expiry_time = session.last_used + timedelta(seconds=self.session_timeout)
        return datetime.now() > expiry_time
    
    async def _capture_session_data(self, session: ExcelWebSession, browser_instance) -> None:
        """Capture session data from browser instance"""
        try:
            # This is a placeholder - actual implementation depends on browser type
            # Will be implemented in the navigator classes
            pass
            
        except Exception as e:
            print(f"⚠️  Failed to capture session data: {e}")
    
    async def list_sessions(self) -> List[ExcelWebSession]:
        """List all sessions"""
        try:
            sessions = []
            session_files = list(self.session_dir.glob("*.json"))
            
            for session_file in session_files:
                session_id = session_file.stem
                session = await self.load_session(session_id)
                if session:
                    sessions.append(session)
            
            return sessions
            
        except Exception as e:
            print(f"❌ Error listing sessions: {e}")
            return []
    
    async def delete_session(self, session_id: str) -> bool:
        """Delete a session"""
        try:
            session_file = self.session_dir / f"{session_id}.json"
            
            if session_file.exists():
                session_file.unlink()
                print(f"✅ Session {session_id} deleted")
                return True
            else:
                print(f"⚠️  Session {session_id} not found")
                return False
                
        except Exception as e:
            print(f"❌ Failed to delete session {session_id}: {e}")
            return False


# Global session manager instance
_session_manager: Optional[SessionManager] = None


def get_session_manager() -> SessionManager:
    """Get the global session manager instance"""
    global _session_manager
    if _session_manager is None:
        _session_manager = SessionManager()
    return _session_manager


# Backward compatibility aliases
SessionManager = SessionManager
