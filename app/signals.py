from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from .models import Enrollment, Notification, EmailLog
import logging

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Enrollment)
def send_enrollment_notification(sender, instance, created, **kwargs):
    """Send notification and email when a student enrolls in a course."""
    if not created:
        return

    # Create Notification
    Notification.objects.create(
        user=instance.student,
        message=f"You have successfully enrolled in {instance.course.title}.",
        type='enrollment',
    )

    # Create EmailLog and send email
    subject = 'Course Enrollment Confirmation'
    body = (
        f"Hello {instance.student.username},\n\n"
        f"You have successfully enrolled in {instance.course.title}.\n\n"
        "Thank you for joining our platform!"
    )

    EmailLog.objects.create(
        user=instance.student,
        subject=subject,
        body=body,
    )

    try:
        send_mail(
            subject,
            body,
            settings.DEFAULT_FROM_EMAIL,
            [instance.student.email],
            fail_silently=True,
        )
    except Exception as e:
        logger.error(f"Failed to send enrollment email to {instance.student.email}: {e}")