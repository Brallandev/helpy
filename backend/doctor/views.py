from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

# Create your views here.

@api_view(['GET'])
def doctor_list(request):
    """List all doctors"""
    # Placeholder - will implement when doctor models are created
    return Response({'message': 'Doctor list endpoint - models not yet implemented'})

@api_view(['GET'])
def doctor_detail(request, pk):
    """Get a specific doctor by ID"""
    # Placeholder - will implement when doctor models are created
    return Response({'message': f'Doctor detail endpoint for ID {pk} - models not yet implemented'})
