from django.urls import path
from .views import (
    ChatDataCreateView,
    ChatDataDetailView,
    ChatDataListView,
    ChatDataUpdateView,
    ChatDataByNumberView
)

app_name = 'conversation'

urlpatterns = [
    # Create a new chat session
    path('chat/create/', ChatDataCreateView.as_view(), name='chat-create'),
    
    # List all chat sessions (with optional filtering)
    path('chat/list/', ChatDataListView.as_view(), name='chat-list'),
    
    # Get all chat sessions with a specific number
    path('chat/number/<str:number>/', ChatDataByNumberView.as_view(), name='chat-by-number'),
    
    # Get, update, or delete a specific chat session by ID
    path('chat/<int:id>/', ChatDataDetailView.as_view(), name='chat-detail'),
    
    # Update chat content by ID (alternative endpoint)
    path('chat/<int:id>/update/', ChatDataUpdateView.as_view(), name='chat-update'),
]
