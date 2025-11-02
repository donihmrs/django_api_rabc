from rest_framework import permissions


ROLE_PERMISSIONS = {
    'admin': {
        'users': {'read': True, 'write': True, 'delete': True , 'update': True},
        'products': {'read': True, 'write': True, 'delete': True , 'update': True},
        'orders': {'read': True, 'write': True, 'delete': True , 'update': True},
        'invitations': {'read': True, 'write': True, 'delete': True , 'update': True},
    },
    'manager': {
        'users': {'read': True, 'write': False, 'delete': False, 'update': False},
        'products': {'read': True, 'write': False, 'delete': False, 'update': True},
        'orders': {'read': True, 'write': False, 'delete': False, 'update': False},
        'invitations': {'read': True, 'write': True, 'delete': False, 'update': True},
    },
    'staff': {
        'users': {'read': False, 'write': False , 'delete': False , 'update': False},
        'products': {'read': True, 'write': False, 'delete': False, 'update': False},
        'orders': {'read': False, 'write': False, 'delete': False, 'update': False},
        'invitations': {'read': False, 'write': False, 'delete': False, 'update': False},
    }
}

class UserPermission(permissions.BasePermission):
    """
    Role-based permission untuk User model:
    - Admin: full access
    - Manager: read-only
    - Staff: no access
    """
    def has_permission(self, request, view):
        user = request.user
        if not user.is_authenticated:
            return False

        role = getattr(user, 'role', None)

        if role == 'admin':
            return True
        elif role == 'manager':
            return request.method in permissions.SAFE_METHODS
        elif role == 'staff':
            return False
        return False

    def has_object_permission(self, request, view, obj):
        return self.has_permission(request, view)


class ProductPermission(permissions.BasePermission):
    """
    Role-based permission untuk Product model:
    - Admin: full access
    - Manager: full access
    - Staff: read-only
    """
    def has_permission(self, request, view):
        user = request.user
        if not user.is_authenticated:
            return False

        role = getattr(user, 'role', None)

        if role == 'admin':
            return True
        elif role == 'manager':
            return True
        elif role == 'staff':
            return request.method in permissions.SAFE_METHODS
        return False

    def has_object_permission(self, request, view, obj):
        return self.has_permission(request, view)


class OrderPermission(permissions.BasePermission):
    """
    Role-based permission untuk Order model:
    - Admin: full access
    - Manager: read-only
    - Staff: no access
    """
    def has_permission(self, request, view):
        user = request.user
        if not user.is_authenticated:
            return False

        role = getattr(user, 'role', None)

        if role == 'admin':
            return True
        elif role == 'manager':
            return request.method in permissions.SAFE_METHODS
        elif role == 'staff':
            return False
        return False

    def has_object_permission(self, request, view, obj):
        return self.has_permission(request, view)
