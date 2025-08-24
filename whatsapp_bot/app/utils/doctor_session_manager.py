"""
Doctor session manager for handling doctor registration and workflow.
"""

from typing import Dict, List, Optional
from app.models.doctor_session import DoctorSession, DoctorSessionState


class DoctorSessionManager:
    """Manages doctor sessions and registration."""
    
    def __init__(self):
        # In-memory storage for doctor sessions
        # In production, this should be moved to Redis or a database
        self.doctor_sessions: Dict[str, DoctorSession] = {}
    
    def is_registered_doctor(self, phone_number: str) -> bool:
        """Check if a phone number belongs to a registered doctor."""
        session = self.doctor_sessions.get(phone_number)
        return session is not None and session.is_active()
    
    def register_doctor(self, phone_number: str) -> DoctorSession:
        """Register a new doctor or reactivate existing one."""
        if phone_number in self.doctor_sessions:
            # Reactivate existing doctor
            session = self.doctor_sessions[phone_number]
            session.state = DoctorSessionState.REGISTERED
            session.mark_activity()
        else:
            # Create new doctor session
            session = DoctorSession(phone_number=phone_number)
            self.doctor_sessions[phone_number] = session
        
        return session
    
    def get_doctor_session(self, phone_number: str) -> Optional[DoctorSession]:
        """Get doctor session if it exists."""
        return self.doctor_sessions.get(phone_number)
    
    def confirm_doctor_registration(self, phone_number: str) -> bool:
        """Confirm doctor registration and activate them."""
        session = self.doctor_sessions.get(phone_number)
        if session and session.state == DoctorSessionState.REGISTRATION_PENDING:
            session.state = DoctorSessionState.REGISTERED
            session.mark_activity()
            return True
        return False
    
    def get_active_doctors(self) -> List[DoctorSession]:
        """Get all active doctors."""
        return [
            session for session in self.doctor_sessions.values()
            if session.is_active()
        ]
    
    def start_case_review(self, doctor_phone: str, patient_phone: str) -> bool:
        """Mark doctor as reviewing a specific case."""
        session = self.doctor_sessions.get(doctor_phone)
        if session and session.is_active():
            session.start_reviewing_case(patient_phone)
            return True
        return False
    
    def complete_case_review(self, doctor_phone: str, patient_phone: str) -> bool:
        """Mark case review as complete."""
        session = self.doctor_sessions.get(doctor_phone)
        if session:
            session.complete_case_review(patient_phone)
            return True
        return False
    
    def deactivate_doctor(self, phone_number: str) -> bool:
        """Deactivate a doctor."""
        session = self.doctor_sessions.get(phone_number)
        if session:
            session.state = DoctorSessionState.INACTIVE
            session.mark_activity()
            return True
        return False
    
    def get_doctor_stats(self, phone_number: str) -> Optional[Dict]:
        """Get doctor statistics."""
        session = self.doctor_sessions.get(phone_number)
        if session:
            return {
                "phone_number": session.phone_number,
                "state": session.state.value,
                "registration_date": session.registration_date.isoformat(),
                "last_activity": session.last_activity.isoformat(),
                "cases_reviewed_count": len(session.cases_reviewed),
                "current_reviewing": session.current_reviewing_patient,
                "is_active": session.is_active()
            }
        return None
