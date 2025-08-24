"""Database service for storing patient intake data."""

import json
import httpx
from typing import Dict, Any

from app.config.settings import settings
from app.models.session import UserSession
from app.config.questions import MENTAL_HEALTH_QUESTIONS


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
            The database API payload in the new format
        """
        # Create question ID to question text mapping
        question_map = {q.id: q.text for q in MENTAL_HEALTH_QUESTIONS}
        
        # Build chat array with initial answers
        chat_array = []
        for answer in session.answers:
            question_text = question_map.get(answer.question_id, answer.question_id)
            chat_array.append({
                "question": question_text,
                "answer": answer.value
            })
        
        return {
            "phone_number": session.phone_number,
            "chat": chat_array
        }
    
    def _prepare_complete_payload(self, session: UserSession, diagnostic_data: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare the complete payload for the database API with the new schema.
        
        Args:
            session: The user session with all answers
            diagnostic_data: The diagnostic response from the API
            
        Returns:
            The database API payload in the new schema format
        """
        # Create question ID to question text mapping
        question_map = {q.id: q.text for q in MENTAL_HEALTH_QUESTIONS}
        
        # Build initial questions and LLM questions
        initial_questions_text = ""
        llm_questions_text = ""
        
        # Process initial questions
        for answer in session.answers:
            question_text = question_map.get(answer.question_id, answer.question_id)
            initial_questions_text += f"Q: {question_text}\nA: {answer.value}\n\n"
        
        # Process follow-up questions if they exist
        if session.followup_questions and session.followup_answers:
            for i, followup_answer in enumerate(session.followup_answers):
                if i < len(session.followup_questions):
                    question_text = session.followup_questions[i]
                    llm_questions_text += f"Q: {question_text}\nA: {followup_answer.value}\n\n"
        
        # Generate unique identifier based on phone number and timestamp
        number = f"{session.phone_number}_{session.created_at.strftime('%Y%m%d_%H%M%S')}"
        
        return {
            "number": number,
            "initial_questions": initial_questions_text.strip(),
            "llm_questions": llm_questions_text.strip(),
            "pre_diagnosis": diagnostic_data.get("pre_diagnosis", "") or diagnostic_data.get("pre-diagnosis", ""),
            "comments": diagnostic_data.get("comments", ""),
            "score": diagnostic_data.get("score", ""),
            "filled_doc": diagnostic_data.get("filled_doc", "")
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
    
    async def store_complete_diagnostic_data(self, session: UserSession, diagnostic_data: Dict[str, Any]) -> Dict[str, Any]:
        """Store complete diagnostic data with the new schema format.
        
        Args:
            session: The user session with all answers
            diagnostic_data: The diagnostic response from the API
            
        Returns:
            Dictionary with success status and response data
        """
        payload = self._prepare_complete_payload(session, diagnostic_data)
        
        # Enhanced logging for database call
        self._log_complete_database_request(payload)
        
        try:
            response = await self.http_client.post(
                self.database_url,
                json=payload,
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {self.auth_token}"
                }
            )
            
            # Enhanced logging for database response
            result = self._log_database_response(response)
            return result
            
        except Exception as e:
            print(f"\n❌ [COMPLETE_DATABASE_ERROR] Connection failed: {repr(e)}")
            return {
                "error": f"Complete database connection failed: {str(e)}",
                "success": False
            }
    
    def _log_complete_database_request(self, payload: Dict[str, Any]) -> None:
        """Log the complete database request in a formatted way."""
        print("\n" + "="*60)
        print("[COMPLETE_DATABASE_CALL] SENDING COMPLETE DATA TO DATABASE")
        print("="*60)
        print(f"🏥 Database URL: {self.database_url}")
        print(f"🔢 Session Number: {payload.get('number', 'Unknown')}")
        print(f"📋 Initial Questions Length: {len(payload.get('initial_questions', ''))}")
        print(f"🤖 LLM Questions Length: {len(payload.get('llm_questions', ''))}")
        print(f"🩺 Pre-diagnosis Length: {len(payload.get('pre_diagnosis', ''))}")
        print(f"💬 Comments Length: {len(payload.get('comments', ''))}")
        print(f"📊 Score: {payload.get('score', 'Unknown')}")
        print(f"📄 Filled Doc Length: {len(payload.get('filled_doc', ''))}")
        
        print("\n📤 COMPLETE PAYLOAD:")
        print("-" * 40)
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        print("-" * 40)
    
    def _log_database_request(self, payload: Dict[str, Any]) -> None:
        """Log the database request in a formatted way."""
        print("\n" + "="*60)
        print("[DATABASE_CALL] STORING DATA IN DATABASE")
        print("="*60)
        print(f"🎯 Endpoint: {self.database_url}")
        print(f"📱 User: {payload.get('phone_number', 'Unknown')}")
        print(f"📊 Total Q&A Pairs: {len(payload.get('chat', []))}")
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
