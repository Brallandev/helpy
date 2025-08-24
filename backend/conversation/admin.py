from django.contrib import admin
from django.utils.html import format_html
from .models import ChatData


@admin.register(ChatData)
class ChatDataAdmin(admin.ModelAdmin):
    list_display = ['id', 'number', 'initial_questions_preview', 'score_display', 'created_at', 'updated_at', 'chat_count']
    list_display_links = ['id', 'number']
    list_filter = ['created_at', 'updated_at', 'number', 'score']
    search_fields = ['number', 'initial_questions', 'llm_questions', 'pre_diagnosis', 'comments', 'id']
    readonly_fields = ['id', 'created_at', 'updated_at']
    ordering = ['-created_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('id', 'number')
        }),
        ('Chat Content', {
            'fields': ('initial_questions', 'llm_questions'),
            'classes': ('wide',)
        }),
        ('Diagnostic Information', {
            'fields': ('pre_diagnosis', 'comments', 'score', 'filled_doc'),
            'classes': ('wide',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def initial_questions_preview(self, obj):
        """Display a preview of the initial questions"""
        if obj.initial_questions:
            preview = obj.initial_questions[:100]
            if len(obj.initial_questions) > 100:
                preview += '...'
            return format_html('<span title="{}">{}</span>', obj.initial_questions, preview)
        return '-'
    initial_questions_preview.short_description = 'Initial Questions Preview'
    
    def chat_count(self, obj):
        """Show how many chats exist with the same number"""
        count = ChatData.objects.filter(number=obj.number).count()
        if count > 1:
            return format_html('<span style="color: orange; font-weight: bold;">{}</span>', count)
        return count
    chat_count.short_description = 'Chats with Same Number'
    
    def score_display(self, obj):
        """Display priority score with color coding"""
        if not obj.score:
            return '-'
        
        color = 'black'
        if 'alta' in obj.score.lower():
            color = 'red'
        elif 'media' in obj.score.lower():
            color = 'orange'
        elif 'baja' in obj.score.lower():
            color = 'green'
            
        return format_html('<span style="color: {}; font-weight: bold;">{}</span>', color, obj.score)
    score_display.short_description = 'Priority Score'
    
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
