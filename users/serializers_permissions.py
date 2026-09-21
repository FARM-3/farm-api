from rest_framework import serializers
from .models import RolePermission, LoginAudit, User


class RolePermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = RolePermission
        fields = '__all__'


class LoginAuditSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.name', read_only=True)

    class Meta:
        model = LoginAudit
        fields = '__all__'


class UserAdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'name', 'phone', 'role', 'is_active', 'is_staff', 'created_at']
        read_only_fields = ['created_at']
