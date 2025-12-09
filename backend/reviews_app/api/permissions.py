from rest_framework import permissions

class IsReviewerOrReadOnly(permissions.BasePermission):
    """Custom permission: Only the reviewer can edit/delete their review"""
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return True
