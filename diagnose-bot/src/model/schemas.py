from pydantic import BaseModel, Field
from typing import List, Union

## --- Schemas for Multi-Agent model -----#

class CriticalAgentSchema(BaseModel):
    name: str = Field(..., description="Role or name of the sub-agent")
    prompt: str = Field(..., description="Prompt for the sub-agent defining its task")

class QuestionerSchema(BaseModel):
    questions: List[str] = Field(..., description="List of questions to ask the user")

class MetaAgentOutputSchema(BaseModel):
    questioner_prompt: str = Field(..., description="Prompt for the questioner agent")
    critical_agents: List[CriticalAgentSchema] = Field(..., description="List of sub-agents with their assigned roles and prompts")

class AgentResponseSchema(BaseModel):
    comments: str = Field(..., description="Here the agent gives its comment given the related task")
    score: Union[str, int] = Field(..., description="Here the agent defines a possible score given the example provided (can be string or number)")
    suggestions: Union[List[str], str] = Field(..., description="Here the agent can provide additional suggestions or considerations that will be sent to the user")

class ConsolidatorOutputSchema(BaseModel):
    pre_diagnosis: str = Field(..., description="Final pre-diagnosis from consolidator")
    comments: str = Field(..., description="Final comments based on sub-agents outputs")
    score: str = Field(..., description="The mode of sub-agents scores")
    filled_doc: str = Field(..., description="Document filled with user's info and analysis")
