#!/usr/bin/env python3
"""
Test script for database integration.
This script simulates the database API call with the exact payload structure.
"""

import asyncio
import json
from datetime import datetime
from app.services.database_service import DatabaseService
from app.models.session import UserSession
from app.models.question import Answer

async def test_database_integration():
    """Test the database integration with sample data."""
    
    print("🧪 Testing Database Integration")
    print("="*50)
    
    # Create a mock session with sample data
    session = UserSession(phone_number="+573213754760")
    session.created_at = datetime.now()
    
    # Add sample answers (matching your mental health questions)
    sample_answers = [
        Answer("name", "David"),
        Answer("age", "25"),
        Answer("main_concern", "Ansiedad por trabajo"),
        Answer("anxiety", "Sí, frecuentemente"),
        Answer("symptom_duration", "2 meses"),
        Answer("relaxation_difficulty", "Sí, mucho"),
        Answer("sadness", "A veces"),
        Answer("loss_of_interest", "Sí, en algunas actividades"),
        Answer("hallucinations_meds", "No"),
        Answer("self_harm_thoughts", "No"),
        Answer("fatigue", "Sí, constantemente"),
        Answer("desired_outcome", "Sentirme mejor"),
        Answer("specialist_connection", "Sí, por favor")
    ]
    
    session.answers = sample_answers
    
    # Test database service
    print("📊 Creating DatabaseService instance...")
    db_service = DatabaseService()
    
    print(f"🔗 Database URL: {db_service.database_url}")
    print(f"🔑 Auth Token: {db_service.auth_token[:20]}...{db_service.auth_token[-10:]}")
    print()
    
    print("📋 Sample payload that will be sent:")
    payload = db_service._prepare_payload(session)
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    print()
    
    print("🚀 Testing database API call...")
    print("⚠️  Note: This will make a real API call to the database endpoint!")
    
    try:
        response = await db_service.store_intake_data(session)
        
        print("\n✅ Database API call completed!")
        print("📋 Response:")
        print(json.dumps(response, ensure_ascii=False, indent=2))
        
        if response.get("success", False):
            print("\n🎉 SUCCESS: Data stored successfully in database!")
        else:
            print(f"\n❌ FAILED: {response.get('error', 'Unknown error')}")
            
    except Exception as e:
        print(f"\n💥 EXCEPTION: {str(e)}")
    
    finally:
        await db_service.close()
        print("\n🔧 Database service closed.")

if __name__ == "__main__":
    print("WhatsApp Mental Health Bot - Database Integration Test")
    print("="*60)
    
    # Check if we should run the test
    response = input("This will make a real API call to the database. Continue? (y/N): ")
    if response.lower() in ['y', 'yes']:
        asyncio.run(test_database_integration())
    else:
        print("Test cancelled.")
