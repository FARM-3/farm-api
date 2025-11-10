from rest_framework.permissions import BasePermission

class IsSuperAdmin(BasePermission):
    """
    Allows access only to users with role 'superadmin' or 'admin'.
    """

    def has_permission(self, request, view):
        user = request.user
        user_role = getattr(user, 'role', '')
        return bool(user and user.is_authenticated and user_role in ['superadmin', 'admin'])