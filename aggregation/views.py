from django.shortcuts import render
from django.views.generic import ListView
from .models import FarmerRegistration
from .models import FarmerHarvest
from .serializers import FarmerRegistrationSerializer
from .serializers import FarmerHarvestSerializer
from rest_framework import viewsets


# Create your views here.
class FarmerRegistrationListView(ListView):
    model = FarmerRegistration
    template_name = 'farmer_list.html'
    context_object_name = 'farmers'
    queryset = FarmerRegistration.objects.all().order_by('first_name')
    
class FarmerRegistrationViewSet(viewsets.ModelViewSet):
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