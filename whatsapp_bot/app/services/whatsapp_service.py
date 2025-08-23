"""WhatsApp messaging service."""

import httpx
from typing import Dict, Any

from app.config.settings import settings


class WhatsAppService:
    """Service for sending messages through WhatsApp Business API."""
    
    def __init__(self):
        self.http_client = httpx.AsyncClient(timeout=30.0)
        self.graph_url = settings.GRAPH_URL
        self.headers = settings.HEADERS
    
    async def send_text_message(self, to: str, body: str) -> Dict[str, Any]:
        """Send a text message via WhatsApp.
        
        Args:
            to: The recipient's phone number
            body: The message text
            
        Returns:
            The API response
            
        Raises:
            httpx.HTTPStatusError: If the API request fails
        """
        payload = {
            "messaging_product": "whatsapp",
            "to": to,
            "text": {"body": body}
        }
        
        print(f"[WHATSAPP_SEND] To: {to}, Message: {body[:50]}...")
        
        response = await self.http_client.post(
            self.graph_url,
            headers=self.headers,
            json=payload
        )
        
        print(f"[WHATSAPP_RESPONSE] Status: {response.status_code}")
        response.raise_for_status()
        
        return response.json()
    
    async def send_interactive_message(self, to: str, body_text: str, button_text: str, buttons: list) -> Dict[str, Any]:
        """Send an interactive message with buttons via WhatsApp.
        
        Args:
            to: The recipient's phone number
            body_text: The main message text
            button_text: The button section text
            buttons: List of button dictionaries with 'id' and 'title'
            
        Returns:
            The API response
            
        Raises:
            httpx.HTTPStatusError: If the API request fails
        """
        payload = {
            "messaging_product": "whatsapp",
            "to": to,
            "type": "interactive",
            "interactive": {
                "type": "button",
                "body": {
                    "text": body_text
                },
                "footer": {
                    "text": button_text
                },
                "action": {
                    "buttons": buttons
                }
            }
        }
        
        print(f"[WHATSAPP_SEND_INTERACTIVE] To: {to}, Buttons: {len(buttons)}")
        print(f"[INTERACTIVE_PAYLOAD] {payload}")
        
        try:
            response = await self.http_client.post(
                self.graph_url,
                headers=self.headers,
                json=payload
            )
            
            print(f"[WHATSAPP_RESPONSE] Status: {response.status_code}")
            print(f"[WHATSAPP_RESPONSE_BODY] {response.text}")
            
            if response.status_code != 200:
                print(f"[ERROR] Interactive message failed: {response.text}")
                # Fallback: send as regular text message with instructions
                fallback_message = f"{body_text}\n\n{button_text}\n\nPor favor responde 'Sí, acepto' o 'No, gracias'"
                return await self.send_text_message(to, fallback_message)
            
            response.raise_for_status()
            return response.json()
            
        except Exception as e:
            print(f"[ERROR] Interactive message exception: {str(e)}")
            # Fallback: send as regular text message
            fallback_message = f"{body_text}\n\n{button_text}\n\nPor favor responde 'Sí, acepto' o 'No, gracias'"
            return await self.send_text_message(to, fallback_message)
    
    async def close(self):
        """Close the HTTP client."""
        await self.http_client.aclose()
