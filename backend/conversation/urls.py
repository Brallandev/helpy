from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ChatDataViewSet, ChatMessageViewSet

router = DefaultRouter()
router.register(r'chat-data', ChatDataViewSet, basename='chatdata')
router.register(r'chat-messages', ChatMessageViewSet, basename='chatmessage')

urlpatterns = [
    path('', include(router.urls)),
]
