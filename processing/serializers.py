from rest_framework import serializers
from .models import Fermenting, Washing, Drying, Bagging

class FermentingSerializer(serializers.ModelSerializer):
    """
    Serializer for Fermenting model
    Includes all fields plus the calculated weight_loss property
    """
    # Read-only field that calculates weight loss automatically
    weight_loss = serializers.ReadOnlyField()
    
    class Meta:
        model = Fermenting
        # List all fields to include in the API response
        fields = [
            'id',  # Django auto-generated primary key
            'processing_id',
            'days',
            'name',
            'grade',
            'cherry_colour',
            'date',
            'weight_before',
            'weight_after',
            'weight_loss',  # Calculated field
            'created_at',
            'updated_at'
        ]
        # Make created_at and updated_at read-only (auto-generated)
        read_only_fields = ['created_at', 'updated_at']

class WashingSerializer(serializers.ModelSerializer):
    """
    Serializer for Washing model
    """
    weight_loss = serializers.ReadOnlyField()
    
    class Meta:
        model = Washing
        fields = [
            'id',
            'processing_id',
            'name',
            'grade',
            'cherry_colour',
            'date',
            'weight_before',
            'weight_after',
            'weight_loss',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']     
    

class DryingSerializer(serializers.ModelSerializer):
    """
    Serializer for Drying model
    Tracks daily drying progress with auto-calculated fields
    All auto-generated fields are read-only
    """

    class Meta:
        model = Drying
        fields = [
            'id',
            # User-provided fields
            'processing_id',
            'lot_id',
            'date',
            'weather_condition',
            'moisture_content',
            'weight',
            'moisture_before',
            'weight_before',
            # Auto-generated fields (read-only)
            'processing_type',
            'type_of_coffee',
            'days',
            'moisture_deviation',
            'rate_of_drying',
            'rate_of_weightloss',
            'outturn',
            'outturn_deviation',
            # Metadata
            'created_at',
            'updated_at'
        ]
        read_only_fields = [
            'lot_id',
            'processing_type',
            'type_of_coffee',
            'days',
            'moisture_deviation',
            'rate_of_drying',
            'rate_of_weightloss',
            'outturn',
            'outturn_deviation',
            'created_at',
            'updated_at'
        ]

    def validate_moisture_content(self, value):
        """
        Validate that moisture content is in valid range
        """
        if value < 0 or value > 100:
            raise serializers.ValidationError(
                "Moisture content must be between 0 and 100%"
            )
        return value
    
class BaggingSerializer(serializers.ModelSerializer):
    """
    Serializer for Bagging model (final stage)
    """
    class Meta:
        model = Bagging
        fields = [
            'id',
            'processing_id',
            'name',
            'grade',
            'moisture_content',
            'date',
            'weight',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def validate_moisture_content(self, value):
        """
        Validate that moisture content is in acceptable range for bagging
        Typically, coffee should be dried to 10-12% moisture before bagging
        """
        if value > 15:
            raise serializers.ValidationError(
                "Moisture content too high for bagging (should be ≤15%)"
            )
        if value < 8:
            raise serializers.ValidationError(
                "Moisture content too low (should be ≥8%)"
            )
        return value


