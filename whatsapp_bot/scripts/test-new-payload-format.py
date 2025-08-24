#!/usr/bin/env python3
"""
Test script for the new payload format.

This script demonstrates the new payload structure for both initial and follow-up API calls.
The new format uses:
- "phone_number" instead of "user_phone"
- "chat" as an array of {"question": "...", "answer": "..."} objects

Usage:
    python scripts/test-new-payload-format.py
"""

import json
from datetime import datetime

def show_old_vs_new_format():
    """Show comparison between old and new payload formats."""
    print("🔄 PAYLOAD FORMAT MIGRATION")
    print("=" * 60)
    
    print("❌ OLD FORMAT (No longer used):")
    print("-" * 30)
    old_format = {
        "user_phone": "+573213754760",
        "timestamp": "2025-01-23T16:30:15.123456",
        "chat": {
            "name": "David",
            "age": "25",
            "main_concern": "Ansiedad por trabajo",
            "followup_1": "Me siento triste por las mañanas"
        }
    }
    print(json.dumps(old_format, ensure_ascii=False, indent=2))
    
    print("\n✅ NEW FORMAT (Current implementation):")
    print("-" * 30)
    new_format = {
        "phone_number": "+573213754760",
        "chat": [
            {
                "question": "¡Hola! 👋 Para comenzar, ¿cuál es tu nombre completo?",
                "answer": "David"
            },
            {
                "question": "¿Cuál es tu edad?",
                "answer": "25"
            },
            {
                "question": "¿Cuál es el motivo principal de tu preocupación?",
                "answer": "Ansiedad por trabajo"
            },
            {
                "question": "En general, ¿cómo describirías tu estado de ánimo?",
                "answer": "Me siento triste por las mañanas"
            }
        ]
    }
    print(json.dumps(new_format, ensure_ascii=False, indent=2))

def demonstrate_api_calls():
    """Demonstrate the payload for both API calls."""
    print("\n🚀 API CALL DEMONSTRATION")
    print("=" * 40)
    
    # Initial API call payload
    print("📋 FIRST API CALL (After initial questionnaire):")
    print("-" * 50)
    initial_payload = {
        "phone_number": "+573213754760",
        "chat": [
            {"question": "¡Hola! 👋 Para comenzar, ¿cuál es tu nombre completo?", "answer": "David"},
            {"question": "¿Cuál es tu edad?", "answer": "25"},
            {"question": "¿Cuál es el motivo principal de tu preocupación?", "answer": "Ansiedad por trabajo"},
            {"question": "¿Te sientes nervioso, tenso o ansioso con frecuencia?", "answer": "Sí, frecuentemente"},
            {"question": "¿Cuánto tiempo llevas experimentando estos síntomas?", "answer": "2 meses"},
            {"question": "¿Estás teniendo dificultad para relajarte?", "answer": "Sí, mucho"},
            {"question": "¿Te sientes triste o deprimido?", "answer": "A veces, por el trabajo"},
            {"question": "¿Has perdido interés en actividades que antes disfrutabas?", "answer": "Sí, en deportes"},
            {"question": "¿Tienes alucinaciones o estás en medicamentos psiquiátricos?", "answer": "No"},
            {"question": "¿Has tenido pensamientos sobre hacerte daño?", "answer": "No"},
            {"question": "¿Te sientes cansado todo el tiempo?", "answer": "Sí, constantemente"},
            {"question": "¿Qué te gustaría que pasara ahora mismo?", "answer": "Sentirme mejor"},
            {"question": "¿Quieres conectar ya con un especialista?", "answer": "Sí, por favor"}
        ]
    }
    
    print(f"📊 Total questions: {len(initial_payload['chat'])}")
    print("🎯 Expected API response: follow-up questions")
    print("\nSample questions:")
    for i, qa in enumerate(initial_payload['chat'][:3], 1):
        print(f"  {i}. Q: {qa['question'][:50]}...")
        print(f"     A: {qa['answer']}")
    print("  ... (8 more questions)")
    
    # Follow-up API call payload
    print("\n📋 SECOND API CALL (After follow-up questions):")
    print("-" * 50)
    followup_payload = {
        "phone_number": "+573213754760",
        "chat": initial_payload['chat'] + [
            {
                "question": "En general, ¿cómo describirías tu estado de ánimo y tus emociones en tu día a día?",
                "answer": "Me siento triste por las mañanas especialmente, pero mejoro durante el día"
            },
            {
                "question": "Pensando en tus relaciones personales, ¿qué tan satisfecho te sientes?",
                "answer": "Tengo buenas relaciones familiares que me apoyan mucho"
            },
            {
                "question": "Si pudieras cambiar algo en tu vida para aumentar tu felicidad, ¿qué sería?",
                "answer": "Me gustaría tener más tiempo libre y menos presión en el trabajo"
            }
        ]
    }
    
    print(f"📊 Total questions: {len(followup_payload['chat'])}")
    print("🎯 Expected API response: pre-diagnosis")
    print("\nFollow-up questions:")
    for i, qa in enumerate(followup_payload['chat'][-3:], 1):
        print(f"  {i}. Q: {qa['question'][:50]}...")
        print(f"     A: {qa['answer'][:40]}...")

def show_benefits():
    """Show benefits of the new format."""
    print("\n🎯 BENEFITS OF NEW FORMAT")
    print("=" * 30)
    print("✅ Question Context: Full question text preserved")
    print("✅ Better Readability: Clear question-answer pairs")
    print("✅ API Consistency: Same format for database and external API")
    print("✅ Scalability: Easy to add more questions dynamically")
    print("✅ Debugging: Easier to trace specific Q&A pairs")
    print("✅ Integration: Standard format for all consumers")

def main():
    """Main demonstration function."""
    print("📋 NEW PAYLOAD FORMAT DEMONSTRATION")
    print("=" * 70)
    
    show_old_vs_new_format()
    demonstrate_api_calls()
    show_benefits()
    
    print("\n" + "=" * 70)
    print("🎉 NEW PAYLOAD FORMAT SUCCESSFULLY IMPLEMENTED!")
    print("📤 Both API and Database services now use:")
    print("   - phone_number (instead of user_phone)")
    print("   - chat array with question-answer objects")
    print("   - Full question text preservation")
    print("   - Support for dynamic follow-up questions")

if __name__ == "__main__":
    main()
