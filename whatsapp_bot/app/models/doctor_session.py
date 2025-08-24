"""
Doctor session model for managing doctor registration and workflows.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import List, Dict, Any, Optional


class DoctorSessionState(Enum):
    """Possible states of a doctor session."""
    REGISTRATION_PENDING = "registration_pending"  # Just said "doctor", needs confirmation
    REGISTERED = "registered"  # Confirmed and ready to receive cases
    REVIEWING_CASE = "reviewing_case"  # Currently reviewing a patient case
    INACTIVE = "inactive"  # Temporarily inactive


@dataclass
class DoctorSession:
    """Represents a doctor's session and state."""
    phone_number: str
    state: DoctorSessionState = DoctorSessionState.REGISTRATION_PENDING
    registration_date: datetime = field(default_factory=datetime.now)
    last_activity: datetime = field(default_factory=datetime.now)
    cases_reviewed: List[str] = field(default_factory=list)  # Patient phone numbers
    current_reviewing_patient: Optional[str] = None
    
    def mark_activity(self):
        """Update the last activity timestamp."""
        self.last_activity = datetime.now()
    
    def start_reviewing_case(self, patient_phone: str):
        """Start reviewing a patient case."""
        self.state = DoctorSessionState.REVIEWING_CASE
        self.current_reviewing_patient = patient_phone
        self.mark_activity()
    
    def complete_case_review(self, patient_phone: str):
        """Complete reviewing a patient case."""
        if patient_phone not in self.cases_reviewed:
            self.cases_reviewed.append(patient_phone)
        self.current_reviewing_patient = None
        self.state = DoctorSessionState.REGISTERED
        self.mark_activity()
    
    def is_active(self) -> bool:
        """Check if doctor is currently active."""
        return self.state in [DoctorSessionState.REGISTERED, DoctorSessionState.REVIEWING_CASE]
