from rest_framework import serializers
from .models import ChatData, ChatMessage


class ChatMessageSerializer(serializers.ModelSerializer):
    """Serializer for ChatMessage model"""
    
    class Meta:
        model = ChatMessage
        fields = ['id', 'question', 'answer', 'order_index', 'created_at']
        read_only_fields = ['id', 'created_at']


class ChatDataSerializer(serializers.ModelSerializer):
    """Serializer for ChatData model"""
    messages = ChatMessageSerializer(many=True, read_only=True)
    message_count = serializers.SerializerMethodField()
    
    class Meta:
        model = ChatData
        fields = ['id', 'session_id', 'created_at', 'updated_at', 'is_processed', 'notes', 'messages', 'message_count']
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_message_count(self, obj):
        return obj.messages.count()


class ChatDataCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating new chat data with messages"""
    chat = serializers.ListField(
        child=serializers.DictField(
            child=serializers.CharField(),
            fields=['question', 'answer']
        ),
        write_only=True
    )
    
    class Meta:
        model = ChatData
        fields = ['session_id', 'notes', 'chat']
    
    def create(self, validated_data):
        chat_messages = validated_data.pop('chat', [])
        chat_data = ChatData.objects.create(**validated_data)
        
        # Create chat messages
        for i, message_data in enumerate(chat_messages, 1):
            ChatMessage.objects.create(
                chat_data=chat_data,
                question=message_data.get('question', ''),
                answer=message_data.get('answer', ''),
                order_index=i
            )
        
        return chat_data
    
    def validate_chat(self, value):
        """Validate chat data structure"""
        if not value:
            raise serializers.ValidationError("Chat data cannot be empty")
        
        for i, message in enumerate(value):
            if not isinstance(message, dict):
                raise serializers.ValidationError(f"Message {i+1} must be a dictionary")
            
            if 'question' not in message or 'answer' not in message:
                raise serializers.ValidationError(f"Message {i+1} must contain 'question' and 'answer' fields")
            
            if not message['question'] or not message['answer']:
                raise serializers.ValidationError(f"Message {i+1} cannot have empty question or answer")
        
        return value


class ChatMessageCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating individual chat messages"""
    
    class Meta:
        model = ChatMessage
        fields = ['chat_data', 'question', 'answer', 'order_index']
    
    def validate(self, data):
        """Validate order_index uniqueness within chat_data"""
        if ChatMessage.objects.filter(
            chat_data=data['chat_data'], 
            order_index=data['order_index']
        ).exists():
            raise serializers.ValidationError(
                f"Message with order_index {data['order_index']} already exists in this chat session"
            )
        return data
