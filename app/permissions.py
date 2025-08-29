from rest_framework.permissions import BasePermission, SAFE_METHODS

# =========================
# Admin Permission
# =========================
class IsAdmin(BasePermission):
    """ Full access for Admins 🔹 """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.groups.filter(name="Admin").exists()

# =========================
# Instructor Permission
# =========================
class IsInstructor(BasePermission):
    """ Full access for Instructors 🔹 """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.groups.filter(name="Instructor").exists()

# =========================
# Instructor or Read-Only 🔹
# Students & Sponsors can read courses/assessments, but only instructors/admins can modify
# =========================
class IsInstructorOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return request.user and request.user.is_authenticated and (
            request.user.groups.filter(name="Instructor").exists() or
            request.user.groups.filter(name="Admin").exists()
        )

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        if request.user.groups.filter(name="Admin").exists():
            return True
        # Instructor can only modify their own courses/assessments
        return hasattr(obj, 'created_by') and obj.created_by == request.user

# =========================
# Student Permission 🔹
# =========================
class IsStudent(BasePermission):
    """ Only students can enroll, submit assignments, and view own progress """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.groups.filter(name="Student").exists()

# =========================
# Sponsor Permission 🔹
# =========================
class IsSponsor(BasePermission):
    """ Only sponsors can create sponsorships and view sponsored students """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.groups.filter(name="Sponsor").exists()

# =========================
# Read-Only for everyone 🔹
# =========================
class ReadOnly(BasePermission):
    """ Safe methods allowed for any authenticated user """
    def has_permission(self, request, view):
        return request.method in SAFE_METHODS
