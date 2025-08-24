"""Predefined messages for the bot."""

# Greeting message
GREETING_MESSAGE = "¡Hola! 👋 Bienvenido/a a nuestro servicio de bienestar. Estamos aquí para apoyarte."

# Informed consent message (shortened for WhatsApp limits)
CONSENT_MESSAGE = """
Este chat ofrece orientación en bienestar personal 🧘‍♀🌿 mediante preguntas y sugerencias.
Tus datos se usarán solo para este servicio, según la Ley 1581 de 2012 🇨🇴🖥🔒.

⚠ Importante: es solo apoyo orientativo, no reemplaza atención psicológica profesional 🚫🩺.

✅ Al aceptar, confirmas que:

Leíste y entendiste la información 📖

Autorizas el uso de tus datos personales 🔏

Reconoces las limitaciones del servicio ⚖️"""

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
