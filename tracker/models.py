from django.db import models
from django.conf import settings

class Application(models.Model):

    STATUS_CHOICES = [
        ('applied', 'Applied'),
        ('interview', 'Interview'),
        ('offer', 'Offer'),
        ('rejected', 'Rejected'),
        ('ghost', 'Ghosted'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='applications'
    )
    company = models.CharField(max_length=255)
    role = models.CharField(max_length=255)
    job_url = models.URLField(blank=True)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='applied'
    )
    applied_date = models.DateField()
    notes = models.TextField(blank=True)
    last_activity = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.role} at {self.company} ({self.status})"

    class Meta:
        ordering = ['-created_at']


class Reminder(models.Model):
    application = models.ForeignKey(
        Application,
        on_delete=models.CASCADE,
        related_name='reminders'
    )
    remind_at = models.DateTimeField()
    message = models.CharField(max_length=500)
    is_sent = models.BooleanField(default=False)

    def __str__(self):
        return f"Reminder for {self.application.company} at {self.remind_at}"