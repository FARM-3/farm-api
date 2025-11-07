from rest_framework import serializers
from .models import Activity

class ActivitySerializer(serializers.ModelSerializer):
    user_name = serializers.SerializerMethodField()
    class Meta:
        model = Activity
        fields = ['id','user','user_name','action','object_repr','object_id','timestamp']

    def get_user_name(self, obj):
        return obj.user.get_full_name() if obj.user else None