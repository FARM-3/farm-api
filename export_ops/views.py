from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from processing.models import Bagging
from .models import Warehouse, InventoryLot, DispatchNote, ExportTraceRecord
from .serializers import (
    WarehouseSerializer, InventoryLotSerializer,
    DispatchNoteSerializer, ExportTraceRecordSerializer,
)


class WarehouseViewSet(viewsets.ModelViewSet):
    queryset = Warehouse.objects.all()
    serializer_class = WarehouseSerializer


class InventoryLotViewSet(viewsets.ModelViewSet):
    queryset = InventoryLot.objects.select_related('warehouse').all()
    serializer_class = InventoryLotSerializer

    @action(detail=False, methods=['post'], url_path='sync-from-bagging')
    def sync_from_bagging(self, request):
        """Create/update inventory lots from bagging records."""
        baggings = Bagging.objects.all()
        created, updated = 0, 0
        for b in baggings:
            lot_id = b.lot_id or f'LOT-{b.id}'
            defaults = {
                'total_kg': b.weight or 0,
                'bags': b.no_of_bags or 0,
                'moisture_pct': b.moisture_content,
                'batch_id': getattr(b, 'batch_id', '') or '',
            }
            lot, was_created = InventoryLot.objects.update_or_create(
                lot_id=lot_id, defaults=defaults,
            )
            if was_created:
                created += 1
            else:
                updated += 1
        return Response({'created': created, 'updated': updated, 'total': created + updated})


class DispatchNoteViewSet(viewsets.ModelViewSet):
    queryset = DispatchNote.objects.select_related('lot').all()
    serializer_class = DispatchNoteSerializer

    def perform_create(self, serializer):
        dispatch = serializer.save(created_by=self.request.user if self.request.user.is_authenticated else None)
        lot = dispatch.lot
        lot.status = 'dispatched'
        lot.save(update_fields=['status', 'updated_at'])


class ExportTraceRecordViewSet(viewsets.ModelViewSet):
    queryset = ExportTraceRecord.objects.select_related('lot', 'dispatch').all()
    serializer_class = ExportTraceRecordSerializer

    @action(detail=False, methods=['post'], url_path='from-harvest')
    def from_harvest(self, request):
        """Build a trace record from harvest trace API data."""
        from processing.trace_service import trace_harvest
        harvest_id = request.data.get('harvest_id')
        if not harvest_id:
            return Response({'error': 'harvest_id required'}, status=status.HTTP_400_BAD_REQUEST)
        trace = trace_harvest(harvest_id)
        if not trace:
            return Response({'detail': 'Harvest not found'}, status=status.HTTP_404_NOT_FOUND)
        record_id = f'TR-{timezone.now().strftime("%Y%m%d")}-{harvest_id[:8]}'
        record, _ = ExportTraceRecord.objects.update_or_create(
            harvest_id=harvest_id,
            defaults={
                'record_id': record_id,
                'supplier_name': (trace.get('source') or {}).get('name', ''),
                'origin_gps': (trace.get('source') or {}).get('gps_coordinates', ''),
                'coffee_type': (trace.get('source') or {}).get('coffee_type', ''),
                'total_kg': ((trace.get('stages') or {}).get('bagging') or {}).get('weight'),
                'trace_data': trace,
                'compliance_status': 'ready',
                'created_by': request.user if request.user.is_authenticated else None,
            },
        )
        return Response(ExportTraceRecordSerializer(record).data)
