# Conversation App

A Django app for saving and reconstructing conversation messages with proper ordering and participant management.

## Features

- **Conversation Management**: Create, update, and archive conversations
- **Message Storage**: Store messages with role-based categorization (user, assistant, system)
- **Automatic Ordering**: Messages are automatically ordered using an index system
- **Participant Management**: Add/remove participants from conversations
- **Reconstruction**: Reconstruct conversations in their original order
- **Bulk Operations**: Create multiple messages at once
- **RESTful API**: Full CRUD operations via Django REST Framework

## Models

### Conversation
- `title`: Optional title for the conversation
- `participants`: Many-to-many relationship with User model
- `created_at`: Timestamp when conversation was created
- `updated_at`: Timestamp when conversation was last updated
- `is_active`: Boolean flag to archive conversations

### Message
- `conversation`: Foreign key to Conversation
- `sender`: Foreign key to User (optional for system messages)
- `role`: Choice field (user, assistant, system)
- `content`: Text content of the message
- `timestamp`: When the message was created
- `order_index`: Integer for maintaining message order

## API Endpoints

### Conversations

- `GET /api/conversations/` - List user's conversations
- `POST /api/conversations/` - Create new conversation
- `GET /api/conversations/{id}/` - Get conversation details
- `PUT /api/conversations/{id}/` - Update conversation
- `DELETE /api/conversations/{id}/` - Delete conversation
- `POST /api/conversations/{id}/add_participant/` - Add participant
- `POST /api/conversations/{id}/remove_participant/` - Remove participant
- `POST /api/conversations/{id}/archive/` - Archive conversation
- `GET /api/conversations/{id}/reconstruct/` - Reconstruct conversation in order

### Messages

- `GET /api/messages/` - List user's messages
- `POST /api/messages/` - Create new message
- `GET /api/messages/{id}/` - Get message details
- `PUT /api/messages/{id}/` - Update message
- `DELETE /api/messages/{id}/` - Delete message
- `GET /api/messages/by_conversation/?conversation_id={id}` - Get messages by conversation
- `POST /api/messages/bulk_create/` - Create multiple messages

## Usage Examples

### Creating a Conversation

```python
# Via API
POST /api/conversations/
{
    "title": "Medical Consultation",
    "participants": [1, 2]  # User IDs
}
```

### Adding Messages

```python
# Single message
POST /api/messages/
{
    "conversation": 1,
    "role": "user",
    "content": "Hello, I have a question about my symptoms."
}

# Multiple messages
POST /api/messages/bulk_create/
{
    "conversation_id": 1,
    "messages": [
        {"role": "user", "content": "I have a headache"},
        {"role": "assistant", "content": "How long have you had it?"},
        {"role": "user", "content": "Since yesterday morning"}
    ]
}
```

### Reconstructing a Conversation

```python
GET /api/conversations/1/reconstruct/
```

Response:
```json
{
    "conversation_id": 1,
    "title": "Medical Consultation",
    "created_at": "2024-01-15T10:00:00Z",
    "message_count": 3,
    "messages": [
        {
            "order": 1,
            "role": "user",
            "sender": "patient123",
            "content": "I have a headache",
            "timestamp": "2024-01-15T10:00:00Z"
        },
        {
            "order": 2,
            "role": "assistant",
            "sender": "System",
            "content": "How long have you had it?",
            "timestamp": "2024-01-15T10:01:00Z"
        },
        {
            "order": 3,
            "role": "user",
            "sender": "patient123",
            "content": "Since yesterday morning",
            "timestamp": "2024-01-15T10:02:00Z"
        }
    ]
}
```

## Admin Interface

The app includes a Django admin interface for managing conversations and messages:

- **ConversationAdmin**: Manage conversations with participant management
- **MessageAdmin**: View and manage messages with content previews

## Testing

Run the tests with:

```bash
python manage.py test conversation
```

## Security Features

- **Authentication Required**: All endpoints require user authentication
- **Access Control**: Users can only access conversations they participate in
- **Validation**: Messages cannot be added to archived conversations
- **Atomic Operations**: Bulk operations use database transactions

## Dependencies

- Django 5.2+
- Django REST Framework
- PostgreSQL (recommended for production)

## Installation

1. Add 'conversation' to INSTALLED_APPS in settings.py
2. Include conversation.urls in your main URL configuration
3. Run migrations: `python manage.py makemigrations conversation && python manage.py migrate`
4. Create a superuser to access the admin interface: `python manage.py createsuperuser`
