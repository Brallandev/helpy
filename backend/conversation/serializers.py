from rest_framework import serializers
from .models import Conversation, Message


class MessageSerializer(serializers.ModelSerializer):
    """Serializer for Message model"""
    sender_name = serializers.CharField(source='sender.username', read_only=True)
    
    class Meta:
        model = Message
        fields = ['id', 'role', 'content', 'timestamp', 'order_index', 'sender_name']
        read_only_fields = ['timestamp', 'order_index']


class ConversationSerializer(serializers.ModelSerializer):
    """Serializer for Conversation model"""
    messages = MessageSerializer(many=True, read_only=True)
    participant_names = serializers.SerializerMethodField()
    message_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Conversation
        fields = ['id', 'title', 'participants', 'created_at', 'updated_at', 'is_active', 'messages', 'participant_names', 'message_count']
        read_only_fields = ['created_at', 'updated_at']
    
    def get_participant_names(self, obj):
        return [user.username for user in obj.participants.all()]
    
    def get_message_count(self, obj):
        return obj.messages.count()


class ConversationCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating new conversations"""
    
    class Meta:
        model = Conversation
        fields = ['title', 'participants']


class MessageCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating new messages"""
    
    class Meta:
        model = Message
        fields = ['conversation', 'role', 'content']
    
    def validate_conversation(self, value):
        # Ensure conversation exists and is active
        if not value.is_active:
            raise serializers.ValidationError("Cannot add messages to inactive conversations")
        return value
