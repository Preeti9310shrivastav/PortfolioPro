"""
Serializers for Customer Support Helpdesk Tickets and Discussion Threads.
"""
from rest_framework import serializers

from apps.support.models import SupportTicket, SupportMessage
from apps.authentication.models import User
from apps.trading.models import TradeOrder


class SupportMessageSerializer(serializers.ModelSerializer):
    """
    Read serializer for chronological messages inside a ticket thread.
    """
    sender_username = serializers.ReadOnlyField(source='sender.username')
    sender_role = serializers.ReadOnlyField(source='sender.role')

    class Meta:
        model = SupportMessage
        fields = [
            'id',
            'ticket',
            'sender',
            'sender_username',
            'sender_role',
            'message_text',
            'is_internal_note',
            'created_at',
        ]
        read_only_fields = ['id', 'ticket', 'sender', 'sender_username', 'sender_role', 'created_at']


class SupportMessageCreateSerializer(serializers.ModelSerializer):
    """
    Write serializer for posting a response message or internal note.
    """
    class Meta:
        model = SupportMessage
        fields = [
            'message_text',
            'is_internal_note',
        ]

    def validate_message_text(self, value):
        stripped = value.strip()
        if not stripped:
            raise serializers.ValidationError("Message content cannot be blank.")
        return stripped


class SupportTicketSerializer(serializers.ModelSerializer):
    """
    Detailed serializer for helpdesk tickets including metadata and message count.
    """
    user_username = serializers.ReadOnlyField(source='user.username')
    assigned_to_username = serializers.ReadOnlyField(source='assigned_to.username')
    message_count = serializers.SerializerMethodField()
    category_display = serializers.CharField(source='get_category_display', read_only=True)
    priority_display = serializers.CharField(source='get_priority_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = SupportTicket
        fields = [
            'id',
            'ticket_number',
            'user',
            'user_username',
            'category',
            'category_display',
            'priority',
            'priority_display',
            'status',
            'status_display',
            'subject',
            'related_order',
            'assigned_to',
            'assigned_to_username',
            'message_count',
            'resolved_at',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id',
            'ticket_number',
            'user',
            'user_username',
            'assigned_to_username',
            'message_count',
            'resolved_at',
            'created_at',
            'updated_at',
        ]

    def get_message_count(self, obj):
        # When accessed by a customer, count public messages only
        request = self.context.get('request')
        if request and request.user.role == User.ROLE_CUSTOMER:
            return obj.messages.filter(is_internal_note=False).count()
        return obj.messages.count()


class SupportTicketCreateSerializer(serializers.ModelSerializer):
    """
    Write serializer for customer-initiated helpdesk ticket creation.
    """
    initial_message = serializers.CharField(write_only=True)
    related_order_id = serializers.PrimaryKeyRelatedField(
        queryset=TradeOrder.objects.all(),
        source='related_order',
        write_only=True,
        required=False,
        allow_null=True
    )

    class Meta:
        model = SupportTicket
        fields = [
            'subject',
            'category',
            'priority',
            'related_order_id',
            'initial_message',
        ]

    def validate_subject(self, value):
        stripped = value.strip()
        if not stripped:
            raise serializers.ValidationError("Subject cannot be blank.")
        return stripped

    def validate_initial_message(self, value):
        stripped = value.strip()
        if not stripped:
            raise serializers.ValidationError("Initial message content cannot be blank.")
        return stripped


class TicketAssignSerializer(serializers.Serializer):
    """
    Write serializer for assigning a ticket to a Finance Officer / Support Agent.
    """
    assigned_to_user_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(role__in=[User.ROLE_FINANCE_OFFICER, User.ROLE_ADMIN]),
        source='assigned_to'
    )


class TicketResolveSerializer(serializers.Serializer):
    """
    Write serializer for resolving a support dispute with resolution notes.
    """
    resolution_notes = serializers.CharField(required=False, allow_blank=True, default='')
