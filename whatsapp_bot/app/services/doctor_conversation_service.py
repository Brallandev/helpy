"""
Doctor conversation service for handling doctor-specific workflows.
"""

from typing import Optional, Dict, Any
from app.models.doctor_session import DoctorSession, DoctorSessionState
from app.utils.doctor_session_manager import DoctorSessionManager
from app.services.whatsapp_service import WhatsAppService
from app.services.doctor_service import DoctorService
from app.utils.session_manager import SessionManager
from app.config.messages import SPECIALIST_APPROVAL_MESSAGES


class DoctorConversationService:
    """Handles conversation flow specifically for doctors."""
    
    def __init__(
        self,
        doctor_session_manager: DoctorSessionManager,
        whatsapp_service: WhatsAppService,
        doctor_service: DoctorService,
        patient_session_manager: SessionManager
    ):
        self.doctor_session_manager = doctor_session_manager
        self.whatsapp_service = whatsapp_service
        self.doctor_service = doctor_service
        self.patient_session_manager = patient_session_manager
    
    async def process_doctor_message(self, phone_number: str, message_text: str) -> None:
        """Process a message from a doctor.
        
        Args:
            phone_number: Doctor's phone number
            message_text: The message content
        """
        print(f"\n[DOCTOR_MESSAGE] Processing message from doctor {phone_number}: {message_text}")
        
        # Get or create doctor session
        doctor_session = self.doctor_session_manager.get_doctor_session(phone_number)
        
        # Handle doctor registration
        if message_text.lower().strip() == "doctor":
            await self._handle_doctor_registration(phone_number)
            return
        
        # If no session exists and message isn't "doctor", inform them
        if not doctor_session:
            await self._handle_unregistered_doctor(phone_number)
            return
        
        # Handle different doctor states
        if doctor_session.state == DoctorSessionState.REGISTRATION_PENDING:
            await self._handle_registration_pending(doctor_session, message_text)
        elif doctor_session.state == DoctorSessionState.REGISTERED:
            await self._handle_registered_doctor(doctor_session, message_text)
        elif doctor_session.state == DoctorSessionState.REVIEWING_CASE:
            await self._handle_case_review(doctor_session, message_text)
        elif doctor_session.state == DoctorSessionState.INACTIVE:
            await self._handle_inactive_doctor(doctor_session, message_text)
    
    async def _handle_doctor_registration(self, phone_number: str) -> None:
        """Handle initial doctor registration."""
        print(f"[DOCTOR_REGISTRATION] Registering doctor {phone_number}")
        
        session = self.doctor_session_manager.register_doctor(phone_number)
        
        registration_message = (
            "👨‍⚕️ **REGISTRO DE ESPECIALISTA INICIADO**\n\n"
            "Bienvenido al sistema de validación de especialistas.\n\n"
            "Para completar tu registro como especialista validador, "
            "por favor confirma tu identidad respondiendo:\n\n"
            "**'CONFIRMAR'** - Para activar tu cuenta\n"
            "**'CANCELAR'** - Para cancelar el registro\n\n"
            "Una vez confirmado, recibirás casos para validación de apoyo diagnóstico."
        )
        
        await self.whatsapp_service.send_text_message(phone_number, registration_message)
    
    async def _handle_registration_pending(self, session: DoctorSession, message_text: str) -> None:
        """Handle doctor in pending registration state."""
        message_lower = message_text.lower().strip()
        
        if message_lower in ["confirmar", "confirm", "si", "sí", "yes"]:
            # Confirm registration
            self.doctor_session_manager.confirm_doctor_registration(session.phone_number)
            
            success_message = (
                "✅ **REGISTRO DE ESPECIALISTA COMPLETADO**\n\n"
                "Tu cuenta ha sido activada exitosamente.\n\n"
                "🏥 **Funciones disponibles:**\n"
                "• Recibirás notificaciones de nuevos casos\n"
                "• Podrás validar apoyos diagnósticos\n"
                "• Responde APROBAR/DENEGAR/MIXTO para cada caso\n\n"
                "**Comandos útiles:**\n"
                "• 'ESTADO' - Ver tu estado actual\n"
                "• 'AYUDA' - Ver comandos disponibles\n"
                "• 'INACTIVO' - Pausar notificaciones\n\n"
                "¡Listo para recibir casos! 🩺"
            )
            
            await self.whatsapp_service.send_text_message(session.phone_number, success_message)
            print(f"[DOCTOR_CONFIRMED] Doctor {session.phone_number} registration confirmed")
            
        elif message_lower in ["cancelar", "cancel", "no"]:
            # Cancel registration
            self.doctor_session_manager.deactivate_doctor(session.phone_number)
            
            cancel_message = (
                "❌ **Registro cancelado**\n\n"
                "Tu registro como médico validador ha sido cancelado.\n\n"
                "Si deseas registrarte nuevamente en el futuro, "
                "simplemente envía 'DOCTOR' para iniciar el proceso."
            )
            
            await self.whatsapp_service.send_text_message(session.phone_number, cancel_message)
            print(f"[DOCTOR_CANCELLED] Doctor {session.phone_number} registration cancelled")
            
        else:
            # Invalid response
            help_message = (
                "⚠️ **Respuesta no válida**\n\n"
                "Para completar tu registro, por favor responde:\n\n"
                "**'CONFIRMAR'** - Para activar tu cuenta\n"
                "**'CANCELAR'** - Para cancelar el registro"
            )
            
            await self.whatsapp_service.send_text_message(session.phone_number, help_message)
    
    async def _handle_registered_doctor(self, session: DoctorSession, message_text: str) -> None:
        """Handle messages from registered doctors."""
        message_lower = message_text.lower().strip()
        
        if message_lower in ["estado", "status"]:
            await self._send_doctor_status(session)
        elif message_lower in ["ayuda", "help"]:
            await self._send_doctor_help(session)
        elif message_lower in ["inactivo", "inactive", "pausar"]:
            await self._set_doctor_inactive(session)
        elif message_lower in ["activo", "active", "reanudar"]:
            await self._set_doctor_active(session)
        else:
            # Check if it's a case approval response
            await self._handle_potential_approval_response(session, message_text)
    
    async def _handle_case_review(self, session: DoctorSession, message_text: str) -> None:
        """Handle doctor responses while reviewing a case."""
        print(f"[CASE_REVIEW] Doctor {session.phone_number} reviewing case, message: {message_text}")
        
        # Process the approval response, but first ensure patient phone is available
        # If no patient phone in button, use the current reviewing patient
        doctor_response = await self.doctor_service.process_doctor_response(
            session.phone_number, message_text, self.whatsapp_service
        )
        
        # If response doesn't have patient phone, add it from current session
        if doctor_response and not doctor_response.get("patient_phone"):
            doctor_response["patient_phone"] = session.current_reviewing_patient
        
        if doctor_response:
            # Mark case as complete
            patient_phone = doctor_response.get("patient_phone", session.current_reviewing_patient)
            if patient_phone:
                self.doctor_session_manager.complete_case_review(session.phone_number, patient_phone)
                print(f"[CASE_COMPLETE] Doctor {session.phone_number} completed review of {patient_phone}")
                
                # Notify the patient directly
                await self._notify_patient_of_decision(doctor_response)
            else:
                print(f"[ERROR] No patient phone found for doctor response from {session.phone_number}")
        else:
            # Invalid response, provide guidance
            guidance_message = (
                "⚠️ **Respuesta no válida para el caso en revisión**\n\n"
                "Para validar el apoyo diagnóstico, responde:\n"
                "• **APROBAR** (o número 1)\n"
                "• **DENEGAR** (o número 2)\n"
                "• **MIXTO** (o número 3)\n\n"
                "Tu decisión se enviará automáticamente al paciente."
            )
            await self.whatsapp_service.send_text_message(session.phone_number, guidance_message)
    
    async def _handle_inactive_doctor(self, session: DoctorSession, message_text: str) -> None:
        """Handle messages from inactive doctors."""
        message_lower = message_text.lower().strip()
        
        if message_lower in ["activo", "active", "reanudar", "activar"]:
            await self._set_doctor_active(session)
        else:
            inactive_message = (
                "😴 **Cuenta inactiva**\n\n"
                "Tu cuenta está actualmente pausada.\n\n"
                "Para reactivarla y recibir casos, responde:\n"
                "**'ACTIVO'** - Reanudar recepción de casos"
            )
            await self.whatsapp_service.send_text_message(session.phone_number, inactive_message)
    
    async def _handle_unregistered_doctor(self, phone_number: str) -> None:
        """Handle messages from unregistered doctors."""
        help_message = (
            "👨‍⚕️ **Sistema de Validación Médica**\n\n"
            "Para registrarte como médico validador, envía:\n"
            "**'DOCTOR'** - Iniciar registro médico\n\n"
            "Una vez registrado, recibirás casos para validación."
        )
        await self.whatsapp_service.send_text_message(phone_number, help_message)
    
    async def _handle_potential_approval_response(self, session: DoctorSession, message_text: str) -> None:
        """Handle potential approval responses from registered doctors."""
        # This might be a response to a case, but check if it's a valid approval
        message_lower = message_text.lower().strip()
        
        if any(word in message_lower for word in ["aprobar", "denegar", "mixto"]) or message_text.strip() in ["1", "2", "3"]:
            # Looks like an approval response but no active case
            no_case_message = (
                "ℹ️ **No hay casos activos para revisar**\n\n"
                "Actualmente no tienes casos asignados.\n"
                "Recibirás una notificación cuando haya nuevos casos disponibles.\n\n"
                "Usa 'ESTADO' para ver tu estado actual."
            )
            await self.whatsapp_service.send_text_message(session.phone_number, no_case_message)
        else:
            # General help for registered doctors
            await self._send_doctor_help(session)
    
    async def _send_doctor_status(self, session: DoctorSession) -> None:
        """Send current status to doctor."""
        status_message = (
            f"📊 **TU ESTADO ACTUAL**\n\n"
            f"🏥 **Estado**: {self._get_state_emoji(session.state)} {session.state.value.replace('_', ' ').title()}\n"
            f"📅 **Registrado**: {session.registration_date.strftime('%Y-%m-%d %H:%M')}\n"
            f"⏰ **Última actividad**: {session.last_activity.strftime('%Y-%m-%d %H:%M')}\n"
            f"📋 **Casos revisados**: {len(session.cases_reviewed)}\n"
        )
        
        if session.current_reviewing_patient:
            status_message += f"👤 **Caso actual**: {session.current_reviewing_patient}\n"
        
        status_message += "\nUsa 'AYUDA' para ver comandos disponibles."
        
        await self.whatsapp_service.send_text_message(session.phone_number, status_message)
    
    async def _send_doctor_help(self, session: DoctorSession) -> None:
        """Send help information to doctor."""
        help_message = (
            "🆘 **COMANDOS DISPONIBLES**\n\n"
            "**📊 Estado y Control:**\n"
            "• 'ESTADO' - Ver estado actual\n"
            "• 'INACTIVO' - Pausar notificaciones\n"
            "• 'ACTIVO' - Reanudar notificaciones\n\n"
            "**📋 Validación de Casos:**\n"
            "• 'APROBAR' o '1' - Aprobar diagnóstico\n"
            "• 'DENEGAR' o '2' - Denegar diagnóstico\n"
            "• 'MIXTO' o '3' - Validación mixta\n\n"
            "**ℹ️ Información:**\n"
            "• 'AYUDA' - Mostrar este menú\n\n"
            "Los casos llegaran automáticamente cuando estén disponibles."
        )
        
        await self.whatsapp_service.send_text_message(session.phone_number, help_message)
    
    async def _set_doctor_inactive(self, session: DoctorSession) -> None:
        """Set doctor as inactive."""
        self.doctor_session_manager.deactivate_doctor(session.phone_number)
        
        inactive_message = (
            "😴 **Cuenta pausada exitosamente**\n\n"
            "No recibirás más notificaciones de casos.\n\n"
            "Para reactivar tu cuenta, envía:\n"
            "**'ACTIVO'** - Reanudar recepción de casos"
        )
        
        await self.whatsapp_service.send_text_message(session.phone_number, inactive_message)
        print(f"[DOCTOR_INACTIVE] Doctor {session.phone_number} set to inactive")
    
    async def _set_doctor_active(self, session: DoctorSession) -> None:
        """Set doctor as active."""
        session.state = DoctorSessionState.REGISTERED
        session.mark_activity()
        
        active_message = (
            "✅ **Cuenta reactivada exitosamente**\n\n"
            "Volverás a recibir notificaciones de nuevos casos.\n\n"
            "🏥 Listo para validar diagnósticos.\n"
            "Usa 'ESTADO' para ver tu información actual."
        )
        
        await self.whatsapp_service.send_text_message(session.phone_number, active_message)
        print(f"[DOCTOR_ACTIVE] Doctor {session.phone_number} set to active")
    
    async def _notify_patient_of_decision(self, doctor_response: dict) -> None:
        """Notify the patient of the doctor's decision.
        
        Args:
            doctor_response: Dictionary with doctor's decision information
        """
        decision = doctor_response.get("decision", "")
        doctor_phone = doctor_response.get("doctor_phone", "")
        patient_phone = doctor_response.get("patient_phone", "")
        
        if not patient_phone:
            print(f"[ERROR] Cannot notify patient - no patient phone in doctor response")
            return
        
        # Use the new specialist approval messages
        if decision in SPECIALIST_APPROVAL_MESSAGES:
            patient_message = SPECIALIST_APPROVAL_MESSAGES[decision]
        else:
            # Fallback message for unknown decisions
            masked_doctor_phone = f"{doctor_phone[:5]}***{doctor_phone[-4:]}" if len(doctor_phone) > 8 else "Esp. ***"
            patient_message = (
                f"ℹ️ **ACTUALIZACIÓN DE SU APOYO DIAGNÓSTICO**\n\n"
                f"Un especialista (Esp. {masked_doctor_phone}) ha revisado su apoyo diagnóstico. Nos pondremos en contacto contigo para más detalles."
            )
        
        try:
            await self.whatsapp_service.send_text_message(patient_phone, patient_message)
            print(f"✅ [PATIENT_NOTIFIED] Patient {patient_phone} notified of decision: {decision}")
            
            # Update patient session to mark conversation as ended
            if patient_phone in self.patient_session_manager.user_sessions:
                from app.models.session import SessionState
                patient_session = self.patient_session_manager.user_sessions[patient_phone]
                patient_session.state = SessionState.CONVERSATION_ENDED
                patient_session.final_specialist_decision = decision
                patient_session.patient_notified_of_decision = True
                
        except Exception as e:
            print(f"❌ [PATIENT_NOTIFICATION_ERROR] Failed to notify patient {patient_phone}: {repr(e)}")
    
    def _get_state_emoji(self, state: DoctorSessionState) -> str:
        """Get emoji for doctor state."""
        emoji_map = {
            DoctorSessionState.REGISTRATION_PENDING: "⏳",
            DoctorSessionState.REGISTERED: "✅",
            DoctorSessionState.REVIEWING_CASE: "📋",
            DoctorSessionState.INACTIVE: "😴"
        }
        return emoji_map.get(state, "❓")
    
    async def notify_doctor_of_new_case(self, doctor_phone: str, patient_phone: str) -> bool:
        """Notify a doctor of a new case assignment.
        
        Args:
            doctor_phone: Doctor's phone number
            patient_phone: Patient's phone number
            
        Returns:
            True if notification was sent successfully
        """
        session = self.doctor_session_manager.get_doctor_session(doctor_phone)
        if not session or not session.is_active():
            return False
        
        # Mark doctor as reviewing this case
        self.doctor_session_manager.start_case_review(doctor_phone, patient_phone)
        
        notification_message = (
            f"🚨 **NUEVO CASO ASIGNADO**\n\n"
            f"👤 **Paciente**: {patient_phone}\n"
            f"📅 **Fecha**: {session.last_activity.strftime('%Y-%m-%d %H:%M')}\n\n"
            f"Recibirás los detalles del apoyo diagnóstico a continuación..."
        )
        
        await self.whatsapp_service.send_text_message(doctor_phone, notification_message)
        return True
