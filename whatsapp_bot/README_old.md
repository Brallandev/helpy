# WhatsApp Conversational Bot

A WhatsApp bot that conducts structured conversations by asking predefined questions, collecting answers, and integrating with external APIs for dynamic responses.

## Features

- **Structured Conversations**: Asks predefined questions in sequence
- **Session Management**: Tracks user state and conversation progress
- **Answer Storage**: Stores user responses with timestamps
- **External API Integration**: Sends collected data to external APIs
- **Dynamic Conversation Flow**: Continues conversations based on API responses
- **Session Reset**: Automatically handles conversation restarts

## Architecture

### Data Models

- **Question**: Represents a question with ID, text, and required flag
- **Answer**: Stores user response with question ID, value, and timestamp
- **UserSession**: Manages conversation state for each user
- **SessionState**: Enum for tracking conversation phases

### Core Components

1. **Session Management**: Tracks users and their conversation progress
2. **Question Engine**: Manages the sequence of predefined questions
3. **Answer Storage**: Stores responses in structured format
4. **API Integration**: Communicates with external services
5. **Conversation Flow**: Handles dynamic conversation continuation

## Configuration

Create a `.env` file with the following variables:

```env
# WhatsApp Business API Configuration
WHATSAPP_TOKEN=your_whatsapp_business_api_token_here
PHONE_NUMBER_ID=your_phone_number_id_here
VERIFY_TOKEN=your_webhook_verify_token_here
GRAPH_API_VERSION=v20.0

# External API Configuration
EXTERNAL_API_URL=https://your-api-endpoint.com/process
```

## Usage

### Running the Bot

```bash
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### Webhook Setup

1. Set up your webhook URL: `https://your-domain.com/webhook`
2. Use the `VERIFY_TOKEN` for webhook verification
3. Configure WhatsApp webhook to send messages to your endpoint

### Customizing Questions

Edit the `QUESTIONS` list in `main.py`:

```python
QUESTIONS = [
    Question("name", "¿Cuál es tu nombre?"),
    Question("email", "¿Cuál es tu email?"),
    Question("issue", "Describe tu consulta"),
    # Add more questions as needed
]
```

### External API Integration

Your external API should:

1. **Accept POST requests** with this payload structure:
```json
{
    "user_phone": "+1234567890",
    "timestamp": "2024-01-15T10:30:00",
    "answers": {
        "name": "Juan Pérez",
        "age": "25",
        "location": "Madrid",
        "issue": "Consulta técnica",
        "urgency": "3"
    }
}
```

2. **Return responses** in this format:
```json
{
    "continue_conversation": true,
    "message": "Gracias por la información. Te contactaremos pronto.",
    "final_message": "Consulta procesada exitosamente",
    "additional_questions": [
        {
            "id": "follow_up",
            "text": "¿Hay algo más que quieras agregar?",
            "required": false
        }
    ]
}
```

### API Response Options

- **continue_conversation**: `true/false` - Whether to continue the conversation
- **message**: Message to send to user when continuing
- **final_message**: Message to send when ending conversation
- **additional_questions**: Array of new questions to ask dynamically

## Conversation Flow

1. **User sends first message** → Bot asks first question
2. **User answers** → Bot saves answer and asks next question
3. **All questions answered** → Bot processes with external API
4. **API responds** → Bot continues or ends conversation based on response
5. **Conversation ends** → User can start new conversation anytime

## Debug Endpoints

- `GET /sessions` - View all active sessions
- `GET /reset-session/{phone_number}` - Reset a specific user's session
- `GET /send-test?to={phone}&text={message}` - Send test message

## Session States

- **WAITING_FOR_ANSWER**: Ready to receive user input
- **PROCESSING_API**: Sending data to external API
- **CONVERSATION_ENDED**: Conversation completed

## Error Handling

- API failures are logged and graceful error messages sent to users
- Invalid responses are handled without breaking the conversation
- Sessions automatically reset when conversations end

## Production Considerations

1. **Replace in-memory storage** with Redis or database
2. **Add rate limiting** for API calls
3. **Implement proper logging** and monitoring
4. **Add authentication** for debug endpoints
5. **Configure proper error handling** and alerting
6. **Set up session cleanup** for inactive sessions

## Development

The bot includes comprehensive logging for debugging:

- `[SESSION]` - Session state changes
- `[MESSAGE]` - Incoming messages
- `[ANSWER_SAVED]` - When answers are stored
- `[API_CALL]` - External API requests
- `[API_RESPONSE]` - External API responses
- `[SEND]` - Outgoing WhatsApp messages

Monitor these logs to understand conversation flow and debug issues. 