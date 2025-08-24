"""Session management utilities."""

from datetime import datetime
from typing import Dict, Optional

from app.models.session import UserSession
from app.config.questions import MENTAL_HEALTH_QUESTIONS


class SessionManager:
    """Manages user sessions and conversation state."""
    
    def __init__(self):
        self.sessions: Dict[str, UserSession] = {}
    
    def get_or_create_session(self, phone_number: str) -> UserSession:
        """Get existing session or create a new one for the user.
        
        Args:
            phone_number: The user's phone number
            
        Returns:
            The user's session
        """
        if phone_number not in self.sessions:
            self.sessions[phone_number] = UserSession(phone_number=phone_number)
        else:
            self.sessions[phone_number].last_activity = datetime.now()
        
        return self.sessions[phone_number]
    
    def reset_session(self, phone_number: str) -> Optional[UserSession]:
        """Reset a user's session.
        
        Args:
            phone_number: The user's phone number
            
        Returns:
            The old session if it existed, None otherwise
        """
        old_session = self.sessions.get(phone_number)
        if old_session:
            self.sessions[phone_number] = UserSession(phone_number=phone_number)
        return old_session
    
    def delete_session(self, phone_number: str) -> bool:
        """Delete a user's session.
        
        Args:
            phone_number: The user's phone number
            
        Returns:
            True if session was deleted, False if it didn't exist
        """
        if phone_number in self.sessions:
            del self.sessions[phone_number]
            return True
        return False
    
    def get_current_question(self, session: UserSession) -> Optional[object]:
        """Get the current question for a session.
        
        Args:
            session: The user session
            
        Returns:
            The current question or None if all questions are answered
        """
        if session.current_question_index < len(MENTAL_HEALTH_QUESTIONS):
            return MENTAL_HEALTH_QUESTIONS[session.current_question_index]
        return None
    
    def all_questions_answered(self, session: UserSession) -> bool:
        """Check if all questions have been answered.
        
        Args:
            session: The user session
            
        Returns:
            True if all questions are answered, False otherwise
        """
        return len(session.answers) >= len(MENTAL_HEALTH_QUESTIONS)
    
    def get_all_sessions(self) -> Dict[str, UserSession]:
        """Get all active sessions.
        
        Returns:
            Dictionary of all sessions keyed by phone number
        """
        return self.sessions.copy()
    
    def get_session_summary(self, phone_number: str) -> Optional[Dict]:
        """Get a summary of a user's session.
        
        Args:
            phone_number: The user's phone number
            
        Returns:
            Session summary dictionary or None if session doesn't exist
        """
        session = self.sessions.get(phone_number)
        if not session:
            return None
        
        current_question = self.get_current_question(session)
        
        return {
            "phone_number": phone_number,
            "current_question_index": session.current_question_index,
            "state": session.state.value,
            "answers": [
                {
                    "question_id": answer.question_id,
                    "value": answer.value,
                    "timestamp": answer.timestamp.isoformat()
                }
                for answer in session.answers
            ],
            "created_at": session.created_at.isoformat(),
            "last_activity": session.last_activity.isoformat(),
            "current_question": current_question.text if current_question else None
        }
