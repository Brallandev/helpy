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
    
    async def close(self):
        """Close the HTTP client."""
        await self.http_client.aclose()
