# WhatsApp Mental Health Triage Bot 🧠💬

A sophisticated conversational bot that conducts mental health triage through WhatsApp by asking predefined questions and integrating with external APIs for professional assessment.

## 🏗️ Project Structure

```
whatsapp_bot/
├── main.py                 # FastAPI application entry point
├── main_old.py            # Backup of original implementation
├── requirements.txt       # Python dependencies
├── .env                   # Environment variables (not in repo)
├── README.md             # This file
├── README_old.md         # Original README backup
└── app/                  # Main application package
    ├── __init__.py
    ├── config/           # Configuration management
    │   ├── __init__.py
    │   ├── settings.py   # Environment settings
    │   └── questions.py  # Mental health questions
    ├── models/           # Data models
    │   ├── __init__.py
    │   ├── session.py    # User session models
    │   └── question.py   # Question and answer models
    ├── services/         # Business logic services
    │   ├── __init__.py
    │   ├── whatsapp_service.py     # WhatsApp API integration
    │   ├── api_service.py          # External API service
    │   └── conversation_service.py # Conversation flow logic
    └── utils/            # Utility functions
        ├── __init__.py
        ├── session_manager.py    # Session management
        └── message_parser.py     # Message parsing utilities
```

## 🚀 Features

### Core Functionality
- **Mental Health Triage**: Conducts structured interviews with 13 specialized questions
- **Session Management**: Tracks conversation state and user progress
- **External API Integration**: Sends collected data for professional analysis
- **Dynamic Conversations**: Supports conversation continuation based on API responses
- **Robust Error Handling**: Graceful handling of API failures and edge cases

### Technical Features
- **Modular Architecture**: Clean separation of concerns with dedicated services
- **Type Safety**: Full type hints throughout the codebase
- **Async/Await**: Non-blocking operations for better performance
- **Comprehensive Logging**: Detailed request/response logging for debugging
- **RESTful API**: Debug endpoints for session management
- **Environment-based Configuration**: Secure credential management

## 🔄 Conversation Flow

### 1. **Consent Process**
When a user first contacts the bot:

1. **Greeting Message**: Welcome message
2. **Informed Consent**: Full legal consent form with:
   - Service information
   - Data treatment (Colombian Law 1581/2012)
   - Privacy & confidentiality
   - User rights
   - Service limitations
   - Consent declaration

3. **Interactive Buttons**: 
   - "Sí, acepto" (Yes, I accept)
   - "No, gracias" (No, thanks)

4. **Response Handling**:
   - **If "Yes"**: Proceed to mental health questionnaire
   - **If "No"**: Send goodbye message and end conversation

### 2. **Mental Health Questions**

After consent is given, the bot asks these triage questions:

1. **Basic Information**
   - Full name
   - Age

2. **Mental Health Assessment**
   - Main concern/worry
   - Anxiety levels
   - Symptom duration
   - Relaxation difficulties
   - Depression symptoms
   - Loss of interest in activities
   - Hallucinations or psychiatric medications
   - Self-harm thoughts
   - Chronic fatigue
   - Desired outcomes
   - Specialist connection preference

## ⚙️ Configuration

### Environment Variables

Create a `.env` file with:

```env
# WhatsApp Business API Configuration
WHATSAPP_TOKEN=your_whatsapp_business_api_token_here
PHONE_NUMBER_ID=your_phone_number_id_here
VERIFY_TOKEN=your_webhook_verify_token_here
GRAPH_API_VERSION=v20.0

# External API Configuration
EXTERNAL_API_URL=https://your-mental-health-api.com/process

# Database API Configuration
DATABASE_API_URL=http://18.190.66.49:8000/api/patients/intake/
DATABASE_API_TOKEN=your_database_bearer_token_here
```

### Dependencies

```bash
pip install -r requirements.txt
```

## 🔄 API Integration

### Dual Endpoint Architecture

When all questions are answered, the bot sends data to **two endpoints**:

1. **📊 Database Storage** (Priority): Stores intake data for record keeping
2. **🧠 External Processing API**: Processes data and generates responses

### Request Format

Both endpoints receive the same payload structure:

```json
{
  "user_phone": "+573213754760", 
  "timestamp": "2025-08-23T16:30:15.123456",
  "answers": {
    "name": "Patient Name",
    "age": "25", 
    "main_concern": "Ansiedad por trabajo",
    "anxiety": "Sí, frecuentemente",
    "symptom_duration": "2 meses",
    "relaxation_difficulty": "Sí, mucho",
    "sadness": "A veces", 
    "loss_of_interest": "Sí, en algunas actividades",
    "hallucinations_meds": "No",
    "self_harm_thoughts": "No",
    "fatigue": "Sí, constantemente",
    "desired_outcome": "Sentirme mejor",
    "specialist_connection": "Sí, por favor"
  }
}
```

