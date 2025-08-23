from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

class RoomType(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return self.name

class Room(models.Model):
    STATUS_CHOICES = [
        ('AVAILABLE', 'Available'),
        ('OCCUPIED', 'Occupied'),
        ('MAINTENANCE', 'Under Maintenance'),
        ('CLEANING', 'Being Cleaned'),
        ('RESERVED', 'Reserved'),
        ('OUT_OF_SERVICE', 'Out of Service'),
    ]
    
    room_number = models.CharField(max_length=20, unique=True)
    room_type = models.ForeignKey(RoomType, on_delete=models.CASCADE, related_name='rooms')
    floor = models.PositiveIntegerField()
    wing = models.CharField(max_length=50, blank=True)
    capacity = models.PositiveIntegerField(default=1, help_text="Number of patients the room can accommodate")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='AVAILABLE')
    
    # Room Details
    is_accessible = models.BooleanField(default=False, help_text="Wheelchair accessible")
    has_private_bathroom = models.BooleanField(default=False)
    has_window = models.BooleanField(default=True)
    temperature_control = models.BooleanField(default=False)
    
    # Equipment and Features
    equipment = models.TextField(blank=True, help_text="List of medical equipment in the room")
    features = models.TextField(blank=True, help_text="Special features of the room")
    
    # Administrative
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['floor', 'room_number']
        verbose_name = "Room"
        verbose_name_plural = "Rooms"
    
    def __str__(self):
        return f"Room {self.room_number} - {self.room_type.name}"
    
    @property
    def is_available(self):
        return self.status == 'AVAILABLE'

class Equipment(models.Model):
    EQUIPMENT_TYPES = [
        ('MONITORING', 'Patient Monitoring'),
        ('DIAGNOSTIC', 'Diagnostic Equipment'),
        ('TREATMENT', 'Treatment Equipment'),
        ('EMERGENCY', 'Emergency Equipment'),
        ('FURNITURE', 'Furniture'),
        ('OTHER', 'Other'),
    ]
    
    STATUS_CHOICES = [
        ('OPERATIONAL', 'Operational'),
        ('MAINTENANCE', 'Under Maintenance'),
        ('OUT_OF_SERVICE', 'Out of Service'),
        ('RETIRED', 'Retired'),
    ]
    
    name = models.CharField(max_length=200)
    equipment_type = models.CharField(max_length=20, choices=EQUIPMENT_TYPES)
    model_number = models.CharField(max_length=100, blank=True)
    serial_number = models.CharField(max_length=100, blank=True, unique=True)
    manufacturer = models.CharField(max_length=200, blank=True)
    
    # Location
    room = models.ForeignKey(Room, on_delete=models.SET_NULL, null=True, blank=True, related_name='equipment_list')
    is_portable = models.BooleanField(default=False)
    
    # Status and Maintenance
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='OPERATIONAL')
    purchase_date = models.DateField(blank=True, null=True)
    warranty_expiry = models.DateField(blank=True, null=True)
    last_maintenance = models.DateField(blank=True, null=True)
    next_maintenance = models.DateField(blank=True, null=True)
    
    # Details
    description = models.TextField(blank=True)
    specifications = models.TextField(blank=True)
    notes = models.TextField(blank=True)
    
    class Meta:
        ordering = ['name']
        verbose_name = "Equipment"
        verbose_name_plural = "Equipment"
    
    def __str__(self):
        return f"{self.name} ({self.get_equipment_type_display()})"

class RoomMaintenance(models.Model):
    MAINTENANCE_TYPES = [
        ('CLEANING', 'Regular Cleaning'),
        ('REPAIR', 'Repair'),
        ('INSPECTION', 'Safety Inspection'),
        ('EQUIPMENT', 'Equipment Maintenance'),
        ('RENOVATION', 'Renovation'),
        ('OTHER', 'Other'),
    ]
    
    PRIORITY_CHOICES = [
        ('LOW', 'Low'),
        ('MEDIUM', 'Medium'),
        ('HIGH', 'High'),
        ('URGENT', 'Urgent'),
    ]
    
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='maintenance_records')
    maintenance_type = models.CharField(max_length=20, choices=MAINTENANCE_TYPES)
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='MEDIUM')
    
    # Schedule
    scheduled_date = models.DateField()
    scheduled_time = models.TimeField(blank=True, null=True)
    estimated_duration = models.DurationField(blank=True, null=True)
    
    # Execution
    start_time = models.DateTimeField(blank=True, null=True)
    end_time = models.DateTimeField(blank=True, null=True)
    is_completed = models.BooleanField(default=False)
    
    # Details
    description = models.TextField()
    assigned_to = models.CharField(max_length=100, blank=True)
    cost = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    notes = models.TextField(blank=True)
    
    # Tracking
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-scheduled_date', 'priority']
    
    def __str__(self):
        return f"{self.room.room_number} - {self.maintenance_type} ({self.scheduled_date})"
    
    @property
    def is_overdue(self):
        from datetime import date
        return not self.is_completed and self.scheduled_date < date.today()
