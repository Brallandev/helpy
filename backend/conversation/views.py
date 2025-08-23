from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.db import transaction

from .models import Conversation, Message
from .serializers import (
    ConversationSerializer, 
    ConversationCreateSerializer,
    MessageSerializer, 
    MessageCreateSerializer
)


class ConversationViewSet(viewsets.ModelViewSet):
    """ViewSet for managing conversations"""
    permission_classes = [IsAuthenticated]
    serializer_class = ConversationSerializer
    
    def get_queryset(self):
        """Return conversations where the user is a participant"""
        return Conversation.objects.filter(participants=self.request.user, is_active=True)
    
    def get_serializer_class(self):
        if self.action == 'create':
            return ConversationCreateSerializer
        return ConversationSerializer
    
    def perform_create(self, serializer):
        """Create conversation and add current user as participant"""
        conversation = serializer.save()
        conversation.participants.add(self.request.user)
    
    @action(detail=True, methods=['post'])
    def add_participant(self, request, pk=None):
        """Add a participant to the conversation"""
        conversation = self.get_object()
        user_id = request.data.get('user_id')
        
        if not user_id:
            return Response({'error': 'user_id is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            from django.contrib.auth.models import User
            user = User.objects.get(id=user_id)
            conversation.participants.add(user)
            return Response({'message': f'User {user.username} added to conversation'})
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=True, methods=['post'])
    def remove_participant(self, request, pk=None):
        """Remove a participant from the conversation"""
        conversation = self.get_object()
        user_id = request.data.get('user_id')
        
        if not user_id:
            return Response({'error': 'user_id is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            from django.contrib.auth.models import User
            user = User.objects.get(id=user_id)
            conversation.participants.remove(user)
            return Response({'message': f'User {user.username} removed from conversation'})
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=True, methods=['post'])
    def archive(self, request, pk=None):
        """Archive a conversation (set is_active to False)"""
        conversation = self.get_object()
        conversation.is_active = False
        conversation.save()
        return Response({'message': 'Conversation archived successfully'})
    
    @action(detail=True, methods=['get'])
    def reconstruct(self, request, pk=None):
        """Reconstruct conversation messages in order"""
        conversation = self.get_object()
        messages = conversation.messages.all().order_by('order_index')
        
        # Create a structured reconstruction
        reconstruction = {
            'conversation_id': conversation.id,
            'title': conversation.title,
            'created_at': conversation.created_at,
            'message_count': messages.count(),
            'messages': []
        }
        
        for message in messages:
            reconstruction['messages'].append({
                'order': message.order_index,
                'role': message.role,
                'sender': message.sender.username if message.sender else 'System',
                'content': message.content,
                'timestamp': message.timestamp
            })
        
        return Response(reconstruction)


class MessageViewSet(viewsets.ModelViewSet):
    """ViewSet for managing messages"""
    permission_classes = [IsAuthenticated]
    serializer_class = MessageSerializer
    
    def get_queryset(self):
        """Return messages from conversations where the user is a participant"""
        return Message.objects.filter(
            conversation__participants=self.request.user,
            conversation__is_active=True
        )
    
    def get_serializer_class(self):
        if self.action == 'create':
            return MessageCreateSerializer
        return MessageSerializer
    
    def perform_create(self, serializer):
        """Create message and set sender"""
        serializer.save(sender=self.request.user)
    
    @action(detail=False, methods=['get'])
    def by_conversation(self, request):
        """Get all messages from a specific conversation"""
        conversation_id = request.query_params.get('conversation_id')
        if not conversation_id:
            return Response({'error': 'conversation_id is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if user has access to this conversation
        try:
            conversation = Conversation.objects.get(
                id=conversation_id,
                participants=request.user,
                is_active=True
            )
        except Conversation.DoesNotExist:
            return Response({'error': 'Conversation not found or access denied'}, status=status.HTTP_404_NOT_FOUND)
        
        messages = conversation.messages.all().order_by('order_index')
        serializer = self.get_serializer(messages, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def bulk_create(self, request):
        """Create multiple messages at once"""
        messages_data = request.data.get('messages', [])
        conversation_id = request.data.get('conversation_id')
        
        if not messages_data or not conversation_id:
            return Response({'error': 'messages and conversation_id are required'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if user has access to this conversation
        try:
            conversation = Conversation.objects.get(
                id=conversation_id,
                participants=request.user,
                is_active=True
            )
        except Conversation.DoesNotExist:
            return Response({'error': 'Conversation not found or access denied'}, status=status.HTTP_404_NOT_FOUND)
        
        created_messages = []
        
        with transaction.atomic():
            for i, msg_data in enumerate(messages_data):
                msg_data['conversation'] = conversation_id
                serializer = MessageCreateSerializer(data=msg_data)
                if serializer.is_valid():
                    message = serializer.save(sender=request.user)
                    created_messages.append(MessageSerializer(message).data)
                else:
                    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        return Response({
            'message': f'Successfully created {len(created_messages)} messages',
            'messages': created_messages
        }, status=status.HTTP_201_CREATED)
