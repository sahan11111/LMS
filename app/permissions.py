from rest_framework.permissions import BasePermission, SAFE_METHODS


def _has_role(user, role_name):
    """Helper to check user role consistently using both role field and groups."""
    if not user or not user.is_authenticated:
        return False
    return user.role == role_name.lower() or user.groups.filter(name=role_name.capitalize()).exists()


class IsAdmin(BasePermission):
    """Allows access only to Admin users."""

    def has_permission(self, request, view):
        return _has_role(request.user, 'admin')


class IsInstructor(BasePermission):
    """Full access for Instructors."""

    def has_permission(self, request, view):
        return _has_role(request.user, 'instructor')


class IsInstructorOrReadOnly(BasePermission):
    """Read-only for everyone; write access for Instructors/Admins only."""

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return _has_role(request.user, 'instructor') or _has_role(request.user, 'admin')

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        if _has_role(request.user, 'admin'):
            return True
        return hasattr(obj, 'created_by') and obj.created_by == request.user


class IsStudent(BasePermission):
    """Only students can access."""

    def has_permission(self, request, view):
        return _has_role(request.user, 'student')


class IsSponsor(BasePermission):
    """Only sponsors can access."""

    def has_permission(self, request, view):
        return _has_role(request.user, 'sponsor')


class ReadOnly(BasePermission):
    """Safe methods allowed for anyone."""

    def has_permission(self, request, view):
        return request.method in SAFE_METHODS