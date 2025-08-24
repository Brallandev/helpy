"""External API service for processing mental health data."""

import json
import httpx
from typing import Dict, Any

from app.config.settings import settings
from app.models.session import UserSession
from app.config.questions import MENTAL_HEALTH_QUESTIONS


class ExternalAPIService:
    """Service for communicating with external mental health processing API."""
    
    def __init__(self):
        self.http_client = httpx.AsyncClient(timeout=30.0)
        self.base_url = settings.EXTERNAL_API_URL
        self.questions_endpoint = f"{self.base_url}/questions"
        self.answers_endpoint = f"{self.base_url}/answers"
    
    def _prepare_payload(self, session: UserSession, include_followup: bool = False) -> Dict[str, Any]:
        """Prepare the payload for the external API.
        
        Args:
            session: The user session with collected answers
            include_followup: Whether to include follow-up answers in the payload
            
        Returns:
            The API payload in the new format
        """
        # Create question ID to question text mapping
        question_map = {q.id: q.text for q in MENTAL_HEALTH_QUESTIONS}
        
        # Build chat array with initial answers
        chat_array = []
        
        # Add initial answers
        for answer in session.answers:
            question_text = question_map.get(answer.question_id, answer.question_id)
            chat_array.append({
                "question": question_text,
                "answer": answer.value
            })
        
        # Add follow-up answers if requested and available
        if include_followup and session.followup_answers:
            for i, answer in enumerate(session.followup_answers):
                # For follow-up questions, we should use the actual question text from session.followup_questions
                if i < len(session.followup_questions):
                    question_text = session.followup_questions[i]
                else:
                    question_text = f"Pregunta adicional {i+1}"
                
                chat_array.append({
                    "question": question_text,
                    "answer": answer.value
                })
        
        return {
            "phone_number": session.phone_number,
            "chat": chat_array
        }
    
    async def send_data(self, session: UserSession) -> Dict[str, Any]:
        """Send collected mental health data to external API (initial questionnaire).
        
        Args:
            session: The user session with all answers
            
        Returns:
            The API response (may contain follow-up questions)
        """
        payload = self._prepare_payload(session, include_followup=False)
        
        # Enhanced logging for API call
        self._log_api_request(payload, "INITIAL", self.questions_endpoint)
        
        try:
            response = await self.http_client.post(
                self.questions_endpoint,
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            
            # Enhanced logging for API response
            result = self._log_api_response(response, "INITIAL")
            return result
            
        except Exception as e:
            print(f"\n❌ [API_ERROR] Connection failed: {repr(e)}")
            return {
                "error": f"API connection failed: {str(e)}",
                "continue_conversation": False
            }
    
    async def send_followup_data(self, session: UserSession) -> Dict[str, Any]:
        """Send follow-up answers to external API for final diagnosis.
        
        Args:
            session: The user session with initial and follow-up answers
            
        Returns:
            The API response with pre-diagnosis
        """
        payload = self._prepare_payload(session, include_followup=True)
        
        # Enhanced logging for API call
        self._log_api_request(payload, "FOLLOWUP", self.answers_endpoint)
        
        try:
            response = await self.http_client.post(
                self.answers_endpoint,
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            
            # Enhanced logging for API response
            result = self._log_api_response(response, "FOLLOWUP")
            return result
            
        except Exception as e:
            print(f"\n❌ [API_ERROR] Follow-up connection failed: {repr(e)}")
            return {
                "error": f"API connection failed: {str(e)}",
                "continue_conversation": False
            }
    
    def _log_api_request(self, payload: Dict[str, Any], request_type: str = "INITIAL", endpoint: str = None) -> None:
        """Log the API request in a formatted way."""
        if endpoint is None:
            endpoint = self.base_url
        
        print("\n" + "="*60)
        print(f"[API_CALL] SENDING {request_type} DATA TO EXTERNAL API")
        print("="*60)
        print(f"🎯 Endpoint: {endpoint}")
        print(f"📱 User: {payload.get('phone_number', 'Unknown')}")
        print(f"📊 Total Q&A Pairs: {len(payload.get('chat', []))}")
        print(f"🔄 Request Type: {request_type}")
        print("\n📋 COMPLETE API PAYLOAD:")
        print("-" * 40)
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        print("-" * 40)
        print("🚀 Sending request...")
        print("="*60 + "\n")
    
    def _log_api_response(self, response: httpx.Response, request_type: str = "INITIAL") -> Dict[str, Any]:
        """Log the API response and return parsed data."""
        print("\n" + "="*60)
        print(f"[API_RESPONSE] RECEIVED {request_type} RESPONSE FROM EXTERNAL API")
        print("="*60)
        print(f"📈 Status Code: {response.status_code}")
        print(f"🔄 Response Type: {request_type}")
        
        if hasattr(response, 'elapsed'):
            print(f"⏱️  Response Time: {response.elapsed.total_seconds():.2f}s")
        
        print("\n📨 RESPONSE BODY:")
        print("-" * 40)
        
        try:
            if response.status_code == 200:
                response_json = response.json()
                print(json.dumps(response_json, ensure_ascii=False, indent=2))
                print("-" * 40)
                
                # Different success messages based on response type
                if request_type == "INITIAL" and "questions" in response_json:
                    print("✅ Initial API call successful! Follow-up questions received.")
                elif request_type == "FOLLOWUP" and ("pre-diagnosis" in response_json or "pre_diagnosis" in response_json):
                    print("✅ Follow-up API call successful! Pre-diagnosis received.")
                else:
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
