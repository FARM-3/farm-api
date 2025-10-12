from rest_framework import serializers
from .models import Harvests






class HarvestsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Harvests
        fields = '__all__'


