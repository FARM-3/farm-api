from rest_framework import serializers
from .models import FarmerRegistration
from .models import FarmerHarvest

class FarmerRegistrationSerializer(serializers.ModelSerializer):
    type_of_seedlings = serializers.ListField(
        child=serializers.CharField(max_length=20),
        allow_empty=False
    )

    class Meta:
        model = FarmerRegistration
        fields = '__all__'  

class FarmerHarvestSerializer(serializers.ModelSerializer):
    class Meta:
        model = FarmerHarvest
        fields = '__all__'