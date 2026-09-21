import mimetypes

from django.http import FileResponse, Http404
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import LookupOption, ConfigCategory, CoffeeType, FarmAsset, FarmDocument, TrainingRecord
from .serializers import (
    LookupOptionSerializer, LookupOptionBulkSerializer,
    CoffeeTypeSerializer, CoffeeTypeWriteSerializer, FarmAssetSerializer,
    FarmDocumentSerializer, TrainingRecordSerializer,
)


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
            grouped.setdefault(opt.category, []).append(opt.display_label)
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
