import uuid
from django.db import models
from django.conf import settings
from apps.common.models import TimeStampedModel

class SupportTicket(TimeStampedModel):
    """
    Customer service helpdesk ticket for trade disputes and technical queries.
    """
    CAT_TRADE_DISPUTE = 'TRADE_DISPUTE'
    CAT_DEPOSIT_WITHDRAWAL = 'DEPOSIT_WITHDRAWAL'
    CAT_KYC_ACCOUNT = 'KYC_ACCOUNT'
    CAT_TECHNICAL = 'TECHNICAL'
    CAT_GENERAL = 'GENERAL'

    CATEGORY_CHOICES = (
        (CAT_TRADE_DISPUTE, 'Trade Dispute / Execution Query'),
        (CAT_DEPOSIT_WITHDRAWAL, 'Fund Deposit / Withdrawal Issue'),
        (CAT_KYC_ACCOUNT, 'KYC Verification / Account Freeze'),
        (CAT_TECHNICAL, 'Platform Bug / Technical Glitch'),
        (CAT_GENERAL, 'General Inquiry / Feedback'),
    )

    PRIO_LOW = 'LOW'
    PRIO_MEDIUM = 'MEDIUM'
    PRIO_HIGH = 'HIGH'
    PRIO_URGENT = 'URGENT'

    PRIORITY_CHOICES = (
        (PRIO_LOW, 'Low Priority'),
        (PRIO_MEDIUM, 'Medium Priority'),
        (PRIO_HIGH, 'High Priority'),
        (PRIO_URGENT, 'Urgent / Immediate Action Required'),
    )

    STATUS_OPEN = 'OPEN'
    STATUS_IN_PROGRESS = 'IN_PROGRESS'
    STATUS_PENDING_CUSTOMER = 'PENDING_CUSTOMER'
    STATUS_RESOLVED = 'RESOLVED'
    STATUS_CLOSED = 'CLOSED'

    STATUS_CHOICES = (
        (STATUS_OPEN, 'Open / Awaiting Agent Review'),
        (STATUS_IN_PROGRESS, 'Under Investigation'),
        (STATUS_PENDING_CUSTOMER, 'Awaiting Customer Feedback'),
        (STATUS_RESOLVED, 'Resolved by Finance Officer / Support'),
        (STATUS_CLOSED, 'Closed / Completed'),
    )

    ticket_number = models.CharField(max_length=32, unique=True, db_index=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='support_tickets'
    )
    category = models.CharField(
        max_length=30,
        choices=CATEGORY_CHOICES,
        db_index=True
    )
    priority = models.CharField(
        max_length=20,
        choices=PRIORITY_CHOICES,
        default=PRIO_MEDIUM,
        db_index=True
    )
    status = models.CharField(
        max_length=30,
        choices=STATUS_CHOICES,
        default=STATUS_OPEN,
        db_index=True
    )
    subject = models.CharField(max_length=255)
    related_order = models.ForeignKey(
        'trading.TradeOrder',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='dispute_tickets'
    )
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_tickets'
    )
    resolved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'support_tickets'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.ticket_number}: {self.subject} ({self.status})"


class SupportMessage(models.Model):
    """
    Chronological discussion thread message inside a support ticket.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    ticket = models.ForeignKey(
        SupportTicket,
        on_delete=models.CASCADE,
        related_name='messages'
    )
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='sent_messages'
    )
    message_text = models.TextField()
    is_internal_note = models.BooleanField(
        default=False,
        help_text="Visible only to Finance Officers and Administrators"
    )
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        db_table = 'support_messages'
        ordering = ['created_at']

    def __str__(self):
        return f"Message by {self.sender.username} on {self.ticket.ticket_number}"
