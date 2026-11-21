import uuid
from decimal import Decimal
from django.db import models
from django.conf import settings
from apps.common.models import TimeStampedModel

class PriceAlert(TimeStampedModel):
    """
    User-configured price alert conditions triggering notifications.
    """
    COND_ABOVE = 'ABOVE'
    COND_BELOW = 'BELOW'
    COND_PCT_CHANGE = 'PCT_CHANGE'

    CONDITION_CHOICES = (
        (COND_ABOVE, 'Price Rises Above Target'),
        (COND_BELOW, 'Price Drops Below Target'),
        (COND_PCT_CHANGE, 'Day Percentage Change Exceeds Target'),
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='price_alerts'
    )
    security = models.ForeignKey(
        'market.Security',
        on_delete=models.CASCADE,
        related_name='alerts'
    )
    condition = models.CharField(
        max_length=20,
        choices=CONDITION_CHOICES,
        db_index=True
    )
    target_value = models.DecimalField(max_digits=18, decimal_places=4)
    is_triggered = models.BooleanField(default=False, db_index=True)
    triggered_at = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True, db_index=True)

    class Meta:
        db_table = 'price_alerts'
        ordering = ['-created_at']

    def __str__(self):
        return f"Alert for {self.user.username}: {self.security.symbol} {self.condition} ₹ {self.target_value:.2f}"


class UserNotification(models.Model):
    """
    In-app notification item dispatched to a specific customer or administrator.
    """
    CAT_TRADE = 'TRADE'
    CAT_PRICE_ALERT = 'PRICE_ALERT'
    CAT_ACCOUNT = 'ACCOUNT'
    CAT_SYSTEM = 'SYSTEM'
    CAT_SUPPORT = 'SUPPORT'

    CATEGORY_CHOICES = (
        (CAT_TRADE, 'Trade Execution Notification'),
        (CAT_PRICE_ALERT, 'Price Threshold Alert'),
        (CAT_ACCOUNT, 'Account / Deposit Notification'),
        (CAT_SYSTEM, 'Platform Announcement'),
        (CAT_SUPPORT, 'Customer Support Update'),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications'
    )
    title = models.CharField(max_length=255)
    message = models.TextField()
    category = models.CharField(
        max_length=30,
        choices=CATEGORY_CHOICES,
        default=CAT_SYSTEM,
        db_index=True
    )
    is_read = models.BooleanField(default=False, db_index=True)
    link_url = models.CharField(max_length=500, blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        db_table = 'user_notifications'
        ordering = ['-created_at']

    def __str__(self):
        return f"[{self.category}] {self.title} for {self.user.username}"


class SystemAnnouncement(models.Model):
    """
    Platform-wide administrative broadcast announcements.
    """
    PRIORITY_NORMAL = 'NORMAL'
    PRIORITY_URGENT = 'URGENT'

    PRIORITY_CHOICES = (
        (PRIORITY_NORMAL, 'Standard System Bulletin'),
        (PRIORITY_URGENT, 'Urgent / Critical Banner Notice'),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='announcements'
    )
    title = models.CharField(max_length=255)
    body = models.TextField()
    priority = models.CharField(
        max_length=20,
        choices=PRIORITY_CHOICES,
        default=PRIORITY_NORMAL
    )
    valid_until = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        db_table = 'system_announcements'
        ordering = ['-created_at']

    def __str__(self):
        return f"[{self.priority}] {self.title}"
