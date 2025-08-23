import os, json
from typing import Any, Dict, List, Optional
from fastapi import FastAPI, Request, HTTPException, Query
from fastapi.responses import PlainTextResponse
from dotenv import load_dotenv
import httpx

load_dotenv()
WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN")
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID")
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")
GRAPH_API_VERSION = os.getenv("GRAPH_API_VERSION", "v20.0")
REPLY_TEXT = os.getenv("REPLY_TEXT", "¡Hola! 👋")

if not all([WHATSAPP_TOKEN, PHONE_NUMBER_ID, VERIFY_TOKEN]):
    raise RuntimeError("Faltan variables de entorno en .env")

GRAPH_URL = f"https://graph.facebook.com/{GRAPH_API_VERSION}/{PHONE_NUMBER_ID}/messages"
HEADERS = {"Authorization": f"Bearer {WHATSAPP_TOKEN}", "Content-Type": "application/json"}

app = FastAPI(title="WhatsApp Bot - Debug")
http = httpx.AsyncClient(timeout=20.0)

async def send_text_message(to: str, body: str) -> None:
    payload = {"messaging_product": "whatsapp", "to": to, "text": {"body": body}}
    r = await http.post(GRAPH_URL, headers=HEADERS, json=payload)
    print("[SEND]", r.status_code, r.text)  # <— ve el error aquí si falla
    r.raise_for_status()

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
    print("[INBOUND]", json.dumps(data, ensure_ascii=False))  # <— mira qué llega
    try:
        for entry in data.get("entry", []):
            for change in entry.get("changes", []):
                value = change.get("value", {})
                msgs = value.get("messages", [])
                if not msgs:
                    continue  # suele venir "statuses" también; lo ignoramos
                for msg in msgs:
                    wa_from = msg.get("from")
                    text = extract_text_from_message(msg)
                    print(f"[MESSAGE] from={wa_from} text={text!r}")
                    # Responder SIEMPRE con mensaje fijo
                    await send_text_message(wa_from, REPLY_TEXT)
        return PlainTextResponse("OK", status_code=200)
    except Exception as e:
        print("[ERROR]", repr(e))
        return PlainTextResponse("ERROR", status_code=200)

@app.get("/send-test")
async def send_test(to: str, text: str = "Hola desde FastAPI 👋"):
    await send_text_message(to, text)
    return {"status": "sent"}
