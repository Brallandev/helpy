from django.urls import path
from .views import (
    ChatDataCreateView,
    ChatDataByNumberView
)

app_name = 'conversation'

urlpatterns = [
    # Create a new chat session
    path('chat/create/', ChatDataCreateView.as_view(), name='chat-create'),
    
    # Get all chat sessions with a specific number
    path('chat/number/<str:number>/', ChatDataByNumberView.as_view(), name='chat-by-number'),
    
]
