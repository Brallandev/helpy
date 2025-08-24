from django.shortcuts import get_object_or_404
from django.db.models import Q
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from .models import Doctor
from .serializers import DoctorListSerializer, DoctorDetailSerializer


class DoctorPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def doctor_list(request):
    """
    GET: List doctors with optional search/filtering and pagination
    Query params:
      - search: name, doctor_id, license_number, email, phone
      - specialty: exact specialty name
      - status: status value (ACTIVE/INACTIVE/ON_LEAVE/RETIRED)
      - is_available: true/false
      - ordering: field to order by (default last_name)
    """
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


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def doctor_detail(request, pk):
    """Retrieve details for a specific doctor by primary key"""
    doctor = get_object_or_404(Doctor, pk=pk)
    serializer = DoctorDetailSerializer(doctor)
    return Response(serializer.data)


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
