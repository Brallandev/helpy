from rest_framework import serializers
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


