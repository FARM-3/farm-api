from django.shortcuts import render
from django.views.generic import ListView
from .models import FarmerRegistration
from .models import FarmerHarvest
from .serializers import FarmerRegistrationSerializer
from .serializers import FarmerHarvestSerializer
from rest_framework import viewsets
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
import requests


# Create your views here.
class FarmerListView(ListView):
    model = FarmerRegistration
    template_name = 'farmer_list.html'
    context_object_name = 'farmers'
    queryset = FarmerRegistration.objects.all().order_by('first_name')
    
class FarmerViewSet(viewsets.ModelViewSet):
    queryset = FarmerRegistration.objects.all()
    serializer_class = FarmerRegistrationSerializer

class FarmerHarvestListView(ListView):
    model = FarmerHarvest
    template_name = 'farmerharvest_list.html'
    context_object_name = 'farmerharvests'
    queryset = FarmerHarvest.objects.all().order_by('date_of_delivery')

class FarmerHarvestViewSet(viewsets.ModelViewSet):
    queryset = FarmerHarvest.objects.all()
    serializer_class = FarmerHarvestSerializer

@api_view(['POST'])
def reverse_geocode(request):
    """
    Convert GPS coordinates (latitude, longitude) to a human-readable address.
    Expects JSON body: {"latitude": "0.3476", "longitude": "32.5825"}
    """
    latitude = request.data.get('latitude')
    longitude = request.data.get('longitude')

    if not latitude or not longitude:
        return Response(
            {'error': 'Both latitude and longitude are required'},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        # Call OpenStreetMap Nominatim API for reverse geocoding
        resp = requests.get(
            'https://nominatim.openstreetmap.org/reverse',
            params={
                'lat': latitude,
                'lon': longitude,
                'format': 'json'
            },
            headers={'User-Agent': 'Rugyeyo-Farm-API/1.0'},
            timeout=5
        )

        if resp.status_code == 200:
            data = resp.json()
            return Response({
                'success': True,
                'address': data.get('display_name', ''),
                'details': {
                    'village': data.get('address', {}).get('village', ''),
                    'county': data.get('address', {}).get('county', ''),
                    'state': data.get('address', {}).get('state', ''),
                    'country': data.get('address', {}).get('country', ''),
                }
            })
        else:
            return Response(
                {'error': 'Failed to fetch address from coordinates'},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )
    except Exception as e:
        return Response(
            {'error': f'Error during geocoding: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )