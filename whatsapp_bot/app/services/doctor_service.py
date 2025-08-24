"""Doctor service for managing doctor notifications and approvals."""

import httpx
import json
from typing import List, Dict, Any, Optional

from app.config.settings import settings
from app.models.session import UserSession


class DoctorService:
    """Service for managing doctor notifications and approval workflow."""

    def __init__(self):
        self.http_client = httpx.AsyncClient(timeout=30.0)
        self.api_url = settings.DATABASE_API_URL.replace('/api/patients/intake/', '/api/doctors/phone-numbers/')
        self.auth_token = settings.DATABASE_API_TOKEN

    async def get_doctor_phone_numbers(self) -> List[str]:
        """Fetch the list of doctor phone numbers from the API.
        
        Returns:
            List of doctor phone numbers
        """
        try:
            print("\n" + "="*60)
            print("[DOCTOR_SERVICE] FETCHING DOCTOR PHONE NUMBERS")
            print("="*60)
            print(f"🎯 Endpoint: {self.api_url}")
            print(f"🔑 Auth: Bearer {self.auth_token[:20]}...{self.auth_token[-10:]}")
            
            response = await self.http_client.get(
                self.api_url,
                headers={
                    "Authorization": f"Bearer {self.auth_token}",
                    "Content-Type": "application/json"
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                phone_numbers = data.get("phone_numbers", [])
                count = data.get("count", len(phone_numbers))
                
                print(f"✅ Successfully retrieved {count} doctor phone numbers")
                print(f"📞 Phone numbers: {phone_numbers}")
                print("="*60 + "\n")
                
                return phone_numbers
            else:
                print(f"❌ Failed to fetch doctor numbers: {response.status_code}")
                print(f"📨 Response: {response.text}")
                print("="*60 + "\n")
                return []
                
        except Exception as e:
            print(f"❌ Error fetching doctor phone numbers: {repr(e)}")
            print("="*60 + "\n")
            return []

    async def notify_doctors_about_diagnosis(self, session: UserSession, pre_diagnosis: Dict[str, Any], whatsapp_service) -> List[str]:
        """Notify all doctors about a new pre-diagnosis.
        
        Args:
            session: The user session with pre-diagnosis
            pre_diagnosis: The pre-diagnosis data from API
            whatsapp_service: WhatsApp service for sending messages
            
        Returns:
            List of doctor phone numbers that were notified
        """
        doctor_numbers = await self.get_doctor_phone_numbers()
        
        if not doctor_numbers:
            print("⚠️ No doctor phone numbers available for notification")
            return []
        
        print(f"\n[DOCTOR_NOTIFICATION] Notifying {len(doctor_numbers)} doctors about new pre-diagnosis")
        
        # Prepare greeting message
        greeting_message = (
            "🏥 **NUEVO APOYO DIAGNÓSTICO DISPONIBLE**\n\n"
            f"📱 Paciente: {session.phone_number}\n"
            f"📊 Prioridad: {pre_diagnosis.get('score', 'No especificado')}\n"
            f"⏰ Fecha: {session.created_at.strftime('%Y-%m-%d %H:%M')}\n\n"
            "Un nuevo apoyo diagnóstico requiere su revisión especializada."
        )
        
        # Prepare detailed diagnosis message
        diagnosis_details = self._format_diagnosis_for_doctors(session, pre_diagnosis)
        
        # Prepare approval buttons
        approval_buttons = [
            {"id": f"approve_{session.phone_number}", "title": "APROBAR"},
            {"id": f"deny_{session.phone_number}", "title": "DENEGAR"},
            {"id": f"mixed_{session.phone_number}", "title": "MIXTO"}
        ]
        
        notified_doctors = []
        
        for doctor_number in doctor_numbers:
            try:
                print(f"📤 Notifying doctor: {doctor_number}")
                
                # Send greeting message
                await whatsapp_service.send_text_message(doctor_number, greeting_message)
                
                # Send detailed diagnosis
                await whatsapp_service.send_text_message(doctor_number, diagnosis_details)
                
                # Send approval buttons
                await whatsapp_service.send_interactive_message(
                    doctor_number,
                    "Por favor, revise el pre-diagnóstico y seleccione su decisión:",
                    "Decisión Médica",
                    approval_buttons
                )
                
                notified_doctors.append(doctor_number)
                print(f"✅ Successfully notified doctor: {doctor_number}")
                
            except Exception as e:
                print(f"❌ Failed to notify doctor {doctor_number}: {repr(e)}")
        
        print(f"\n🎉 Notification complete: {len(notified_doctors)}/{len(doctor_numbers)} doctors notified")
        return notified_doctors

    def _format_diagnosis_for_doctors(self, session: UserSession, pre_diagnosis: Dict[str, Any]) -> str:
        """Format the pre-diagnosis information for doctors.
        
        Args:
            session: The user session
            pre_diagnosis: The pre-diagnosis data
            
        Returns:
            Formatted diagnosis message for doctors
        """
        patient_phone = session.phone_number
        score = pre_diagnosis.get('score', 'No especificado')
        diagnosis = pre_diagnosis.get('pre-diagnosis', 'No disponible')
        comments = pre_diagnosis.get('comments', 'No disponible')
        
        # Get key answers for context
        key_answers = self._get_key_patient_answers(session)
        
        formatted_message = f"""🏥 **DETALLES DEL APOYO DIAGNÓSTICO**

👤 **Paciente**: {patient_phone}
📊 **Prioridad**: {score}
📅 **Fecha**: {session.created_at.strftime('%Y-%m-%d %H:%M')}

🔍 **Apoyo Diagnóstico**:
{diagnosis}

💬 **Comentarios y Recomendaciones**:
{comments}

📋 **Respuestas Clave del Paciente**:
{key_answers}

⚕️ **Su revisión especializada es requerida para continuar con el tratamiento del paciente.**"""
        
        return formatted_message

    def _get_key_patient_answers(self, session: UserSession) -> str:
        """Extract key patient answers for doctor review.
        
        Args:
            session: The user session
            
        Returns:
            Formatted string of key answers
        """
        key_questions = [
            'main_concern', 'anxiety', 'sadness', 'self_harm_thoughts', 
            'desired_outcome', 'specialist_connection'
        ]
        
        key_answers = []
        for answer in session.answers:
            if answer.question_id in key_questions:
                # Get question text from config
                from app.config.questions import MENTAL_HEALTH_QUESTIONS
                question_map = {q.id: q.text for q in MENTAL_HEALTH_QUESTIONS}
                question_text = question_map.get(answer.question_id, answer.question_id)
                
                # Shorten question for display
                short_question = question_text.replace("¿", "").replace("?", "").strip()
                if len(short_question) > 50:
                    short_question = short_question[:47] + "..."
                
                key_answers.append(f"• {short_question}: {answer.value}")
        
        return "\n".join(key_answers) if key_answers else "No hay respuestas clave disponibles"

    async def process_doctor_response(self, doctor_phone: str, response_text: str, whatsapp_service) -> Optional[Dict[str, Any]]:
        """Process a doctor's approval/denial response.
        
        Args:
            doctor_phone: The doctor's phone number
            response_text: The response text or button ID
            whatsapp_service: WhatsApp service for sending messages
            
        Returns:
            Dictionary with processing results or None if not a doctor response
        """
        # Note: We'll let the calling service (doctor_conversation_service) 
        # validate if this is a registered doctor since it has access to doctor_session_manager
        
        # Extract patient phone number from button ID or response
        patient_phone = None
        decision = None
        
        # Check if it's a button response (most reliable)
        if "approve_" in response_text:
            patient_phone = response_text.replace("approve_", "")
            decision = "APROBAR"
        elif "deny_" in response_text:
            patient_phone = response_text.replace("deny_", "")
            decision = "DENEGAR"
        elif "mixed_" in response_text:
            patient_phone = response_text.replace("mixed_", "")
            decision = "MIXTO"
        
        # Check for numbered responses (fallback options)
        elif response_text.strip() in ["1", "1.", "APROBAR"]:
            decision = "APROBAR"
        elif response_text.strip() in ["2", "2.", "DENEGAR"]:
            decision = "DENEGAR" 
        elif response_text.strip() in ["3", "3.", "MIXTO"]:
            decision = "MIXTO"
        
        # Check for text responses (less reliable, more specific)
        elif any(word in response_text.lower() for word in ["aprobar", "aprobado", "approve"]) and len(response_text.split()) <= 3:
            decision = "APROBAR"
        elif any(word in response_text.lower() for word in ["denegar", "denegado", "deny", "denied"]) and len(response_text.split()) <= 3:
            decision = "DENEGAR"
        elif any(word in response_text.lower() for word in ["mixto", "mixed"]) and len(response_text.split()) <= 3:
            decision = "MIXTO"
        
        if not decision:
            # Send help message to doctor if response unclear
            help_message = (
                "Para validar el apoyo diagnóstico, por favor responde:\n"
                "1. APROBAR\n"
                "2. DENEGAR\n"
                "3. MIXTO\n\n"
                "O usa el número correspondiente (1, 2, 3)."
            )
            await whatsapp_service.send_text_message(doctor_phone, help_message)
            return None  # Not a valid doctor response
        
        print(f"\n[DOCTOR_RESPONSE] Doctor {doctor_phone} responded: {decision}")
        
        # Send confirmation to doctor
        confirmation_message = f"✅ Su decisión '{decision}' ha sido registrada y enviada al paciente."
        await whatsapp_service.send_text_message(doctor_phone, confirmation_message)
        
        from datetime import datetime
        return {
            "doctor_phone": doctor_phone,
            "decision": decision,
            "patient_phone": patient_phone,
            "timestamp": datetime.now().isoformat()
        }

    async def notify_patient_of_decision(self, patient_phone: str, decision: str, doctor_phone: str, whatsapp_service) -> None:
        """Notify the patient of the doctor's decision.
        
        Args:
            patient_phone: The patient's phone number
            decision: The doctor's decision (APROBAR/DENEGAR/MIXTO)
            doctor_phone: The doctor's phone number (masked for privacy)
            whatsapp_service: WhatsApp service for sending messages
        """
        # Mask doctor phone for privacy
        masked_doctor = f"{doctor_phone[:6]}***{doctor_phone[-4:]}"
        
        if decision == "APROBAR":
            message = (
                "✅ **DIAGNÓSTICO APROBADO**\n\n"
                f"Un médico especialista (Dr. {masked_doctor}) ha revisado y **APROBADO** su pre-diagnóstico.\n\n"
                "📞 **Próximos pasos**: Un especialista se contactará con usted pronto para continuar con su tratamiento.\n\n"
                "🏥 Gracias por confiar en nuestros servicios de salud mental."
            )
        elif decision == "DENEGAR":
            message = (
                "⚠️ **DIAGNÓSTICO REQUIERE REVISIÓN**\n\n"
                f"Un médico especialista (Dr. {masked_doctor}) ha revisado su pre-diagnóstico y considera que **requiere evaluación adicional**.\n\n"
                "📞 **Próximos pasos**: Un especialista se contactará con usted para realizar una evaluación más detallada.\n\n"
                "🏥 Esto es parte normal del proceso para asegurar el mejor cuidado para usted."
            )
        else:  # MIXTO
            message = (
                "🔄 **DIAGNÓSTICO EN REVISIÓN**\n\n"
                f"Un médico especialista (Dr. {masked_doctor}) ha revisado su pre-diagnóstico y requiere **evaluación mixta**.\n\n"
                "📞 **Próximos pasos**: Un especialista se contactará con usted para discutir los detalles y próximos pasos.\n\n"
                "🏥 Su caso será tratado con especial atención."
            )
        
        print(f"[PATIENT_NOTIFICATION] Notifying patient {patient_phone} of decision: {decision}")
        await whatsapp_service.send_text_message(patient_phone, message)

    async def close(self):
        """Close the HTTP client."""
        await self.http_client.aclose()
