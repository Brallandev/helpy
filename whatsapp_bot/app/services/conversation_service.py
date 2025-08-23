"""Conversation flow management service."""

from typing import Dict, Any, List

from app.models.session import UserSession, SessionState
from app.models.question import Answer, Question
from app.config.questions import MENTAL_HEALTH_QUESTIONS
from app.utils.session_manager import SessionManager
from app.services.whatsapp_service import WhatsAppService
from app.services.api_service import ExternalAPIService


class ConversationService:
    """Service for managing conversation flow and logic."""
    
    def __init__(
        self,
        session_manager: SessionManager,
        whatsapp_service: WhatsAppService,
        api_service: ExternalAPIService
    ):
        self.session_manager = session_manager
        self.whatsapp_service = whatsapp_service
        self.api_service = api_service
    
    async def process_user_message(self, phone_number: str, message_text: str) -> None:
        """Process a user message and handle the conversation flow.
        
        Args:
            phone_number: The user's phone number
            message_text: The text content of the message
        """
        session = self.session_manager.get_or_create_session(phone_number)
        
        print(f"[SESSION] User: {phone_number}, State: {session.state.value}, "
              f"Question: {session.current_question_index}, Answers: {len(session.answers)}")
        print(f"[MESSAGE_RECEIVED] Text: {message_text!r}")
        
        # Handle different session states
        if session.state == SessionState.CONVERSATION_ENDED:
            await self._handle_conversation_restart(phone_number, session)
            return
        
        if session.state == SessionState.PROCESSING_API:
            await self._handle_processing_state(phone_number)
            return
        
        # Handle the main conversation flow
        await self._handle_conversation_flow(session, message_text)
    
    async def _handle_conversation_restart(self, phone_number: str, session: UserSession) -> None:
        """Handle restarting a conversation that has ended."""
        print(f"[CONVERSATION_ENDED] Resetting session for {phone_number}")
        
        await self.whatsapp_service.send_text_message(
            phone_number,
            "Esta conversación ha terminado. Envía cualquier mensaje para comenzar una nueva consulta."
        )
        
        # Reset session for new conversation
        self.session_manager.reset_session(phone_number)
        new_session = self.session_manager.get_or_create_session(phone_number)
        
        print(f"[SESSION_RESET] New session: index={new_session.current_question_index}, "
              f"answers={len(new_session.answers)}")
        
        # Ask the first question of the new conversation
        current_question = self.session_manager.get_current_question(new_session)
        if current_question:
            print(f"[ASKING_FIRST_QUESTION] {current_question.text[:50]}...")
            await self.whatsapp_service.send_text_message(phone_number, current_question.text)
    
    async def _handle_processing_state(self, phone_number: str) -> None:
        """Handle messages received while processing API call."""
        print("[PROCESSING_API] Rejecting message while processing")
        await self.whatsapp_service.send_text_message(
            phone_number,
            "Estoy procesando tu información, por favor espera un momento..."
        )
    
    async def _handle_conversation_flow(self, session: UserSession, message_text: str) -> None:
        """Handle the main conversation flow logic."""
        # Simple logic: if we haven't asked the first question yet, ask it
        if not session.first_question_asked:
            print("[FIRST_MESSAGE] Asking first question")
            current_question = self.session_manager.get_current_question(session)
            if current_question:
                print(f"[ASKING_QUESTION] {current_question.text[:50]}...")
                await self.whatsapp_service.send_text_message(
                    session.phone_number, current_question.text
                )
                session.first_question_asked = True
            return
        
        # We've asked the first question, so this message is an answer
        print(f"[PROCESSING_ANSWER] Received: {message_text}")
        current_question = self.session_manager.get_current_question(session)
        
        if current_question:
            print(f"[SAVING_ANSWER] For question '{current_question.id}': {message_text}")
            self._save_answer(session, current_question, message_text)
            print(f"[ANSWER_SAVED] {current_question.id}: {message_text} "
                  f"(new index: {session.current_question_index})")
        else:
            print("[WARNING] No current question to save answer for!")
        
        # Check if all questions answered
        if self.session_manager.all_questions_answered(session):
            await self._handle_all_questions_answered(session)
        else:
            # Ask next question
            await self._ask_next_question(session)
    
    def _save_answer(self, session: UserSession, question: Question, answer_text: str) -> None:
        """Save a user's answer to a question."""
        answer = Answer(question_id=question.id, value=answer_text)
        session.answers.append(answer)
        session.current_question_index += 1
    
    async def _ask_next_question(self, session: UserSession) -> None:
        """Ask the next question in the sequence."""
        next_question = self.session_manager.get_current_question(session)
        if next_question:
            print(f"[ASKING_NEXT_QUESTION] {next_question.text[:50]}...")
            await self.whatsapp_service.send_text_message(
                session.phone_number, next_question.text
            )
        else:
            print("[ERROR] No next question available!")
    
    async def _handle_all_questions_answered(self, session: UserSession) -> None:
        """Handle the case when all questions have been answered."""
        print("[ALL_QUESTIONS_ANSWERED] Processing with API")
        session.state = SessionState.PROCESSING_API
        
        await self.whatsapp_service.send_text_message(
            session.phone_number,
            "Perfecto! He recopilado toda la información. Déjame procesarla..."
        )
        
        # Send to external API
        api_response = await self.api_service.send_data(session)
        response_message = await self._handle_api_response(session, api_response)
        await self.whatsapp_service.send_text_message(session.phone_number, response_message)
        
        # Continue conversation if API indicates to do so
        if session.state == SessionState.WAITING_FOR_ANSWER:
            next_question = self.session_manager.get_current_question(session)
            if next_question:
                print(f"[CONTINUING_CONVERSATION] Next question: {next_question.text[:50]}...")
                await self.whatsapp_service.send_text_message(
                    session.phone_number, next_question.text
                )
    
    async def _handle_api_response(self, session: UserSession, api_response: Dict[str, Any]) -> str:
        """Process API response and generate appropriate message for user."""
        if "error" in api_response:
            session.state = SessionState.CONVERSATION_ENDED
            return "Lo siento, ha ocurrido un error procesando tu información. Por favor intenta más tarde."
        
        # Check if conversation should continue
        should_continue = api_response.get("continue_conversation", False)
        
        if not should_continue:
            session.state = SessionState.CONVERSATION_ENDED
            message = api_response.get(
                "final_message",
                "Gracias por tu tiempo. Tu consulta ha sido procesada."
            )
            return message
        
        # If conversation continues, the API can provide new questions or messages
        new_message = api_response.get("message", "Gracias por la información.")
        
        # Check if API provides new questions to ask
        new_questions = api_response.get("additional_questions", [])
        if new_questions:
            # Add new questions to the list (extend conversation dynamically)
            global MENTAL_HEALTH_QUESTIONS
            for q_data in new_questions:
                new_question = Question(
                    id=q_data.get("id", f"dynamic_{len(MENTAL_HEALTH_QUESTIONS)}"),
                    text=q_data.get("text", ""),
                    required=q_data.get("required", True)
                )
                MENTAL_HEALTH_QUESTIONS.append(new_question)
        
        # Reset to continue asking questions
        session.state = SessionState.WAITING_FOR_ANSWER
        return new_message
