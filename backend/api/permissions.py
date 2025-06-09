from rest_framework import permissions


class AdminOrReadOnlyPermission(permissions.BasePermission):
    """Разрешение для просмотра профиля пользователя"""

    def has_object_permission(self, request, view, obj):
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_staff
        )


class AuthorOrAdminPermission(permissions.BasePermission):
    """Разрешение на изменение контента"""

    def has_object_permission(self, request, view, obj):
        return (
            request.method in permissions.SAFE_METHODS
            or obj.author == request.user
            or request.user.is_staff
        )
