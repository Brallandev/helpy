"""Conversation flow management service."""

from typing import Dict, Any, List

from app.models.session import UserSession, SessionState
from app.models.question import Answer, Question
from app.config.questions import MENTAL_HEALTH_QUESTIONS
from app.config.messages import (
    GREETING_MESSAGE, 
    CONSENT_MESSAGE, 
    CONSENT_DECLINED_MESSAGE, 
    CONSENT_BUTTONS, 
    CONSENT_BUTTON_TEXT
)
from app.utils.session_manager import SessionManager
from app.services.whatsapp_service import WhatsAppService
from app.services.api_service import ExternalAPIService
from app.services.database_service import DatabaseService
from app.services.doctor_service import DoctorService


class ConversationService:
    """Service for managing conversation flow and logic."""
    
    def __init__(
        self,
        session_manager: SessionManager,
        whatsapp_service: WhatsAppService,
        api_service: ExternalAPIService,
        database_service: DatabaseService,
        doctor_service: DoctorService
    ):
        self.session_manager = session_manager
        self.whatsapp_service = whatsapp_service
        self.api_service = api_service
        self.database_service = database_service
        self.doctor_service = doctor_service
    
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
        
        if session.state == SessionState.CONSENT_DECLINED:
            await self._handle_consent_declined(phone_number, session)
            return
        
        if session.state == SessionState.PROCESSING_API:
            await self._handle_processing_state(phone_number)
            return
        
        if session.state == SessionState.WAITING_FOR_CONSENT:
            await self._handle_consent_flow(session, message_text)
            return
        
        if session.state == SessionState.WAITING_FOR_FOLLOWUP:
            await self._handle_followup_flow(session, message_text)
            return
        
        if session.state == SessionState.WAITING_FOR_DOCTOR_APPROVAL:
            await self._handle_waiting_for_doctor_approval(phone_number)
            return
        
        # Handle the main conversation flow (questions)
        # Note: Doctor responses are now handled in main.py routing, not here
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
        
        # Start the consent flow for the new conversation
        await self._start_consent_flow(new_session)
    
    async def _handle_consent_declined(self, phone_number: str, session: UserSession) -> None:
        """Handle when user has declined consent."""
        print(f"[CONSENT_DECLINED] User declined consent, sending goodbye message")
        await self.whatsapp_service.send_text_message(phone_number, CONSENT_DECLINED_MESSAGE)
        session.state = SessionState.CONVERSATION_ENDED
    
    async def _handle_consent_flow(self, session: UserSession, message_text: str) -> None:
        """Handle the consent flow logic."""
        # Send greeting first if not sent
        if not session.greeting_sent:
            print("[SENDING_GREETING] Sending greeting message")
            await self.whatsapp_service.send_text_message(session.phone_number, GREETING_MESSAGE)
            session.greeting_sent = True
            
            # Send consent message with buttons
            print("[SENDING_CONSENT] Sending consent message with buttons")
            await self.whatsapp_service.send_interactive_message(
                session.phone_number,
                CONSENT_MESSAGE,
                CONSENT_BUTTON_TEXT,
                CONSENT_BUTTONS
            )
            return
        
        # Process consent response
        await self._process_consent_response(session, message_text)
    
    async def _start_consent_flow(self, session: UserSession) -> None:
        """Start the consent flow for a new session."""
        print("[STARTING_CONSENT_FLOW] Beginning consent process")
        session.state = SessionState.WAITING_FOR_CONSENT
        
        # Send greeting message
        print("[SENDING_GREETING] Sending greeting message")
        await self.whatsapp_service.send_text_message(session.phone_number, GREETING_MESSAGE)
        session.greeting_sent = True
        
        # Send consent message with buttons
        print("[SENDING_CONSENT] Sending consent message with buttons")
        await self.whatsapp_service.send_interactive_message(
            session.phone_number,
            CONSENT_MESSAGE,
            CONSENT_BUTTON_TEXT,
            CONSENT_BUTTONS
        )
    
    async def _process_consent_response(self, session: UserSession, message_text: str) -> None:
        """Process the user's consent response."""
        message_lower = message_text.lower().strip()
        
        # Check for positive consent (button response or text)
        if (message_lower in ["sí, acepto", "si, acepto", "si acepto", "sí acepto", "acepto", "si", "sí", "yes"] or
            "consent_yes" in message_text):
            print("[CONSENT_ACCEPTED] User accepted consent")
            session.consent_given = True
            session.state = SessionState.WAITING_FOR_ANSWER
            
            # Start the questionnaire
            await self._start_questionnaire(session)
            
        # Check for negative consent
        elif (message_lower in ["no, gracias", "no gracias", "no", "decline"] or
              "consent_no" in message_text):
            print("[CONSENT_DECLINED] User declined consent")
            session.consent_given = False
            session.state = SessionState.CONSENT_DECLINED
            await self.whatsapp_service.send_text_message(session.phone_number, CONSENT_DECLINED_MESSAGE)
            
        else:
            # Ask for clarification
            print("[CONSENT_UNCLEAR] User response unclear, asking for clarification")
            await self.whatsapp_service.send_text_message(
                session.phone_number,
                "Por favor, responde 'Sí, acepto' para continuar o 'No, gracias' si no deseas proceder."
            )
    
    async def _start_questionnaire(self, session: UserSession) -> None:
        """Start the mental health questionnaire."""
        print("[STARTING_QUESTIONNAIRE] Beginning mental health questions")
        current_question = self.session_manager.get_current_question(session)
        if current_question:
            print(f"[ASKING_FIRST_QUESTION] {current_question.text[:50]}...")
            await self.whatsapp_service.send_text_message(session.phone_number, current_question.text)
            session.first_question_asked = True
    
    async def _handle_processing_state(self, phone_number: str) -> None:
        """Handle messages received while processing API call."""
        print("[PROCESSING_API] Rejecting message while processing")
        await self.whatsapp_service.send_text_message(
            phone_number,
            "Estoy procesando tu información, por favor espera un momento..."
        )
    
    async def _handle_conversation_flow(self, session: UserSession, message_text: str) -> None:
        """Handle the main conversation flow logic for questionnaire phase."""
        # User should have consent at this point
        if not session.consent_given:
            print("[ERROR] User in questionnaire phase without consent!")
            return
        
        # If we haven't started the questionnaire yet, start it
        if not session.first_question_asked:
            await self._start_questionnaire(session)
            return
        
        # We're in the questionnaire, so this message is an answer
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
        print("[ALL_QUESTIONS_ANSWERED] Processing with API and Database")
        session.state = SessionState.PROCESSING_API
        
        await self.whatsapp_service.send_text_message(
            session.phone_number,
            "Perfecto! muchas gracias por responder c: , Saber esto me permitira entenderte un poco mejor, pero ahora, me gustaria hacerte unas preguntas mas personalizadas. Déjame pensar un instante..., no te preocupes! te escribire apenas termine de pensar."
        )
        
        # Store data in database first (most important)
        print("[STORING_IN_DATABASE] Saving intake data...")
        database_response = await self.database_service.store_intake_data(session)
        
        if database_response.get("success", False):
            print("[DATABASE_SUCCESS] Intake data stored successfully")
        else:
            print(f"[DATABASE_ERROR] Failed to store data: {database_response.get('error', 'Unknown error')}")
        
        # Send to external API for processing (should return follow-up questions)
        print("[PROCESSING_WITH_API] Sending initial data to external API...")
        api_response = await self.api_service.send_data(session)
        
        # Check if we received follow-up questions
        if "questions" in api_response and api_response["questions"]:
            await self._handle_followup_questions(session, api_response["questions"], database_response)
        else:
            # No follow-up questions, handle as final response
            response_message = await self._handle_api_response(session, api_response)
            
            # Add database status to response if there was an error
            if not database_response.get("success", False):
                response_message = f"{response_message}\n\n⚠️ Nota: Hubo un problema guardando los datos, pero tu información ha sido procesada."
            
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
    
    async def _handle_followup_questions(self, session: UserSession, questions: list, database_response: dict) -> None:
        """Handle follow-up questions received from the API."""
        print(f"[FOLLOWUP_QUESTIONS] Received {len(questions)} follow-up questions")
        
        # Store follow-up questions in session
        session.followup_questions = questions
        session.current_followup_index = 0
        session.state = SessionState.WAITING_FOR_FOLLOWUP
        
        # Add database status message if there was an error
        status_message = ""
        if not database_response.get("success", False):
            status_message = "\n\n⚠️ Nota: Hubo un problema guardando los datos iniciales, pero continuaré con las preguntas adicionales."
        
        # Send transition message and first follow-up question
        await self.whatsapp_service.send_text_message(
            session.phone_number,
            f"Gracias por completar las preguntas iniciales. Ahora tengo algunas preguntas adicionales para brindarte un mejor análisis.{status_message}"
        )
        
        # Ask first follow-up question
        await self._ask_current_followup_question(session)
    
    async def _handle_followup_flow(self, session: UserSession, message_text: str) -> None:
        """Handle the follow-up questions flow."""
        print(f"[FOLLOWUP_FLOW] Processing answer to follow-up question {session.current_followup_index + 1}")
        
        # Save the current follow-up answer
        self._save_followup_answer(session, message_text)
        
        # Check if all follow-up questions have been answered
        if session.current_followup_index >= len(session.followup_questions):
            await self._handle_all_followup_answered(session)
        else:
            # Ask next follow-up question
            await self._ask_current_followup_question(session)
    
    def _save_followup_answer(self, session: UserSession, answer_text: str) -> None:
        """Save a user's answer to a follow-up question."""
        from app.models.question import Answer
        
        # Create answer with a generic ID for follow-up questions
        answer = Answer(
            question_id=f"followup_{session.current_followup_index + 1}",
            value=answer_text
        )
        session.followup_answers.append(answer)
        session.current_followup_index += 1
        
        print(f"[FOLLOWUP_ANSWER_SAVED] followup_{session.current_followup_index}: {answer_text}")
    
    async def _ask_current_followup_question(self, session: UserSession) -> None:
        """Ask the current follow-up question."""
        if session.current_followup_index < len(session.followup_questions):
            question_text = session.followup_questions[session.current_followup_index]
            question_number = session.current_followup_index + 1
            total_questions = len(session.followup_questions)
            
            print(f"[ASKING_FOLLOWUP] Question {question_number}/{total_questions}")
            await self.whatsapp_service.send_text_message(
                session.phone_number,
                f"Pregunta adicional {question_number}/{total_questions}:\n\n{question_text}"
            )
        else:
            print("[ERROR] No current follow-up question available!")
    
    async def _handle_all_followup_answered(self, session: UserSession) -> None:
        """Handle when all follow-up questions have been answered."""
        print("[ALL_FOLLOWUP_ANSWERED] Processing final data with API")
        session.state = SessionState.PROCESSING_API
        
        await self.whatsapp_service.send_text_message(
            session.phone_number,
            "Excelente! He completado todas las preguntas. Ahora analizaré toda la información para darte un diagnóstico preliminar..."
        )
        
        # Send complete data (initial + follow-up) to API for final diagnosis
        print("[PROCESSING_FINAL_DATA] Sending complete data to external API...")
        api_response = await self.api_service.send_followup_data(session)
        
        # Handle the pre-diagnosis response (check both possible field names)
        if "pre-diagnosis" in api_response or "pre_diagnosis" in api_response:
            await self._handle_pre_diagnosis(session, api_response)
        else:
            # Fallback response
            response_message = await self._handle_api_response(session, api_response)
            await self.whatsapp_service.send_text_message(session.phone_number, response_message)
            session.state = SessionState.CONVERSATION_ENDED
    
    async def _handle_pre_diagnosis(self, session: UserSession, api_response: dict) -> None:
        """Handle and display the pre-diagnosis to the user."""
        print("[PRE_DIAGNOSIS] Processing and sending pre-diagnosis")
        
        session.pre_diagnosis = api_response
        
        # Handle both possible field names from API
        pre_diagnosis = api_response.get("pre-diagnosis", "") or api_response.get("pre_diagnosis", "")
        comments = api_response.get("comments", "")
        score = api_response.get("score", "")
        
        # Format the pre-diagnosis message
        diagnosis_message = "🏥 **TU ANÁLISIS PRELIMINAR**\n\n"
        
        if score:
            diagnosis_message += f"📊 **Nivel de Prioridad**: {score}\n\n"
        
        if pre_diagnosis:
            diagnosis_message += f"📋 **Diagnóstico Preliminar**:\n{pre_diagnosis}\n\n"
        
        if comments:
            diagnosis_message += f"💬 **Comentarios y Recomendaciones**:\n{comments}"
        
        # Send the pre-diagnosis to the user first
        await self.whatsapp_service.send_text_message(session.phone_number, diagnosis_message)
        
        # Send explanation about doctor validation process
        validation_message = (
            "📋 **Este es tu pre-diagnóstico**\n\n"
            "Es importante para nosotros que un médico lo valide, por lo cual, "
            "en este mismo instante enviaré a los diferentes doctores el mensaje "
            "para que lo validen y te proporcionen la mejor atención médica.\n\n"
            "⏰ **Recibirás una respuesta de nuestros especialistas pronto.**"
        )
        
        await self.whatsapp_service.send_text_message(session.phone_number, validation_message)
        
        # Notify doctors about the new pre-diagnosis
        print("[DOCTOR_NOTIFICATION] Starting doctor notification process")
        await self.whatsapp_service.send_text_message(
            session.phone_number,
            "📤 Enviando tu pre-diagnóstico a nuestros médicos especialistas para validación..."
        )
        
        try:
            # Import doctor services at runtime to avoid circular imports
            from main import doctor_session_manager, doctor_conversation_service
            
            # Get active registered doctors instead of using API
            active_doctors = doctor_session_manager.get_active_doctors()
            notified_doctors = []
            
            if active_doctors:
                print(f"📋 Found {len(active_doctors)} active registered doctors")
                for doctor_session in active_doctors:
                    try:
                        # Notify doctor of new case assignment
                        success = await doctor_conversation_service.notify_doctor_of_new_case(
                            doctor_session.phone_number, session.phone_number
                        )
                        
                        if success:
                            # Send the diagnosis details directly
                            await self._send_diagnosis_to_doctor(
                                doctor_session.phone_number, session, api_response
                            )
                            notified_doctors.append(doctor_session.phone_number)
                            print(f"✅ Notified registered doctor: {doctor_session.phone_number}")
                        
                    except Exception as e:
                        print(f"❌ Failed to notify registered doctor {doctor_session.phone_number}: {repr(e)}")
            else:
                print("⚠️ No active registered doctors found, using API fallback...")
                # Fallback to API-based doctor notification
                notified_doctors = await self.doctor_service.notify_doctors_about_diagnosis(
                    session, api_response, self.whatsapp_service
                )
            
            session.doctors_notified = notified_doctors
            
            if notified_doctors:
                await self.whatsapp_service.send_text_message(
                    session.phone_number,
                    f"✅ Tu pre-diagnóstico ha sido enviado a {len(notified_doctors)} médicos especialistas. "
                    f"Recibirás la validación médica pronto."
                )
            else:
                await self.whatsapp_service.send_text_message(
                    session.phone_number,
                    "⚠️ Hubo un problema notificando a los médicos. Por favor contacta a nuestro soporte."
                )
                
        except Exception as e:
            print(f"❌ Error notifying doctors: {repr(e)}")
            await self.whatsapp_service.send_text_message(
                session.phone_number,
                "⚠️ Hubo un problema técnico. Tu diagnóstico se ha guardado y será revisado pronto."
            )
        
        # Set state to wait for doctor approval instead of ending conversation
        session.state = SessionState.WAITING_FOR_DOCTOR_APPROVAL
        print("[CONVERSATION_COMPLETE] Pre-diagnosis delivered and doctors notified, waiting for approval")
    
    async def _handle_waiting_for_doctor_approval(self, phone_number: str) -> None:
        """Handle messages from patients while waiting for doctor approval.
        
        Args:
            phone_number: The patient's phone number
        """
        print(f"[WAITING_FOR_DOCTOR] Patient {phone_number} sent message while waiting for doctor approval")
        
        waiting_message = (
            "⏳ **Tu diagnóstico está siendo revisado**\n\n"
            "Hemos enviado tu pre-diagnóstico a nuestros médicos especialistas "
            "para su validación. Te notificaremos tan pronto como recibamos "
            "la respuesta médica.\n\n"
            "🏥 **No es necesario que envíes más mensajes por ahora.** "
            "Recibirás una notificación automática cuando el médico "
            "haya completado la revisión.\n\n"
            "⏰ **Tiempo estimado de respuesta: 1-2 horas**"
        )
        
        await self.whatsapp_service.send_text_message(phone_number, waiting_message)
    
    async def _send_diagnosis_to_doctor(self, doctor_phone: str, session: UserSession, api_response: Dict[str, Any]) -> None:
        """Send diagnosis details to a specific registered doctor.
        
        Args:
            doctor_phone: Doctor's phone number
            session: Patient session
            api_response: API response with diagnosis
        """
        pre_diagnosis_text = api_response.get("pre-diagnosis", "") or api_response.get("pre_diagnosis", "")
        comments_text = api_response.get("comments", "")
        score_text = api_response.get("score", "")
        
        # Format diagnosis for doctor
        diagnosis_message = (
            f"🏥 **DETALLES DEL PRE-DIAGNÓSTICO**\n\n"
            f"👤 **Paciente**: {session.phone_number}\n"
            f"📊 **Prioridad**: {score_text}\n"
            f"📅 **Fecha**: {session.created_at.strftime('%Y-%m-%d %H:%M')}\n\n"
        )
        
        if pre_diagnosis_text:
            diagnosis_message += f"🔍 **Pre-Diagnóstico**:\n{pre_diagnosis_text}\n\n"
        
        if comments_text:
            diagnosis_message += f"💬 **Comentarios**:\n{comments_text}\n\n"
        
        diagnosis_message += "Por favor, valida este diagnóstico respondiendo:\n**APROBAR** / **DENEGAR** / **MIXTO**"
        
        # Send diagnosis details
        await self.whatsapp_service.send_text_message(doctor_phone, diagnosis_message)
        
        # Send interactive buttons
        buttons = [
            {"id": f"approve_{session.phone_number}", "title": "APROBAR"},
            {"id": f"deny_{session.phone_number}", "title": "DENEGAR"}, 
            {"id": f"mixed_{session.phone_number}", "title": "MIXTO"}
        ]
        
        try:
            await self.whatsapp_service.send_interactive_message(
                doctor_phone,
                "Selecciona tu decisión médica:",
                "Validación",
                buttons
            )
        except Exception as e:
            print(f"[ERROR] Failed to send interactive buttons to {doctor_phone}: {repr(e)}")
            # Buttons were already mentioned in the text message as fallback
