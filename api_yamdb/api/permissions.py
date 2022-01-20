from rest_framework import permissions
from django.contrib.auth import get_user_model

User = get_user_model()


class AdminOrModeratorOrAuthorPermission(permissions.BasePermission):
    """Класс пермишена для доступа к изменению контента,
    генерируемого пользователями. Такой контент могут изменять модераторы,
    администраторы или авторы."""

    def has_permission(self, request, view):
        """Метод проверяет тип запроса.
        На чтение - доступно любому пользователю.
        На создание - доступно только авторизованному.
        """
        return (request.method in permissions.SAFE_METHODS
                or request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        """Метод проверяет сначала, имеет ли пользователь
        группу модератора или администратора,
        а затем проверяет является ли пользователь автором поста."""
        if request.method in permissions.SAFE_METHODS:
            return True
        if not request.user.is_authenticated:
            return False
        if request.user.role in (User.MODERATOR, User.ADMIN):
            return True
        return obj.author == request.user


class AdminOnlyPermission(permissions.BasePermission):
    """Класс пермишена для доступа к изменению контента администратора.
    Такой контент могут изменять только администраторы и суперпользователь."""

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        if request.user.role == User.ADMIN or request.user.is_superuser:
            return True
        return False

    def has_object_permission(self, request, view, obj):
        """Метод проверяет является ли пользователь
        администратором или суперпользователем."""
        if not request.user.is_authenticated:
            return False
        if request.user.role == User.ADMIN or request.user.is_superuser:
            return True
        return False


class AdminOrReadOnlyPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        if request.user.role == User.ADMIN or request.user.is_superuser:
            return True

    def has_object_permission(self, request, view, obj):
        """Метод проверяет является ли пользователь
        администратором или суперпользователем."""
        if request.method in permissions.SAFE_METHODS:
            return True
        if request.user.is_authenticated:
            if request.user.role == User.ADMIN or request.user.is_superuser:
                return True
        return False
