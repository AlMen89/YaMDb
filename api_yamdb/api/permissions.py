from rest_framework import permissions
from users.models import User


class AdminOrSuperuserOnly(permissions.BasePermission):

    def has_permission(self, request, view):
        return User.admin_access(self, request)


class AdminOrReadOnly(permissions.BasePermission):

    def has_permission(self, request, view):
        return (
            request.method in permissions.SAFE_METHODS
            or User.admin_access(self, request)
        )


class CommentReviewPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        return (
            request.method in permissions.SAFE_METHODS
            or User.authenticated_user_access(self, request)
        )

    def has_object_permission(self, request, view, obj):
        return (
            request.method in permissions.SAFE_METHODS
            or User.moderator_access(self, request)
            or User.admin_access(self, request)
            or (
                User.authenticated_user_access(self, request)
                and obj.author == request.user
            )
        )
