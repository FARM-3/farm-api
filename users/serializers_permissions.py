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
    role_display = serializers.CharField(source='get_role_display', read_only=True)

    class Meta:
        model = User
        fields = ['id', 'name', 'phone', 'role', 'role_display', 'is_active', 'is_staff', 'created_at']
        read_only_fields = ['created_at']


class UserCreateSerializer(serializers.ModelSerializer):
    pin = serializers.CharField(write_only=True, min_length=4, max_length=4)

    class Meta:
        model = User
        fields = ['id', 'name', 'phone', 'role', 'pin', 'is_active']

    def validate_phone(self, value):
        value = (value or '').strip()
        if not value:
            raise serializers.ValidationError('Phone number is required.')
        if User.objects.filter(phone=value).exists():
            raise serializers.ValidationError('A user with this phone number already exists.')
        return value

    def validate_pin(self, value):
        if not value.isdigit():
            raise serializers.ValidationError('PIN must be 4 digits.')
        return value

    def create(self, validated_data):
        pin = validated_data.pop('pin')
        is_active = validated_data.pop('is_active', True)
        user = User.objects.create_user(
            phone=validated_data['phone'],
            pin=pin,
            name=validated_data.get('name', ''),
            role=validated_data.get('role', 'block_champion'),
        )
        if not is_active:
            user.is_active = False
            user.save(update_fields=['is_active'])
        return user


class UserUpdateSerializer(serializers.ModelSerializer):
    pin = serializers.CharField(write_only=True, required=False, min_length=4, max_length=4)

    class Meta:
        model = User
        fields = ['name', 'phone', 'role', 'pin', 'is_active']

    def validate_pin(self, value):
        if value and not value.isdigit():
            raise serializers.ValidationError('PIN must be 4 digits.')
        return value

    def update(self, instance, validated_data):
        pin = validated_data.pop('pin', None)
        for attr, val in validated_data.items():
            setattr(instance, attr, val)
        if pin:
            instance.set_password(pin)
        instance.save()
        return instance
