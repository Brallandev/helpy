"""External API service for processing mental health data."""

import json
import httpx
import asyncio
from typing import Dict, Any

from app.config.settings import settings
from app.models.session import UserSession
from app.config.questions import MENTAL_HEALTH_QUESTIONS


class ExternalAPIService:
    """Service for communicating with external mental health processing API."""
    
    def __init__(self):
        # Configure timeout with more specific settings
        timeout_config = httpx.Timeout(
            connect=10.0,  # Connection timeout
            read=60.0,     # Read timeout (longer for processing)
            write=10.0,    # Write timeout
            pool=5.0       # Pool timeout
        )
        self.http_client = httpx.AsyncClient(timeout=timeout_config)
        self.base_url = settings.EXTERNAL_API_URL
        self.questions_endpoint = f"{self.base_url}/questions"
        self.answers_endpoint = f"{self.base_url}/answers"
        self.max_retries = 3
    
    async def _make_api_request_with_retry(self, endpoint: str, payload: Dict[str, Any], request_type: str) -> Dict[str, Any]:
        """Make API request with retry logic and exponential backoff.
        
        Args:
            endpoint: The API endpoint to call
            payload: The request payload
            request_type: Type of request (INITIAL/FOLLOWUP) for logging
            
        Returns:
            The API response or error response
        """
        last_exception = None
        
        for attempt in range(self.max_retries):
            try:
                print(f"[API_RETRY] Attempt {attempt + 1}/{self.max_retries} for {request_type} request")
                
                response = await self.http_client.post(
                    endpoint,
                    json=payload,
                    headers={"Content-Type": "application/json"}
                )
                
                # Enhanced logging for API response
                result = self._log_api_response(response, request_type)
                print(f"✅ [API_SUCCESS] {request_type} request succeeded on attempt {attempt + 1}")
                return result
                
            except httpx.TimeoutException as e:
                last_exception = e
                wait_time = 2 ** attempt  # Exponential backoff: 1s, 2s, 4s
                print(f"⏰ [API_TIMEOUT] {request_type} request timed out on attempt {attempt + 1}")
                print(f"   Timeout details: {repr(e)}")
                
                if attempt < self.max_retries - 1:  # Don't wait after the last attempt
                    print(f"   Retrying in {wait_time} seconds...")
                    await asyncio.sleep(wait_time)
                
            except httpx.RequestError as e:
                last_exception = e
                wait_time = 2 ** attempt
                print(f"🌐 [API_CONNECTION_ERROR] {request_type} request failed on attempt {attempt + 1}")
                print(f"   Connection error: {repr(e)}")
                
                if attempt < self.max_retries - 1:
                    print(f"   Retrying in {wait_time} seconds...")
                    await asyncio.sleep(wait_time)
                
            except Exception as e:
                last_exception = e
                print(f"❌ [API_UNEXPECTED_ERROR] {request_type} request failed with unexpected error: {repr(e)}")
                break  # Don't retry on unexpected errors
        
        # All retries failed
        print(f"\n❌ [API_ERROR] {request_type} connection failed after {self.max_retries} attempts")
        print(f"   Final error: {repr(last_exception)}")
        
        return {
            "error": f"API connection failed after {self.max_retries} attempts: {str(last_exception)}",
            "continue_conversation": False,
            "retry_attempts": self.max_retries,
            "final_error_type": type(last_exception).__name__
        }
    
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
        
        # Use retry logic for the API call
        return await self._make_api_request_with_retry(self.questions_endpoint, payload, "INITIAL")
    
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
        
        # Use retry logic for the API call
        return await self._make_api_request_with_retry(self.answers_endpoint, payload, "FOLLOWUP")
    
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
