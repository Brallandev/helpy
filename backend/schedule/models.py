from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from datetime import time, timedelta

class TimeSlot(models.Model):
    start_time = models.TimeField()
    end_time = models.TimeField()
    duration_minutes = models.PositiveIntegerField(default=30, help_text="Duration in minutes")
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['start_time']
        unique_together = ['start_time', 'end_time']
    
    def __str__(self):
        return f"{self.start_time} - {self.end_time} ({self.duration_minutes} min)"
    
    def save(self, *args, **kwargs):
        if not self.end_time:
            # Calculate end_time based on duration if not provided
            start_minutes = self.start_time.hour * 60 + self.start_time.minute
            end_minutes = start_minutes + self.duration_minutes
            self.end_time = time(end_minutes // 60, end_minutes % 60)
        super().save(*args, **kwargs)

class DoctorSchedule(models.Model):
    DAYS_OF_WEEK = [
        (0, 'Monday'),
        (1, 'Tuesday'),
        (2, 'Wednesday'),
        (3, 'Thursday'),
        (4, 'Friday'),
        (5, 'Saturday'),
        (6, 'Sunday'),
    ]
    
    doctor = models.ForeignKey('doctor.Doctor', on_delete=models.CASCADE, related_name='schedules')
    day_of_week = models.IntegerField(choices=DAYS_OF_WEEK)
    time_slot = models.ForeignKey(TimeSlot, on_delete=models.CASCADE)
    is_available = models.BooleanField(default=True)
    max_patients = models.PositiveIntegerField(default=1, help_text="Maximum number of patients per slot")
    notes = models.TextField(blank=True)
    
    class Meta:
        ordering = ['day_of_week', 'time_slot__start_time']
        unique_together = ['doctor', 'day_of_week', 'time_slot']
    
    def __str__(self):
        return f"{self.doctor.full_name} - {self.get_day_of_week_display()} {self.time_slot}"
    
    @property
    def is_conflicting(self):
        """Check if this schedule conflicts with doctor's availability"""
        from doctor.models import DoctorAvailability
        
        try:
            availability = DoctorAvailability.objects.get(
                doctor=self.doctor,
                day_of_week=self.day_of_week
            )
            
            # Check if time slot overlaps with availability
            return not (
                availability.start_time <= self.time_slot.start_time and
                availability.end_time >= self.time_slot.end_time
            )
        except DoctorAvailability.DoesNotExist:
            return True

class ScheduleTemplate(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    doctor = models.ForeignKey('doctor.Doctor', on_delete=models.CASCADE, related_name='schedule_templates')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} - {self.doctor.full_name}"

class ScheduleTemplateItem(models.Model):
    template = models.ForeignKey(ScheduleTemplate, on_delete=models.CASCADE, related_name='items')
    day_of_week = models.IntegerField(choices=DoctorSchedule.DAYS_OF_WEEK)
    time_slot = models.ForeignKey(TimeSlot, on_delete=models.CASCADE)
    max_patients = models.PositiveIntegerField(default=1)
    notes = models.TextField(blank=True)
    
    class Meta:
        ordering = ['day_of_week', 'time_slot__start_time']
        unique_together = ['template', 'day_of_week', 'time_slot']
    
    def __str__(self):
        return f"{self.template.name} - {self.get_day_of_week_display()} {self.time_slot}"

class ScheduleException(models.Model):
    EXCEPTION_TYPES = [
        ('UNAVAILABLE', 'Unavailable'),
        ('REDUCED_CAPACITY', 'Reduced Capacity'),
        ('EXTENDED_HOURS', 'Extended Hours'),
        ('SPECIAL_SESSION', 'Special Session'),
        ('OTHER', 'Other'),
    ]
    
    doctor = models.ForeignKey('doctor.Doctor', on_delete=models.CASCADE, related_name='schedule_exceptions')
    exception_type = models.CharField(max_length=20, choices=EXCEPTION_TYPES)
    date = models.DateField()
    start_time = models.TimeField(blank=True, null=True)
    end_time = models.TimeField(blank=True, null=True)
    is_all_day = models.BooleanField(default=False)
    max_patients = models.PositiveIntegerField(default=0, help_text="0 means unavailable")
    reason = models.TextField(blank=True)
    notes = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-date', 'start_time']
        unique_together = ['doctor', 'date', 'start_time']
    
    def __str__(self):
        if self.is_all_day:
            return f"{self.doctor.full_name} - {self.get_exception_type_display()} on {self.date}"
        return f"{self.doctor.full_name} - {self.get_exception_type_display()} on {self.date} {self.start_time}-{self.end_time}"
    
    @property
    def affects_schedule(self):
        """Check if this exception affects the regular schedule"""
        return self.date >= timezone.now().date()

class WorkingHours(models.Model):
    DAYS_OF_WEEK = [
        (0, 'Monday'),
        (1, 'Tuesday'),
        (2, 'Wednesday'),
        (3, 'Thursday'),
        (4, 'Friday'),
        (5, 'Saturday'),
        (6, 'Sunday'),
    ]
    
    day_of_week = models.IntegerField(choices=DAYS_OF_WEEK, unique=True)
    is_working_day = models.BooleanField(default=True)
    start_time = models.TimeField(default=time(9, 0))  # 9:00 AM
    end_time = models.TimeField(default=time(17, 0))   # 5:00 PM
    lunch_start = models.TimeField(blank=True, null=True)
    lunch_end = models.TimeField(blank=True, null=True)
    
    class Meta:
        ordering = ['day_of_week']
    
    def __str__(self):
        if not self.is_working_day:
            return f"{self.get_day_of_week_display()} - Closed"
        return f"{self.get_day_of_week_display()} - {self.start_time} to {self.end_time}"
    
    @property
    def working_hours(self):
        """Calculate total working hours excluding lunch"""
        if not self.is_working_day:
            return timedelta(0)
        
        total_time = timedelta(
            hours=self.end_time.hour - self.start_time.hour,
            minutes=self.end_time.minute - self.start_time.minute
        )
        
        if self.lunch_start and self.lunch_end:
            lunch_time = timedelta(
                hours=self.lunch_end.hour - self.lunch_start.hour,
                minutes=self.lunch_end.minute - self.lunch_start.minute
            )
            total_time -= lunch_time
        
        return total_time
