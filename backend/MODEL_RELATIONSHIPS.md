# Auto Triage System - Model Relationships

This document outlines the comprehensive model structure and relationships between all apps in the Auto Triage System.

## Overview

The system consists of 5 main apps, each with specific responsibilities and interconnected models:

1. **Patient** - Manages patient information and medical history
2. **Doctor** - Handles doctor profiles, specialties, and availability
3. **Rooms** - Manages hospital/clinic rooms and equipment
4. **Schedule** - Handles doctor scheduling and time management
5. **Appointment** - Core appointment management connecting all other entities

## Model Relationships

### 1. Patient App

#### Core Models:
- **Patient**: Main patient entity with personal and medical information
- **MedicalHistory**: Patient's medical history records
- **PatientDocument**: Patient-related documents and files

#### Relationships:
- `Patient` ↔ `User` (OneToOne) - Links to Django's built-in User model
- `MedicalHistory` → `Patient` (ForeignKey) - Medical records belong to patients
- `PatientDocument` → `Patient` (ForeignKey) - Documents belong to patients

### 2. Doctor App

#### Core Models:
- **Specialty**: Medical specialties (Cardiology, Neurology, etc.)
- **Doctor**: Doctor profiles with professional information
- **DoctorAvailability**: Weekly availability schedules
- **DoctorLeave**: Leave and vacation management

#### Relationships:
- `Doctor` ↔ `User` (OneToOne) - Links to Django's built-in User model
- `Doctor` ↔ `Specialty` (ManyToMany) - Doctors can have multiple specialties
- `DoctorAvailability` → `Doctor` (ForeignKey) - Availability belongs to doctors
- `DoctorLeave` → `Doctor` (ForeignKey) - Leave records belong to doctors
- `DoctorLeave` → `User` (ForeignKey) - Approved by admin users

### 3. Rooms App

#### Core Models:
- **RoomType**: Types of rooms (Consultation, Treatment, etc.)
- **Room**: Individual room instances
- **Equipment**: Medical equipment in rooms
- **RoomMaintenance**: Maintenance and cleaning schedules

#### Relationships:
- `Room` → `RoomType` (ForeignKey) - Rooms belong to specific types
- `Equipment` → `Room` (ForeignKey) - Equipment can be assigned to rooms
- `RoomMaintenance` → `Room` (ForeignKey) - Maintenance records belong to rooms

### 4. Schedule App

#### Core Models:
- **TimeSlot**: Reusable time slots (30min, 1hr, etc.)
- **DoctorSchedule**: Doctor's weekly schedule
- **ScheduleTemplate**: Reusable schedule templates
- **ScheduleTemplateItem**: Individual items in templates
- **ScheduleException**: Exceptions to regular schedules
- **WorkingHours**: General working hours for the facility

#### Relationships:
- `DoctorSchedule` → `Doctor` (ForeignKey) - Schedules belong to doctors
- `DoctorSchedule` → `TimeSlot` (ForeignKey) - Schedules use time slots
- `ScheduleTemplate` → `Doctor` (ForeignKey) - Templates belong to doctors
- `ScheduleTemplateItem` → `ScheduleTemplate` (ForeignKey) - Items belong to templates
- `ScheduleTemplateItem` → `TimeSlot` (ForeignKey) - Items use time slots
- `ScheduleException` → `Doctor` (ForeignKey) - Exceptions belong to doctors

### 5. Appointment App

#### Core Models:
- **AppointmentType**: Types of appointments (Consultation, Follow-up, etc.)
- **Appointment**: Main appointment entity
- **AppointmentFollowUp**: Follow-up appointment scheduling
- **AppointmentReminder**: Appointment reminders
- **AppointmentWaitlist**: Waitlist for appointments

#### Relationships:
- `Appointment` → `AppointmentType` (ForeignKey) - Appointments have types
- `Appointment` → `Patient` (ForeignKey) - Appointments belong to patients
- `Appointment` → `Doctor` (ForeignKey) - Appointments are with doctors
- `Appointment` → `Room` (ForeignKey) - Appointments can be assigned to rooms
- `Appointment` → `User` (ForeignKey) - Created by admin users
- `AppointmentFollowUp` → `Appointment` (ForeignKey) - Follow-ups belong to appointments
- `AppointmentReminder` → `Appointment` (ForeignKey) - Reminders belong to appointments
- `AppointmentWaitlist` → `Patient` (ForeignKey) - Waitlist entries belong to patients
- `AppointmentWaitlist` → `Doctor` (ForeignKey) - Waitlist entries are for doctors
- `AppointmentWaitlist` → `AppointmentType` (ForeignKey) - Waitlist entries have types

## Cross-App Relationships

### Key Integration Points:

1. **Appointment Scheduling**:
   - Connects patients, doctors, rooms, and schedules
   - Validates against doctor availability and room status
   - Checks for scheduling conflicts

2. **Doctor Management**:
   - Links doctor profiles with their schedules and availability
   - Manages specialties and professional information
   - Tracks leave and availability exceptions

3. **Room Management**:
   - Rooms can be assigned to appointments
   - Equipment tracking within rooms
   - Maintenance scheduling

4. **Patient Care**:
   - Complete medical history tracking
   - Document management
   - Appointment history and follow-ups

## Database Schema Benefits

### 1. **Normalization**:
- Proper separation of concerns
- Minimal data duplication
- Efficient data storage

### 2. **Referential Integrity**:
- Foreign key constraints ensure data consistency
- Cascade deletions where appropriate
- Proper relationship management

### 3. **Scalability**:
- Modular design allows for easy expansion
- Separate apps can be developed independently
- Clear separation of business logic

### 4. **Maintainability**:
- Well-organized model structure
- Clear naming conventions
- Comprehensive admin interfaces

## Usage Examples

### Creating an Appointment:
```python
# Check doctor availability
doctor = Doctor.objects.get(doctor_id='DR001')
patient = Patient.objects.get(patient_id='P001')
room = Room.objects.get(room_number='101')

# Create appointment
appointment = Appointment.objects.create(
    appointment_id='APT001',
    appointment_type=AppointmentType.objects.get(name='Consultation'),
    patient=patient,
    doctor=doctor,
    room=room,
    scheduled_date=date(2024, 1, 15),
    scheduled_time=time(9, 0),
    duration_minutes=30,
    reason='Regular checkup'
)
```

### Checking Doctor Schedule:
```python
# Get doctor's schedule for a specific day
schedule = DoctorSchedule.objects.filter(
    doctor=doctor,
    day_of_week=0  # Monday
).select_related('time_slot')

# Check for conflicts
conflicts = [s for s in schedule if s.is_conflicting]
```

### Room Assignment:
```python
# Find available rooms for a specific time
available_rooms = Room.objects.filter(
    status='AVAILABLE',
    room_type__name='Consultation'
).exclude(
    appointments__scheduled_date=date(2024, 1, 15),
    appointments__scheduled_time__lt=time(9, 30),
    appointments__end_time__gt=time(9, 0)
)
```

## Future Enhancements

1. **Notification System**: Integration with email/SMS services
2. **Calendar Integration**: Sync with external calendar systems
3. **Reporting**: Advanced analytics and reporting features
4. **Mobile App**: API endpoints for mobile applications
5. **Integration**: EHR system integration capabilities

This model structure provides a solid foundation for a comprehensive healthcare appointment and management system with clear separation of concerns and robust relationships between all entities.
