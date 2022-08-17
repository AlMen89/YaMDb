from rest_framework import permissions


def admin_access(request):
    """Проверяет наличие прав админа/суперпользователя."""
    return (hasattr(request.user, 'role') and request.user.role == 'admin'
            or request.user.is_superuser)


class AdminOrSuperuserOnly(permissions.BasePermission):

    def has_permission(self, request, view):
        return request.user.is_authenticated and admin_access(request)


class AdminOrReadOnly(permissions.BasePermission):

    def has_permission(self, request, view):
        return (request.method in permissions.SAFE_METHODS
                or admin_access(request))
