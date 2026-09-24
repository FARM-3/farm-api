from django.http import HttpResponse
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.response import Response
from django.utils import timezone

from processing.models import Bagging
from .models import (
    Warehouse, InventoryLot, DispatchNote, ExportTraceRecord, ExportComplianceDocument,
)
from .serializers import (
    WarehouseSerializer, InventoryLotSerializer,
    DispatchNoteSerializer, ExportTraceRecordSerializer,
    ExportComplianceDocumentSerializer,
)
from .services import build_eudr_dossier, sync_inventory_from_bagging


class WarehouseViewSet(viewsets.ModelViewSet):
    queryset = Warehouse.objects.all()
    serializer_class = WarehouseSerializer


class InventoryLotViewSet(viewsets.ModelViewSet):
    queryset = InventoryLot.objects.select_related('warehouse').all()
    serializer_class = InventoryLotSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        status_filter = self.request.query_params.get('status')
        warehouse = self.request.query_params.get('warehouse')
        grade = self.request.query_params.get('grade')
        coffee_type = self.request.query_params.get('coffee_type')
        if status_filter:
            qs = qs.filter(status=status_filter)
        if warehouse:
            qs = qs.filter(warehouse_id=warehouse)
        if grade:
            qs = qs.filter(grade=grade)
        if coffee_type:
            qs = qs.filter(coffee_type=coffee_type)
        return qs

    @action(detail=False, methods=['post'], url_path='sync-from-bagging')
    def sync_from_bagging(self, request):
        """Backfill inventory from all bagging records."""
        created, updated = 0, 0
        seen = set()
        for b in Bagging.objects.order_by('lot_id', 'date'):
            key = b.lot_id
            if key in seen:
                sync_inventory_from_bagging(b)
                updated += 1
            else:
                seen.add(key)
                before = InventoryLot.objects.filter(lot_id=b.lot_id).exists()
                sync_inventory_from_bagging(b)
                if before:
                    updated += 1
                else:
                    created += 1
        return Response({'created': created, 'updated': updated, 'lots': InventoryLot.objects.count()})


class DispatchNoteViewSet(viewsets.ModelViewSet):
    queryset = DispatchNote.objects.select_related('lot', 'sale').all()
    serializer_class = DispatchNoteSerializer

    def perform_create(self, serializer):
        dispatch = serializer.save(created_by=self.request.user if self.request.user.is_authenticated else None)
        lot = dispatch.lot
        qty = dispatch.quantity_kg or 0
        bags = dispatch.bags or 0

        if qty and lot.total_kg and qty < lot.total_kg:
            lot.total_kg = lot.total_kg - qty
            lot.bags = max(0, (lot.bags or 0) - bags)
            lot.status = 'in_stock'
        else:
            lot.status = 'dispatched'
        lot.save(update_fields=['total_kg', 'bags', 'status', 'updated_at'])

    @action(detail=True, methods=['get'], url_path='pdf')
    def pdf_note(self, request, pk=None):
        """Printable HTML dispatch note (save as PDF from browser)."""
        dispatch = self.get_object()
        lot = dispatch.lot
        html = f"""<!DOCTYPE html><html><head><meta charset="utf-8"><title>{dispatch.dispatch_id}</title>
        <style>body{{font-family:Arial,sans-serif;padding:32px;color:#222}} h1{{color:#4A3423}}
        table{{width:100%;border-collapse:collapse;margin-top:16px}} td,th{{border:1px solid #ddd;padding:8px;text-align:left}}
        </style></head><body>
        <h1>Dispatch Note — {dispatch.dispatch_id}</h1>
        <p><strong>Date:</strong> {dispatch.dispatch_date}</p>
        <table>
        <tr><th>Lot</th><td>{lot.lot_id if lot else '—'}</td></tr>
        <tr><th>Harvest</th><td>{lot.source_harvest_id if lot else '—'}</td></tr>
        <tr><th>Buyer</th><td>{dispatch.buyer_name}</td></tr>
        <tr><th>Contact</th><td>{dispatch.buyer_contact or '—'}</td></tr>
        <tr><th>Quantity</th><td>{dispatch.quantity_kg} kg / {dispatch.bags} bags</td></tr>
        <tr><th>Vehicle</th><td>{dispatch.vehicle or '—'}</td></tr>
        <tr><th>Driver</th><td>{dispatch.driver or '—'}</td></tr>
        <tr><th>Destination</th><td>{dispatch.destination or '—'}</td></tr>
        <tr><th>Status</th><td>{dispatch.status}</td></tr>
        <tr><th>Proof notes</th><td>{dispatch.proof_notes or '—'}</td></tr>
        </table>
        <p style="margin-top:32px">Signature: _________________________</p>
        </body></html>"""
        return HttpResponse(html, content_type='text/html')


class ExportComplianceDocumentViewSet(viewsets.ModelViewSet):
    queryset = ExportComplianceDocument.objects.all()
    serializer_class = ExportComplianceDocumentSerializer
    parser_classes = [MultiPartParser, FormParser]

    def get_queryset(self):
        qs = super().get_queryset()
        harvest_id = self.request.query_params.get('harvest_id')
        if harvest_id:
            qs = qs.filter(harvest_id=harvest_id)
        return qs

    def perform_create(self, serializer):
        serializer.save(uploaded_by=self.request.user if self.request.user.is_authenticated else None)


class ExportTraceRecordViewSet(viewsets.ModelViewSet):
    queryset = ExportTraceRecord.objects.select_related('lot', 'dispatch').all()
    serializer_class = ExportTraceRecordSerializer

    @action(detail=False, methods=['post'], url_path='from-harvest')
    def from_harvest(self, request):
        from processing.trace_service import trace_harvest
        harvest_id = request.data.get('harvest_id')
        if not harvest_id:
            return Response({'error': 'harvest_id required'}, status=status.HTTP_400_BAD_REQUEST)
        trace = trace_harvest(harvest_id)
        if not trace:
            return Response({'detail': 'Harvest not found'}, status=status.HTTP_404_NOT_FOUND)
        record_id = f'TR-{timezone.now().strftime("%Y%m%d")}-{harvest_id[:8]}'
        source = trace.get('source') or {}
        loss = trace.get('loss_summary') or {}
        record, _ = ExportTraceRecord.objects.update_or_create(
            harvest_id=harvest_id,
            defaults={
                'record_id': record_id,
                'supplier_name': trace.get('farmer_name') or source.get('farmer_name', ''),
                'origin_gps': source.get('gps_coordinates', ''),
                'coffee_type': source.get('coffee_type', ''),
                'total_kg': loss.get('output_kg'),
                'trace_data': trace,
                'compliance_status': 'ready',
                'created_by': request.user if request.user.is_authenticated else None,
            },
        )
        return Response(ExportTraceRecordSerializer(record).data)

    @action(detail=False, methods=['get', 'post'], url_path='eudr-dossier')
    def eudr_dossier(self, request):
        """Prototype EUDR due-diligence pack — not certified EU DDS."""
        harvest_id = request.data.get('harvest_id') if request.method == 'POST' else None
        harvest_id = harvest_id or request.query_params.get('harvest_id')
        if not harvest_id:
            return Response({'error': 'harvest_id required'}, status=status.HTTP_400_BAD_REQUEST)
        dossier = build_eudr_dossier(harvest_id)
        if not dossier:
            return Response({'detail': 'Harvest not found'}, status=status.HTTP_404_NOT_FOUND)
        return Response(dossier)
