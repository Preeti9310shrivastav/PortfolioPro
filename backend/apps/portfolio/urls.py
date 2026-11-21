"""
URL routing for Portfolio Management Module.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.portfolio.views import PortfolioViewSet

router = DefaultRouter()
router.register(r'portfolios', PortfolioViewSet, basename='portfolios')
router.register(r'', PortfolioViewSet, basename='portfolio')

urlpatterns = [
    path('', include(router.urls)),
]
