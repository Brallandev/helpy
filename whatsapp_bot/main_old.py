import os, json
from typing import Any, Dict, List, Optional, Union
from datetime import datetime
from enum import Enum
from dataclasses import dataclass, field
from fastapi import FastAPI, Request, HTTPException, Query
from fastapi.responses import PlainTextResponse
from dotenv import load_dotenv
import httpx
import asyncio

load_dotenv()
WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN")
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID")
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")
GRAPH_API_VERSION = os.getenv("GRAPH_API_VERSION", "v20.0")
EXTERNAL_API_URL = os.getenv("EXTERNAL_API_URL", "https://api.example.com/process")  # Configure your API endpoint

if not all([WHATSAPP_TOKEN, PHONE_NUMBER_ID, VERIFY_TOKEN]):
    raise RuntimeError("Faltan variables de entorno en .env")

GRAPH_URL = f"https://graph.facebook.com/{GRAPH_API_VERSION}/{PHONE_NUMBER_ID}/messages"
HEADERS = {"Authorization": f"Bearer {WHATSAPP_TOKEN}", "Content-Type": "application/json"}

# Data Models
class SessionState(Enum):
    WAITING_FOR_ANSWER = "waiting_for_answer"
    PROCESSING_API = "processing_api"
    CONVERSATION_ENDED = "conversation_ended"

@dataclass
class Question:
    id: str
    text: str
    required: bool = True
    
@dataclass
class Answer:
    question_id: str
    value: str
    timestamp: datetime = field(default_factory=datetime.now)

@dataclass
class UserSession:
    phone_number: str
    current_question_index: int = 0
    answers: List[Answer] = field(default_factory=list)
    state: SessionState = SessionState.WAITING_FOR_ANSWER
    created_at: datetime = field(default_factory=datetime.now)
    last_activity: datetime = field(default_factory=datetime.now)
    first_question_asked: bool = False  # Track if we've asked the first question

# Predefined Questions - Mental Health Triage
QUESTIONS = [
    Question("name", "¡Hola! 👋 Para comenzar, ¿cuál es tu nombre completo?"),
    Question("age", "¿Cuál es tu edad?"),
    Question("main_concern", "¿Cuál es el motivo principal de tu preocupación?"),
    Question("anxiety", "¿Te sientes nervioso, tenso o ansioso con frecuencia?"),
    Question("symptom_duration", "¿Cuánto tiempo llevas experimentando estos síntomas?"),
    Question("relaxation_difficulty", "¿Estás teniendo dificultad para relajarte?"),
    Question("sadness", "¿Te sientes triste o deprimido?"),
    Question("loss_of_interest", "¿Has perdido interés en actividades que antes disfrutabas?"),
    Question("hallucinations_meds", "¿Tienes alucinaciones o estás en medicamentos psiquiátricos?"),
    Question("self_harm_thoughts", "¿Has tenido pensamientos sobre hacerte daño o acabar con tu vida?"),
    Question("fatigue", "¿Te sientes cansado todo el tiempo sin razón aparente?"),
    Question("desired_outcome", "¿Qué te gustaría que pasara ahora mismo?"),
    Question("specialist_connection", "¿Quieres conectar ya con un especialista?")
]

# In-memory session storage (use Redis/Database in production)
user_sessions: Dict[str, UserSession] = {}

app = FastAPI(title="WhatsApp Bot - Conversational")
http = httpx.AsyncClient(timeout=30.0)

async def send_text_message(to: str, body: str) -> None:
    payload = {"messaging_product": "whatsapp", "to": to, "text": {"body": body}}
    r = await http.post(GRAPH_URL, headers=HEADERS, json=payload)
    print("[SEND]", r.status_code, r.text)
    r.raise_for_status()

def get_or_create_session(phone_number: str) -> UserSession:
    if phone_number not in user_sessions:
        user_sessions[phone_number] = UserSession(phone_number=phone_number)
    else:
        user_sessions[phone_number].last_activity = datetime.now()
    return user_sessions[phone_number]

def get_current_question(session: UserSession) -> Optional[Question]:
    if session.current_question_index < len(QUESTIONS):
        return QUESTIONS[session.current_question_index]
    return None

def save_answer(session: UserSession, answer_text: str) -> None:
    current_question = get_current_question(session)
    if current_question:
        answer = Answer(question_id=current_question.id, value=answer_text)
        session.answers.append(answer)
        session.current_question_index += 1

def all_questions_answered(session: UserSession) -> bool:
    return len(session.answers) >= len(QUESTIONS)

