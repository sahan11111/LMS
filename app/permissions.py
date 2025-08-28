from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsStudent(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.role == 'student'


class IsSponsor(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.role == 'sponsor'
    


class IsAdmin(BasePermission):
    """ Full access for Admins """
    def has_permission(self, request, view):
        return (
            request.user 
            and request.user.is_authenticated 
            and request.user.groups.filter(name="Admin").exists()
        )


class IsInstructorOrReadOnly(BasePermission):
    """
    Instructors can create and manage their own courses.
    Students & Sponsors only have read-only access.
    Admin has full access.
    """
    def has_permission(self, request, view):
        # Everyone can view courses
        if request.method in SAFE_METHODS:
            return True
        # Only Instructors & Admins can create/update/delete
        return (
            request.user 
            and request.user.is_authenticated 
            and (
                request.user.groups.filter(name="Instructor").exists() or
                request.user.groups.filter(name="Admin").exists()
            )
        )

    def has_object_permission(self, request, view, obj):
        # Allow safe methods (GET, HEAD, OPTIONS) for all
        if request.method in SAFE_METHODS:
            return True
        # Admin can edit/delete anything
        if request.user.groups.filter(name="Admin").exists():
            return True
        # Instructors can only modify their own courses
        return obj.created_by == request.user
