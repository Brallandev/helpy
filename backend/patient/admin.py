from django.contrib import admin
from django.utils.html import format_html
from .models import Patient, MedicalHistory, PatientDocument

@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ['phone_number', 'full_name', 'age', 'gender', 'is_active', 'registration_date']
    list_filter = ['gender', 'blood_type', 'is_active', 'registration_date']
    search_fields = ['first_name', 'last_name', 'phone_number', 'email']
    readonly_fields = ['registration_date', 'age']
    fieldsets = (
        ('Basic Information', {
            'fields': ('first_name', 'last_name', 'date_of_birth', 'gender')
        }),
        ('Contact Information', {
            'fields': ('phone_number', 'email', 'address', 'emergency_contact_name', 'emergency_contact_phone')
        }),
        ('Medical Information', {
            'fields': ('blood_type', 'height', 'weight', 'allergies', 'medical_conditions', 'medications')
        }),
        ('Administrative', {
            'fields': ('insurance_provider', 'insurance_number', 'is_active')
        }),
    )
    


@admin.register(MedicalHistory)
class MedicalHistoryAdmin(admin.ModelAdmin):
    list_display = ['patient', 'details', 'approved', 'created_at', 'updated_at']
    list_filter = ['approved', 'created_at', 'updated_at']
    search_fields = ['patient__first_name', 'patient__last_name', 'details']
    date_hierarchy = 'created_at'
    fieldsets = (
        ('Patient Information', {
            'fields': ('patient',)
        }),
        ('Medical Details', {
            'fields': ('details', 'approved')
        }),
    )

@admin.register(PatientDocument)
class PatientDocumentAdmin(admin.ModelAdmin):
    list_display = ['patient', 'document_type', 'title', 'uploaded_at']
    list_filter = ['document_type', 'uploaded_at']
    search_fields = ['patient__first_name', 'patient__last_name', 'title']
    date_hierarchy = 'uploaded_at'
    fieldsets = (
        ('Document Information', {
            'fields': ('patient', 'document_type', 'title', 'file')
        }),
        ('Additional Details', {
            'fields': ('notes',)
        }),
    )
