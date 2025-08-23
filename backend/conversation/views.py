from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.db import transaction
import uuid

from .models import ChatData, ChatMessage
from .serializers import (
    ChatDataSerializer,
    ChatDataCreateSerializer,
    ChatMessageSerializer,
    ChatMessageCreateSerializer
)


class ChatDataViewSet(viewsets.ModelViewSet):
    """ViewSet for managing chat data"""
    permission_classes = [IsAuthenticated]
    serializer_class = ChatDataSerializer
    queryset = ChatData.objects.all()
    
    def get_serializer_class(self):
        if self.action == 'create':
            return ChatDataCreateSerializer
        return ChatDataSerializer
    
    def perform_create(self, serializer):
        """Create chat data with auto-generated session ID if not provided"""
        if not serializer.validated_data.get('session_id'):
            serializer.validated_data['session_id'] = f"chat_{uuid.uuid4().hex[:8]}"
        serializer.save()
    
    @action(detail=False, methods=['post'])
    def receive_chat(self, request):
        """Receive chat data in the specified format"""
        chat_data = request.data.get('chat', [])
        
        if not chat_data:
            return Response(
                {'error': 'Chat data is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validate chat data structure
        for i, message in enumerate(chat_data):
            if not isinstance(message, dict):
                return Response(
                    {'error': f'Message {i+1} must be a dictionary'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            if 'question' not in message or 'answer' not in message:
                return Response(
                    {'error': f'Message {i+1} must contain question and answer fields'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            if not message['question'] or not message['answer']:
                return Response(
                    {'error': f'Message {i+1} cannot have empty question or answer'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        try:
            with transaction.atomic():
                # Create chat data record
                session_id = f"chat_{uuid.uuid4().hex[:8]}"
                chat_data_obj = ChatData.objects.create(
                    session_id=session_id,
                    notes="Chat data received via API"
                )
                
                # Create chat messages
                created_messages = []
                for i, message_data in enumerate(chat_data, 1):
                    chat_message = ChatMessage.objects.create(
                        chat_data=chat_data_obj,
                        question=message_data['question'],
                        answer=message_data['answer'],
                        order_index=i
                    )
                    created_messages.append({
                        'order_index': chat_message.order_index,
                        'question': chat_message.question,
                        'answer': chat_message.answer
                    })
                
                return Response({
                    'message': 'Chat data received successfully',
                    'session_id': session_id,
                    'message_count': len(created_messages),
                    'messages': created_messages,
                    'created_at': chat_data_obj.created_at
                }, status=status.HTTP_201_CREATED)
                
        except Exception as e:
            return Response(
                {'error': f'Failed to save chat data: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['post'])
    def mark_processed(self, request, pk=None):
        """Mark chat data as processed"""
        chat_data = self.get_object()
        chat_data.is_processed = True
        chat_data.save()
        return Response({'message': 'Chat data marked as processed'})
    
    @action(detail=True, methods=['get'])
    def export(self, request, pk=None):
        """Export chat data in the original format"""
        chat_data = self.get_object()
        messages = chat_data.messages.all().order_by('order_index')
        
        export_data = {
            'chat': [
                {
                    'question': msg.question,
                    'answer': msg.answer
                }
                for msg in messages
            ]
        }
        
        return Response(export_data)
    
    @action(detail=True, methods=['get'])
    def messages(self, request, pk=None):
        """Get all messages for a specific chat session"""
        chat_data = self.get_object()
        messages = chat_data.messages.all().order_by('order_index')
        serializer = ChatMessageSerializer(messages, many=True)
        return Response(serializer.data)


class ChatMessageViewSet(viewsets.ModelViewSet):
    """ViewSet for managing individual chat messages"""
    permission_classes = [IsAuthenticated]
    serializer_class = ChatMessageSerializer
    queryset = ChatMessage.objects.all()
    
    def get_serializer_class(self):
        if self.action == 'create':
            return ChatMessageCreateSerializer
        return ChatMessageSerializer
    
    def get_queryset(self):
        """Return messages from chat sessions accessible to the user"""
        return ChatMessage.objects.filter(
            chat_data__is_processed=False
        ).select_related('chat_data')
    
    @action(detail=False, methods=['get'])
    def by_session(self, request):
        """Get all messages from a specific chat session"""
        session_id = request.query_params.get('session_id')
        if not session_id:
            return Response({'error': 'session_id is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            chat_data = ChatData.objects.get(session_id=session_id)
            messages = chat_data.messages.all().order_by('order_index')
            serializer = self.get_serializer(messages, many=True)
            return Response(serializer.data)
        except ChatData.DoesNotExist:
            return Response({'error': 'Chat session not found'}, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=False, methods=['post'])
    def bulk_create(self, request):
        """Create multiple messages for a chat session"""
        messages_data = request.data.get('messages', [])
        session_id = request.data.get('session_id')
        
        if not messages_data or not session_id:
            return Response({'error': 'messages and session_id are required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            chat_data = ChatData.objects.get(session_id=session_id)
        except ChatData.DoesNotExist:
            return Response({'error': 'Chat session not found'}, status=status.HTTP_404_NOT_FOUND)
        
        created_messages = []
        
        with transaction.atomic():
            for i, msg_data in enumerate(messages_data, 1):
                msg_data['chat_data'] = chat_data.id
                msg_data['order_index'] = msg_data.get('order_index', i)
                
                serializer = ChatMessageCreateSerializer(data=msg_data)
                if serializer.is_valid():
                    message = serializer.save()
                    created_messages.append(ChatMessageSerializer(message).data)
                else:
                    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        return Response({
            'message': f'Successfully created {len(created_messages)} messages',
            'messages': created_messages
        }, status=status.HTTP_201_CREATED)
