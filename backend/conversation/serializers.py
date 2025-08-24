from rest_framework import serializers
from .models import ChatData


class ChatDataSerializer(serializers.ModelSerializer):
    """Serializer for ChatData model"""
    
    class Meta:
        model = ChatData
        fields = ['id', 'number', 'content', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class ChatDataCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating ChatData (allows number to be optional for auto-generation)"""
    
    class Meta:
        model = ChatData
        fields = ['number', 'content']
    
    def create(self, validated_data):
        """Create ChatData instance, auto-generating number if not provided"""
        if 'number' not in validated_data or not validated_data['number']:
            # Generate a unique number if not provided
            import uuid
            validated_data['number'] = str(uuid.uuid4())[:8].upper()
        
        return super().create(validated_data)
