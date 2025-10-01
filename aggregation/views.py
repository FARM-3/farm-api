from django.shortcuts import render
from django.views.generic import ListView
from .models import Farmer
from .models import FarmerHarvest
from .serializers import FarmerSerializer
from .serializers import FarmerHarvestSerializer
from rest_framework import viewsets


# Create your views here.
class FarmerListView(ListView):
    model = Farmer
    template_name = 'farmer_list.html'
    context_object_name = 'farmers'
    queryset = Farmer.objects.all().order_by('name')
class FarmerViewSet(viewsets.ModelViewSet):
    queryset = Farmer.objects.all()
    serializer_class = FarmerSerializer

class FarmerHarvestListView(ListView):
    model = FarmerHarvest
    template_name = 'farmerharvest_list.html'
    context_object_name = 'farmerharvests'
    queryset = FarmerHarvest.objects.all().order_by('date_harvested')

class FarmerHarvestViewSet(viewsets.ModelViewSet):
    queryset = FarmerHarvest.objects.all()
    serializer_class = FarmerHarvestSerializer