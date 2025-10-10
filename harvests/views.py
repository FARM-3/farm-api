from django.shortcuts import render
from django.views.generic import ListView
from .models import Harvests
from .serializers import HarvestsSerializer
from rest_framework import viewsets



# Create your views here.
class HarvestListView(ListView):
    model = Harvests
    template_name = 'harvest_list.html'
    context_object_name = 'harvests'
    queryset = Harvests.objects.all().order_by('date')

class HarvestsViewSet(viewsets.ModelViewSet):
    queryset = Harvests.objects.all()
    serializer_class = HarvestsSerializer

    



