from django.contrib import admin
from django.utils.html import format_html
from .models import RoomType, Room, Equipment, RoomMaintenance

@admin.register(RoomType)
class RoomTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'description', 'is_active', 'room_count']
    list_filter = ['is_active']
    search_fields = ['name', 'description']
    
    def room_count(self, obj):
        return obj.rooms.count()
    room_count.short_description = 'Number of Rooms'

@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ['room_number', 'room_type', 'floor', 'wing', 'status', 'capacity', 'is_accessible', 'equipment_count']
    list_filter = ['room_type', 'floor', 'wing', 'status', 'is_accessible', 'has_private_bathroom', 'has_window']
    search_fields = ['room_number', 'wing', 'equipment', 'features']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Room Information', {
            'fields': ('room_number', 'room_type', 'floor', 'wing', 'capacity', 'status')
        }),
        ('Room Features', {
            'fields': ('is_accessible', 'has_private_bathroom', 'has_window', 'temperature_control')
        }),
        ('Equipment and Features', {
            'fields': ('equipment', 'features')
        }),
        ('Administrative', {
            'fields': ('notes',)
        }),
    )
    
    def equipment_count(self, obj):
        return obj.equipment_list.count()
    equipment_count.short_description = 'Equipment Count'
    
    def status(self, obj):
        colors = {
            'AVAILABLE': 'green',
            'OCCUPIED': 'red',
            'MAINTENANCE': 'orange',
            'CLEANING': 'yellow',
            'RESERVED': 'blue',
            'OUT_OF_SERVICE': 'gray'
        }
        color = colors.get(obj.status, 'black')
        return format_html('<span style="color: {};">{}</span>', color, obj.get_status_display())
    status.short_description = 'Status'

@admin.register(Equipment)
class EquipmentAdmin(admin.ModelAdmin):
    list_display = ['name', 'equipment_type', 'room', 'status', 'manufacturer', 'last_maintenance', 'next_maintenance']
    list_filter = ['equipment_type', 'status', 'manufacturer', 'is_portable']
    search_fields = ['name', 'model_number', 'serial_number', 'manufacturer']
    
    fieldsets = (
        ('Equipment Information', {
            'fields': ('name', 'equipment_type', 'model_number', 'serial_number', 'manufacturer')
        }),
        ('Location and Status', {
            'fields': ('room', 'is_portable', 'status')
        }),
        ('Maintenance', {
            'fields': ('purchase_date', 'warranty_expiry', 'last_maintenance', 'next_maintenance')
        }),
        ('Details', {
            'fields': ('description', 'specifications', 'notes')
        }),
    )
    
    def status(self, obj):
        colors = {
            'OPERATIONAL': 'green',
            'MAINTENANCE': 'orange',
            'OUT_OF_SERVICE': 'red',
            'RETIRED': 'gray'
        }
        color = colors.get(obj.status, 'black')
        return format_html('<span style="color: {};">{}</span>', color, obj.get_status_display())
    status.short_description = 'Status'

@admin.register(RoomMaintenance)
class RoomMaintenanceAdmin(admin.ModelAdmin):
    list_display = ['room', 'maintenance_type', 'priority', 'scheduled_date', 'is_completed', 'assigned_to', 'cost']
    list_filter = ['maintenance_type', 'priority', 'is_completed', 'scheduled_date']
    search_fields = ['room__room_number', 'assigned_to', 'description']
    readonly_fields = ['created_at', 'updated_at', 'is_overdue']
    date_hierarchy = 'scheduled_date'
    
    fieldsets = (
        ('Maintenance Information', {
            'fields': ('room', 'maintenance_type', 'priority', 'description')
        }),
        ('Schedule', {
            'fields': ('scheduled_date', 'scheduled_time', 'estimated_duration')
        }),
        ('Execution', {
            'fields': ('start_time', 'end_time', 'is_completed', 'assigned_to', 'cost')
        }),
        ('Additional Details', {
            'fields': ('notes',)
        }),
    )
    
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
        return super().get_queryset(request).select_related('room')
