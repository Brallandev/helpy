from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Conversation(models.Model):
    """Model to store conversation sessions"""
    title = models.CharField(max_length=255, blank=True)
    participants = models.ManyToManyField(User, related_name='conversations')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['-updated_at']
    
    def __str__(self):
        return f"Conversation {self.id}: {self.title or 'Untitled'}"


class Message(models.Model):
    """Model to store individual messages within conversations"""
    ROLE_CHOICES = [
        ('user', 'User'),
        ('assistant', 'Assistant'),
        ('system', 'System'),
    ]
    
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages', null=True, blank=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='user')
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    order_index = models.PositiveIntegerField()
    
    class Meta:
        ordering = ['order_index', 'timestamp']
        unique_together = ['conversation', 'order_index']
    
    def __str__(self):
        return f"Message {self.order_index} in {self.conversation}: {self.content[:50]}..."
    
    def save(self, *args, **kwargs):
        if not self.order_index:
            # Auto-assign order index if not provided
            last_message = Message.objects.filter(conversation=self.conversation).order_by('-order_index').first()
            self.order_index = (last_message.order_index + 1) if last_message else 1
        super().save(*args, **kwargs)
