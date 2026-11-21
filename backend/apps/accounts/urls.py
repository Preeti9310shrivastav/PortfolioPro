"""
URL Configuration for PortfolioPro Accounts Module.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from apps.accounts.views import (
    TradingAccountViewSet,
    AccountTransactionListView,
    KYCViewSet,
)

router = DefaultRouter()
router.register(r'accounts', TradingAccountViewSet, basename='trading-account')
router.register(r'kyc', KYCViewSet, basename='kyc')

urlpatterns = [
    # Convenient Direct / Checklist Endpoints
    path('summary/', TradingAccountViewSet.as_view({'get': 'summary'}), name='account-summary'),
    path('deposit/', TradingAccountViewSet.as_view({'post': 'deposit'}), name='account-deposit'),
    path('withdraw/', TradingAccountViewSet.as_view({'post': 'withdraw'}), name='account-withdraw'),
    path('transactions/', AccountTransactionListView.as_view(), name='account-transactions'),
    path('kyc/me/', KYCViewSet.as_view({'get': 'me'}), name='account-kyc-me'),
    path('admin/all/', TradingAccountViewSet.as_view({'get': 'admin_all'}), name='accounts-admin-all'),
    path(
        'admin/kyc/<uuid:pk>/verify/',
        KYCViewSet.as_view({'patch': 'verify', 'post': 'verify'}),
        name='accounts-admin-kyc-verify'
    ),

    # Router generated routes
    path('', include(router.urls)),
]

urlpatterns = [
    path('trading-accounts/', TradingAccountViewSet.as_view({'get': 'list'})),
    path('trading-accounts/deposit/', TradingAccountViewSet.as_view({'post': 'deposit'})),
    path('trading-accounts/withdraw/', TradingAccountViewSet.as_view({'post': 'withdraw'})),
] + urlpatterns
