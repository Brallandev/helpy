"""
WhatsApp Mental Health Triage Bot

A conversational bot that conducts mental health triage through WhatsApp
by asking predefined questions and integrating with external APIs.
"""

import json
from typing import Optional
from fastapi import FastAPI, Request, HTTPException, Query
from fastapi.responses import PlainTextResponse

from app.config.settings import settings
from app.utils.session_manager import SessionManager
from app.utils.message_parser import MessageParser
from app.services.whatsapp_service import WhatsAppService
from app.services.api_service import ExternalAPIService
from app.services.database_service import DatabaseService
from app.services.conversation_service import ConversationService


# Validate configuration
settings.validate()

# Initialize services
session_manager = SessionManager()
whatsapp_service = WhatsAppService()
api_service = ExternalAPIService()
database_service = DatabaseService()
conversation_service = ConversationService(
    session_manager=session_manager,
    whatsapp_service=whatsapp_service,
    api_service=api_service,
    database_service=database_service
)

# Initialize FastAPI app
app = FastAPI(
    title="WhatsApp Mental Health Triage Bot",
    description="A conversational bot for mental health triage via WhatsApp",
    version="1.0.0"
)


@app.get("/")
@app.get("/webhook")
async def verify_webhook(
    hub_mode: Optional[str] = Query(None, alias="hub.mode"),
    hub_verify_token: Optional[str] = Query(None, alias="hub.verify_token"),
    hub_challenge: Optional[str] = Query(None, alias="hub.challenge"),
):
    """Verify WhatsApp webhook."""
    if (
        (hub_mode or "").strip() == "subscribe" and
        (hub_verify_token or "").strip() == (settings.VERIFY_TOKEN or "").strip()
    ):
        return PlainTextResponse(hub_challenge or "", status_code=200)
    return PlainTextResponse("Verificación fallida", status_code=403)


@app.post("/")
@app.post("/webhook")
async def receive_webhook(request: Request):
    """Receive and process WhatsApp webhook messages."""
    data = await request.json()
    print("[INBOUND]", json.dumps(data, ensure_ascii=False))
    
    try:
        for entry in data.get("entry", []):
            for change in entry.get("changes", []):
                value = change.get("value", {})
                messages = value.get("messages", [])
                
                if not messages:
                    continue
                
                for message in messages:
                    sender_phone = message.get("from")
                    text_content = MessageParser.extract_text_from_message(message)
                    
                    if text_content:  # Only process if we have text
                        print(f"[MESSAGE] from={sender_phone} text={text_content!r}")
                        await conversation_service.process_user_message(sender_phone, text_content)
        
        return PlainTextResponse("OK", status_code=200)
    
    except Exception as e:
        print("[ERROR]", repr(e))
        return PlainTextResponse("ERROR", status_code=200)


@app.get("/send-test")
async def send_test_message(to: str, text: str = "Hola desde FastAPI 👋"):
    """Send a test message (for debugging)."""
    try:
        response = await whatsapp_service.send_text_message(to, text)
        return {"status": "sent", "response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/sessions")
async def get_all_sessions():
    """Get all active sessions (for debugging)."""
    sessions = session_manager.get_all_sessions()
    return {
        phone: {
            "current_question": session.current_question_index,
            "state": session.state.value,
            "answers_count": len(session.answers),
            "last_activity": session.last_activity.isoformat(),
            "first_question_asked": session.first_question_asked,
            "consent_given": session.consent_given,
            "greeting_sent": session.greeting_sent,
            "followup_questions_count": len(session.followup_questions),
            "current_followup_index": session.current_followup_index,
            "followup_answers_count": len(session.followup_answers),
            "has_pre_diagnosis": session.pre_diagnosis is not None
        }
        for phone, session in sessions.items()
    }


@app.get("/sessions/{phone_number}")
async def get_session_details(phone_number: str):
    """Get detailed information about a specific session."""
    session_summary = session_manager.get_session_summary(phone_number)
    if session_summary:
        return session_summary
    return {"status": f"No session found for {phone_number}"}


@app.delete("/sessions/{phone_number}")
async def reset_session(phone_number: str):
    """Reset a user's session."""
    old_session = session_manager.reset_session(phone_number)
    if old_session:
        return {
            "status": f"Session reset for {phone_number}",
            "old_session": {
                "question_index": old_session.current_question_index,
                "answers_count": len(old_session.answers),
                "state": old_session.state.value
            }
        }
    return {"status": f"No session found for {phone_number}"}


@app.on_event("shutdown")
async def shutdown_event():
    """Clean up resources on shutdown."""
    await whatsapp_service.close()
    await api_service.close()
    await database_service.close()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
