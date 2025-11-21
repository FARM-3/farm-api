from django.shortcuts import render
from django.views.generic import ListView
from .models import Harvests, Block
from .serializers import HarvestsSerializer, BlockSerializer
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated


# Django Generic View for HTML rendering
class HarvestListView(ListView):
    model = Harvests
    template_name = 'harvest_list.html'
    context_object_name = 'harvests'
    queryset = Harvests.objects.all().order_by('date_of_delivery')


# Django REST Framework ViewSets for API
class HarvestsViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Production Harvests - allows all CRUD operations (POST, GET, PUT, DELETE)

    Endpoints:
    - GET /api/harvests/ - List all harvests
    - POST /api/harvests/ - Create new harvest
    - GET /api/harvests/{id}/ - Get single harvest
    - PUT /api/harvests/{id}/ - Full update
    - PATCH /api/harvests/{id}/ - Partial update
    - DELETE /api/harvests/{id}/ - Delete harvest
    """
    queryset = Harvests.objects.all()
    serializer_class = HarvestsSerializer


class BlockViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Block management

    Endpoints:
    - GET /api/blocks/ - List all blocks
    - POST /api/blocks/ - Create new block
    - GET /api/blocks/{block_id}/ - Get single block
    - PUT /api/blocks/{block_id}/ - Full update
    - PATCH /api/blocks/{block_id}/ - Partial update
    - DELETE /api/blocks/{block_id}/ - Delete block
    """
    queryset = Block.objects.all()
    serializer_class = BlockSerializer
    lookup_field = 'block_id'

    def perform_create(self, serializer):
        """
        Create new block and associate with current user if needed
        """
        serializer.save()
