from rest_framework import serializers
from .models import ChatData


class ChatDataSerializer(serializers.ModelSerializer):
    """Serializer for ChatData model - full data representation"""
    
    class Meta:
        model = ChatData
        fields = [
            'id', 'number', 'initial_questions', 'llm_questions', 
            'pre_diagnosis', 'comments', 'score', 'filled_doc',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class ChatDataUpsertSerializer(serializers.ModelSerializer):
    """Unified serializer for creating or updating ChatData"""
    
    class Meta:
        model = ChatData
        fields = [
            'number', 'initial_questions', 'llm_questions', 
            'pre_diagnosis', 'comments', 'score', 'filled_doc'
        ]
    
    def create(self, validated_data):
        """Create ChatData instance, auto-generating number if not provided"""
        if 'number' not in validated_data or not validated_data['number']:
            # Generate a unique number if not provided
            import uuid
            validated_data['number'] = str(uuid.uuid4())[:8].upper()
        
        return super().create(validated_data)
    
    def update(self, instance, validated_data):
        """Update ChatData instance with provided data"""
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance
