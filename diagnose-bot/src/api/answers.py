from fastapi import APIRouter, HTTPException  
from src.api.schemas import BodyRequest
from src.model.agents import AgentsGroup, ConsolidatorAgent
from src.utils.config_manager import get_config, get_doc
from src.utils.agent_registry import get_session, remove_session
from langchain_community.chat_models import ChatOpenAI
from src.config import OPENROUTER_API_KEY

router = APIRouter()

@router.post("")
async def give_answers(req: BodyRequest):
    questions_answers = req.chat
    session = get_session(req.phone_number)
    
    if session is None:
        raise HTTPException(status_code = 404)

    llm = ChatOpenAI
    # Pass the LLM instance to your AgentsGroup
    agents = AgentsGroup(session['critical_agents'], llm, {"model_name":"google/gemini-2.5-flash-lite",
                                                          "openai_api_base":"https://openrouter.ai/api/v1",
                                                          "api_key":OPENROUTER_API_KEY,
                                                          "temperature":0.7,
                                                          "max_tokens":1024})
    agents.run(questions_answers)
    responses = agents.responses
    llm = ChatOpenAI(model_name="google/gemini-2.5-flash-lite",
                     openai_api_base="https://openrouter.ai/api/v1",
                     api_key=OPENROUTER_API_KEY,
                     temperature=0.7,
                     max_tokens=1024)
    consolidator = ConsolidatorAgent(responses, llm)
    consolidator.run(get_doc())
    remove_session(req.phone_number)
    return consolidator.response