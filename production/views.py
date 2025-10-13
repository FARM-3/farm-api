from django.shortcuts import render
from django.views.generic import ListView
from .models import Harvests
from .serializers import HarvestsSerializer
from rest_framework import viewsets
<<<<<<< HEAD
=======
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Block
from .serializers import BlockSerializer
>>>>>>> 32f5cd754438efd6bf2c5652d930d014e74a421b



# Create your views here.
class HarvestListView(ListView):
    model = Harvests
    template_name = 'harvest_list.html'
    context_object_name = 'harvests'
<<<<<<< HEAD
    queryset = Harvests.objects.all().order_by('date')
=======
    queryset = Harvests.objects.all().order_by('date_of_delivery')
>>>>>>> 32f5cd754438efd6bf2c5652d930d014e74a421b

class HarvestsViewSet(viewsets.ModelViewSet):
    queryset = Harvests.objects.all()
    serializer_class = HarvestsSerializer

<<<<<<< HEAD
=======

class BlockViewSet(viewsets.ModelViewSet):
    """ViewSet for Block management"""
    queryset = Block.objects.all()
    serializer_class = BlockSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'block_id'
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

>>>>>>> 32f5cd754438efd6bf2c5652d930d014e74a421b
    



