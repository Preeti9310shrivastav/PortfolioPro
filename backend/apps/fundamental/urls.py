"""
URL routing for Fundamental Valuation & Financials Module.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.fundamental.views import FundamentalAnalysisViewSet

router = DefaultRouter()
router.register(r'', FundamentalAnalysisViewSet, basename='fundamental')

urlpatterns = [
    path('', include(router.urls)),
]

urlpatterns = [
    path('securities/<str:security_id>/analysis/', FundamentalAnalysisViewSet.as_view({'get': 'analysis'})),
    path('securities/<str:security_id>/peers/', FundamentalAnalysisViewSet.as_view({'get': 'peers'})),
] + urlpatterns
