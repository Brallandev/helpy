from pydantic import BaseModel
from typing import List, Optional

class ChatEntry(BaseModel):
    question: Optional[str]
    answer: Optional[str]

class BodyRequest(BaseModel):
    phone_number: str
    chat: List[ChatEntry]

class ConfigStructure(BaseModel):
    min_agents: int
    max_agents: int
    language: str
    decision_scores: dict
    num_questions: int

class ConfigDocStructure(BaseModel):
    doc: str