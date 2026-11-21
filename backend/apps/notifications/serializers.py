"""
Serializers for Price Alerts, In-App User Notifications, and System Announcements.
"""
from decimal import Decimal
from rest_framework import serializers

from apps.notifications.models import PriceAlert, UserNotification, SystemAnnouncement
from apps.market.models import Security


class PriceAlertSerializer(serializers.ModelSerializer):
    """
    Read serializer for user price alert rules with stock details.
    """
    symbol = serializers.ReadOnlyField(source='security.symbol')
    company_name = serializers.ReadOnlyField(source='security.company_name')
    current_ltp = serializers.SerializerMethodField()

    class Meta:
        model = PriceAlert
        fields = [
            'id',
            'user',
            'security',
            'symbol',
            'company_name',
            'current_ltp',
            'condition',
            'target_value',
            'is_triggered',
            'triggered_at',
            'is_active',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id',
            'user',
            'symbol',
            'company_name',
            'current_ltp',
            'is_triggered',
            'triggered_at',
            'created_at',
            'updated_at',
        ]

    def get_current_ltp(self, obj):
        if hasattr(obj.security, 'quote') and obj.security.quote:
            return obj.security.quote.ltp
        return Decimal('0.0000')


class PriceAlertCreateSerializer(serializers.ModelSerializer):
    """
    Write serializer for establishing price alert rules.
    """
    security_id = serializers.PrimaryKeyRelatedField(
        queryset=Security.objects.filter(is_active=True),
        source='security',
        write_only=True
    )

    class Meta:
        model = PriceAlert
        fields = [
            'security_id',
            'condition',
            'target_value',
        ]

    def validate_target_value(self, value):
        if value <= Decimal('0.0000'):
            raise serializers.ValidationError("Target value must be greater than zero.")
        return value


class UserNotificationSerializer(serializers.ModelSerializer):
    """
    Serializer for in-app alert notifications.
    """
    class Meta:
        model = UserNotification
        fields = [
            'id',
            'user',
            'title',
            'message',
            'category',
            'is_read',
            'link_url',
            'created_at',
        ]
        read_only_fields = ['id', 'user', 'created_at']


class SystemAnnouncementSerializer(serializers.ModelSerializer):
    """
    Serializer for platform-wide administrative announcements.
    """
    created_by_username = serializers.ReadOnlyField(source='created_by.username')

    class Meta:
        model = SystemAnnouncement
        fields = [
            'id',
            'created_by',
            'created_by_username',
            'title',
            'body',
            'priority',
            'valid_until',
            'created_at',
        ]
        read_only_fields = ['id', 'created_by', 'created_by_username', 'created_at']

    def validate_title(self, value):
        stripped = value.strip()
        if not stripped:
            raise serializers.ValidationError("Title cannot be blank.")
        return stripped
