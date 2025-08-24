"""User session models."""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import List, Optional, Dict, Any

from .question import Answer


class SessionState(Enum):
    """Possible states of a user session."""
    WAITING_FOR_CONSENT = "waiting_for_consent"
    WAITING_FOR_ANSWER = "waiting_for_answer"
    PROCESSING_API = "processing_api"
    WAITING_FOR_FOLLOWUP = "waiting_for_followup"  # New state for follow-up questions
    WAITING_FOR_DOCTOR_APPROVAL = "waiting_for_doctor_approval"  # Waiting for doctor decision
    CONVERSATION_ENDED = "conversation_ended"
    CONSENT_DECLINED = "consent_declined"


@dataclass
class UserSession:
    """Represents a user's conversation session."""
    phone_number: str
    current_question_index: int = 0
    answers: List[Answer] = field(default_factory=list)
    state: SessionState = SessionState.WAITING_FOR_CONSENT
    created_at: datetime = field(default_factory=datetime.now)
    last_activity: datetime = field(default_factory=datetime.now)
    first_question_asked: bool = False  # Track if we've asked the first question
    consent_given: bool = False  # Track if user has given consent
    greeting_sent: bool = False  # Track if greeting has been sent
    
    # New fields for dynamic follow-up questions
    followup_questions: List[str] = field(default_factory=list)  # Follow-up questions from API
    current_followup_index: int = 0  # Current follow-up question index
    followup_answers: List[Answer] = field(default_factory=list)  # Answers to follow-up questions
    pre_diagnosis: Optional[Dict[str, Any]] = None  # Final pre-diagnosis from API
    
    # Doctor approval workflow fields
    doctors_notified: List[str] = field(default_factory=list)  # List of doctor phone numbers notified
    doctor_responses: List[Dict[str, Any]] = field(default_factory=list)  # Doctor approval responses
    final_doctor_decision: Optional[str] = None  # Final doctor decision (APROBAR/DENEGAR/MIXTO)
    patient_notified_of_decision: bool = False  # Whether patient was notified of doctor decision
