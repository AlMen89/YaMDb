from rest_framework import permissions


class AdminOrSuperuserOnly(permissions.BasePermission):

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.admin_access


class AdminOrReadOnly(permissions.BasePermission):

    def has_permission(self, request, view):
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_authenticated and request.user.admin_access
        )


class CommentReviewPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_authenticated
        )

    def has_object_permission(self, request, view, obj):
        return (
            request.method in permissions.SAFE_METHODS
            or (request.user.is_authenticated and (
                request.user.moderator_access
                or request.user.admin_access
                or obj.author == request.user
            )
            )
        )
