from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class ChatData(models.Model):
    """Model to store chat data with question-answer pairs"""
    number = models.CharField(max_length=30, unique=False, help_text="Unique identifier for the chat session")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    initial_questions = models.TextField(blank=True, help_text="The content of the chat session")
    llm_questions = models.TextField(blank=True, help_text="The content of the chat session")
    
    # Diagnostic fields
    pre_diagnosis = models.TextField(blank=True, null=True, help_text="Pre-diagnostic analysis of the user's condition")
    comments = models.TextField(blank=True, null=True, help_text="Comments from sub-agent analysis")
    score = models.CharField(max_length=50, blank=True, null=True, help_text="Priority score (e.g., 'Alta prioridad', 'Media prioridad')")
    filled_doc = models.TextField(blank=True, null=True, help_text="Complete diagnostic document with detailed analysis")
    


 

    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Chat Data"
        verbose_name_plural = "Chat Data"
    
    def __str__(self):
        return f"Chat Session {self.number} - {self.created_at.strftime('%Y-%m-%d %H:%M')}"

