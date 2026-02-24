from django.contrib.auth.models import Group, Permission
from django.db.models.signals import post_migrate
from django.dispatch import receiver
import logging

logger = logging.getLogger(__name__)


@receiver(post_migrate)
def create_default_groups(sender, **kwargs):
    """Create default role groups with their permissions after migration."""
    if sender.name != 'auth':
        return

    roles = {
        'Admin': [
            'auth.add_user', 'auth.change_user', 'auth.delete_user', 'auth.view_user',
        ],
        'Instructor': [
            'app.add_course', 'app.change_course', 'app.delete_course', 'app.view_course',
        ],
        'Student': [
            'app.view_course', 'app.add_enrollment', 'app.change_enrollment',
        ],
        'Sponsor': [
            'app.view_course', 'app.add_sponsorship', 'app.change_sponsorship',
        ],
    }

    for role, perm_list in roles.items():
        group, _ = Group.objects.get_or_create(name=role)

        for perm_str in perm_list:
            app_label, codename = perm_str.split('.')
            try:
                perm = Permission.objects.get(
                    content_type__app_label=app_label,
                    codename=codename,
                )
                group.permissions.add(perm)
            except Permission.DoesNotExist:
                logger.warning(f'Permission {perm_str} not found (yet)')