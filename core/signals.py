# core/signals.py
from django.contrib.auth.models import Group, Permission
from django.db.models.signals import post_migrate
from django.dispatch import receiver

@receiver(post_migrate)
def create_default_groups(sender, **kwargs):
    # Create Groups
    roles = ['Admin', 'Instructor', 'Student', 'Sponsor']
    for role in roles:
        Group.objects.get_or_create(name=role)