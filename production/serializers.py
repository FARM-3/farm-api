from rest_framework import serializers
<<<<<<< HEAD
=======
<<<<<<< HEAD
from .models import Harvests






class HarvestsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Harvests
        fields = '__all__'
=======
>>>>>>> 447798b3a9fca5fed9ccfbdbfbdeb8a9db50aeb0
from .models import Harvests, Block
from rest_framework import serializers



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
            'use_pesticides',
            'pesticides_list',
            'standard_practices',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['created_at', 'updated_at']


from rest_framework import serializers
from .models import Harvests
from financialmanagement.models import Staff

class HarvestsSerializer(serializers.ModelSerializer):
    """
    Serializer for Harvests model
    Handles serialization/deserialization of harvest data
    """
    
    # Read-only field to display staff member's full name
    paid_by_name = serializers.SerializerMethodField()
    
    # Read-only field - harvest_id is auto-generated
    harvest_id = serializers.CharField(read_only=True)
    
    class Meta:
        model = Harvests
        fields = '__all__'
        read_only_fields = ['harvest_id', 'created_at', 'updated_at']
    
    def get_paid_by_name(self, obj):
        """
        Return the full name of the staff member who processed payment
        """
        if obj.paid_by:
            return obj.paid_by.get_full_name()
        return None
    
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
    
    def validate_paid_by(self, value):
        """
        Ensure the staff member is active
        """
        if not value.is_active:
            raise serializers.ValidationError(
                f"Staff member {value.get_full_name()} is not currently active"
            )
        return value
    
    def to_representation(self, instance):
        """
        Customize the output representation
        Add additional context to the response
        """
        data = super().to_representation(instance)
        
        # Add paid_by_name to the response
        data['paid_by_name'] = self.get_paid_by_name(instance)
        
        # Format weight to always show 2 decimal places
        if 'weight_on_delivery' in data:
            data['weight_on_delivery'] = f"{float(data['weight_on_delivery']):.2f}"
        
        return data


class HarvestsListSerializer(serializers.ModelSerializer):
    """
    Simplified serializer for listing harvests
    Shows only essential information for list views
    """
    paid_by_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Harvests
        fields = [
            'harvest_id', 
            'worker_name', 
            'block_id', 
            'weight_on_delivery',
            'date_of_delivery', 
            'amount_paid',
            'paid_by_name'
        ]
    
    def get_paid_by_name(self, obj):
        """
        Return the staff member's full name
        """
        if obj.paid_by:
            return obj.paid_by.get_full_name()
        return None


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
<<<<<<< HEAD
=======
>>>>>>> 32f5cd754438efd6bf2c5652d930d014e74a421b
>>>>>>> 447798b3a9fca5fed9ccfbdbfbdeb8a9db50aeb0


