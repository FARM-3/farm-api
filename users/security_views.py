from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from .models import RolePermission, LoginAudit, User
from .serializers_permissions import RolePermissionSerializer, LoginAuditSerializer, UserAdminSerializer


class RolePermissionViewSet(viewsets.ModelViewSet):
    queryset = RolePermission.objects.all()
    serializer_class = RolePermissionSerializer
    permission_classes = [AllowAny]


class LoginAuditViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = LoginAudit.objects.select_related('user').all()
    serializer_class = LoginAuditSerializer
    permission_classes = [AllowAny]


class UserAdminViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserAdminSerializer
    permission_classes = [AllowAny]
    http_method_names = ['get', 'patch', 'head', 'options']
