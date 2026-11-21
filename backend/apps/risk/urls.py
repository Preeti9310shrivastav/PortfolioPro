"""
URL routing for Portfolio Risk Analytics Module.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.risk.views import RiskViewSet, SystemRiskView

router = DefaultRouter()
router.register(r'', RiskViewSet, basename='risk')

urlpatterns = [
    path('system-overview/', SystemRiskView.as_view(), name='system-risk-overview'),
    path('', include(router.urls)),
]

urlpatterns = [path('system/', SystemRiskView.as_view())] + urlpatterns
