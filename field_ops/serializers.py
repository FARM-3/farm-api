from rest_framework import serializers
from .models import BlockActivityLog, SurveillanceReport


class BlockActivityLogSerializer(serializers.ModelSerializer):
    photo_url = serializers.SerializerMethodField()
    has_photo = serializers.SerializerMethodField()
    reported_by_display = serializers.SerializerMethodField()

    class Meta:
        model = BlockActivityLog
        fields = [
            'id', 'log_id', 'activity_scope', 'location_label', 'block_id', 'log_type', 'title', 'description',
            'practices', 'input_type', 'input_name', 'quantity', 'unit',
            'activity_date', 'weather_conditions', 'gps_coordinates', 'photo', 'photo_url', 'has_photo',
            'reported_by', 'reported_by_name', 'reported_by_display', 'harvest_id', 'notes',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_photo_url(self, obj):
        if not obj.photo:
            return ''
        request = self.context.get('request')
        if request:
            return request.build_absolute_uri(f'/api/field-ops/block-activities/{obj.pk}/photo/')
        return f'/api/field-ops/block-activities/{obj.pk}/photo/'

    def get_has_photo(self, obj):
        return bool(obj.photo)

    def get_reported_by_display(self, obj):
        if obj.reported_by_name:
            return obj.reported_by_name
        if obj.reported_by:
            return getattr(obj.reported_by, 'full_name', None) or str(obj.reported_by.phone)
        return ''


class SurveillanceReportSerializer(serializers.ModelSerializer):
    photo_url = serializers.SerializerMethodField()
    has_photo = serializers.SerializerMethodField()
    reported_by_display = serializers.SerializerMethodField()

    class Meta:
        model = SurveillanceReport
        fields = [
            'id', 'report_id', 'block_id', 'title', 'description', 'severity', 'issue_type',
            'weather_conditions', 'location', 'gps_coordinates', 'photo', 'photo_url', 'has_photo',
            'reported_by', 'reported_by_name', 'reported_by_display', 'status',
            'resolution_notes', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_photo_url(self, obj):
        if not obj.photo:
            return ''
        request = self.context.get('request')
        if request:
            return request.build_absolute_uri(f'/api/field-ops/surveillance/{obj.pk}/photo/')
        return f'/api/field-ops/surveillance/{obj.pk}/photo/'

    def get_has_photo(self, obj):
        return bool(obj.photo)

    def get_reported_by_display(self, obj):
        if obj.reported_by_name:
            return obj.reported_by_name
        if obj.reported_by:
            return getattr(obj.reported_by, 'full_name', None) or str(obj.reported_by.phone)
        return ''
