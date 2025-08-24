from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.shortcuts import get_object_or_404
from .models import ChatData
from .serializers import ChatDataSerializer, ChatDataCreateSerializer


class ChatDataCreateView(generics.CreateAPIView):
    """API view to create a new chat session"""
    queryset = ChatData.objects.all()
    serializer_class = ChatDataCreateSerializer
    permission_classes = [AllowAny]  # Allow anyone to create chat sessions
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        chat_data = serializer.save()
        
        # Return the created data with full serializer
        response_serializer = ChatDataSerializer(chat_data)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)


class ChatDataByNumberView(generics.ListAPIView):
    """API view to get all chat sessions with a specific number"""
    serializer_class = ChatDataSerializer
    permission_classes = [AllowAny]
    
    def get_queryset(self):
        """Get all chats with the specified number"""
        number = self.kwargs.get('number')
        return ChatData.objects.filter(number=number).order_by('-created_at')

