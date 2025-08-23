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


class ChatDataDetailView(generics.RetrieveUpdateDestroyAPIView):
    """API view to retrieve, update, and delete a specific chat session by ID"""
    queryset = ChatData.objects.all()
    serializer_class = ChatDataSerializer
    permission_classes = [AllowAny]
    lookup_field = 'id'  # Use ID field for lookup since number is not unique


class ChatDataByNumberView(generics.ListAPIView):
    """API view to get all chat sessions with a specific number"""
    serializer_class = ChatDataSerializer
    permission_classes = [AllowAny]
    
    def get_queryset(self):
        """Get all chats with the specified number"""
        number = self.kwargs.get('number')
        return ChatData.objects.filter(number=number).order_by('-created_at')


class ChatDataListView(generics.ListAPIView):
    """API view to list all chat sessions"""
    queryset = ChatData.objects.all()
    serializer_class = ChatDataSerializer
    permission_classes = [AllowAny]
    
    def get_queryset(self):
        """Allow filtering by query parameters"""
        queryset = ChatData.objects.all()
        
        # Filter by number if provided
        number = self.request.query_params.get('number', None)
        if number:
            queryset = queryset.filter(number=number)
        
        # Filter by content if search parameter is provided
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(content__icontains=search)
        
        # Filter by date range if provided
        date_from = self.request.query_params.get('date_from', None)
        if date_from:
            queryset = queryset.filter(created_at__gte=date_from)
        
        date_to = self.request.query_params.get('date_to', None)
        if date_to:
            queryset = queryset.filter(created_at__lte=date_to)
        
        return queryset.order_by('-created_at')


class ChatDataUpdateView(generics.UpdateAPIView):
    """API view to update chat content by ID"""
    queryset = ChatData.objects.all()
    serializer_class = ChatDataSerializer
    permission_classes = [AllowAny]
    lookup_field = 'id'  # Use ID field for lookup since number is not unique
    
    def patch(self, request, *args, **kwargs):
        """Partial update for chat content"""
        chat_data = self.get_object()
        serializer = self.get_serializer(chat_data, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
    
    def put(self, request, *args, **kwargs):
        """Full update for chat data"""
        return self.patch(request, *args, **kwargs)
