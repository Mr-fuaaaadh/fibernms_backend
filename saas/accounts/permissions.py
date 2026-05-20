from rest_framework.permissions import BasePermission


ROLE_LEVEL = {
    'viewer': 1,
    'operator': 2,
    'engineer': 3,
    'admin': 4,
    'superAdmin': 5,
}


class RolePermission(BasePermission):
    minimum_role = 'viewer'

    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False
        return ROLE_LEVEL.get(user.role, 0) >= ROLE_LEVEL[self.minimum_role]


class IsSuperAdmin(RolePermission):
    minimum_role = 'superAdmin'


class IsAdmin(RolePermission):
    minimum_role = 'admin'


class IsEngineer(RolePermission):
    minimum_role = 'engineer'


class IsOperator(RolePermission):
    minimum_role = 'operator'
