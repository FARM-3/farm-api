from rest_framework import serializers
from .models import Harvests, Block
from financialmanagement.models import Staff


class BlockSerializer(serializers.ModelSerializer):
    """Serializer for Block model"""

    class Meta:
        model = Block
        fields = [
            'block_id',
            'no_of_trees',
            'date_planted',
            'type_of_coffee',
            'source_of_seedling',
            'type_of_seedling',
            'age_of_seedling',
            'fertilizers',
            'fertilizer_names',
            'use_pesticides',
            'pesticides_list',
            'standard_practices',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['created_at', 'updated_at']


class HarvestsSerializer(serializers.ModelSerializer):
    """
    Serializer for Harvests model
    Handles serialization/deserialization of harvest data
    Supports offline-first: accepts frontend-generated harvest_id
    """

    # COMMENTED OUT: This field expects get_paid_by_name() method which requires paid_by to be a ForeignKey
    # Read-only field to display staff member's full name
    # paid_by_name = serializers.SerializerMethodField()

    # Explicitly define harvest_id as writable field (model has editable=False, but we override for offline-first)
    harvest_id = serializers.CharField(max_length=20, required=False, allow_blank=False)

    class Meta:
        model = Harvests
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']

    # COMMENTED OUT: This method requires paid_by to be a ForeignKey to Staff model
    # Currently paid_by is a CharField, so this would cause AttributeError
    # def get_paid_by_name(self, obj):
    #     """
    #     Return the full name of the staff member who processed payment
    #     """
    #     if obj.paid_by:
    #         return obj.paid_by.get_full_name()
    #     return None

    def validate_harvest_id(self, value):
        """
        Validate harvest_id format and requirement
        harvest_id must be provided by frontend (offline-first approach)
        """
        if not value or value.strip() == '':
            raise serializers.ValidationError("harvest_id is required and cannot be empty")
        return value

    def validate_weight_on_delivery(self, value):
        """
        Ensure weight is positive
        """
        if value <= 0:
            raise serializers.ValidationError("Weight must be greater than zero")
        return value

    def validate_amount_paid(self, value):
        """
        Ensure amount paid is non-negative
        """
        if value < 0:
            raise serializers.ValidationError("Amount paid cannot be negative")
        return value

    def validate_date_of_delivery(self, value):
        """
        Ensure date of delivery is not in the future
        """
        from django.utils import timezone
        if value > timezone.now().date():
            raise serializers.ValidationError("Date of delivery cannot be in the future")
        return value

    # COMMENTED OUT: This validation requires paid_by to be a ForeignKey to Staff model
    # Currently paid_by is a CharField, so this would cause AttributeError
    # def validate_paid_by(self, value):
    #     """
    #     Ensure the staff member is active
    #     """
    #     if not value.is_active:
    #         raise serializers.ValidationError(
    #             f"Staff member {value.get_full_name()} is not currently active"
    #         )
    #     return value

    def to_representation(self, instance):
        """
        Customize the output representation
        Add additional context to the response
        """
        data = super().to_representation(instance)

        # COMMENTED OUT: This line calls get_paid_by_name() which is commented out above
        # Add paid_by_name to the response
        # data['paid_by_name'] = self.get_paid_by_name(instance)

        # Format weight to always show 2 decimal places
        if 'weight_on_delivery' in data:
            data['weight_on_delivery'] = f"{float(data['weight_on_delivery']):.2f}"

        return data


class HarvestsListSerializer(serializers.ModelSerializer):
    """
    Simplified serializer for listing harvests
    Shows only essential information for list views
    """
    # COMMENTED OUT: This field expects get_paid_by_name() method which requires paid_by to be a ForeignKey
    # paid_by_name = serializers.SerializerMethodField()

    class Meta:
        model = Harvests
        fields = [
            'harvest_id',
            'worker_name',
            'block_id',
            'weight_on_delivery',
            'date_of_delivery',
            'amount_paid',
            'paid_by'
        ]

    # COMMENTED OUT: This method requires paid_by to be a ForeignKey to Staff model
    # Currently paid_by is a CharField, so this would cause AttributeError
    # def get_paid_by_name(self, obj):
    #     """
    #     Return the staff member's full name
    #     """
    #     if obj.paid_by:
    #         return obj.paid_by.get_full_name()
    #     return None


class HarvestsSummarySerializer(serializers.Serializer):
    """
    Serializer for harvest summary statistics
    Used for aggregated data endpoints
    """
    total_harvests = serializers.IntegerField()
    total_weight = serializers.DecimalField(max_digits=10, decimal_places=2)
    total_amount_paid = serializers.DecimalField(max_digits=10, decimal_places=2)
    average_weight = serializers.DecimalField(max_digits=10, decimal_places=2)
    date_range = serializers.DictField()
