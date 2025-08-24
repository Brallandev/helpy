"""Database service for storing patient intake data."""

import json
import httpx
from typing import Dict, Any

from app.config.settings import settings
from app.models.session import UserSession


class DatabaseService:
    """Service for storing mental health intake data in the database."""
    
    def __init__(self):
        self.http_client = httpx.AsyncClient(timeout=30.0)
        self.database_url = settings.DATABASE_API_URL
        self.auth_token = settings.DATABASE_API_TOKEN
    
    def _prepare_payload(self, session: UserSession) -> Dict[str, Any]:
        """Prepare the payload for the database API.
        
        Args:
            session: The user session with collected answers
            
        Returns:
            The database API payload
        """
        return {
            "user_phone": session.phone_number,
            "timestamp": session.created_at.isoformat(),
            "answers": {answer.question_id: answer.value for answer in session.answers}
        }
    
    async def store_intake_data(self, session: UserSession) -> Dict[str, Any]:
        """Store collected mental health intake data in the database.
        
        Args:
            session: The user session with all answers
            
        Returns:
            The database API response
        """
        payload = self._prepare_payload(session)
        
        # Enhanced logging for database call
        self._log_database_request(payload)
        
        try:
            headers = {
                "Authorization": f"Bearer {self.auth_token}",
                "Content-Type": "application/json"
            }
            
            response = await self.http_client.post(
                self.database_url,
                json=payload,
                headers=headers
            )
            
            # Enhanced logging for database response
            result = self._log_database_response(response)
            return result
            
        except Exception as e:
            print(f"\n❌ [DATABASE_ERROR] Connection failed: {repr(e)}")
            return {
                "error": f"Database connection failed: {str(e)}",
                "success": False
            }
    
    def _log_database_request(self, payload: Dict[str, Any]) -> None:
        """Log the database request in a formatted way."""
        print("\n" + "="*60)
        print("[DATABASE_CALL] STORING DATA IN DATABASE")
        print("="*60)
        print(f"🎯 Endpoint: {self.database_url}")
        print(f"📱 User: {payload.get('user_phone', 'Unknown')}")
        print(f"📊 Total Answers: {len(payload.get('answers', {}))}")
        print(f"🔑 Auth: Bearer {self.auth_token[:20]}...{self.auth_token[-10:]}")
        print("\n📋 COMPLETE DATABASE PAYLOAD:")
        print("-" * 40)
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        print("-" * 40)
        print("🚀 Sending to database...")
        print("="*60 + "\n")
    
    def _log_database_response(self, response: httpx.Response) -> Dict[str, Any]:
        """Log the database response and return parsed data."""
        print("\n" + "="*60)
        print("[DATABASE_RESPONSE] RECEIVED RESPONSE FROM DATABASE")
        print("="*60)
        print(f"📈 Status Code: {response.status_code}")
        
        if hasattr(response, 'elapsed'):
            print(f"⏱️  Response Time: {response.elapsed.total_seconds():.2f}s")
        
        print("\n📨 RESPONSE BODY:")
        print("-" * 40)
        
        try:
            if response.status_code in [200, 201]:
                try:
                    response_json = response.json()
                    print(json.dumps(response_json, ensure_ascii=False, indent=2))
                except:
                    print(f"Success response (no JSON): {response.text}")
                    response_json = {"success": True, "message": "Data stored successfully"}
                print("-" * 40)
                print("✅ Database storage successful!")
                print("="*60 + "\n")
                return {**response_json, "success": True}
            else:
                print(f"❌ Error Response: {response.text}")
                print("-" * 40)
                print(f"🚨 Database storage failed with status {response.status_code}")
                print("="*60 + "\n")
                return {
                    "error": f"Database error: {response.status_code}",
                    "success": False,
                    "details": response.text
                }
        except Exception as parse_error:
            print(f"❌ Failed to parse response: {response.text}")
            print(f"🚨 Parse error: {str(parse_error)}")
            print("-" * 40)
            print("="*60 + "\n")
            return {
                "error": f"Database parse error: {str(parse_error)}",
                "success": False
            }
    
    async def close(self):
        """Close the HTTP client."""
        await self.http_client.aclose()
