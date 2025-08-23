from django.contrib import admin
from django.utils.html import format_html
from .models import Specialty, Doctor, DoctorAvailability, DoctorLeave

@admin.register(Specialty)
class SpecialtyAdmin(admin.ModelAdmin):
    list_display = ['name', 'description', 'is_active', 'doctor_count']
    list_filter = ['is_active']
    search_fields = ['name', 'description']
    
    def doctor_count(self, obj):
        return obj.doctors.count()
    doctor_count.short_description = 'Number of Doctors'

@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = ['doctor_id', 'full_name', 'specialties_display', 'status', 'department', 'hire_date', 'is_available']
    list_filter = ['status', 'department', 'hire_date', 'is_available', 'specialties']
    search_fields = ['doctor_id', 'first_name', 'last_name', 'license_number', 'email']
    readonly_fields = ['hire_date', 'age']
    filter_horizontal = ['specialties']
    fieldsets = (
        ('Basic Information', {
            'fields': ('user', 'doctor_id', 'first_name', 'last_name', 'date_of_birth', 'gender')
        }),
        ('Professional Information', {
            'fields': ('specialties', 'license_number', 'medical_school', 'graduation_year', 'board_certifications', 'years_of_experience')
        }),
        ('Contact Information', {
            'fields': ('phone_number', 'email', 'office_address')
        }),
        ('Administrative', {
            'fields': ('status', 'department', 'is_available')
        }),
    )
    
    def specialties_display(self, obj):
        return ", ".join([spec.name for spec in obj.specialties.all()])
    specialties_display.short_description = 'Specialties'
    
    def status(self, obj):
        colors = {
            'ACTIVE': 'green',
            'INACTIVE': 'red',
            'ON_LEAVE': 'orange',
            'RETIRED': 'gray'
        }
        color = colors.get(obj.status, 'black')
        return format_html('<span style="color: {};">{}</span>', color, obj.get_status_display())
    status.short_description = 'Status'

@admin.register(DoctorAvailability)
class DoctorAvailabilityAdmin(admin.ModelAdmin):
    list_display = ['doctor', 'day_of_week', 'start_time', 'end_time', 'is_available']
    list_filter = ['day_of_week', 'is_available', 'doctor']
    search_fields = ['doctor__first_name', 'doctor__last_name']
    ordering = ['doctor', 'day_of_week', 'start_time']
    
    fieldsets = (
        ('Schedule Information', {
            'fields': ('doctor', 'day_of_week', 'start_time', 'end_time', 'is_available')
        }),
        ('Additional Details', {
            'fields': ('notes',)
        }),
    )

@admin.register(DoctorLeave)
class DoctorLeaveAdmin(admin.ModelAdmin):
    list_display = ['doctor', 'leave_type', 'start_date', 'end_date', 'is_approved', 'approved_by']
    list_filter = ['leave_type', 'is_approved', 'start_date', 'end_date']
    search_fields = ['doctor__first_name', 'doctor__last_name', 'reason']
    date_hierarchy = 'start_date'
    
    fieldsets = (
        ('Leave Information', {
            'fields': ('doctor', 'leave_type', 'start_date', 'end_date', 'reason')
        }),
        ('Approval', {
            'fields': ('is_approved', 'approved_by')
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('doctor', 'approved_by')
