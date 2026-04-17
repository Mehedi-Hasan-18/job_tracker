from celery import shared_task
from django.core.mail import send_mail
from django.utils import timezone
from django.conf import settings


@shared_task
def send_reminder_email(reminder_id):
    from .models import Reminder

    try:
        reminder = Reminder.objects.select_related('application__user').get(
            id=reminder_id
        )
        user = reminder.application.user
        application = reminder.application

        send_mail(
            subject=f'Reminder: {application.role} at {application.company}',
            message=f"""
Hi {user.username},

This is your reminder for:
Role: {application.role}
Company: {application.company}
Status: {application.status}

Message: {reminder.message}

Good luck!
— JobTrackr
            """,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
        )

        reminder.is_sent = True
        reminder.save()

        return f'Reminder {reminder_id} sent to {user.email}'

    except Reminder.DoesNotExist:
        return f'Reminder {reminder_id} not found'


@shared_task
def auto_ghost_applications():
    """
    Runs daily — marks applications as 'ghost'
    if no activity in 30 days and status is still 'applied'
    """
    from .models import Application

    threshold = timezone.now() - timezone.timedelta(days=30)
    ghosted = Application.objects.filter(
        status='applied',
        last_activity__lt=threshold
    )
    count = ghosted.update(status='ghost')
    return f'{count} applications marked as ghosted'