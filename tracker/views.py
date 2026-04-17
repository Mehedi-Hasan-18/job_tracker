from rest_framework import viewsets, permissions, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Application, Reminder
from .serializers import ApplicationSerializer, ReminderSerializer
from .tasks import send_reminder_email
from django.utils import timezone


class ApplicationViewSet(viewsets.ModelViewSet):
    serializer_class = ApplicationSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['company', 'role']
    ordering_fields = ['applied_date', 'created_at']

    def get_queryset(self):
        # users only see their own applications
        return Application.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=False, methods=['get'])
    def stats(self, request):
        qs = self.get_queryset()
        return Response({
            'total': qs.count(),
            'applied': qs.filter(status='applied').count(),
            'interview': qs.filter(status='interview').count(),
            'offer': qs.filter(status='offer').count(),
            'rejected': qs.filter(status='rejected').count(),
            'ghost': qs.filter(status='ghost').count(),
        })


class ReminderViewSet(viewsets.ModelViewSet):
    serializer_class = ReminderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Reminder.objects.filter(
            application__user=self.request.user
        )
        

class ReminderViewSet(viewsets.ModelViewSet):
    serializer_class = ReminderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Reminder.objects.filter(
            application__user=self.request.user
        )

    def perform_create(self, serializer):
        reminder = serializer.save()

        # schedule email at the remind_at time
        delay = (reminder.remind_at - timezone.now()).total_seconds()
        if delay > 0:
            send_reminder_email.apply_async(
                args=[reminder.id],
                countdown=delay  # fires after N seconds
            )