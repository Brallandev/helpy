# Conversation App

A Django app for saving and managing chat data with question-answer pairs and session management.

## Features

- **Chat Session Management**: Create and manage chat sessions with unique identifiers
- **Message Storage**: Store question-answer pairs with proper ordering
- **Automatic Ordering**: Messages are automatically ordered using an index system
- **Session Processing**: Track whether chat sessions have been processed
- **Bulk Operations**: Create multiple messages at once
- **RESTful API**: Full CRUD operations via Django REST Framework
- **Export Functionality**: Export chat data in the original format

## Models

### ChatData
- `session_id`: Unique identifier for the chat session
- `created_at`: Timestamp when session was created
- `updated_at`: Timestamp when session was last updated
- `is_processed`: Boolean flag to track processing status
- `notes`: Additional notes about the chat session

### ChatMessage
- `chat_data`: Foreign key to ChatData
- `question`: The question asked in the conversation
- `answer`: The answer provided
- `order_index`: Integer for maintaining message order
- `created_at`: When the message was created

## API Endpoints

### Chat Data

- `GET /api/chat-data/` - List all chat sessions
- `POST /api/chat-data/` - Create new chat session with messages
- `GET /api/chat-data/{id}/` - Get chat session details
- `PUT /api/chat-data/{id}/` - Update chat session
- `DELETE /api/chat-data/{id}/` - Delete chat session
- `POST /api/chat-data/receive_chat/` - Receive chat data in bulk
- `POST /api/chat-data/{id}/mark_processed/` - Mark session as processed
- `GET /api/chat-data/{id}/export/` - Export chat data
- `GET /api/chat-data/{id}/messages/` - Get all messages for a session

### Chat Messages

- `GET /api/chat-messages/` - List all chat messages
- `POST /api/chat-messages/` - Create new chat message
- `GET /api/chat-messages/{id}/` - Get message details
- `PUT /api/chat-messages/{id}/` - Update message
- `DELETE /api/chat-messages/{id}/` - Delete message
- `GET /api/chat-messages/by_session/?session_id={id}` - Get messages by session
- `POST /api/chat-messages/bulk_create/` - Create multiple messages

## Usage Examples

### Creating a Chat Session with Messages

```python
# Via API
POST /api/chat-data/
{
    "session_id": "chat_abc123",
    "notes": "Medical consultation session",
    "chat": [
        {
            "question": "What are your symptoms?",
            "answer": "I have a headache and fever."
        },
        {
            "question": "How long have you had these symptoms?",
            "answer": "Since yesterday morning."
        }
    ]
}
```

### Receiving Chat Data

```python
# Receive chat data in bulk
POST /api/chat-data/receive_chat/
{
    "chat": [
        {
            "question": "What is your main concern?",
            "answer": "I'm experiencing chest pain."
        },
        {
            "question": "When did this start?",
            "answer": "About an hour ago."
        }
    ]
}
```

### Adding Individual Messages

```python
# Single message
POST /api/chat-messages/
{
    "chat_data": 1,
    "question": "Are you taking any medications?",
    "answer": "Yes, I take aspirin daily.",
    "order_index": 3
}

# Multiple messages
POST /api/chat-messages/bulk_create/
{
    "session_id": "chat_abc123",
    "messages": [
        {"question": "Any allergies?", "answer": "No known allergies"},
        {"question": "Family history?", "answer": "Father had heart disease"}
    ]
}
```

### Exporting Chat Data

```python
GET /api/chat-data/1/export/
```

Response:
```json
{
    "chat": [
        {
            "question": "What are your symptoms?",
            "answer": "I have a headache and fever."
        },
        {
            "question": "How long have you had these symptoms?",
            "answer": "Since yesterday morning."
        }
    ]
}
```

### Marking Session as Processed

```python
POST /api/chat-data/1/mark_processed/
```

## Data Structure

The app stores chat data in a hierarchical structure:

1. **ChatData**: Represents a complete chat session
2. **ChatMessage**: Individual question-answer pairs within a session

Each message has an `order_index` to maintain the conversation flow, and sessions can be marked as processed to track workflow status.

## Authentication

All API endpoints require authentication. Use Django's built-in authentication system or integrate with your preferred authentication method.
