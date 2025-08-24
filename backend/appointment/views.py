from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

# Create your views here.

@api_view(['GET'])
def appointment_list(request):
    """List all appointments"""
    # Placeholder - will implement when appointment models are created
    return Response({'message': 'Appointment list endpoint - models not yet implemented'})

@api_view(['GET'])
def appointment_detail(request, pk):
    """Get a specific appointment by ID"""
    # Placeholder - will implement when appointment models are created
    return Response({'message': f'Appointment detail endpoint for ID {pk} - models not yet implemented'})
