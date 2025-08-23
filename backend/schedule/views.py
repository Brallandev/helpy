from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

# Create your views here.

@api_view(['GET'])
def schedule_list(request):
    """List all schedules"""
    # Placeholder - will implement when schedule models are created
    return Response({'message': 'Schedule list endpoint - models not yet implemented'})

@api_view(['GET'])
def schedule_detail(request, pk):
    """Get a specific schedule by ID"""
    # Placeholder - will implement when schedule models are created
    return Response({'message': f'Schedule detail endpoint for ID {pk} - models not yet implemented'})
