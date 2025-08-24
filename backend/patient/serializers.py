from rest_framework import serializers
from .models import Patient, MedicalHistory, PatientDocument


class PatientIntakeSerializer(serializers.Serializer):
    """Schema-only serializer for the patient intake endpoint."""
    user_phone = serializers.CharField()
    timestamp = serializers.DateTimeField(required=False, allow_null=True)
    answers = serializers.JSONField()


class PatientDocumentSerializer(serializers.ModelSerializer):
    """Serializer for PatientDocument model"""
    
    class Meta:
        model = PatientDocument
        fields = [
            'id', 'document_type', 'title', 'file', 'uploaded_at', 'notes'
        ]
        read_only_fields = ['id', 'uploaded_at']


class MedicalHistorySerializer(serializers.ModelSerializer):
    """Serializer for MedicalHistory model"""
    
    class Meta:
        model = MedicalHistory
        fields = [
            'id', 'details', 'created_at', 'updated_at', 'approved'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class PatientListSerializer(serializers.ModelSerializer):
    """Serializer for Patient list view (minimal fields)"""
    full_name = serializers.ReadOnlyField()
    age = serializers.ReadOnlyField()
    
    class Meta:
        model = Patient
        fields = [
            'id', 'phone_number', 'first_name', 'last_name', 'full_name',
            'date_of_birth', 'age', 'gender', 'email', 'is_active',
            'registration_date'
        ]
        read_only_fields = ['id', 'registration_date', 'full_name', 'age']


class PatientDetailSerializer(serializers.ModelSerializer):
    """Serializer for Patient detail view (all fields)"""
    full_name = serializers.ReadOnlyField()
    age = serializers.ReadOnlyField()
    medical_histories = MedicalHistorySerializer(many=True, read_only=True)
    documents = PatientDocumentSerializer(many=True, read_only=True)
    
    class Meta:
        model = Patient
        fields = [
            'id', 'phone_number', 'first_name', 'last_name', 'full_name',
            'date_of_birth', 'age', 'gender', 'email', 'address',
            'emergency_contact_name', 'emergency_contact_phone',
            'blood_type', 'height', 'weight', 'allergies',
            'medical_conditions', 'medications', 'insurance_provider',
            'insurance_number', 'registration_date', 'is_active',
            'medical_histories', 'documents'
        ]
        read_only_fields = ['id', 'registration_date', 'full_name', 'age']

    def validate_phone_number(self, value):
        """Custom validation for phone number"""
        if not value:
            raise serializers.ValidationError("Phone number is required.")
        return value

    def validate_date_of_birth(self, value):
        """Custom validation for date of birth"""
        from datetime import date
        if value and value > date.today():
            raise serializers.ValidationError("Date of birth cannot be in the future.")
        return value

    def validate_height(self, value):
        """Custom validation for height"""
        if value and (value < 30 or value > 300):
            raise serializers.ValidationError("Height must be between 30 and 300 cm.")
        return value

    def validate_weight(self, value):
        """Custom validation for weight"""
        if value and (value < 1 or value > 500):
            raise serializers.ValidationError("Weight must be between 1 and 500 kg.")
        return value


class PatientCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating new patients"""
    
    class Meta:
        model = Patient
        fields = [
            'phone_number', 'first_name', 'last_name', 'date_of_birth',
            'gender', 'email', 'address', 'emergency_contact_name',
            'emergency_contact_phone', 'blood_type', 'height', 'weight',
            'allergies', 'medical_conditions', 'medications',
            'insurance_provider', 'insurance_number'
        ]

    def validate_phone_number(self, value):
        """Custom validation for phone number"""
        if not value:
            raise serializers.ValidationError("Phone number is required.")
        return value

    def validate_first_name(self, value):
        """Custom validation for first name"""
        if not value or len(value.strip()) < 2:
            raise serializers.ValidationError("First name must be at least 2 characters long.")
        return value.strip()

    def validate_last_name(self, value):
        """Custom validation for last name"""
        if not value or len(value.strip()) < 2:
            raise serializers.ValidationError("Last name must be at least 2 characters long.")
        return value.strip()


class PatientUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating existing patients"""
    
    class Meta:
        model = Patient
        fields = [
            'first_name', 'last_name', 'date_of_birth', 'gender',
            'email', 'address', 'emergency_contact_name',
            'emergency_contact_phone', 'blood_type', 'height', 'weight',
            'allergies', 'medical_conditions', 'medications',
            'insurance_provider', 'insurance_number', 'is_active'
        ]

    def validate_first_name(self, value):
        """Custom validation for first name"""
        if value and len(value.strip()) < 2:
            raise serializers.ValidationError("First name must be at least 2 characters long.")
        return value.strip() if value else value

    def validate_last_name(self, value):
        """Custom validation for last name"""
        if value and len(value.strip()) < 2:
            raise serializers.ValidationError("Last name must be at least 2 characters long.")
        return value.strip() if value else value
