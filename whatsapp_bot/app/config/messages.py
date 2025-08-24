"""Predefined messages for the bot."""

# Greeting message
GREETING_MESSAGE = (
    "¡Hola! 👋 Bienvenido/a a nuestro servicio de bienestar. "
    "Sabemos que la IA, como ChatGPT, puede ser una gran aliada, pero tu bienestar necesita algo más que respuestas automáticas. "
    "Aquí encontrarás procesos diseñados y guiados por expertos, que combinan lo mejor de la tecnología con la guía experta de profesionales asegurando procesos confiables, humanos y basados en evidencia. "
    "Y lo más importante: cada apoyo diagnóstico generado por la IA es revisado y validado por un grupo de profesionales en el área, "
    "para que avances con confianza y respaldo en cada paso."
)
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

# Specialist approval response messages
SPECIALIST_APPROVAL_MESSAGES = {
    "APROBAR": """✅ **APOYO DIAGNÓSTICO APROBADO**

Un especialista ha revisado y **APROBADO** tu apoyo diagnóstico.

📞 **Próximos pasos**: Teniendo en cuenta el diagnóstico, nos gustaría que sepas que parece adecuado que te conectes con un especialista para un seguimiento más detallado.""",

    "DENEGAR": """⚠️ **APOYO DIAGNÓSTICO REQUIERE REVISIÓN**

Un especialista ha pensado que este diagnóstico tiene opciones de mejorar en su estado actual, por lo cual, te aconsejamos esperar la validacion de mas especialistas.""",

    "MIXTO": """🔄 **APOYO DIAGNÓSTICO EN EVALUACIÓN**

Este apoyo diagnóstico tiene aspectos verdaderos y aspectos de mejora, entonces es mejor seguir esperando la validación de otros especialistas! No te preocupes, en breve seguro recibirás más opciones de este diagnóstico."""
}
