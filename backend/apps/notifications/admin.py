"""
Django Admin registration for Price Alerts, Notifications, and System Announcements.
"""
from django.contrib import admin
from apps.notifications.models import PriceAlert, UserNotification, SystemAnnouncement


@admin.register(PriceAlert)
class PriceAlertAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'security',
        'condition',
        'target_value',
        'is_triggered',
        'is_active',
        'triggered_at',
        'created_at',
    )
    list_filter = ('condition', 'is_triggered', 'is_active', 'created_at')
    search_fields = ('user__username', 'security__symbol', 'security__company_name')


@admin.register(UserNotification)
class UserNotificationAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'category',
        'title',
        'is_read',
        'created_at',
    )
    list_filter = ('category', 'is_read', 'created_at')
    search_fields = ('user__username', 'title', 'message')


@admin.register(SystemAnnouncement)
class SystemAnnouncementAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'priority',
        'created_by',
        'valid_until',
        'created_at',
    )
    list_filter = ('priority', 'created_at')
    search_fields = ('title', 'body', 'created_by__username')
