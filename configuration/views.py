import mimetypes

from django.http import FileResponse, Http404
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import (
    LookupOption, ConfigCategory, CoffeeType, FertilizerType,
    FarmAsset, FarmDocument, TrainingRecord,
)
from .serializers import (
    LookupOptionSerializer, LookupOptionBulkSerializer,
    CoffeeTypeSerializer, CoffeeTypeWriteSerializer,
    FertilizerTypeSerializer, FertilizerTypeWriteSerializer,
    FarmAssetSerializer, FarmDocumentSerializer, TrainingRecordSerializer,
)
from .services import sync_fertilizer_lookups_from_types


class LookupOptionViewSet(viewsets.ModelViewSet):
    queryset = LookupOption.objects.all()
    serializer_class = LookupOptionSerializer
    filterset_fields = ['category', 'is_active']

    def get_queryset(self):
        qs = super().get_queryset()
        category = self.request.query_params.get('category')
        if category:
            qs = qs.filter(category=category)
        if self.action == 'list' and self.request.query_params.get('active_only') == '1':
            qs = qs.filter(is_active=True)
        return qs

    @action(detail=False, methods=['get'], url_path='grouped')
    def grouped(self, request):
        """Return all active options grouped by category for form pickers."""
        options = LookupOption.objects.filter(is_active=True).order_by('category', 'sort_order', 'value')
        grouped = {choice.value: [] for choice in ConfigCategory}
        for opt in options:
            if opt.category == ConfigCategory.SALE_ITEM:
                grouped.setdefault(opt.category, []).append({
                    'name': opt.display_label,
                    'default_rate': str(opt.default_rate) if opt.default_rate is not None else '',
                    'unit_label': opt.unit_label or 'kg',
                })
            else:
                grouped.setdefault(opt.category, []).append(opt.display_label)

        fert_types = FertilizerType.objects.filter(is_active=True).prefetch_related('sub_types').order_by('sort_order', 'name')
        grouped['fertilizer_types'] = FertilizerTypeSerializer(fert_types, many=True).data
        for ft in fert_types:
            key = ft.name.lower()
            if key in ('organic', 'inorganic', 'mixed'):
                grouped[f'fertilizer_{key}'] = [
                    st.name for st in ft.sub_types.filter(is_active=True).order_by('sort_order', 'name')
                ]

        return Response(grouped)

    @action(detail=False, methods=['post'], url_path='bulk-replace')
    def bulk_replace(self, request):
        """Replace all options for a category (admin settings UI)."""
        serializer = LookupOptionBulkSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        category = serializer.validated_data['category']
        values = serializer.validated_data['options']

        LookupOption.objects.filter(category=category).delete()
        created = []
        for idx, val in enumerate(values):
            val = val.strip()
            if not val:
                continue
            created.append(
                LookupOption.objects.create(
                    category=category,
                    value=val,
                    label=val,
                    sort_order=idx,
                    is_active=True,
                )
            )
        return Response(
            LookupOptionSerializer(created, many=True).data,
            status=status.HTTP_200_OK,
        )


class CoffeeTypeViewSet(viewsets.ModelViewSet):
    queryset = CoffeeType.objects.prefetch_related('sub_types').all()

    def get_serializer_class(self):
        if self.action in ('create', 'update', 'partial_update'):
            return CoffeeTypeWriteSerializer
        return CoffeeTypeSerializer


class FertilizerTypeViewSet(viewsets.ModelViewSet):
    queryset = FertilizerType.objects.prefetch_related('sub_types').all()

    def get_queryset(self):
        qs = super().get_queryset()
        if self.action in ('list', 'retrieve') and self.request.query_params.get('active_only') == '1':
            qs = qs.filter(is_active=True)
        return qs.order_by('sort_order', 'name')

    def get_serializer_class(self):
        if self.action in ('create', 'update', 'partial_update'):
            return FertilizerTypeWriteSerializer
        return FertilizerTypeSerializer

    def perform_create(self, serializer):
        serializer.save()
        sync_fertilizer_lookups_from_types()

    def perform_update(self, serializer):
        serializer.save()
        sync_fertilizer_lookups_from_types()

    def perform_destroy(self, instance):
        instance.delete()
        sync_fertilizer_lookups_from_types()


class FarmAssetViewSet(viewsets.ModelViewSet):
    queryset = FarmAsset.objects.all()
    serializer_class = FarmAssetSerializer


class FarmDocumentViewSet(viewsets.ModelViewSet):
    queryset = FarmDocument.objects.all()
    serializer_class = FarmDocumentSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

    @action(detail=True, methods=['get'], url_path='file')
    def file(self, request, pk=None):
        """Serve uploaded document — works when DEBUG=False on Render."""
        doc = self.get_object()
        if not doc.file:
            raise Http404('No file attached')
        content_type, _ = mimetypes.guess_type(doc.file.name)
        return FileResponse(doc.file.open('rb'), content_type=content_type or 'application/octet-stream')


class TrainingRecordViewSet(viewsets.ModelViewSet):
    queryset = TrainingRecord.objects.all()
    serializer_class = TrainingRecordSerializer
