"""
Session memory management for workflow state.
"""

import json
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from ..models import SessionMemory

logger = logging.getLogger(__name__)


class SessionMemoryManager:
    """Manages session memory for workflow state persistence."""
    
    def __init__(self):
        """Initialize the session memory manager."""
        self.sessions: Dict[str, SessionMemory] = {}
        self.session_file = "data/sessions.json"
        self.load_sessions()
    
    def create_session(self) -> str:
        """Create a new session."""
        import uuid
        session_id = str(uuid.uuid4())
        
        session = SessionMemory(
            session_id=session_id,
            created_at=datetime.now(),
            last_accessed=datetime.now()
        )
        
        self.sessions[session_id] = session
        self.save_sessions()
        
        logger.info(f"Created new session: {session_id}")
        return session_id
    
    def get_session(self, session_id: str) -> Optional[SessionMemory]:
        """Get a session by ID."""
        if session_id in self.sessions:
            self.sessions[session_id].last_accessed = datetime.now()
            return self.sessions[session_id]
        return None
    
    def store_workflow_state(self, session_id: str, state: Any) -> bool:
        """Store workflow state for a session."""
        if session_id not in self.sessions:
            logger.warning(f"Session {session_id} not found")
            return False
        
        try:
            # Convert state to dict if it's a Pydantic model
            if hasattr(state, 'model_dump'):
                state_dict = state.model_dump(mode='json')
            else:
                state_dict = state
            
            self.sessions[session_id].workflow_state = state_dict
            self.sessions[session_id].last_accessed = datetime.now()
            self.save_sessions()
            return True
            
        except Exception as e:
            logger.error(f"Failed to store workflow state: {str(e)}")
            return False
    
    def get_workflow_state(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get workflow state for a session."""
        session = self.get_session(session_id)
        if session:
            return session.workflow_state
        return None
    
    def add_conversation_entry(self, session_id: str, entry: Dict[str, Any]) -> bool:
        """Add a conversation entry to session history."""
        if session_id not in self.sessions:
            return False
        
        entry["timestamp"] = datetime.now().isoformat()
        self.sessions[session_id].conversation_history.append(entry)
        self.sessions[session_id].last_accessed = datetime.now()
        self.save_sessions()
        return True
    
    def get_conversation_history(self, session_id: str) -> List[Dict[str, Any]]:
        """Get conversation history for a session."""
        session = self.get_session(session_id)
        if session:
            return session.conversation_history
        return []
    
    def update_context_data(self, session_id: str, key: str, value: Any) -> bool:
        """Update context data for a session."""
        if session_id not in self.sessions:
            return False
        
        self.sessions[session_id].context_data[key] = value
        self.sessions[session_id].last_accessed = datetime.now()
        self.save_sessions()
        return True
    
    def get_context_data(self, session_id: str, key: str) -> Any:
        """Get context data for a session."""
        session = self.get_session(session_id)
        if session and key in session.context_data:
            return session.context_data[key]
        return None
    
    def cleanup_expired_sessions(self, timeout_minutes: int = 60) -> int:
        """Clean up expired sessions."""
        cutoff_time = datetime.now() - timedelta(minutes=timeout_minutes)
        expired_sessions = [
            session_id for session_id, session in self.sessions.items()
            if session.last_accessed < cutoff_time
        ]
        
        for session_id in expired_sessions:
            del self.sessions[session_id]
        
        if expired_sessions:
            self.save_sessions()
            logger.info(f"Cleaned up {len(expired_sessions)} expired sessions")
        
        return len(expired_sessions)
    
    def get_session_summary(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get a summary of session information."""
        session = self.get_session(session_id)
        if not session:
            return None
        
        return {
            "session_id": session.session_id,
            "created_at": session.created_at.isoformat(),
            "last_accessed": session.last_accessed.isoformat(),
            "is_active": session.is_active,
            "conversation_count": len(session.conversation_history),
            "context_keys": list(session.context_data.keys()),
            "has_workflow_state": session.workflow_state is not None
        }
    
    def list_active_sessions(self) -> List[Dict[str, Any]]:
        """List all active sessions."""
        active_sessions = []
        for session in self.sessions.values():
            if session.is_active:
                summary = self.get_session_summary(session.session_id)
                if summary:
                    active_sessions.append(summary)
        
        return active_sessions
    
    def deactivate_session(self, session_id: str) -> bool:
        """Deactivate a session."""
        if session_id in self.sessions:
            self.sessions[session_id].is_active = False
            self.sessions[session_id].last_accessed = datetime.now()
            self.save_sessions()
            return True
        return False
    
    def save_sessions(self):
        """Save sessions to disk."""
        try:
            # Ensure data directory exists
            import os
            os.makedirs(os.path.dirname(self.session_file), exist_ok=True)
            
            sessions_data = {}
            for session_id, session in self.sessions.items():
                sessions_data[session_id] = {
                    "session_id": session.session_id,
                    "created_at": session.created_at.isoformat(),
                    "last_accessed": session.last_accessed.isoformat(),
                    "is_active": session.is_active,
                    "conversation_history": session.conversation_history,
                    "context_data": session.context_data,
                    "workflow_state": session.workflow_state
                }
            
            with open(self.session_file, 'w') as f:
                json.dump(sessions_data, f, indent=2)
                
        except Exception as e:
            logger.error(f"Failed to save sessions: {str(e)}")
    
    def load_sessions(self):
        """Load sessions from disk."""
        try:
            with open(self.session_file, 'r') as f:
                sessions_data = json.load(f)
            
            for session_id, data in sessions_data.items():
                session = SessionMemory(
                    session_id=data["session_id"],
                    created_at=datetime.fromisoformat(data["created_at"]),
                    last_accessed=datetime.fromisoformat(data["last_accessed"]),
                    is_active=data["is_active"],
                    conversation_history=data.get("conversation_history", []),
                    context_data=data.get("context_data", {}),
                    workflow_state=data.get("workflow_state")
                )
                self.sessions[session_id] = session
            
            logger.info(f"Loaded {len(self.sessions)} sessions from disk")
            
        except FileNotFoundError:
            logger.info("No existing sessions file found, starting with empty sessions")
        except Exception as e:
            logger.error(f"Failed to load sessions: {str(e)}")
            self.sessions = {}
