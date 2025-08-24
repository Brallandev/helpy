"""Predefined questions for mental health triage."""

from app.models.question import Question

# Mental Health Triage Questions
MENTAL_HEALTH_QUESTIONS = [
    Question("name", "¡Hola! 😊 Queremos acompañarte de la mejor manera posible, por eso nos gustaría conocerte un poquito más. Para comenzar, ¿podrías compartirnos tu nombre completo?"),
    Question("age", "Gracias por compartirlo. Para poder entender mejor tu situación, ¿nos podrías indicar tu edad?"),
    Question("main_concern", "Queremos escucharte con atención. ¿Qué es lo que más te preocupa en este momento?"),
    Question("anxiety", "En ocasiones todos sentimos nervios o tensión. ¿Sueles sentirte nervioso/a, tenso/a o ansioso/a con frecuencia?"),
    Question("sadness", " ¿Has estado sintiéndote triste o desanimado/a? Si te sientes con confianza, ¿podrías contarnos un poco más sobre lo que lo ha ocasionado?"),
    Question("loss_of_interest", "A veces dejamos de disfrutar cosas que antes nos hacían bien. ¿Te ha pasado que ya no disfrutas actividades que antes te gustaban? ¿Qué actividades eran y qué sientes ahora cuando las intentas hacer?"),
    Question("hallucinations_meds", "Para poder apoyarte mejor, ¿actualmente estás en algún tratamiento médico o psiquiátrico, o has tenido experiencias como alucinaciones?"),
    Question("self_harm_thoughts", "Esta es una pregunta muy importante: ¿Has tenido pensamientos de hacerte daño o de no querer seguir viviendo? (Si es así, recuerda que no estás solo/a, y podemos buscar ayuda juntos)."),
    Question("desired_outcome", "Gracias por compartir todo esto. Para finalizar, ¿cómo te gustaría sentirte en este momento? ¿Qué sería un pequeño paso hacia sentirte mejor?")
]