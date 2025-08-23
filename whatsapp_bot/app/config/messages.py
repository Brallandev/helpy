"""Predefined messages for the bot."""

# Greeting message
GREETING_MESSAGE = "¡Hola! 👋 Bienvenido/a a nuestro servicio de bienestar. Estamos aquí para apoyarte."

# Informed consent message (shortened for WhatsApp limits)
CONSENT_MESSAGE = """🔒 CONSENTIMIENTO INFORMADO

📋 INFORMACIÓN DEL SERVICIO
Este chatbot brinda apoyo y orientación sobre bienestar personal mediante preguntas personalizadas. NO constituye atención médica o psicológica profesional.

📊 TRATAMIENTO DE DATOS (Ley 1581/2012)
• Recolectamos: respuestas sobre bienestar y datos de interacción
• Finalidad: brindar sugerencias personalizadas y mejorar el servicio
• Confidencialidad: información tratada con estricta privacidad
• No compartimos datos con terceros

⚖️ SUS DERECHOS
• Conocer, actualizar y rectificar sus datos
• Revocar autorización y solicitar supresión
• Acceder gratuitamente a su información
• Presentar quejas ante la SIC

⚠️ LIMITACIONES
• NO reemplaza atención médica profesional
• Solo sugerencias informativas
• En emergencias, busque ayuda profesional inmediata

✅ CONSENTIMIENTO
Al aceptar, declara que:
• Ha leído y comprendido este consentimiento
• Autoriza el tratamiento de datos
• Comprende las limitaciones del servicio
• Consiente voluntariamente el uso del chatbot"""

# Consent declined message
CONSENT_DECLINED_MESSAGE = "Entendemos, igualmente estaremos acá dispuestos a ayudarte en un futuro 😊"

# Button configuration for consent
CONSENT_BUTTONS = [
    {
        "type": "reply",
        "reply": {
            "id": "consent_yes",
            "title": "Sí, acepto"
        }
    },
    {
        "type": "reply", 
        "reply": {
            "id": "consent_no",
            "title": "No, gracias"
        }
    }
]

CONSENT_BUTTON_TEXT = "¿Acepta estos términos y condiciones?"
