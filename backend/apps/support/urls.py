"""
URL routing for Customer Support & Helpdesk Module.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.support.views import SupportTicketViewSet, AllTicketsViewSet

router = DefaultRouter()
router.register(r'tickets', SupportTicketViewSet, basename='support-ticket')
router.register(r'officer/tickets', AllTicketsViewSet, basename='support-officer-ticket')
router.register(r'all-tickets', AllTicketsViewSet, basename='support-all-ticket')

urlpatterns = [
    path('', include(router.urls)),
]
