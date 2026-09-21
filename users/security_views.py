from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from .models import RolePermission, LoginAudit, User
from .serializers_permissions import (
    RolePermissionSerializer, LoginAuditSerializer,
    UserAdminSerializer, UserCreateSerializer, UserUpdateSerializer,
)


class RolePermissionViewSet(viewsets.ModelViewSet):
    queryset = RolePermission.objects.all()
    serializer_class = RolePermissionSerializer
    permission_classes = [AllowAny]


class LoginAuditViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = LoginAudit.objects.select_related('user').all()
    serializer_class = LoginAuditSerializer
    permission_classes = [AllowAny]


class UserAdminViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all().order_by('-created_at')
    permission_classes = [AllowAny]

    def get_serializer_class(self):
        if self.action == 'create':
            return UserCreateSerializer
        if self.action in ('update', 'partial_update'):
            return UserUpdateSerializer
        return UserAdminSerializer

    http_method_names = ['get', 'post', 'patch', 'delete', 'head', 'options']
