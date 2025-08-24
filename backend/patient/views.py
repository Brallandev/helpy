from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.db import transaction
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.pagination import PageNumberPagination
from django.db.models import Q
from .models import Patient, MedicalHistory, PatientDocument
from .serializers import (
    PatientListSerializer, PatientDetailSerializer, PatientCreateSerializer,
    PatientUpdateSerializer, MedicalHistorySerializer, PatientDocumentSerializer,
    PatientIntakeSerializer
)
import json
from datetime import datetime
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

# Create your views here.

class PatientPagination(PageNumberPagination):
    """Custom pagination for patient list"""
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def patient_list(request):
    """
    GET: List all patients with optional search and filtering
    POST: Create a new patient
    """
    if request.method == 'GET':
        queryset = Patient.objects.all()
        
        # Search functionality
        search = request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(
                Q(first_name__icontains=search) |
                Q(last_name__icontains=search) |
                Q(phone_number__icontains=search) |
                Q(email__icontains=search)
            )
        
        # Filter by active status
        is_active = request.query_params.get('is_active', None)
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
        
        # Filter by gender
        gender = request.query_params.get('gender', None)
        if gender:
            queryset = queryset.filter(gender=gender.upper())
        
        # Ordering
        ordering = request.query_params.get('ordering', 'last_name')
        if ordering:
            queryset = queryset.order_by(ordering)
        
        # Pagination
        paginator = PatientPagination()
        page = paginator.paginate_queryset(queryset, request)
        if page is not None:
            serializer = PatientListSerializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)
        
        serializer = PatientListSerializer(queryset, many=True)
        return Response(serializer.data)
    
    elif request.method == 'POST':
        serializer = PatientCreateSerializer(data=request.data)
        if serializer.is_valid():
            try:
                with transaction.atomic():
                    patient = serializer.save()
                    response_serializer = PatientDetailSerializer(patient)
                    return Response(response_serializer.data, status=status.HTTP_201_CREATED)
            except Exception as e:
                return Response(
                    {'error': 'Failed to create patient', 'details': str(e)},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
@permission_classes([IsAuthenticated])
def patient_detail(request, pk):
    """
    GET: Retrieve a specific patient
    PUT/PATCH: Update a specific patient
    DELETE: Soft delete a patient (set is_active=False)
    """
    patient = get_object_or_404(Patient, pk=pk)
    
    if request.method == 'GET':
        serializer = PatientDetailSerializer(patient)
        return Response(serializer.data)
    
    elif request.method in ['PUT', 'PATCH']:
        partial = request.method == 'PATCH'
        serializer = PatientUpdateSerializer(patient, data=request.data, partial=partial)
        if serializer.is_valid():
            try:
                with transaction.atomic():
                    updated_patient = serializer.save()
                    response_serializer = PatientDetailSerializer(updated_patient)
                    return Response(response_serializer.data)
            except Exception as e:
                return Response(
                    {'error': 'Failed to update patient', 'details': str(e)},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'DELETE':
        try:
            with transaction.atomic():
                # Soft delete - set is_active to False instead of actually deleting
                patient.is_active = False
                patient.save()
                return Response(
                    {'message': 'Patient deactivated successfully'},
                    status=status.HTTP_200_OK
                )
        except Exception as e:
            return Response(
                {'error': 'Failed to deactivate patient', 'details': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def patient_medical_history(request, patient_pk):
    """
    GET: List medical history for a specific patient
    POST: Add new medical history entry for a patient
    """
    patient = get_object_or_404(Patient, pk=patient_pk)
    
    if request.method == 'GET':
        medical_histories = MedicalHistory.objects.filter(patient=patient)
        serializer = MedicalHistorySerializer(medical_histories, many=True)
        return Response(serializer.data)
    
    elif request.method == 'POST':
        serializer = MedicalHistorySerializer(data=request.data)
        if serializer.is_valid():
            try:
                with transaction.atomic():
                    medical_history = serializer.save(patient=patient)
                    response_serializer = MedicalHistorySerializer(medical_history)
                    return Response(response_serializer.data, status=status.HTTP_201_CREATED)
            except Exception as e:
                return Response(
                    {'error': 'Failed to create medical history', 'details': str(e)},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser, JSONParser])
def patient_documents(request, patient_pk):
    """
    GET: List documents for a specific patient
    POST: Upload a new document for a patient
    """
    patient = get_object_or_404(Patient, pk=patient_pk)
    
    if request.method == 'GET':
        documents = PatientDocument.objects.filter(patient=patient)
        serializer = PatientDocumentSerializer(documents, many=True)
        return Response(serializer.data)
    
    elif request.method == 'POST':
        serializer = PatientDocumentSerializer(data=request.data)
        if serializer.is_valid():
            try:
                with transaction.atomic():
                    document = serializer.save(patient=patient)
                    response_serializer = PatientDocumentSerializer(document)
                    return Response(response_serializer.data, status=status.HTTP_201_CREATED)
            except Exception as e:
                return Response(
                    {'error': 'Failed to upload document', 'details': str(e)},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def patient_search(request):
    """Advanced patient search with multiple criteria"""
    queryset = Patient.objects.filter(is_active=True)
    
    # Search by name or phone
    query = request.query_params.get('q', '')
    if query:
        queryset = queryset.filter(
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query) |
            Q(phone_number__icontains=query)
        )
    
    # Age range filter
    min_age = request.query_params.get('min_age')
    max_age = request.query_params.get('max_age')
    if min_age or max_age:
        from datetime import date, timedelta
        today = date.today()
        
        if min_age:
            max_birth_date = today - timedelta(days=int(min_age) * 365)
            queryset = queryset.filter(date_of_birth__lte=max_birth_date)
        
        if max_age:
            min_birth_date = today - timedelta(days=(int(max_age) + 1) * 365)
            queryset = queryset.filter(date_of_birth__gte=min_birth_date)
    
    # Medical condition filter
    condition = request.query_params.get('condition')
    if condition:
        queryset = queryset.filter(medical_conditions__icontains=condition)
    
    # Blood type filter
    blood_type = request.query_params.get('blood_type')
    if blood_type:
        queryset = queryset.filter(blood_type=blood_type)
    
    serializer = PatientListSerializer(queryset[:50], many=True)  # Limit to 50 results
    return Response(serializer.data)


intake_response_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'patient_id': openapi.Schema(type=openapi.TYPE_INTEGER),
        'phone_number': openapi.Schema(type=openapi.TYPE_STRING),
        'created_new_patient': openapi.Schema(type=openapi.TYPE_BOOLEAN),
        'medical_history_id': openapi.Schema(type=openapi.TYPE_INTEGER),
    }
)


@swagger_auto_schema(
    method='post',
    request_body=PatientIntakeSerializer,
    responses={
        201: openapi.Response('Created', intake_response_schema),
        400: 'Bad Request',
        500: 'Server Error',
    },
    operation_id='patients_intake_create',
    operation_description='Find or create a patient by phone and record intake answers as medical history.'
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def patient_intake(request):
    """
    POST body example:
    {
      "user_phone": "+573213754760",
      "timestamp": "2025-08-23T16:30:00",
      "answers": {
        "name": "David",
        "age": "25",
        ... other free-form keys ...
      }
    }

    Behavior:
    - If a patient exists with phone_number == user_phone, use it and ignore name/age
    - Otherwise, create a patient using name (split to first/last) and phone
    - Create a MedicalHistory entry with details containing the remaining answers (excluding name, age), plus timestamp if provided
    """
    # Validate input using serializer so Swagger shows fields and types
    intake_serializer = PatientIntakeSerializer(data=request.data)
    if not intake_serializer.is_valid():
        return Response(intake_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    validated = intake_serializer.validated_data
    user_phone = validated.get('user_phone')
    timestamp = validated.get('timestamp')
    answers = validated.get('answers') or {}

    # Normalize timestamp if present
    ts_iso = None
    if timestamp:
        try:
            # Accept ISO8601
            ts_iso = datetime.fromisoformat(timestamp.replace('Z', '+00:00')).isoformat()
        except Exception:
            # keep raw
            ts_iso = str(timestamp)

    try:
        with transaction.atomic():
            patient = Patient.objects.filter(phone_number=user_phone).first()
            if not patient:
                # Create new patient using provided name if available
                name = answers.get('name') or ''
                first_name = ''
                last_name = ''
                if isinstance(name, str) and name.strip():
                    parts = name.strip().split()
                    first_name = parts[0]
                    last_name = ' '.join(parts[1:]) if len(parts) > 1 else ''
                else:
                    first_name = 'Patient'
                    last_name = user_phone

                patient = Patient.objects.create(
                    phone_number=user_phone,
                    first_name=first_name,
                    last_name=last_name,
                    gender='P'
                )

            # Build details excluding name and age
            details_payload = {k: v for k, v in answers.items() if k not in ['name', 'age']}
            if ts_iso:
                details_payload['timestamp'] = ts_iso
            details_payload['source'] = 'intake'

            # Persist as JSON text
            details_text = json.dumps(details_payload, ensure_ascii=False)

            history = MedicalHistory.objects.create(
                patient=patient,
                details=details_text
            )

            response = {
                'patient_id': patient.id,
                'phone_number': patient.phone_number,
                'created_new_patient': history.created_at == patient.registration_date,  # approximate
                'medical_history_id': history.id,
            }
            return Response(response, status=status.HTTP_201_CREATED)
    except Exception as e:
        return Response({'error': 'Failed to process intake', 'details': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
