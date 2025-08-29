# utils/permissions_helpers.py

from .permissions import IsAdmin, IsInstructorOrReadOnly, IsStudent, IsSponsor
from rest_framework.permissions import IsAuthenticated

def get_role_permissions(user):
    if not user.is_authenticated:
        return [IsAuthenticated()]  # 🟢 CHANGED: unified fallback

    if user.groups.filter(name="Admin").exists():
        return [IsAdmin()]
    elif user.groups.filter(name="Instructor").exists():
        return [IsInstructorOrReadOnly()]
    elif user.groups.filter(name="Student").exists():
        return [IsStudent()]
    elif user.groups.filter(name="Sponsor").exists():
        return [IsSponsor()]

    return [IsAuthenticated()]
