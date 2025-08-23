from django.contrib import admin
from .models import Conversation, Message


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'created_at', 'updated_at', 'is_active', 'get_participant_count']
    list_filter = ['is_active', 'created_at', 'updated_at']
    search_fields = ['title']
    readonly_fields = ['created_at', 'updated_at']
    filter_horizontal = ['participants']
    
    def get_participant_count(self, obj):
        return obj.participants.count()
    get_participant_count.short_description = 'Participants'
    
    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('participants')


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ['id', 'conversation', 'role', 'sender', 'order_index', 'timestamp', 'content_preview']
    list_filter = ['role', 'timestamp', 'conversation']
    search_fields = ['content', 'conversation__title', 'sender__username']
    readonly_fields = ['timestamp', 'order_index']
    ordering = ['conversation', 'order_index']
    
    def content_preview(self, obj):
        return obj.content[:100] + '...' if len(obj.content) > 100 else obj.content
    content_preview.short_description = 'Content Preview'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('conversation', 'sender')