async def send_to_external_api(session: UserSession) -> Dict[str, Any]:
    """Send collected answers to external API and return response"""
    # Prepare data for API
    api_payload = {
        "user_phone": session.phone_number,
        "timestamp": session.created_at.isoformat(),
        "chat": {answer.question_id: answer.value for answer in session.answers}
    }
    
    try:
        print("\n" + "="*60)
        print("[API_CALL] SENDING DATA TO EXTERNAL API")
        print("="*60)
        print(f"🎯 Endpoint: {EXTERNAL_API_URL}")
        print(f"📱 User: {session.phone_number}")
        print(f"📊 Total Answers: {len(session.answers)}/{len(QUESTIONS)}")
        print("\n📋 COMPLETE API PAYLOAD:")
        print("-" * 40)
        print(json.dumps(api_payload, ensure_ascii=False, indent=2))
        print("-" * 40)
        print("🚀 Sending request...")
        print("="*60 + "\n")
        
        response = await http.post(
            EXTERNAL_API_URL,
            json=api_payload,
            headers={"Content-Type": "application/json"}
        )
        
        print("\n" + "="*60)
        print("[API_RESPONSE] RECEIVED RESPONSE FROM EXTERNAL API")
        print("="*60)
        print(f"📈 Status Code: {response.status_code}")
        print(f"⏱️  Response Time: {response.elapsed.total_seconds():.2f}s" if hasattr(response, 'elapsed') else "")
        print("\n📨 RESPONSE BODY:")
        print("-" * 40)
        try:
            if response.status_code == 200:
                response_json = response.json()
                print(json.dumps(response_json, ensure_ascii=False, indent=2))
                print("-" * 40)
                print("✅ API call successful!")
                print("="*60 + "\n")
                return response_json
            else:
                print(f"❌ Error Response: {response.text}")
                print("-" * 40)
                print(f"🚨 API call failed with status {response.status_code}")
                print("="*60 + "\n")
                return {"error": f"API error: {response.status_code}", "continue_conversation": False}
        except Exception as parse_error:
            print(f"❌ Failed to parse response: {response.text}")
            print(f"🚨 Parse error: {str(parse_error)}")
            print("-" * 40)
            print("="*60 + "\n")
            return {"error": f"API parse error: {str(parse_error)}", "continue_conversation": False}
            
    except Exception as e:
        print(f"[API_ERROR] {repr(e)}")
        return {"error": f"API connection failed: {str(e)}", "continue_conversation": False}

async def handle_api_response(session: UserSession, api_response: Dict[str, Any]) -> str:
    """Process API response and generate appropriate message for user"""
    
    if "error" in api_response:
        session.state = SessionState.CONVERSATION_ENDED
        return "Lo siento, ha ocurrido un error procesando tu información. Por favor intenta más tarde."
    
    # Check if conversation should continue
    should_continue = api_response.get("continue_conversation", False)
    
    if not should_continue:
        session.state = SessionState.CONVERSATION_ENDED
        message = api_response.get("final_message", "Gracias por tu tiempo. Tu consulta ha sido procesada.")
        return message
    
    # If conversation continues, the API can provide new questions or messages
    new_message = api_response.get("message", "Gracias por la información.")
    
    # Check if API provides new questions to ask
    new_questions = api_response.get("additional_questions", [])
    if new_questions:
        # Add new questions to the list (extend conversation dynamically)
        global QUESTIONS
        for q_data in new_questions:
            new_question = Question(
                id=q_data.get("id", f"dynamic_{len(QUESTIONS)}"),
                text=q_data.get("text", ""),
                required=q_data.get("required", True)
            )
            QUESTIONS.append(new_question)
    
    # Reset to continue asking questions
    session.state = SessionState.WAITING_FOR_ANSWER
    return new_message

async def process_user_message(phone_number: str, message_text: str) -> None:
    session = get_or_create_session(phone_number)
    
    print(f"[SESSION] User: {phone_number}, State: {session.state.value}, Question: {session.current_question_index}, Answers: {len(session.answers)}")
    print(f"[MESSAGE_RECEIVED] Text: {message_text!r}")
    
    if session.state == SessionState.CONVERSATION_ENDED:
        print(f"[CONVERSATION_ENDED] Resetting session for {phone_number}")
        await send_text_message(phone_number, "Esta conversación ha terminado. Envía cualquier mensaje para comenzar una nueva consulta.")
        # Reset session for new conversation
        user_sessions[phone_number] = UserSession(phone_number=phone_number)
        session = user_sessions[phone_number]
        print(f"[SESSION_RESET] New session: index={session.current_question_index}, answers={len(session.answers)}")
        # Ask the first question of the new conversation
        current_question = get_current_question(session)
        if current_question:
            print(f"[ASKING_FIRST_QUESTION] {current_question.text[:50]}...")
            await send_text_message(phone_number, current_question.text)
        return
    
    if session.state == SessionState.PROCESSING_API:
        print(f"[PROCESSING_API] Rejecting message while processing")
        await send_text_message(phone_number, "Estoy procesando tu información, por favor espera un momento...")
        return
    
    # Simple logic: if we haven't asked the first question yet, ask it
    if not session.first_question_asked:
        print(f"[FIRST_MESSAGE] Asking first question")
        current_question = get_current_question(session)
        if current_question:
            print(f"[ASKING_QUESTION] {current_question.text[:50]}...")
            await send_text_message(phone_number, current_question.text)
            session.first_question_asked = True
        return
    
    # We've asked the first question, so this message is an answer
    print(f"[PROCESSING_ANSWER] Received: {message_text}")
    current_question = get_current_question(session)
    if current_question:
        print(f"[SAVING_ANSWER] For question '{current_question.id}': {message_text}")
        save_answer(session, message_text)
        print(f"[ANSWER_SAVED] {current_question.id}: {message_text} (new index: {session.current_question_index})")
    else:
        print(f"[WARNING] No current question to save answer for!")
    
    # Check if all questions answered
    if all_questions_answered(session):
        print(f"[ALL_QUESTIONS_ANSWERED] Processing with API")
        session.state = SessionState.PROCESSING_API
        await send_text_message(phone_number, "Perfecto! He recopilado toda la información. Déjame procesarla...")
        
        # Send to external API
        api_response = await send_to_external_api(session)
        response_message = await handle_api_response(session, api_response)
        await send_text_message(phone_number, response_message)
        
        # Continue conversation if API indicates to do so
        if session.state == SessionState.WAITING_FOR_ANSWER:
            next_question = get_current_question(session)
            if next_question:
                print(f"[CONTINUING_CONVERSATION] Next question: {next_question.text[:50]}...")
                await send_text_message(phone_number, next_question.text)
    else:
        # Ask next question
        next_question = get_current_question(session)
        if next_question:
            print(f"[ASKING_NEXT_QUESTION] {next_question.text[:50]}...")
            await send_text_message(phone_number, next_question.text)
        else:
            print(f"[ERROR] No next question available!")

