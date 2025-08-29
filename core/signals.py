# core/signals.py
from django.contrib.auth.models import Group, Permission
from django.db.models.signals import post_migrate
from django.dispatch import receiver

@receiver(post_migrate)
def create_default_groups(sender, **kwargs):
    roles = {
        "Admin": ["add_user", "change_user", "delete_user", "view_user"],
        "Instructor": ["add_course", "change_course", "delete_course", "view_course"],
        "Student": ["view_course", "add_enrollment", "change_enrollment"],
        "Sponsor": ["view_course", "add_sponsorship", "change_sponsorship"],
    }

    for role, perms in roles.items():
        group, created = Group.objects.get_or_create(name=role)

        for perm_codename in perms:
            try:
                perm = Permission.objects.get(codename=perm_codename)
                group.permissions.add(perm)
            except Permission.DoesNotExist:
                pass  # Permission may not exist yet