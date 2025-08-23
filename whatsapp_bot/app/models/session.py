"""User session models."""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import List

from .question import Answer


class SessionState(Enum):
    """Possible states of a user session."""
    WAITING_FOR_ANSWER = "waiting_for_answer"
    PROCESSING_API = "processing_api"
    CONVERSATION_ENDED = "conversation_ended"


@dataclass
class UserSession:
    """Represents a user's conversation session."""
    phone_number: str
    current_question_index: int = 0
    answers: List[Answer] = field(default_factory=list)
    state: SessionState = SessionState.WAITING_FOR_ANSWER
    created_at: datetime = field(default_factory=datetime.now)
    last_activity: datetime = field(default_factory=datetime.now)
    first_question_asked: bool = False  # Track if we've asked the first question
