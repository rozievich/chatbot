from rest_framework.permissions import BasePermission


class OwnerBasePermission(BasePermission):
    def has_object_permission(self, request, view, obj):
        if obj.from_user == request.user or obj.to_user == request.user:
            return True
        return False
