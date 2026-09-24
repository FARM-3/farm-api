from django.shortcuts import render
from django.views.generic import ListView
from .models import Harvests, Block
from .serializers import HarvestsSerializer, BlockSerializer
from io import BytesIO

from django.http import HttpResponse
from rest_framework import viewsets, status
from rest_framework.decorators import action
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

    @staticmethod
    def _block_qr_payload(block_id):
        return f'BLOCK:{block_id}'

    @action(detail=True, methods=['get'], url_path='qr-image')
    def qr_image(self, request, block_id=None):
        """PNG QR code for block scan payload (BLOCK:{block_id})."""
        import qrcode

        block = self.get_object()
        payload = self._block_qr_payload(block.block_id)
        img = qrcode.make(payload)
        buf = BytesIO()
        img.save(buf, format='PNG')
        return HttpResponse(buf.getvalue(), content_type='image/png')

    @action(detail=True, methods=['get'], url_path='profile')
    def profile(self, request, block_id=None):
        """Full block profile — same payload as scanning the block QR."""
        from processing.trace_service import trace_block

        block = self.get_object()
        data = trace_block(block.block_id)
        if not data:
            return Response({'detail': 'Block profile unavailable.'}, status=status.HTTP_404_NOT_FOUND)
        return Response(data)
