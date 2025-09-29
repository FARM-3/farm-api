from rest_framework import serializers
from .models import Fermenting, Washing, Sundrying, Bagging


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
            'date',
            'weight_before',
            'weight_after',
            'weight_loss',  # Calculated field
            'created_at',
            'updated_at'
        ]
        # Make created_at and updated_at read-only (auto-generated)
        read_only_fields = ['created_at', 'updated_at']
    
