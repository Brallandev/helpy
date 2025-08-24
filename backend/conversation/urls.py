from django.urls import path
from .views import (
    ChatDataUpsertView,
    ChatDataByNumberView
)

app_name = 'conversation'

urlpatterns = [
    # Unified endpoint to create or update chat data
    path('chat/data/', ChatDataUpsertView.as_view(), name='chat-upsert'),
    
    # Get all chat sessions with a specific number
    path('chat/number/<str:number>/', ChatDataByNumberView.as_view(), name='chat-by-number'),
    
]
