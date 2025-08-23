from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class ChatData(models.Model):
    """Model to store chat data with question-answer pairs"""
    number = models.CharField(max_length=30, unique=False, help_text="Unique identifier for the chat session")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    content = models.TextField(blank=True, help_text="The content of the chat session")
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Chat Data"
        verbose_name_plural = "Chat Data"
    
    def __str__(self):
        return f"Chat Session {self.number} - {self.created_at.strftime('%Y-%m-%d %H:%M')}"

