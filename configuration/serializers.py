from rest_framework import serializers
from .models import LookupOption, ConfigCategory, CoffeeType, CoffeeSubType, FarmAsset, FarmDocument, TrainingRecord


class LookupOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = LookupOption
        fields = ['id', 'category', 'value', 'label', 'sort_order', 'is_active']


class CoffeeSubTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = CoffeeSubType
        fields = ['id', 'name', 'code', 'sort_order', 'is_active']


class CoffeeTypeSerializer(serializers.ModelSerializer):
    sub_types = CoffeeSubTypeSerializer(many=True, read_only=True)

    class Meta:
        model = CoffeeType
        fields = ['id', 'name', 'description', 'is_active', 'sort_order', 'sub_types', 'created_at']


class CoffeeTypeWriteSerializer(serializers.ModelSerializer):
    sub_types = CoffeeSubTypeSerializer(many=True, required=False)

    class Meta:
        model = CoffeeType
        fields = ['id', 'name', 'description', 'is_active', 'sort_order', 'sub_types']

    def create(self, validated_data):
        sub_types_data = validated_data.pop('sub_types', [])
        coffee_type = CoffeeType.objects.create(**validated_data)
        for idx, st in enumerate(sub_types_data):
            CoffeeSubType.objects.create(coffee_type=coffee_type, sort_order=idx, **st)
        return coffee_type

    def update(self, instance, validated_data):
        sub_types_data = validated_data.pop('sub_types', None)
        for attr, val in validated_data.items():
            setattr(instance, attr, val)
        instance.save()
        if sub_types_data is not None:
            instance.sub_types.all().delete()
            for idx, st in enumerate(sub_types_data):
                CoffeeSubType.objects.create(coffee_type=instance, sort_order=idx, **st)
        return instance


class FarmAssetSerializer(serializers.ModelSerializer):
    class Meta:
        model = FarmAsset
        fields = '__all__'


class FarmDocumentSerializer(serializers.ModelSerializer):
    file_url = serializers.SerializerMethodField()
    file_name = serializers.SerializerMethodField()

    class Meta:
        model = FarmDocument
        fields = [
            'id', 'doc_id', 'title', 'doc_type', 'issuer', 'reference_no',
            'issue_date', 'expiry_date', 'file', 'file_url', 'file_name',
            'notes', 'status', 'created_at',
        ]

    def get_file_url(self, obj):
        if obj.file:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(f'/api/config/documents/{obj.pk}/file/')
            return f'/api/config/documents/{obj.pk}/file/'
        return obj.file_url or ''

    def get_file_name(self, obj):
        if obj.file:
            return obj.file.name.split('/')[-1]
        return ''


class TrainingRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrainingRecord
        fields = '__all__'


class LookupOptionBulkSerializer(serializers.Serializer):
    """Replace all options for a category in one request."""

    category = serializers.ChoiceField(choices=ConfigCategory.choices)
    options = serializers.ListField(
        child=serializers.CharField(max_length=120),
        allow_empty=True,
    )
