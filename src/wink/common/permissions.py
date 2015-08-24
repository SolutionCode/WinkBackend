from rest_framework import permissions


def IsOwner(owner_attr=None):
    class IsOwnerGeneric(permissions.BasePermission):
        def has_object_permission(self, request, view, obj):
            if owner_attr is None:
                owner = obj
            else:
                owner = getattr(obj, owner_attr)

            return owner == request.user
    return IsOwnerGeneric

