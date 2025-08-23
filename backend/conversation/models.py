from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class ChatData(models.Model):
    """Model to store chat data with question-answer pairs"""
    session_id = models.CharField(max_length=100, unique=True, help_text="Unique identifier for the chat session")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_processed = models.BooleanField(default=False, help_text="Whether the chat data has been processed")
    notes = models.TextField(blank=True, help_text="Additional notes about the chat session")
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Chat Data"
        verbose_name_plural = "Chat Data"
    
    def __str__(self):
        return f"Chat Session {self.session_id} - {self.created_at.strftime('%Y-%m-%d %H:%M')}"


class ChatMessage(models.Model):
    """Model to store individual question-answer pairs from chat data"""
    chat_data = models.ForeignKey(ChatData, on_delete=models.CASCADE, related_name='messages')
    question = models.TextField(help_text="The question asked")
    answer = models.TextField(help_text="The answer provided")
    order_index = models.PositiveIntegerField(help_text="Order of the message in the conversation")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['order_index', 'created_at']
        unique_together = ['chat_data', 'order_index']
        verbose_name = "Chat Message"
        verbose_name_plural = "Chat Messages"
    
    def __str__(self):
        return f"Q&A {self.order_index}: {self.question[:50]}..."
