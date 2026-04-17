from django.contrib import admin
from .models import Application, Reminder

class ReminderInline(admin.TabularInline):
    model = Reminder
    extra = 1  # shows 1 empty reminder form by default

@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ['company', 'role', 'status', 'applied_date', 'user']
    list_filter = ['status', 'applied_date']
    search_fields = ['company', 'role', 'user__username']
    inlines = [ReminderInline]
    ordering = ['-created_at']

@admin.register(Reminder)
class ReminderAdmin(admin.ModelAdmin):
    list_display = ['application', 'remind_at', 'is_sent']
    list_filter = ['is_sent']