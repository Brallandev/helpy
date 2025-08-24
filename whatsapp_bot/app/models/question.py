"""Question and Answer models."""

from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class Question:
    """Represents a question in the conversation flow."""
    id: str
    text: str
    required: bool = True


@dataclass
class Answer:
    """Represents a user's answer to a question."""
    question_id: str
    value: str
    timestamp: datetime = field(default_factory=datetime.now)
