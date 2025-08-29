# core/signals.py
from django.contrib.auth.models import Group, Permission
from django.db.models.signals import post_migrate
from django.dispatch import receiver
from django.apps import apps

@receiver(post_migrate)
def create_default_groups(sender, **kwargs):
    # Only run once for the "core" app to avoid duplicate executions
    if sender.name != "core":
        return

    roles = {
        "Admin": ["auth.add_user", "auth.change_user", "auth.delete_user", "auth.view_user"],
        "Instructor": ["app.add_course", "app.change_course", "app.delete_course", "app.view_course"],
        "Student": ["app.view_course", "app.add_enrollment", "app.change_enrollment"],
        "Sponsor": ["app.view_course", "app.add_sponsorship", "app.change_sponsorship"],
    }

    for role, perm_list in roles.items():
        group, _ = Group.objects.get_or_create(name=role)

        for perm_str in perm_list:
            try:
                app_label, codename = perm_str.split(".")
                perm = Permission.objects.get(content_type__app_label=app_label, codename=codename)
                group.permissions.add(perm)
            except Permission.DoesNotExist:
                print(f"⚠️ Permission {perm_str} not found (maybe migrations not applied yet)")
