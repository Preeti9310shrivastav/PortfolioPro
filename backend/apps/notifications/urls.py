"""
URL routing for Notifications, Price Alerts, and Announcements Module.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.notifications.views import (
    PriceAlertViewSet,
    NotificationViewSet,
    SystemAnnouncementViewSet,
)

router = DefaultRouter()
router.register(r'alerts', PriceAlertViewSet, basename='price-alert')
router.register(r'inbox', NotificationViewSet, basename='user-notification')
router.register(r'announcements', SystemAnnouncementViewSet, basename='system-announcement')

urlpatterns = [
    path('', include(router.urls)),
]
