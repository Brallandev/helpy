from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

# Create your views here.

@api_view(['GET'])
def room_list(request):
    """List all rooms"""
    # Placeholder - will implement when room models are created
    return Response({'message': 'Room list endpoint - models not yet implemented'})

@api_view(['GET'])
def room_detail(request, pk):
    """Get a specific room by ID"""
    # Placeholder - will implement when room models are created
    return Response({'message': f'Room detail endpoint for ID {pk} - models not yet implemented'})
