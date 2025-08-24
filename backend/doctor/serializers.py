from rest_framework import serializers
from drf_spectacular.utils import extend_schema_field
from drf_spectacular.types import OpenApiTypes
from .models import Doctor, Specialty, DoctorAvailability, DoctorLeave


class SpecialtySerializer(serializers.ModelSerializer):
    class Meta:
        model = Specialty
        fields = ['id', 'name', 'description']


class DoctorAvailabilitySerializer(serializers.ModelSerializer):
    day_of_week_display = serializers.CharField(source='get_day_of_week_display', read_only=True)

    class Meta:
        model = DoctorAvailability
        fields = [
            'id', 'day_of_week', 'day_of_week_display', 'start_time', 'end_time', 'is_available', 'notes'
        ]


class DoctorLeaveSerializer(serializers.ModelSerializer):
    leave_type_display = serializers.CharField(source='get_leave_type_display', read_only=True)

    class Meta:
        model = DoctorLeave
        fields = [
            'id', 'leave_type', 'leave_type_display', 'start_date', 'end_date', 'reason', 'is_approved', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class DoctorListSerializer(serializers.ModelSerializer):
    full_name = serializers.ReadOnlyField()
    age = serializers.ReadOnlyField()
    specialties = serializers.SlugRelatedField(
        many=True,
        read_only=True,
        slug_field='name'
    )

    class Meta:
        model = Doctor
        fields = [
            'id', 'doctor_id', 'first_name', 'last_name', 'full_name', 'age', 'gender',
            'specialties', 'license_number', 'years_of_experience', 'status', 'is_available',
            'phone_number', 'email', 'department', 'hire_date'
        ]
        read_only_fields = ['id', 'full_name', 'age', 'hire_date']


class DoctorDetailSerializer(serializers.ModelSerializer):
    full_name = serializers.ReadOnlyField()
    age = serializers.ReadOnlyField()
    specialties = SpecialtySerializer(many=True, read_only=True)
    availabilities = DoctorAvailabilitySerializer(many=True, read_only=True)
    leaves = DoctorLeaveSerializer(many=True, read_only=True)

    class Meta:
        model = Doctor
        fields = [
            'id', 'doctor_id', 'first_name', 'last_name', 'full_name', 'date_of_birth', 'age', 'gender',
            'specialties', 'license_number', 'medical_school', 'graduation_year', 'board_certifications',
            'years_of_experience', 'phone_number', 'email', 'office_address', 'status', 'hire_date',
            'department', 'is_available', 'created_at', 'updated_at', 'availabilities', 'leaves'
        ]
        read_only_fields = ['id', 'full_name', 'age', 'created_at', 'updated_at', 'hire_date']


class DoctorCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating a new doctor.
    
    This serializer handles the creation of doctor records with validation
    for unique constraints and proper data formatting.
    """
    specialties = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Specialty.objects.filter(is_active=True),
        required=False,
        help_text="List of specialty IDs to assign to the doctor"
    )

    class Meta:
        model = Doctor
        fields = [
            'doctor_id', 'first_name', 'last_name', 'date_of_birth', 'gender',
            'specialties', 'license_number', 'medical_school', 'graduation_year', 
            'board_certifications', 'years_of_experience', 'phone_number', 'email', 
            'office_address', 'status', 'department', 'is_available'
        ]
        extra_kwargs = {
            'doctor_id': {'help_text': 'Unique identifier for the doctor (e.g., DOC001)'},
            'first_name': {'help_text': 'Doctor\'s first name'},
            'last_name': {'help_text': 'Doctor\'s last name'},
            'date_of_birth': {'help_text': 'Date of birth in YYYY-MM-DD format'},
            'gender': {'help_text': 'Gender: M (Male), F (Female), O (Other), P (Prefer not to say)'},
            'license_number': {'help_text': 'Medical license number (must be unique)'},
            'medical_school': {'help_text': 'Name of the medical school attended'},
            'graduation_year': {'help_text': 'Year of graduation from medical school'},
            'board_certifications': {'help_text': 'Board certifications and dates (optional)'},
            'years_of_experience': {'help_text': 'Total years of medical experience'},
            'phone_number': {'help_text': 'Phone number in international format (e.g., +1234567890)'},
            'email': {'help_text': 'Email address (optional)'},
            'office_address': {'help_text': 'Office or clinic address (optional)'},
            'status': {'help_text': 'Current status: ACTIVE, INACTIVE, ON_LEAVE, or RETIRED'},
            'department': {'help_text': 'Department or unit (optional)'},
            'is_available': {'help_text': 'Whether the doctor is currently available for appointments'},
        }

    def validate_doctor_id(self, value):
        """Ensure doctor_id is unique"""
        if Doctor.objects.filter(doctor_id=value).exists():
            raise serializers.ValidationError("A doctor with this ID already exists.")
        return value

    def validate_license_number(self, value):
        """Ensure license_number is unique"""
        if Doctor.objects.filter(license_number=value).exists():
            raise serializers.ValidationError("A doctor with this license number already exists.")
        return value

    def validate_graduation_year(self, value):
        """Ensure graduation year is reasonable"""
        from datetime import date
        current_year = date.today().year
        if value < 1950 or value > current_year:
            raise serializers.ValidationError(f"Graduation year must be between 1950 and {current_year}.")
        return value

    def create(self, validated_data):
        specialties_data = validated_data.pop('specialties', [])
        doctor = Doctor.objects.create(**validated_data)
        if specialties_data:
            doctor.specialties.set(specialties_data)
        return doctor


