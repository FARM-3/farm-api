import json
import mimetypes

from django.http import FileResponse, Http404
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.response import Response

from .models import BlockActivityLog, SurveillanceReport
from .serializers import BlockActivityLogSerializer, SurveillanceReportSerializer


def _parse_json_list(value):
    if value is None or value == '':
        return []
    if isinstance(value, list):
        return value
    if isinstance(value, str):
        try:
            parsed = json.loads(value)
            return parsed if isinstance(parsed, list) else [value]
        except json.JSONDecodeError:
            return [v.strip() for v in value.split(',') if v.strip()]
    return []


class BlockActivityLogViewSet(viewsets.ModelViewSet):
    queryset = BlockActivityLog.objects.all()
    serializer_class = BlockActivityLogSerializer
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    filterset_fields = ['block_id', 'log_type', 'harvest_id']

    def get_queryset(self):
        qs = super().get_queryset()
        block_id = self.request.query_params.get('block_id')
        if block_id:
            qs = qs.filter(block_id=block_id)
        activity_scope = self.request.query_params.get('activity_scope')
        if activity_scope:
            qs = qs.filter(activity_scope=activity_scope)
        location = self.request.query_params.get('location_label')
        if location:
            qs = qs.filter(location_label__icontains=location)
        harvest_id = self.request.query_params.get('harvest_id')
        if harvest_id:
            qs = qs.filter(harvest_id=harvest_id)
        log_type = self.request.query_params.get('log_type')
        if log_type:
            qs = qs.filter(log_type=log_type)
        date_from = self.request.query_params.get('date_from')
        if date_from:
            qs = qs.filter(activity_date__gte=date_from)
        date_to = self.request.query_params.get('date_to')
        if date_to:
            qs = qs.filter(activity_date__lte=date_to)
        return qs.order_by('-activity_date', '-created_at')

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        ctx['request'] = self.request
        return ctx

    def perform_create(self, serializer):
        user = self.request.user if self.request.user.is_authenticated else None
        name = self.request.data.get('reported_by_name', '')
        if user and not name:
            name = getattr(user, 'full_name', '') or str(getattr(user, 'phone', ''))
        serializer.save(reported_by=user, reported_by_name=name)

    def create(self, request, *args, **kwargs):
        data = request.data.copy()
        if 'practices' in data:
            data['practices'] = _parse_json_list(data.get('practices'))
        if 'weather_conditions' in data:
            data['weather_conditions'] = _parse_json_list(data.get('weather_conditions'))
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=201, headers=headers)

    @action(detail=True, methods=['get'], url_path='photo')
    def photo(self, request, pk=None):
        log = self.get_object()
        if not log.photo:
            raise Http404('No photo')
        content_type, _ = mimetypes.guess_type(log.photo.name)
        return FileResponse(log.photo.open('rb'), content_type=content_type or 'image/jpeg')


class SurveillanceReportViewSet(viewsets.ModelViewSet):
    queryset = SurveillanceReport.objects.all()
    serializer_class = SurveillanceReportSerializer
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    filterset_fields = ['block_id', 'severity', 'status', 'issue_type']

    def get_queryset(self):
        qs = super().get_queryset()
        status = self.request.query_params.get('status')
        if status:
            qs = qs.filter(status=status)
        block_id = self.request.query_params.get('block_id')
        if block_id:
            qs = qs.filter(block_id=block_id)
        severity = self.request.query_params.get('severity')
        if severity:
            qs = qs.filter(severity=severity)
        issue_type = self.request.query_params.get('issue_type')
        if issue_type:
            qs = qs.filter(issue_type=issue_type)
        date_from = self.request.query_params.get('date_from')
        if date_from:
            qs = qs.filter(created_at__date__gte=date_from)
        date_to = self.request.query_params.get('date_to')
        if date_to:
            qs = qs.filter(created_at__date__lte=date_to)
        return qs.order_by('-created_at')

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        ctx['request'] = self.request
        return ctx

    def perform_create(self, serializer):
        user = self.request.user if self.request.user.is_authenticated else None
        name = self.request.data.get('reported_by_name', '')
        if user and not name:
            name = getattr(user, 'full_name', '') or str(getattr(user, 'phone', ''))
        serializer.save(reported_by=user, reported_by_name=name)

    def create(self, request, *args, **kwargs):
        data = request.data.copy()
        if 'weather_conditions' in data:
            data['weather_conditions'] = _parse_json_list(data.get('weather_conditions'))
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=201, headers=headers)

    @action(detail=True, methods=['get'], url_path='photo')
    def photo(self, request, pk=None):
        report = self.get_object()
        if not report.photo:
            raise Http404('No photo')
        content_type, _ = mimetypes.guess_type(report.photo.name)
        return FileResponse(report.photo.open('rb'), content_type=content_type or 'image/jpeg')
