from django.shortcuts import render
from django.http import JsonResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Patient

# Create your views here.

@api_view(['GET'])
def patient_list(request):
    """List all patients"""
    patients = Patient.objects.all()
    data = [{
        'id': patient.id,
        'patient_id': patient.patient_id,
        'first_name': patient.first_name,
        'last_name': patient.last_name,
        'full_name': patient.full_name,
        'date_of_birth': patient.date_of_birth,
        'age': patient.age,
        'gender': patient.gender,
        'phone_number': patient.phone_number,
        'email': patient.email,
        'is_active': patient.is_active
    } for patient in patients]
    return Response(data)

@api_view(['GET'])
def patient_detail(request, pk):
    """Get a specific patient by ID"""
    try:
        patient = Patient.objects.get(pk=pk)
        data = {
            'id': patient.id,
            'patient_id': patient.patient_id,
            'first_name': patient.first_name,
            'last_name': patient.last_name,
            'full_name': patient.full_name,
            'date_of_birth': patient.date_of_birth,
            'age': patient.age,
            'gender': patient.gender,
            'phone_number': patient.phone_number,
            'email': patient.email,
            'address': patient.address,
            'blood_type': patient.blood_type,
            'height': patient.height,
            'weight': patient.weight,
            'allergies': patient.allergies,
            'medical_conditions': patient.medical_conditions,
            'medications': patient.medications,
            'insurance_provider': patient.insurance_provider,
            'insurance_number': patient.insurance_number,
            'registration_date': patient.registration_date,
            'is_active': patient.is_active
        }
        return Response(data)
    except Patient.DoesNotExist:
        return Response({'error': 'Patient not found'}, status=status.HTTP_404_NOT_FOUND)
