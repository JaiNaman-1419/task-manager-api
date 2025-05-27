from rest_framework import permissions


class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object or admins to edit it.
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions for any authenticated user
        if request.method in permissions.SAFE_METHODS:
            return request.user.role == "admin" or obj.user == request.user

        # Write permissions only to the owner or admin
        return request.user.role == "admin" or obj.user == request.user
