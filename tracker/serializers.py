from rest_framework import serializers
from .models import Application, Reminder

class ReminderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reminder
        fields = ['id', 'remind_at', 'message', 'is_sent']


class ApplicationSerializer(serializers.ModelSerializer):
    reminders = ReminderSerializer(many=True, read_only=True)
    days_since_applied = serializers.SerializerMethodField()

    class Meta:
        model = Application
        fields = [
            'id', 'company', 'role', 'job_url',
            'status', 'applied_date', 'notes',
            'reminders', 'days_since_applied', 'created_at'
        ]
        read_only_fields = ['created_at']

    def get_days_since_applied(self, obj):
        from django.utils import timezone
        return (timezone.now().date() - obj.applied_date).days