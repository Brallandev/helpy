from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from datetime import timedelta, time

class AppointmentType(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    duration_minutes = models.PositiveIntegerField(default=30, help_text="Default duration in minutes")
    color = models.CharField(max_length=7, default="#007bff", help_text="Hex color for calendar display")
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.duration_minutes} min)"

class Appointment(models.Model):
    STATUS_CHOICES = [
        ('SCHEDULED', 'Scheduled'),
        ('CONFIRMED', 'Confirmed'),
        ('IN_PROGRESS', 'In Progress'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled'),
        ('NO_SHOW', 'No Show'),
        ('RESCHEDULED', 'Rescheduled'),
    ]
    
    PRIORITY_CHOICES = [
        ('ROUTINE', 'Routine'),
        ('URGENT', 'Urgent'),
        ('EMERGENCY', 'Emergency'),
        ('FOLLOW_UP', 'Follow-up'),
    ]
    
    # Core Information
    appointment_id = models.CharField(max_length=20, unique=True, help_text="Unique appointment identifier")
    appointment_type = models.ForeignKey(AppointmentType, on_delete=models.CASCADE, related_name='appointments')
    patient = models.ForeignKey('patient.Patient', on_delete=models.CASCADE, related_name='appointments')
    doctor = models.ForeignKey('doctor.Doctor', on_delete=models.CASCADE, related_name='appointments')
    room = models.ForeignKey('rooms.Room', on_delete=models.SET_NULL, null=True, blank=True, related_name='appointments')
    
    # Scheduling
    scheduled_date = models.DateField()
    scheduled_time = models.TimeField()
    duration_minutes = models.PositiveIntegerField(default=30, help_text="Duration in minutes")
    end_time = models.TimeField(blank=True, null=True)
    
    # Status and Priority
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='SCHEDULED')
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='ROUTINE')
    
    # Clinical Information
    reason = models.TextField(help_text="Reason for appointment")
    symptoms = models.TextField(blank=True)
    diagnosis = models.TextField(blank=True)
    treatment_plan = models.TextField(blank=True)
    prescription = models.TextField(blank=True)
    
    # Administrative
    notes = models.TextField(blank=True)
    internal_notes = models.TextField(blank=True, help_text="Notes visible only to staff")
    created_by = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True, related_name='created_appointments')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-scheduled_date', 'scheduled_time']
        verbose_name = "Appointment"
        verbose_name_plural = "Appointments"
    
    def __str__(self):
        return f"{self.appointment_id} - {self.patient.full_name} with Dr. {self.doctor.last_name} on {self.scheduled_date}"
    
    def save(self, *args, **kwargs):
        if not self.end_time:
            # Calculate end_time based on duration
            start_minutes = self.scheduled_time.hour * 60 + self.scheduled_time.minute
            end_minutes = start_minutes + self.duration_minutes
            self.end_time = time(end_minutes // 60, end_minutes % 60)
        super().save(*args, **kwargs)
    
    @property
    def is_overdue(self):
        """Check if appointment is overdue"""
        now = timezone.now()
        appointment_datetime = timezone.make_aware(
            timezone.datetime.combine(self.scheduled_date, self.scheduled_time)
        )
        return now > appointment_datetime and self.status not in ['COMPLETED', 'CANCELLED']
    
    @property
    def is_today(self):
        """Check if appointment is scheduled for today"""
        return self.scheduled_date == timezone.now().date()
    
    @property
    def is_conflicting(self):
        """Check if this appointment conflicts with doctor's schedule"""
        from schedule.models import DoctorSchedule, ScheduleException
        
        # Check regular schedule
        day_of_week = self.scheduled_date.weekday()
        try:
            schedule = DoctorSchedule.objects.get(
                doctor=self.doctor,
                day_of_week=day_of_week,
                time_slot__start_time__lte=self.scheduled_time,
                time_slot__end_time__gte=self.end_time
            )
            return not schedule.is_available
        except DoctorSchedule.DoesNotExist:
            return True
        
        # Check exceptions
        exceptions = ScheduleException.objects.filter(
            doctor=self.doctor,
            date=self.scheduled_date
        )
        for exception in exceptions:
            if exception.is_all_day and exception.max_patients == 0:
                return True
            if exception.start_time and exception.end_time:
                if (self.scheduled_time >= exception.start_time and 
                    self.scheduled_time < exception.end_time):
                    return True
        return False

class AppointmentFollowUp(models.Model):
    appointment = models.ForeignKey(Appointment, on_delete=models.CASCADE, related_name='follow_ups')
    follow_up_date = models.DateField()
    follow_up_time = models.TimeField()
    reason = models.TextField()
    notes = models.TextField(blank=True)
    is_scheduled = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-follow_up_date']
    
    def __str__(self):
        return f"Follow-up for {self.appointment.appointment_id} on {self.follow_up_date}"

class AppointmentReminder(models.Model):
    REMINDER_TYPES = [
        ('SMS', 'SMS'),
        ('EMAIL', 'Email'),
        ('PHONE', 'Phone Call'),
        ('PUSH', 'Push Notification'),
    ]
    
    appointment = models.ForeignKey(Appointment, on_delete=models.CASCADE, related_name='reminders')
    reminder_type = models.CharField(max_length=20, choices=REMINDER_TYPES)
    reminder_time = models.DateTimeField(help_text="When to send the reminder")
    message = models.TextField(blank=True)
    is_sent = models.BooleanField(default=False)
    sent_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['reminder_time']
    
    def __str__(self):
        return f"{self.reminder_type} reminder for {self.appointment.appointment_id} at {self.reminder_time}"
    
    @property
    def is_overdue(self):
        """Check if reminder is overdue"""
        return timezone.now() > self.reminder_time and not self.is_sent

class AppointmentWaitlist(models.Model):
    PRIORITY_CHOICES = [
        ('LOW', 'Low'),
        ('MEDIUM', 'Medium'),
        ('HIGH', 'High'),
        ('URGENT', 'Urgent'),
    ]
    
    patient = models.ForeignKey('patient.Patient', on_delete=models.CASCADE, related_name='waitlist_entries')
    doctor = models.ForeignKey('doctor.Doctor', on_delete=models.CASCADE, related_name='waitlist_entries')
    appointment_type = models.ForeignKey(AppointmentType, on_delete=models.CASCADE)
    preferred_date = models.DateField()
    preferred_time_start = models.TimeField()
    preferred_time_end = models.TimeField()
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='MEDIUM')
    reason = models.TextField()
    notes = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['priority', 'preferred_date', 'created_at']
    
    def __str__(self):
        return f"{self.patient.full_name} - {self.appointment_type.name} with Dr. {self.doctor.last_name}"

class AppointmentDesire(models.Model):
    patient = models.ForeignKey('patient.Patient', on_delete=models.CASCADE, related_name='appointment_desires')
    created_at = models.DateTimeField(auto_now_add=True)
    want_appointment = models.BooleanField(default=False)