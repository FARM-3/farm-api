from rest_framework import serializers
from .models import Fermenting,Washing,Sundrying

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
            'date',
            'weight_before',
            'weight_after',
            'weight_loss',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']     
    

class SundryingSerializer(serializers.ModelSerializer):
    """
    Serializer for Sundrying model
    Includes weather and moisture tracking
    """
    weight_loss = serializers.ReadOnlyField()
    
    class Meta:
        model = Sundrying
        fields = [
            'id',
            'processing_id',
            'name',
            'grade',
            'weather',
            'temperature',
            'moisture_content',
            'date',
            'weight_before',
            'weight_after',
            'weight_loss',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def validate(self, data):
        """
        Validate weight and moisture content
        """
        # Check weight consistency
        if 'weight_before' in data and 'weight_after' in data:
            if data['weight_after'] > data['weight_before']:
                raise serializers.ValidationError(
                    "Weight after sundrying cannot exceed weight before"
                )
        
        # Moisture content should be within reasonable range
        if 'moisture_content' in data:
            if data['moisture_content'] < 0 or data['moisture_content'] > 100:
                raise serializers.ValidationError(
                    "Moisture content must be between 0 and 100%"
                )
        
        return data


