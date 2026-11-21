"""
URL Configuration for PortfolioPro Market Module.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from apps.market.views import (
    SecurityViewSet,
    WatchlistViewSet,
    DefaultWatchlistView,
    DefaultWatchlistDeleteView,
    MarketFeedStatusView,
)

router = DefaultRouter()
router.register(r'securities', SecurityViewSet, basename='security')
router.register(r'watchlists', WatchlistViewSet, basename='watchlist')

urlpatterns = [
    # Direct / Checklist Endpoints
    path('stocks/', SecurityViewSet.as_view({'get': 'list'}), name='market-stocks'),
    path('quotes/<str:symbol>/', SecurityViewSet.as_view({'get': 'quote'}), name='market-quote-symbol'),
    path('history/<str:symbol>/', SecurityViewSet.as_view({'get': 'history'}), name='market-history-symbol'),
    path('watchlist/', DefaultWatchlistView.as_view(), name='market-default-watchlist'),
    path('watchlist/<str:symbol>/', DefaultWatchlistDeleteView.as_view(), name='market-default-watchlist-delete'),
    path('admin/feed-status/', MarketFeedStatusView.as_view(), name='market-admin-feed-status'),

    # Router generated routes
    path('', include(router.urls)),
]
