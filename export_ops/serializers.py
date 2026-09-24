from rest_framework import serializers
from .models import Warehouse, InventoryLot, DispatchNote, ExportTraceRecord, ExportComplianceDocument


class WarehouseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Warehouse
        fields = '__all__'


class InventoryLotSerializer(serializers.ModelSerializer):
    warehouse_name = serializers.CharField(source='warehouse.name', read_only=True)

    class Meta:
        model = InventoryLot
        fields = '__all__'


class DispatchNoteSerializer(serializers.ModelSerializer):
    lot_id_display = serializers.CharField(source='lot.lot_id', read_only=True)
    sale_display = serializers.CharField(source='sale.get_customer_name', read_only=True)

    class Meta:
        model = DispatchNote
        fields = '__all__'


class ExportComplianceDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExportComplianceDocument
        fields = '__all__'
        read_only_fields = ['uploaded_at', 'uploaded_by']


class ExportTraceRecordSerializer(serializers.ModelSerializer):
    lot_id_display = serializers.CharField(source='lot.lot_id', read_only=True)
    dispatch_id_display = serializers.CharField(source='dispatch.dispatch_id', read_only=True)

    class Meta:
        model = ExportTraceRecord
        fields = '__all__'