def extract_text_from_message(msg: Dict[str, Any]) -> Optional[str]:
    t = msg.get("type")
    if t == "text":
        return msg.get("text", {}).get("body")
    if t == "button":
        return msg.get("button", {}).get("text")
    if t == "interactive":
        inter = msg.get("interactive", {})
        it = inter.get("type")
        if it == "button_reply":
            return inter.get("button_reply", {}).get("title")
        if it == "list_reply":
            return inter.get("list_reply", {}).get("title")
    return None

@app.get("/")
@app.get("/webhook")
async def verify_webhook(
    hub_mode: Optional[str] = Query(None, alias="hub.mode"),
    hub_verify_token: Optional[str] = Query(None, alias="hub.verify_token"),
    hub_challenge: Optional[str] = Query(None, alias="hub.challenge"),
):
    if (hub_mode or "").strip() == "subscribe" and (hub_verify_token or "").strip() == (VERIFY_TOKEN or "").strip():
        return PlainTextResponse(hub_challenge or "", status_code=200)
    return PlainTextResponse("Verificación fallida", status_code=403)

@app.post("/")
@app.post("/webhook")
async def receive_webhook(request: Request):
    data = await request.json()
    print("[INBOUND]", json.dumps(data, ensure_ascii=False))
    try:
        for entry in data.get("entry", []):
            for change in entry.get("changes", []):
                value = change.get("value", {})
                msgs = value.get("messages", [])
                if not msgs:
                    continue
                for msg in msgs:
                    wa_from = msg.get("from")
                    text = extract_text_from_message(msg)
                    if text:  # Only process if we have text
                        print(f"[MESSAGE] from={wa_from} text={text!r}")
                        await process_user_message(wa_from, text)
        return PlainTextResponse("OK", status_code=200)
    except Exception as e:
        print("[ERROR]", repr(e))
        return PlainTextResponse("ERROR", status_code=200)

@app.get("/send-test")
async def send_test(to: str, text: str = "Hola desde FastAPI 👋"):
    await send_text_message(to, text)
    return {"status": "sent"}

@app.get("/sessions")
async def get_sessions():
    """Debug endpoint to view current sessions"""
    return {phone: {
        "current_question": session.current_question_index,
        "state": session.state.value,
        "answers_count": len(session.answers),
        "last_activity": session.last_activity.isoformat()
    } for phone, session in user_sessions.items()}

@app.get("/reset-session/{phone_number}")
async def reset_session(phone_number: str):
    """Debug endpoint to reset a user's session"""
    if phone_number in user_sessions:
        old_session = user_sessions[phone_number]
        del user_sessions[phone_number]
        return {
            "status": f"Session reset for {phone_number}",
            "old_session": {
                "question_index": old_session.current_question_index,
                "answers_count": len(old_session.answers),
                "state": old_session.state.value
            }
        }
    return {"status": f"No session found for {phone_number}"}

@app.get("/debug-session/{phone_number}")
async def debug_session(phone_number: str):
    """Debug endpoint to view a specific user's session"""
    if phone_number in user_sessions:
        session = user_sessions[phone_number]
        return {
            "phone_number": phone_number,
            "current_question_index": session.current_question_index,
            "state": session.state.value,
            "answers": [{"question_id": a.question_id, "value": a.value, "timestamp": a.timestamp.isoformat()} for a in session.answers],
            "created_at": session.created_at.isoformat(),
            "last_activity": session.last_activity.isoformat(),
            "current_question": get_current_question(session).text if get_current_question(session) else None
        }
    return {"status": f"No session found for {phone_number}"}
