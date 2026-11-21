"""
URL routing for Technical Indicators & Chart Preferences Module.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.technical.views import TechnicalAnalysisViewSet

router = DefaultRouter()
router.register(r'', TechnicalAnalysisViewSet, basename='technical')

urlpatterns = [
    path('', include(router.urls)),
]

urlpatterns = [
    path('securities/<str:security_id>/analysis/', TechnicalAnalysisViewSet.as_view({'get': 'analysis'})),
    path('securities/<str:security_id>/indicators/', TechnicalAnalysisViewSet.as_view({'get': 'indicators'})),
] + urlpatterns
