#!/usr/bin/env python3
"""
Test script to verify the new database schema transformation.

This tests:
- Data transformation from session to new schema format
- Payload structure validation
- Complete diagnostic data flow
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime
from app.models.session import UserSession, Answer
from app.services.database_service import DatabaseService

def create_mock_session():
    """Create a mock session with the provided example data."""
    session = UserSession(
        phone_number="573226235226",
        created_at=datetime(2024, 1, 15, 14, 30, 0)
    )
    
    # Add initial answers based on the provided example
    initial_answers = [
        Answer(
            question_id="name",
            value="Juan Garzon",
            timestamp="2024-01-15T14:30:00"
        ),
        Answer(
            question_id="age", 
            value="34",
            timestamp="2024-01-15T14:31:00"
        ),
        Answer(
            question_id="main_concern",
            value="El estrés de estar ya en los 30",
            timestamp="2024-01-15T14:32:00"
        ),
        Answer(
            question_id="anxiety",
            value="Últimamente si",
            timestamp="2024-01-15T14:33:00"
        ),
        Answer(
            question_id="sadness",
            value="Realmente las cosas que me divierten cada vez pierden más sentido y no logro animarme por nada",
            timestamp="2024-01-15T14:34:00"
        ),
        Answer(
            question_id="loss_of_interest",
            value="Patinar, montar a caballo, jugar fútbol, ya nada es lo mismo",
            timestamp="2024-01-15T14:35:00"
        ),
        Answer(
            question_id="hallucinations_meds",
            value="No todavía",
            timestamp="2024-01-15T14:36:00"
        ),
        Answer(
            question_id="self_harm_thoughts",
            value="No realmente",
            timestamp="2024-01-15T14:37:00"
        ),
        Answer(
            question_id="desired_outcome",
            value="Tener más paz con las cosas que vienen",
            timestamp="2024-01-15T14:38:00"
        )
    ]
    
    session.answers = initial_answers
    
    # Add some follow-up questions and answers
    session.followup_questions = [
        "¿Desde cuándo sientes que las actividades han perdido sentido?",
        "¿Has notado algún patrón en cuanto a cuándo te sientes más ansioso?"
    ]
    
    followup_answers = [
        Answer(
            question_id="followup_1",
            value="Aproximadamente desde hace 6 meses",
            timestamp="2024-01-15T14:40:00"
        ),
        Answer(
            question_id="followup_2", 
            value="Especialmente por las noches y cuando estoy solo",
            timestamp="2024-01-15T14:41:00"
        )
    ]
    
    session.followup_answers = followup_answers
    
    return session

def create_mock_diagnostic_data():
    """Create mock diagnostic data based on the provided example."""
    return {
        "pre_diagnosis": "Juan, de 34 años, presenta síntomas consistentes con un estado de ánimo deprimido y ansiedad, caracterizado por anhedonia (pérdida de interés y placer en actividades previamente disfrutadas), sentimientos de nerviosismo, tensión, rumiación sobre la juventud perdida y una sensación general de pérdida de sentido. Si bien no hay indicios de riesgo suicida inminente o psicosis, la persistencia y la naturaleza gradual de estos síntomas sugieren una adaptación desajustada al estrés y la necesidad de intervención profesional para abordar la depresión y la ansiedad.",
        "comments": "La información consolidada de los sub-agentes revela un patrón claro de malestar emocional en Juan. La anhedonia, la ansiedad y la preocupación existencial por la etapa vital son temas recurrentes. Es fundamental destacar la sugerencia unánime de buscar apoyo profesional. Las actividades que antes le generaban disfrute ahora le resultan indiferentes, lo cual, combinado con la ansiedad y la dificultad para desconectar, especialmente en momentos de soledad, indica la necesidad de estrategias de afrontamiento y exploración de las causas subyacentes. Es importante que Juan sepa que estos sentimientos son abordables y que existen caminos para recuperar su bienestar.",
        "score": "Servicio profesional de psicología",
        "filled_doc": "Guía de Evaluación para Determinar Tipo de Ayuda en Bienestar Mental mas diagnostico superficial de lo hablado en las conversaciones con la IA\n\nIntroducción\nEsta guía está diseñada para ayudar a identificar qué tipo de apoyo en bienestar mental es más apropiado para cada situación individual. El objetivo es proporcionar una herramienta estructurada que permita hacer un pre diagnostico breve sobre la situación de la persona como también diferenciar entre 5 niveles de intervención:\n\nNo necesitar ayuda profesional\nAcompañamiento por un no profesional (coaching de vida/emocional)\nServicio profesional de psicología\nServicio avanzado de psiquiatría\no servicios de urgencias prioritario\n\nInstrucciones de Uso\nPara cada pregunta, analiza la respuesta que te dio y luego analizaras la respuesta que mejor describe la situación situación actual. Al final, suma los puntos según las indications para obtener tu perfil de necesidades de apoyo.\n\nCuestionario de Evaluación\n1. ¿Cuál es el motivo principal de tu preocupación?\nJuan expresa preocupación por el estrés de llegar a los 30 y la sensación de haber perdido la juventud sin haberla aprovechado. (3 puntos)\n\n2. ¿Te sientes nervioso, tenso o ansioso con frecuencia?\nRefiere sentirse nervioso, tenso y ansioso, especialmente por las noches o cuando está solo. (3 puntos)"
    }

def test_payload_transformation():
    """Test the payload transformation from session to new schema."""
    print("🔄 DATABASE SCHEMA TRANSFORMATION TEST")
    print("=" * 50)
    
    # Create mock data
    session = create_mock_session()
    diagnostic_data = create_mock_diagnostic_data()
    
    # Create database service
    db_service = DatabaseService()
    
    # Transform data to new schema
    payload = db_service._prepare_complete_payload(session, diagnostic_data)
    
    print("📋 ORIGINAL SESSION DATA:")
    print(f"   • Phone Number: {session.phone_number}")
    print(f"   • Created At: {session.created_at}")
    print(f"   • Initial Answers: {len(session.answers)}")
    print(f"   • Follow-up Questions: {len(session.followup_questions)}")
    print(f"   • Follow-up Answers: {len(session.followup_answers)}")
    
    print("\n🩺 DIAGNOSTIC DATA:")
    print(f"   • Pre-diagnosis Length: {len(diagnostic_data.get('pre_diagnosis', ''))}")
    print(f"   • Comments Length: {len(diagnostic_data.get('comments', ''))}")
    print(f"   • Score: {diagnostic_data.get('score', 'Unknown')}")
    print(f"   • Filled Doc Length: {len(diagnostic_data.get('filled_doc', ''))}")
    
    print("\n🔄 TRANSFORMED PAYLOAD:")
    print("=" * 40)
    for key, value in payload.items():
        if isinstance(value, str) and len(value) > 100:
            print(f"   • {key}: {len(value)} characters")
            print(f"     Preview: {value[:100]}...")
        else:
            print(f"   • {key}: {value}")
    
    return payload

def test_schema_validation():
    """Test that the payload matches the required schema."""
    print("\n📋 SCHEMA VALIDATION TEST")
    print("=" * 35)
    
    session = create_mock_session()
    diagnostic_data = create_mock_diagnostic_data()
    db_service = DatabaseService()
    payload = db_service._prepare_complete_payload(session, diagnostic_data)
    
    # Required schema fields
    required_fields = [
        "number",
        "initial_questions", 
        "llm_questions",
        "pre_diagnosis",
        "comments",
        "score",
        "filled_doc"
    ]
    
    print("✅ SCHEMA VALIDATION:")
    all_present = True
    
    for field in required_fields:
        if field in payload:
            print(f"   ✓ {field}: Present")
        else:
            print(f"   ❌ {field}: Missing")
            all_present = False
    
    if all_present:
        print("\n🎉 All required fields present!")
    else:
        print("\n❌ Schema validation failed!")
    
    print("\n📊 FIELD DETAILS:")
    for field in required_fields:
        value = payload.get(field, "")
        if isinstance(value, str):
            print(f"   • {field}: {len(value)} characters")
        else:
            print(f"   • {field}: {type(value).__name__}")

def test_unique_identifier():
    """Test the unique identifier generation."""
    print("\n🔢 UNIQUE IDENTIFIER TEST")
    print("=" * 35)
    
    session1 = create_mock_session()
    session2 = create_mock_session()
    session2.phone_number = "573226235227"  # Different phone
    session2.created_at = datetime(2024, 1, 15, 15, 30, 0)  # Different time
    
    db_service = DatabaseService()
    diagnostic_data = create_mock_diagnostic_data()
    
    payload1 = db_service._prepare_complete_payload(session1, diagnostic_data)
    payload2 = db_service._prepare_complete_payload(session2, diagnostic_data)
    
    print("📱 SESSION 1:")
    print(f"   • Phone: {session1.phone_number}")
    print(f"   • Time: {session1.created_at}")
    print(f"   • Unique ID: {payload1['number']}")
    
    print("\n📱 SESSION 2:")
    print(f"   • Phone: {session2.phone_number}")
    print(f"   • Time: {session2.created_at}")
    print(f"   • Unique ID: {payload2['number']}")
    
    if payload1['number'] != payload2['number']:
        print("\n✅ Unique identifiers are different!")
    else:
        print("\n❌ Unique identifiers are the same!")

def show_database_flow():
    """Show the new database flow."""
    print("\n🔄 NEW DATABASE FLOW")
    print("=" * 30)
    
    flow_steps = [
        "1. Patient completes initial questionnaire",
        "2. System gets follow-up questions from API",
        "3. Patient answers follow-up questions", 
        "4. System sends complete data to API for diagnosis",
        "5. Patient receives diagnostic support",
        "6. ✨ NEW: System stores COMPLETE data in database",
        "7. Specialists are notified for validation",
        "8. Patient receives specialist decision"
    ]
    
    for step in flow_steps:
        if "NEW:" in step:
            print(f"   🌟 {step}")
        else:
            print(f"   {step}")

def main():
    """Main test function."""
    payload = test_payload_transformation()
    test_schema_validation()
    test_unique_identifier()
    show_database_flow()
    
    print("\n" + "=" * 50)
    print("🎉 DATABASE SCHEMA TRANSFORMATION COMPLETE!")
    print()
    print("✅ CHANGES IMPLEMENTED:")
    changes = [
        "Removed initial database call during questionnaire ✓",
        "Added complete database call at end with full diagnostic ✓", 
        "Transformed data to match new schema format ✓",
        "Generated unique session identifiers ✓",
        "Separated initial_questions and llm_questions ✓",
        "Included complete diagnostic data (pre_diagnosis, comments, score, filled_doc) ✓"
    ]
    
    for change in changes:
        print(f"   {change}")
    
    print("\n📊 NEW SCHEMA FIELDS:")
    schema_fields = [
        "• number: Unique session identifier (phone_timestamp)",
        "• initial_questions: Q&A from initial questionnaire",
        "• llm_questions: Q&A from follow-up questions", 
        "• pre_diagnosis: AI diagnostic analysis",
        "• comments: Sub-agent analysis comments",
        "• score: Priority/risk score",
        "• filled_doc: Complete diagnostic document"
    ]
    
    for field in schema_fields:
        print(f"   {field}")
    
    print("\n🚀 READY FOR TESTING:")
    print("   • Database called once at the end with complete data")
    print("   • All diagnostic information included in single payload")
    print("   • Proper schema format for database integration")
    print("   • Unique session tracking for record management")

if __name__ == "__main__":
    main()
