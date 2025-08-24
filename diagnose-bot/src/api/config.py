from fastapi import APIRouter
from pydantic import BaseModel
from src.api.schemas import ConfigStructure, ConfigDocStructure
from src.utils.config_manager import update_config, get_config, update_doc, get_doc
from src.config import OPENROUTER_API_KEY

router = APIRouter()

@router.get("/haskey")
async def get_statusAPIKey():
    boolean = isinstance(OPENROUTER_API_KEY, str)
    return {"config": boolean}

@router.post("")
async def set_config(cfg: ConfigStructure):
    update_config(cfg.dict())
    return {"status": "Config updated", "config": get_config()}

@router.post("/doc")
async def set_doc(doc: ConfigDocStructure):
    update_doc(doc.doc)
    return {"status": "Document updated", "doc_first_10" : get_doc()[:10]}