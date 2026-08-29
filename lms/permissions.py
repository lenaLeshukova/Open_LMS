from rest_framework.permissions import BasePermission

class IsModerator(BasePermission):
    """Проверяет, входит ли пользователь в группу модераторов."""
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return request.user.groups.filter(name='модераторы').exists()

class IsOwner(BasePermission):
    """Проверяет, является ли пользователь владельцем объекта."""
    def has_object_permission(self, request, view, obj):
        # Если пользователь не авторизован, доступа нет
        if not request.user or not request.user.is_authenticated:
            return False
        # Проверяем, совпадает ли владелец объекта с пользователем из запроса
        return obj.owner == request.user
