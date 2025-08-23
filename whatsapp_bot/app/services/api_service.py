"""External API service for processing mental health data."""

import json
import httpx
from typing import Dict, Any

from app.config.settings import settings
from app.models.session import UserSession


class ExternalAPIService:
    """Service for communicating with external mental health processing API."""
    
    def __init__(self):
        self.http_client = httpx.AsyncClient(timeout=30.0)
        self.api_url = settings.EXTERNAL_API_URL
    
    def _prepare_payload(self, session: UserSession) -> Dict[str, Any]:
        """Prepare the payload for the external API.
        
        Args:
            session: The user session with collected answers
            
        Returns:
            The API payload
        """
        return {
            "user_phone": session.phone_number,
            "timestamp": session.created_at.isoformat(),
            "chat": {answer.question_id: answer.value for answer in session.answers}
        }
    
    async def send_data(self, session: UserSession) -> Dict[str, Any]:
        """Send collected mental health data to external API.
        
        Args:
            session: The user session with all answers
            
        Returns:
            The API response
        """
        payload = self._prepare_payload(session)
        
        # Enhanced logging for API call
        self._log_api_request(payload)
        
        try:
            response = await self.http_client.post(
                self.api_url,
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            
            # Enhanced logging for API response
            result = self._log_api_response(response)
            return result
            
        except Exception as e:
            print(f"\n❌ [API_ERROR] Connection failed: {repr(e)}")
            return {
                "error": f"API connection failed: {str(e)}",
                "continue_conversation": False
            }
    
    def _log_api_request(self, payload: Dict[str, Any]) -> None:
        """Log the API request in a formatted way."""
        print("\n" + "="*60)
        print("[API_CALL] SENDING DATA TO EXTERNAL API")
        print("="*60)
        print(f"🎯 Endpoint: {self.api_url}")
        print(f"📱 User: {payload.get('user_phone', 'Unknown')}")
        print(f"📊 Total Answers: {len(payload.get('chat', {}))}")
        print("\n📋 COMPLETE API PAYLOAD:")
        print("-" * 40)
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        print("-" * 40)
        print("🚀 Sending request...")
        print("="*60 + "\n")
    
    def _log_api_response(self, response: httpx.Response) -> Dict[str, Any]:
        """Log the API response and return parsed data."""
        print("\n" + "="*60)
        print("[API_RESPONSE] RECEIVED RESPONSE FROM EXTERNAL API")
        print("="*60)
        print(f"📈 Status Code: {response.status_code}")
        
        if hasattr(response, 'elapsed'):
            print(f"⏱️  Response Time: {response.elapsed.total_seconds():.2f}s")
        
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
                return {
                    "error": f"API error: {response.status_code}",
                    "continue_conversation": False
                }
        except Exception as parse_error:
            print(f"❌ Failed to parse response: {response.text}")
            print(f"🚨 Parse error: {str(parse_error)}")
            print("-" * 40)
            print("="*60 + "\n")
            return {
                "error": f"API parse error: {str(parse_error)}",
                "continue_conversation": False
            }
    
    async def close(self):
        """Close the HTTP client."""
        await self.http_client.aclose()
