"""Predefined questions for mental health triage."""

from app.models.question import Question

# Mental Health Triage Questions
MENTAL_HEALTH_QUESTIONS = [
    Question("name", "¡Hola! 👋 Para comenzar, ¿cuál es tu nombre completo?"),
    Question("age", "¿Cuál es tu edad?"),
    Question("main_concern", "¿Cuál es el motivo principal de tu preocupación?"),
    Question("anxiety", "¿Te sientes nervioso, tenso o ansioso con frecuencia?"),
    Question("symptom_duration", "¿Cuánto tiempo llevas experimentando estos síntomas?"),
    Question("relaxation_difficulty", "¿Estás teniendo dificultad para relajarte?"),
    Question("sadness", "¿Te sientes triste o deprimido y me puedes comentar un poco mas del contexto del porque?"),
    Question("loss_of_interest", "¿Has perdido interés en actividades que antes disfrutabas? ¿Que actividades eran las que te interesaban antes y que sientes ahora cuando las haces?"),
    Question("hallucinations_meds", "¿Tienes alucinaciones o estás en medicamentos psiquiátricos?"),
    Question("self_harm_thoughts", "¿Has tenido pensamientos sobre hacerte daño o acabar con tu vida?"),
    Question("fatigue", "¿Te sientes cansado todo el tiempo sin razón aparente?"),
    Question("desired_outcome", "¿Qué te gustaría que pasara ahora mismo?"),
    Question("specialist_connection", "¿Quieres conectar ya con un especialista?")
]
