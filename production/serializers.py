from rest_framework import serializers
from .models import Harvests






class HarvestsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Harvests
        fields = '__all__'


from rest_framework import serializers
from .models import Block

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


