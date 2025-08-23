from django.contrib import admin
from django.utils.html import format_html
from .models import TimeSlot, DoctorSchedule, ScheduleTemplate, ScheduleTemplateItem, ScheduleException, WorkingHours

@admin.register(TimeSlot)
class TimeSlotAdmin(admin.ModelAdmin):
    list_display = ['start_time', 'end_time', 'duration_minutes', 'is_active']
    list_filter = ['is_active', 'duration_minutes']
    search_fields = ['start_time', 'end_time']
    ordering = ['start_time']
    
    fieldsets = (
        ('Time Information', {
            'fields': ('start_time', 'end_time', 'duration_minutes')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
    )

@admin.register(DoctorSchedule)
class DoctorScheduleAdmin(admin.ModelAdmin):
    list_display = ['doctor', 'day_of_week', 'time_slot', 'is_available', 'max_patients', 'conflict_status']
    list_filter = ['day_of_week', 'is_available', 'doctor', 'time_slot']
    search_fields = ['doctor__first_name', 'doctor__last_name']
    ordering = ['doctor', 'day_of_week', 'time_slot__start_time']
    
    fieldsets = (
        ('Schedule Information', {
            'fields': ('doctor', 'day_of_week', 'time_slot', 'is_available', 'max_patients')
        }),
        ('Additional Details', {
            'fields': ('notes',)
        }),
    )
    
    def conflict_status(self, obj):
        if obj.is_conflicting:
            return format_html('<span style="color: red;">Conflict</span>')
        return format_html('<span style="color: green;">OK</span>')
    conflict_status.short_description = 'Conflict Status'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('doctor', 'time_slot')

@admin.register(ScheduleTemplate)
class ScheduleTemplateAdmin(admin.ModelAdmin):
    list_display = ['name', 'doctor', 'is_active', 'item_count', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'doctor__first_name', 'doctor__last_name']
    ordering = ['name']
    
    fieldsets = (
        ('Template Information', {
            'fields': ('name', 'description', 'doctor', 'is_active')
        }),
    )
    
    def item_count(self, obj):
        return obj.items.count()
    item_count.short_description = 'Schedule Items'

@admin.register(ScheduleTemplateItem)
class ScheduleTemplateItemAdmin(admin.ModelAdmin):
    list_display = ['template', 'day_of_week', 'time_slot', 'max_patients']
    list_filter = ['day_of_week', 'template']
    search_fields = ['template__name', 'template__doctor__first_name']
    ordering = ['template', 'day_of_week', 'time_slot__start_time']
    
    fieldsets = (
        ('Schedule Item', {
            'fields': ('template', 'day_of_week', 'time_slot', 'max_patients')
        }),
        ('Additional Details', {
            'fields': ('notes',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('template', 'time_slot')

@admin.register(ScheduleException)
class ScheduleExceptionAdmin(admin.ModelAdmin):
    list_display = ['doctor', 'exception_type', 'date', 'time_range', 'max_patients', 'affects_schedule']
    list_filter = ['exception_type', 'date', 'is_all_day', 'doctor']
    search_fields = ['doctor__first_name', 'doctor__last_name', 'reason']
    date_hierarchy = 'date'
    ordering = ['-date', 'start_time']
    
    fieldsets = (
        ('Exception Information', {
            'fields': ('doctor', 'exception_type', 'date', 'is_all_day')
        }),
        ('Time Details', {
            'fields': ('start_time', 'end_time')
        }),
        ('Capacity and Reason', {
            'fields': ('max_patients', 'reason')
        }),
        ('Additional Details', {
            'fields': ('notes',)
        }),
    )
    
    def time_range(self, obj):
        if obj.is_all_day:
            return "All Day"
        if obj.start_time and obj.end_time:
            return f"{obj.start_time} - {obj.end_time}"
        return "No time specified"
    time_range.short_description = 'Time Range'
    
    def affects_schedule(self, obj):
        if obj.affects_schedule:
            return format_html('<span style="color: orange;">Active</span>')
        return format_html('<span style="color: gray;">Past</span>')
    affects_schedule.short_description = 'Schedule Impact'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('doctor')

@admin.register(WorkingHours)
class WorkingHoursAdmin(admin.ModelAdmin):
    list_display = ['day_of_week', 'is_working_day', 'start_time', 'end_time', 'lunch_break', 'total_hours']
    list_filter = ['is_working_day']
    ordering = ['day_of_week']
    
    fieldsets = (
        ('Day Information', {
            'fields': ('day_of_week', 'is_working_day')
        }),
        ('Working Hours', {
            'fields': ('start_time', 'end_time')
        }),
        ('Lunch Break', {
            'fields': ('lunch_start', 'lunch_end')
        }),
    )
    
    def lunch_break(self, obj):
        if obj.lunch_start and obj.lunch_end:
            return f"{obj.lunch_start} - {obj.lunch_end}"
        return "No lunch break"
    lunch_break.short_description = 'Lunch Break'
    
    def total_hours(self, obj):
        hours = obj.working_hours
        total_minutes = int(hours.total_seconds() / 60)
        hours_part = total_minutes // 60
        minutes_part = total_minutes % 60
        return f"{hours_part}h {minutes_part}m"
    total_hours.short_description = 'Total Hours'
