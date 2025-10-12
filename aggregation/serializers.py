from rest_framework import serializers
from .models import FarmerRegistration
from .models import FarmerHarvest

class FarmerSerializer(serializers.ModelSerializer):
    class Meta:
        model = FarmerRegistration
        fields = '__all__'  

class FarmerHarvestSerializer(serializers.ModelSerializer):
    class Meta:
        model = FarmerHarvest
        fields = '__all__'