from rest_framework import permissions

class IsBusinessUserOrReadOnly(permissions.BasePermission):
    """Custom permission: Only business users can create/edit offers"""
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.is_authenticated and getattr(request.user, 'user_type', None) == 'business'

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.business_user == request.user
