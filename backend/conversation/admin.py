from django.contrib import admin
from .models import ChatData, ChatMessage


class ChatMessageInline(admin.TabularInline):
    model = ChatMessage
    extra = 0
    readonly_fields = ['created_at']


@admin.register(ChatData)
class ChatDataAdmin(admin.ModelAdmin):
    list_display = ['session_id', 'created_at', 'updated_at', 'is_processed', 'message_count']
    list_filter = ['is_processed', 'created_at', 'updated_at']
    search_fields = ['session_id', 'notes']
    readonly_fields = ['created_at', 'updated_at']
    inlines = [ChatMessageInline]
    
    def message_count(self, obj):
        return obj.messages.count()
    message_count.short_description = 'Messages'


@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ['id', 'chat_data', 'order_index', 'question_preview', 'answer_preview', 'created_at']
    list_filter = ['created_at', 'chat_data']
    search_fields = ['question', 'answer', 'chat_data__session_id']
    readonly_fields = ['created_at']
    
    def question_preview(self, obj):
        return obj.question[:50] + '...' if len(obj.question) > 50 else obj.question
    question_preview.short_description = 'Question'
    
    def answer_preview(self, obj):
        return obj.answer[:50] + '...' if len(obj.answer) > 50 else obj.answer
    answer_preview.short_description = 'Answer'
