from django.shortcuts import get_object_or_404
from django.db.models import Q
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample
from drf_spectacular.types import OpenApiTypes
from .models import Doctor
from .serializers import DoctorListSerializer, DoctorDetailSerializer, DoctorCreateSerializer


class DoctorPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


@extend_schema(
    methods=['GET'],
    summary="List doctors",
    description="Retrieve a paginated list of doctors with optional filtering and search capabilities.",
    parameters=[
        OpenApiParameter(
            name='search',
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
            description='Search across doctor names, ID, license number, email, and phone number',
            examples=[
                OpenApiExample('Search by name', value='John'),
                OpenApiExample('Search by doctor ID', value='DOC001'),
            ]
        ),
        OpenApiParameter(
            name='specialty',
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
            description='Filter by exact specialty name',
            examples=[
                OpenApiExample('Cardiology', value='Cardiology'),
                OpenApiExample('Neurology', value='Neurology'),
            ]
        ),
        OpenApiParameter(
            name='status',
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
            description='Filter by doctor status',
            enum=['ACTIVE', 'INACTIVE', 'ON_LEAVE', 'RETIRED'],
            examples=[
                OpenApiExample('Active doctors', value='ACTIVE'),
                OpenApiExample('On leave doctors', value='ON_LEAVE'),
            ]
        ),
        OpenApiParameter(
            name='is_available',
            type=OpenApiTypes.BOOL,
            location=OpenApiParameter.QUERY,
            description='Filter by availability status',
            examples=[
                OpenApiExample('Available doctors', value=True),
                OpenApiExample('Unavailable doctors', value=False),
            ]
        ),
        OpenApiParameter(
            name='ordering',
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
            description='Order results by field (default: last_name)',
            examples=[
                OpenApiExample('By last name', value='last_name'),
                OpenApiExample('By first name', value='first_name'),
                OpenApiExample('By hire date', value='hire_date'),
                OpenApiExample('By experience (desc)', value='-years_of_experience'),
            ]
        ),
        OpenApiParameter(
            name='page',
            type=OpenApiTypes.INT,
            location=OpenApiParameter.QUERY,
            description='Page number for pagination',
            examples=[OpenApiExample('First page', value=1)]
        ),
        OpenApiParameter(
            name='page_size',
            type=OpenApiTypes.INT,
            location=OpenApiParameter.QUERY,
            description='Number of results per page (max 100)',
            examples=[OpenApiExample('Default page size', value=20)]
        ),
    ],
    responses={
        200: DoctorListSerializer(many=True),
        401: OpenApiExample('Unauthorized', value={'detail': 'Authentication credentials were not provided.'}),
    },
    tags=['Doctors']
)
@extend_schema(
    methods=['POST'],
    summary="Create a new doctor",
    description="Register a new doctor in the system with all required information.",
    request=DoctorCreateSerializer,
    responses={
        201: OpenApiExample(
            'Doctor created successfully',
            value={
                'message': 'Doctor created successfully.',
                'doctor_id': 1,
                'doctor': {
                    'id': 1,
                    'doctor_id': 'DOC001',
                    'first_name': 'John',
                    'last_name': 'Doe',
                    'full_name': 'Dr. John Doe',
                    'date_of_birth': '1980-01-01',
                    'age': 44,
                    'gender': 'M',
                    'specialties': [],
                    'license_number': 'LIC123456',
                    'medical_school': 'Harvard Medical School',
                    'graduation_year': 2005,
                    'board_certifications': '',
                    'years_of_experience': 15,
                    'phone_number': '+1234567890',
                    'email': 'john.doe@example.com',
                    'office_address': '',
                    'status': 'ACTIVE',
                    'hire_date': '2024-01-01',
                    'department': '',
                    'is_available': True,
                    'created_at': '2024-01-01T00:00:00Z',
                    'updated_at': '2024-01-01T00:00:00Z',
                    'availabilities': [],
                    'leaves': []
                }
            }
        ),
        400: OpenApiExample(
            'Validation error',
            value={
                'doctor_id': ['A doctor with this ID already exists.'],
                'license_number': ['A doctor with this license number already exists.']
            }
        ),
        401: OpenApiExample('Unauthorized', value={'detail': 'Authentication credentials were not provided.'}),
    },
    examples=[
        OpenApiExample(
            'Create doctor request',
            value={
                'doctor_id': 'DOC001',
                'first_name': 'John',
                'last_name': 'Doe',
                'date_of_birth': '1980-01-01',
                'gender': 'M',
                'license_number': 'LIC123456',
                'medical_school': 'Harvard Medical School',
                'graduation_year': 2005,
                'years_of_experience': 15,
                'phone_number': '+1234567890',
                'email': 'john.doe@example.com',
                'status': 'ACTIVE',
                'specialties': [1, 2]
            }
        )
    ],
    tags=['Doctors']
)
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def doctor_list_create(request):
    """
    GET: List doctors with optional search/filtering and pagination
    POST: Create a new doctor
    """
    if request.method == 'GET':
        queryset = Doctor.objects.all()

        search = request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(first_name__icontains=search) |
                Q(last_name__icontains=search) |
                Q(doctor_id__icontains=search) |
                Q(license_number__icontains=search) |
                Q(email__icontains=search) |
                Q(phone_number__icontains=search)
            )

        specialty = request.query_params.get('specialty')
        if specialty:
            queryset = queryset.filter(specialties__name__iexact=specialty)

        status_param = request.query_params.get('status')
        if status_param:
            queryset = queryset.filter(status=status_param)

        is_available = request.query_params.get('is_available')
        if is_available is not None:
            queryset = queryset.filter(is_available=is_available.lower() == 'true')

        ordering = request.query_params.get('ordering', 'last_name')
        if ordering:
            queryset = queryset.order_by(ordering)

        paginator = DoctorPagination()
        page = paginator.paginate_queryset(queryset, request)
        if page is not None:
            serializer = DoctorListSerializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)

        serializer = DoctorListSerializer(queryset, many=True)
        return Response(serializer.data)
    
    elif request.method == 'POST':
        serializer = DoctorCreateSerializer(data=request.data)
        if serializer.is_valid():
            doctor = serializer.save()
            return Response(
                {
                    "message": "Doctor created successfully.",
                    "doctor_id": doctor.id,
                    "doctor": DoctorDetailSerializer(doctor).data
                },
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    summary="Get doctor details",
    description="Retrieve detailed information for a specific doctor including specialties, availability, and leave records.",
    parameters=[
        OpenApiParameter(
            name='pk',
            type=OpenApiTypes.INT,
            location=OpenApiParameter.PATH,
            description='Primary key of the doctor to retrieve',
            examples=[OpenApiExample('Doctor ID', value=1)]
        )
    ],
    responses={
        200: DoctorDetailSerializer,
        404: OpenApiExample(
            'Doctor not found',
            value={'detail': 'Not found.'}
        ),
        401: OpenApiExample(
            'Unauthorized',
            value={'detail': 'Authentication credentials were not provided.'}
        ),
    },
    tags=['Doctors']
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def doctor_detail(request, pk):
    """Retrieve details for a specific doctor by primary key"""
    doctor = get_object_or_404(Doctor, pk=pk)
    serializer = DoctorDetailSerializer(doctor)
    return Response(serializer.data)


@extend_schema(
    summary="Get doctor phone numbers",
    description="Retrieve a simple list of doctor phone numbers with optional filtering by status and availability.",
    parameters=[
        OpenApiParameter(
            name='status',
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
            description='Filter by doctor status (default: ACTIVE only)',
            enum=['ACTIVE', 'INACTIVE', 'ON_LEAVE', 'RETIRED'],
            examples=[
                OpenApiExample('Active doctors', value='ACTIVE'),
                OpenApiExample('All statuses', value=''),
            ]
        ),
        OpenApiParameter(
            name='is_available',
            type=OpenApiTypes.BOOL,
            location=OpenApiParameter.QUERY,
            description='Filter by availability status (default: true only)',
            examples=[
                OpenApiExample('Available doctors', value=True),
                OpenApiExample('All doctors', value=''),
            ]
        ),
    ],
    responses={
        200: OpenApiExample(
            'Phone numbers list',
            value={
                'phone_numbers': ['+1234567890', '+0987654321', '+1122334455'],
                'count': 3
            }
        ),
        401: OpenApiExample(
            'Unauthorized',
            value={'detail': 'Authentication credentials were not provided.'}
        ),
    },
    tags=['Doctors']
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def doctor_phone_numbers(request):
    """
    GET: Return a simple list of doctor phone numbers
    Query params:
      - status: filter by status (default: ACTIVE only)
      - is_available: filter by availability (default: true only)
    """
    queryset = Doctor.objects.exclude(phone_number='').exclude(phone_number__isnull=True)
    
    # Default to active doctors only
    status_param = request.query_params.get('status', 'ACTIVE')
    if status_param:
        queryset = queryset.filter(status=status_param)
    
    # Default to available doctors only
    is_available = request.query_params.get('is_available', 'true')
    if is_available is not None:
        queryset = queryset.filter(is_available=is_available.lower() == 'true')
    
    # Extract just the phone numbers
    phone_numbers = list(queryset.values_list('phone_number', flat=True))
    
    return Response({
        'phone_numbers': phone_numbers,
        'count': len(phone_numbers)
    })


