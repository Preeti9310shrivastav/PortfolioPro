"""
Views for Price Alerts, In-App Notifications, and System Announcements.
"""
from django.utils import timezone
from django.db import models
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny

from apps.notifications.models import PriceAlert, UserNotification, SystemAnnouncement
from apps.notifications.serializers import (
    PriceAlertSerializer,
    PriceAlertCreateSerializer,
    UserNotificationSerializer,
    SystemAnnouncementSerializer,
)
from apps.common.responses import api_success, api_error
from apps.common.permissions import IsFinanceOfficer


class PriceAlertViewSet(viewsets.ModelViewSet):
    """
    ViewSet for user price alert management, activation, and deactivation.
    """
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return (
            PriceAlert.objects.filter(user=self.request.user)
            .select_related('security', 'security__quote')
            .order_by('-created_at')
        )

    def get_serializer_class(self):
        if self.action == 'create':
            return PriceAlertCreateSerializer
        return PriceAlertSerializer

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = PriceAlertSerializer(queryset, many=True)
        return api_success(
            data={"alerts": serializer.data},
            message="Price alerts retrieved successfully."
        )

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = PriceAlertSerializer(instance)
        return api_success(
            data={"alert": serializer.data},
            message="Price alert retrieved successfully."
        )

    def create(self, request, *args, **kwargs):
        serializer = PriceAlertCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return api_error(
                message="Failed to create price alert.",
                errors=serializer.errors,
                status_code=status.HTTP_400_BAD_REQUEST
            )

        alert = serializer.save(user=request.user)
        return api_success(
            data={"alert": PriceAlertSerializer(alert).data},
            message=f"Alert set for {alert.security.symbol} when price is {alert.condition} ₹ {alert.target_value:.2f}",
            status_code=status.HTTP_201_CREATED
        )

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete()
        return api_success(message="Price alert deleted successfully.")

    @action(detail=True, methods=['post'])
    def activate(self, request, pk=None):
        """
        Re-enable a dormant or previously triggered alert.
        """
        alert = self.get_object()
        alert.is_active = True
        alert.is_triggered = False
        alert.triggered_at = None
        alert.save(update_fields=['is_active', 'is_triggered', 'triggered_at', 'updated_at'])
        return api_success(
            data={"alert": PriceAlertSerializer(alert).data},
            message=f"Alert for {alert.security.symbol} activated successfully."
        )

    @action(detail=True, methods=['post'])
    def deactivate(self, request, pk=None):
        """
        Disable an alert rule without deleting it.
        """
        alert = self.get_object()
        alert.is_active = False
        alert.save(update_fields=['is_active', 'updated_at'])
        return api_success(
            data={"alert": PriceAlertSerializer(alert).data},
            message=f"Alert for {alert.security.symbol} deactivated successfully."
        )


class NotificationViewSet(viewsets.GenericViewSet):
    """
    ViewSet for user notification inbox, mark-as-read, and unread counters.
    """
    serializer_class = UserNotificationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = UserNotification.objects.filter(user=self.request.user)
        is_read_param = self.request.query_params.get('is_read')
        if is_read_param is not None:
            if is_read_param.lower() in ['true', '1']:
                qs = qs.filter(is_read=True)
            elif is_read_param.lower() in ['false', '0']:
                qs = qs.filter(is_read=False)

        category = self.request.query_params.get('category')
        if category:
            qs = qs.filter(category=category.upper())

        return qs.order_by('-created_at')

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return api_success(
            data={"notifications": serializer.data},
            message="Notifications retrieved successfully."
        )

    @action(detail=True, methods=['post'])
    def mark_read(self, request, pk=None):
        """
        Mark a single notification as read.
        """
        try:
            notification = UserNotification.objects.get(pk=pk, user=request.user)
        except UserNotification.DoesNotExist:
            return api_error(
                message="Notification not found.",
                status_code=status.HTTP_404_NOT_FOUND
            )

        notification.is_read = True
        notification.save(update_fields=['is_read'])
        return api_success(
            data={"notification": self.get_serializer(notification).data},
            message="Notification marked as read."
        )

    @action(detail=False, methods=['post'])
    def mark_all_read(self, request):
        """
        Mark all pending notifications as read for current user.
        """
        updated_count = UserNotification.objects.filter(
            user=request.user,
            is_read=False
        ).update(is_read=True)

        return api_success(
            data={"updated_count": updated_count},
            message=f"{updated_count} notification(s) marked as read."
        )

    @action(detail=False, methods=['get'])
    def unread_count(self, request):
        """
        Count of unread messages for notification bell badges.
        """
        count = UserNotification.objects.filter(
            user=request.user,
            is_read=False
        ).count()

        return api_success(
            data={"unread_count": count},
            message="Unread notification count retrieved."
        )


class SystemAnnouncementViewSet(viewsets.ModelViewSet):
    """
    ViewSet for broadcasting platform bulletins. Finance Officers create, all users read.
    """
    serializer_class = SystemAnnouncementSerializer

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAuthenticated(), IsFinanceOfficer()]
        return [IsAuthenticated()]

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated and (user.role == 'FINANCE_OFFICER' or user.is_staff or user.is_superuser):
            return SystemAnnouncement.objects.all().order_by('-created_at')

        return SystemAnnouncement.objects.filter(
            models.Q(valid_until__isnull=True) | models.Q(valid_until__gte=timezone.now())
        ).order_by('-created_at')

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return api_success(
            data={"announcements": serializer.data},
            message="Announcements retrieved successfully."
        )

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return api_success(
            data={"announcement": serializer.data},
            message="Announcement details retrieved."
        )

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            return api_error(
                message="Announcement creation failed.",
                errors=serializer.errors,
                status_code=status.HTTP_400_BAD_REQUEST
            )

        announcement = serializer.save(created_by=request.user)
        return api_success(
            data={"announcement": self.get_serializer(announcement).data},
            message="System announcement broadcasted successfully.",
            status_code=status.HTTP_201_CREATED
        )

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete()
        return api_success(message="Announcement deleted successfully.")
