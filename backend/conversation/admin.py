from django.contrib import admin
from django.utils.html import format_html
from .models import ChatData


@admin.register(ChatData)
class ChatDataAdmin(admin.ModelAdmin):
    list_display = ['id', 'number', 'content_preview', 'created_at', 'updated_at', 'chat_count']
    list_display_links = ['id', 'number']
    list_filter = ['created_at', 'updated_at', 'number']
    search_fields = ['number', 'content', 'id']
    readonly_fields = ['id', 'created_at', 'updated_at']
    ordering = ['-created_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('id', 'number', 'content')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def content_preview(self, obj):
        """Display a preview of the chat content"""
        if obj.content:
            preview = obj.content[:100]
            if len(obj.content) > 100:
                preview += '...'
            return format_html('<span title="{}">{}</span>', obj.content, preview)
        return '-'
    content_preview.short_description = 'Content Preview'
    
    def chat_count(self, obj):
        """Show how many chats exist with the same number"""
        count = ChatData.objects.filter(number=obj.number).count()
        if count > 1:
            return format_html('<span style="color: orange; font-weight: bold;">{}</span>', count)
        return count
    chat_count.short_description = 'Chats with Same Number'
    
    def get_queryset(self, request):
        """Optimize queryset for admin display"""
        return super().get_queryset(request).select_related()
    
    def has_add_permission(self, request):
        """Allow adding new chat sessions"""
        return True
    
    def has_delete_permission(self, request, obj=None):
        """Allow deleting chat sessions"""
        return True
    
    def has_change_permission(self, request, obj=None):
        """Allow editing chat sessions"""
        return True
