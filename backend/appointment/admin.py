from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone
from .models import AppointmentType, Appointment, AppointmentFollowUp, AppointmentReminder, AppointmentWaitlist

@admin.register(AppointmentType)
class AppointmentTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'description', 'duration_minutes', 'color_display', 'is_active', 'appointment_count']
    list_filter = ['is_active', 'duration_minutes']
    search_fields = ['name', 'description']
    ordering = ['name']
    
    fieldsets = (
        ('Type Information', {
            'fields': ('name', 'description', 'duration_minutes', 'color')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
    )
    
    def color_display(self, obj):
        return format_html('<div style="background-color: {}; width: 20px; height: 20px; border: 1px solid #ccc;"></div>', obj.color)
    color_display.short_description = 'Color'
    
    def appointment_count(self, obj):
        return obj.appointments.count()
    appointment_count.short_description = 'Appointments'

@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ['appointment_id', 'patient', 'doctor', 'appointment_type', 'scheduled_date', 'scheduled_time', 'status', 'priority', 'room', 'conflict_status']
    list_filter = ['status', 'priority', 'appointment_type', 'scheduled_date', 'doctor', 'room']
    search_fields = ['appointment_id', 'patient__first_name', 'patient__last_name', 'doctor__first_name', 'doctor__last_name', 'reason']
    readonly_fields = ['created_at', 'updated_at', 'is_overdue', 'is_today', 'is_conflicting']
    date_hierarchy = 'scheduled_date'
    ordering = ['-scheduled_date', 'scheduled_time']
    
    fieldsets = (
        ('Appointment Information', {
            'fields': ('appointment_id', 'appointment_type', 'patient', 'doctor', 'room')
        }),
        ('Scheduling', {
            'fields': ('scheduled_date', 'scheduled_time', 'duration_minutes', 'end_time')
        }),
        ('Status and Priority', {
            'fields': ('status', 'priority')
        }),
        ('Clinical Information', {
            'fields': ('reason', 'symptoms', 'diagnosis', 'treatment_plan', 'prescription')
        }),
        ('Notes', {
            'fields': ('notes', 'internal_notes')
        }),
        ('System Information', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def status(self, obj):
        colors = {
            'SCHEDULED': 'blue',
            'CONFIRMED': 'green',
            'IN_PROGRESS': 'orange',
            'COMPLETED': 'darkgreen',
            'CANCELLED': 'red',
            'NO_SHOW': 'darkred',
            'RESCHEDULED': 'purple'
        }
        color = colors.get(obj.status, 'black')
        return format_html('<span style="color: {};">{}</span>', color, obj.get_status_display())
    status.short_description = 'Status'
    
    def priority(self, obj):
        colors = {
            'ROUTINE': 'green',
            'URGENT': 'orange',
            'EMERGENCY': 'red',
            'FOLLOW_UP': 'blue'
        }
        color = colors.get(obj.priority, 'black')
        return format_html('<span style="color: {};">{}</span>', color, obj.get_priority_display())
    priority.short_description = 'Priority'
    
    def conflict_status(self, obj):
        if obj.is_conflicting:
            return format_html('<span style="color: red;">Conflict</span>')
        return format_html('<span style="color: green;">OK</span>')
    conflict_status.short_description = 'Conflict Status'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('patient', 'doctor', 'room', 'appointment_type', 'created_by')

@admin.register(AppointmentFollowUp)
class AppointmentFollowUpAdmin(admin.ModelAdmin):
    list_display = ['appointment', 'follow_up_date', 'follow_up_time', 'reason', 'is_scheduled', 'created_at']
    list_filter = ['follow_up_date', 'is_scheduled', 'created_at']
    search_fields = ['appointment__appointment_id', 'appointment__patient__first_name', 'reason']
    date_hierarchy = 'follow_up_date'
    ordering = ['-follow_up_date']
    
    fieldsets = (
        ('Follow-up Information', {
            'fields': ('appointment', 'follow_up_date', 'follow_up_time', 'reason')
        }),
        ('Status', {
            'fields': ('is_scheduled', 'notes')
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('appointment__patient', 'appointment__doctor')

@admin.register(AppointmentReminder)
class AppointmentReminderAdmin(admin.ModelAdmin):
    list_display = ['appointment', 'reminder_type', 'reminder_time', 'is_sent', 'sent_at', 'overdue_status']
    list_filter = ['reminder_type', 'is_sent', 'reminder_time']
    search_fields = ['appointment__appointment_id', 'appointment__patient__first_name', 'message']
    date_hierarchy = 'reminder_time'
    ordering = ['reminder_time']
    
    fieldsets = (
        ('Reminder Information', {
            'fields': ('appointment', 'reminder_type', 'reminder_time', 'message')
        }),
        ('Status', {
            'fields': ('is_sent', 'sent_at')
        }),
    )
    
    def overdue_status(self, obj):
        if obj.is_overdue:
            return format_html('<span style="color: red;">Overdue</span>')
        return format_html('<span style="color: green;">On Time</span>')
    overdue_status.short_description = 'Status'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('appointment__patient', 'appointment__doctor')

@admin.register(AppointmentWaitlist)
class AppointmentWaitlistAdmin(admin.ModelAdmin):
    list_display = ['patient', 'doctor', 'appointment_type', 'preferred_date', 'preferred_time_range', 'priority', 'is_active', 'created_at']
    list_filter = ['priority', 'is_active', 'preferred_date', 'created_at']
    search_fields = ['patient__first_name', 'patient__last_name', 'doctor__first_name', 'doctor__last_name', 'reason']
    date_hierarchy = 'preferred_date'
    ordering = ['priority', 'preferred_date', 'created_at']
    
    fieldsets = (
        ('Waitlist Information', {
            'fields': ('patient', 'doctor', 'appointment_type')
        }),
        ('Preferred Schedule', {
            'fields': ('preferred_date', 'preferred_time_start', 'preferred_time_end')
        }),
        ('Details', {
            'fields': ('priority', 'reason', 'notes', 'is_active')
        }),
    )
    
    def preferred_time_range(self, obj):
        return f"{obj.preferred_time_start} - {obj.preferred_time_end}"
    preferred_time_range.short_description = 'Preferred Time'
    
    def priority(self, obj):
        colors = {
            'LOW': 'green',
            'MEDIUM': 'yellow',
            'HIGH': 'orange',
            'URGENT': 'red'
        }
        color = colors.get(obj.priority, 'black')
        return format_html('<span style="color: {};">{}</span>', color, obj.get_priority_display())
    priority.short_description = 'Priority'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('patient', 'doctor', 'appointment_type')