### Database Endpoint

- **URL**: `http://18.190.66.49:8000/api/patients/intake/`
- **Method**: `POST`
- **Auth**: `Bearer eyJhbGciOiJIUzI1NiIs...`
- **Purpose**: Store patient intake data for records

### Response Format

Your API should respond with:

```json
{
  "continue_conversation": true,
  "message": "Thank you for completing the assessment. A specialist will contact you soon.",
  "final_message": "Assessment completed successfully",
  "additional_questions": [
    {
      "id": "follow_up",
      "text": "Is there anything else you'd like to add?",
      "required": false
    }
  ]
}
```

## 🚀 Running the Application

### 🐳 Docker (Recommended)

#### Quick Start
```bash
# Copy environment template
cp env.example .env
# Edit .env with your WhatsApp credentials

# Development
docker-compose -f docker-compose.dev.yml up --build

# Production
docker-compose up -d --build
```

#### Full Production (with Redis & Nginx)
```bash
docker-compose --profile production up -d --build
```

📖 **See [DOCKER.md](DOCKER.md) for complete Docker deployment guide**

### 🐍 Local Development

#### Prerequisites
```bash
pip install -r requirements.txt
```

#### Development
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

#### Production
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

## 🛠️ Debug Endpoints

### Session Management
- `GET /sessions` - List all active sessions
- `GET /sessions/{phone_number}` - Get detailed session info
- `DELETE /sessions/{phone_number}` - Reset a user's session

### Testing
- `GET /send-test?to={phone}&text={message}` - Send test message

### Webhook
- `GET /webhook` - Webhook verification
- `POST /webhook` - Receive WhatsApp messages

## 📊 Conversation Flow

```mermaid
graph TD
    A[User sends message] --> B{New session?}
    B -->|Yes| C[Send greeting]
    C --> D[Send consent form with buttons]
    D --> E[Wait for consent response]
    E --> F{Consent given?}
    F -->|Yes| G[Start questionnaire]
    F -->|No| H[Send goodbye message]
    H --> I[End conversation]
    G --> J[Ask first question]
    J --> K[Wait for answer]
    K --> L[Save answer]
    L --> M{All questions answered?}
    M -->|No| N[Ask next question]
    M -->|Yes| O[Send to API]
    O --> P{Continue conversation?}
    P -->|Yes| Q[Ask additional questions]
    P -->|No| I
    N --> K
    Q --> K
    B -->|No| R{Session state?}
    R -->|Waiting consent| E
    R -->|Waiting answer| L
    R -->|Consent declined| H
    R -->|Processing API| S[Ask to wait]
    R -->|Ended| T[Restart flow]
    T --> C
```

## 🏥 Mental Health Considerations

### Critical Response Handling
- **Self-harm indicators**: Immediate escalation protocols
- **Hallucinations**: Priority flagging for clinical review
- **Severe symptoms**: Urgent referral pathways

### Privacy & Security
- **Data encryption**: All mental health data encrypted in transit
- **HIPAA compliance**: Ensure your external API meets healthcare standards
- **Audit trails**: Comprehensive logging for clinical accountability

### Clinical Integration
- **Risk stratification**: API should classify risk levels
- **Provider matching**: Connect users with appropriate specialists
- **Follow-up scheduling**: Automated appointment booking integration

## 🔧 Development

### Adding New Questions
1. Update `app/config/questions.py`
2. Modify the API payload structure if needed
3. Update documentation

### Custom Services
1. Create new service in `app/services/`
2. Add to `app/services/__init__.py`
3. Inject into main application

### Testing
```bash
# Test the conversation flow
curl "http://localhost:8000/send-test?to=YOUR_PHONE&text=test"

# Check session state
curl "http://localhost:8000/sessions/YOUR_PHONE"

# Reset if needed
curl -X DELETE "http://localhost:8000/sessions/YOUR_PHONE"
```

## 🚨 Deployment Considerations

### Production Checklist
- [ ] Use Redis/Database for session storage
- [ ] Implement rate limiting
- [ ] Set up proper logging and monitoring
- [ ] Configure SSL/TLS
- [ ] Add authentication for debug endpoints
- [ ] Set up session cleanup for inactive users
- [ ] Implement backup and recovery procedures
- [ ] Configure alerting for critical responses

### Scaling
- Use horizontal scaling with load balancers
- Implement session affinity or distributed session storage
- Monitor API response times and scale external API accordingly
- Set up auto-scaling based on message volume

## 📝 License

This project is intended for mental health triage and should be used in compliance with local healthcare regulations and professional standards.

## 🆘 Support

For technical issues or clinical integration questions, please refer to the project documentation or contact the development team.

---

**⚠️ Important**: This bot is designed for initial triage only and should not replace professional mental health assessment or emergency services.
