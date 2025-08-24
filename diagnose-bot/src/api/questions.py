from http.client import HTTPException
from fastapi import APIRouter
from src.api.schemas import BodyRequest
from src.model.agents import MetaAgent, QuestionerAgent
from src.utils.config_manager import get_config
from src.utils.agent_registry import create_session
from src.utils.config_manager import get_doc
from langchain_community.chat_models import ChatOpenAI
from src.config import OPENROUTER_API_KEY

router = APIRouter()

@router.post("")
async def get_questions(req: BodyRequest):
    cfg = get_config()
    doc = get_doc()
    if doc is None:
        raise HTTPException(status_code=400, detail="No document found.")

    # Initialize LLM with OpenRouter pointing to Gemini 2.5 Flash-Lite
    llm = ChatOpenAI(
        model_name="google/gemini-2.5-flash-lite",
        openai_api_base="https://openrouter.ai/api/v1",
        api_key=OPENROUTER_API_KEY,
        temperature=0.7,
        max_tokens=4096
    )

    # Begin MetaAgent task
    meta_agent = MetaAgent(doc=doc, user_info=req.chat, config=cfg, llm=llm)
    meta_agent.run()

    # Save the session in memory
    create_session(req.phone_number, meta_agent)

    # SimpleAgent uses the same LLM
    questioner = QuestionerAgent(meta_agent.questions_agent, llm)
    questioner.run()
    questions = questioner.response

    return questions