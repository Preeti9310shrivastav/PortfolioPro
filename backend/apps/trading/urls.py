"""
URL Configuration for PortfolioPro Trading Module.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from apps.trading.views import (
    OrderViewSet,
    TradeExecutionListView,
    AllOrdersViewSet,
)

router = DefaultRouter()
router.register(r'orders', OrderViewSet, basename='trade-order')
router.register(r'admin/orders', AllOrdersViewSet, basename='admin-trade-order')
router.register(r'all-orders', AllOrdersViewSet, basename='all-trade-order')

urlpatterns = [
    # Direct / Checklist Endpoints
    path('executions/', TradeExecutionListView.as_view(), name='trade-executions-list'),
    path(
        'orders/<uuid:pk>/cancel/',
        OrderViewSet.as_view({'post': 'cancel'}),
        name='trade-order-cancel'
    ),
    path(
        'orders/<uuid:pk>/trades/',
        OrderViewSet.as_view({'get': 'trades'}),
        name='trade-order-trades'
    ),
    path(
        'admin/orders/<uuid:pk>/intervene/',
        AllOrdersViewSet.as_view({'post': 'intervene'}),
        name='admin-trade-order-intervene'
    ),

    # Router generated routes
    path('', include(router.urls)),
]
