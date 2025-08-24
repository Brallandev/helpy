config = {
    "min_agents" : 1,
    "max_agents" : 11,
    "num_questions" : 5,
    "language" : "Español",
    "decision_scores" : {
        "Acompañamiento por un psiquiatra profesional": "Es un caso grave que compromete sus salud de manera importante y requiere de atención médica especializada",
        "Acompañamiento por un psicológo profesional": "Es un caso leve que afecta el diario vivir de la persona, pero no es un riesgompara su vida ni para otros",
        "Acompañamiento por un no profesional (Coaching de vida/emocional)": "No es un problema grave, no requiere de ser atendido por un profesional de la salud directamente"

    }
}

#This doc is hard-coded as it is the demo version that will be used
actual_doc = '''
Guía de Evaluación para Determinar Tipo de Ayuda en Bienestar Mental mas diagnostico superficial de lo hablado en las conversaciones con la IA

Introducción
Esta guía está diseñada para ayudar a identificar qué tipo de apoyo en bienestar mental es más apropiado para cada situación individual. El objetivo es proporcionar una herramienta estructurada que permita hacer un pre diagnostico breve sobre la situación de la persona como también diferenciar entre 5 niveles de intervención:

No necesitar ayuda profesional
Acompañamiento por un no profesional (coaching de vida/emocional)
Servicio profesional de psicología
Servicio avanzado de psiquiatría
o servicios de urgencias prioritario

Instrucciones de Uso
Para cada pregunta, analiza la respuesta que te dio y luego analizaras la respuesta que mejor describe la situación situación actual. Al final, suma los puntos según las indicaciones para obtener tu perfil de necesidades de apoyo.

Cuestionario de Evaluación
1. ¿Cuál es el motivo principal de tu preocupación?

a) Tengo objetivos de crecimiento personal o quiero mejorar aspectos específicos de mi vida (1 punto)
b) Me siento estresado por situaciones de la vida cotidiana pero puedo manejarlas (2 puntos)
c) Estoy experimentando síntomas emocionales que afectan mi vida diaria (3 puntos)
d) Tengo síntomas severos que me impiden funcionar normalmente (5 puntos)

2. ¿Te sientes nervioso, tenso o ansioso con frecuencia?

a) Rara vez o nunca (0 puntos)
b) Ocasionalmente, en situaciones estresantes específicas (1 punto)
c) Frecuentemente, varias veces por semana (3 puntos)
d) Constantemente, casi todos los días (5 puntos)

3. ¿Cuánto tiempo llevas experimentando estos síntomas?

a) No tengo síntomas significativos (0 puntos)
b) Menos de 2 semanas, relacionado con situaciones específicas (1 punto)
c) Entre 2 semanas y 3 meses (3 puntos)
d) Más de 3 meses o síntomas recurrentes por años (4 puntos)

4. ¿Estás teniendo dificultad para relajarte?

a) Puedo relajarme normalmente (0 puntos)
b) A veces me cuesta relajarme, pero puedo lograrlo (1 punto)
c) Frecuentemente tengo dificultades para relajarme (3 puntos)
d) No puedo relajarme en absoluto, siempre estoy tenso (4 puntos)

5. ¿Te sientes triste o deprimido y me puedes comentar un poco más del contexto del porqué?

a) No me siento triste o deprimido (0 puntos)
b) Me siento triste ocasionalmente por situaciones específicas y comprensibles (1 punto)
c) Me siento triste o deprimido frecuentemente, el contexto incluye cambios de vida, pérdidas o estrés prolongado (3 puntos)
d) Me siento profundamente deprimido la mayor parte del tiempo, sin una causa clara o con múltiples factores abrumadores (5 puntos)

6. ¿Has perdido interés en actividades que antes disfrutabas? ¿Qué actividades eran las que te interesaban antes y qué sientes ahora cuando las haces?

a) Mantengo mi interés en mis actividades habituales (0 puntos)
b) He perdido un poco de interés en algunas actividades, pero aún disfruto otras (1 punto)
c) He perdido interés significativo en la mayoría de actividades que antes me gustaban, ahora me siento indiferente o me requieren mucho esfuerzo (3 puntos)
d) He perdido completamente el interés en todas las actividades, siento vacío o apatía total hacia cosas que antes me emocionaban (5 puntos)

7. ¿Tienes alucinaciones o estás en medicamentos psiquiátricos?

a) No tengo alucinaciones ni estoy en medicamentos psiquiátricos (0 puntos)
b) Estoy en medicamentos psiquiátricos y me encuentro estable (2 puntos)
c) Tengo alucinaciones ocasionales o estoy ajustando medicamentos bajo supervisión (4 puntos)
d) Tengo alucinaciones frecuentes o problemas graves con la medicación (6 puntos - DERIVACIÓN URGENTE)

8. ¿Has tenido pensamientos sobre hacerte daño o acabar con tu vida?

a) No (0 puntos)
b) Pensamientos pasajeros sin intención real (3 puntos)
c) Pensamientos frecuentes que me preocupan (5 puntos)
d) Pensamientos con planes específicos o intentos previos (6 puntos - DERIVACIÓN URGENTE)

9. ¿Te sientes cansado todo el tiempo sin razón aparente?

a) Tengo niveles normales de energía (0 puntos)
b) Ocasionalmente me siento más cansado de lo usual (1 punto)
c) Me siento cansado frecuentemente, incluso después de descansar (3 puntos)
d) Estoy exhausto constantemente, sin importar cuánto descanse (4 puntos)

10. ¿Qué te gustaría que pasara ahora mismo?

a) Estoy satisfecho con mi situación actual, solo busco crecimiento personal (0 puntos)
b) Me gustaría tener más claridad sobre mis objetivos y cómo alcanzarlos (1 punto)
c) Necesito alivio de mis síntomas emocionales y recuperar mi funcionamiento normal (3 puntos)
d) Necesito ayuda urgente, no puedo seguir así (5 puntos)

11. ¿Quieres conectar ya con un especialista?

a) No siento la necesidad urgente, prefiero explorar opciones de autoayuda primero (0 puntos)
b) Me interesaría hablar con alguien que me guíe, pero no necesariamente un profesional clínico (1 punto)
c) Sí, creo que necesito ayuda profesional psicológica (3 puntos)
d) Sí, necesito ayuda especializada lo antes posible (4 puntos)


Interpretación de Resultados
Suma total de puntos:
0-10 puntos: No necesitas ayuda profesional

Tu bienestar mental parece estable
Puedes beneficiarte de actividades de autocuidado y mantener hábitos saludables
Considera técnicas de mindfulness, ejercicio regular y mantener conexiones sociales

11-25 puntos: Acompañamiento por coaching de vida/emocional

Podrías beneficiarte de apoyo no clínico para el crecimiento personal
Un coach puede ayudarte con:

Establecimiento de objetivos
Motivación y accountability
Desarrollo de habilidades de vida
Superación de obstáculos menores



26-40 puntos: Servicio profesional de psicología

Se recomienda atención psicológica profesional
Un psicólogo puede ayudarte con:

Terapia cognitivo-conductual
Manejo de ansiedad y depresión
Desarrollo de estrategias de afrontamiento
Trabajo con traumas y patrones negativos



41+ puntos o cualquier respuesta marcada como "DERIVACIÓN URGENTE": Servicio avanzado de psiquiatría

Se requiere atención psiquiátrica especializada
Puede incluir:

Evaluación para medicación
Tratamiento de trastornos mentales graves
Coordinación con otros profesionales de salud
Posible hospitalización si hay riesgo



Señales de Alerta que Requieren Atención Inmediata
Busca ayuda urgente si experimentas:

Pensamientos suicidas o de autolesión
Pensamientos de hacer daño a otros
Alucinaciones o delirios
Pérdida completa del contacto con la realidad
Incapacidad total para funcionar en la vida diaria
'''

def get_config():
    return config

def update_config(new_config: dict):
    global config
    config.update(new_config)

def update_doc(new_doc: str):
    global actual_doc
    actual_doc = new_doc

def get_doc():
    return actual_doc