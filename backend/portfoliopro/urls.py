"""
PortfolioPro Root URL Configuration
"""
from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

urlpatterns = [
    path('admin/', admin.site.urls),

    # OpenAPI 3.0 Documentation Endpoints
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),

    # Domain Application Routes
    path('api/auth/', include('apps.authentication.urls')),
    path('api/accounts/', include('apps.accounts.urls')),
    path('api/market/', include('apps.market.urls')),
    path('api/trading/', include('apps.trading.urls')),
    path('api/portfolio/', include('apps.portfolio.urls')),
    path('api/risk/', include('apps.risk.urls')),
    path('api/technical/', include('apps.technical.urls')),
    path('api/fundamental/', include('apps.fundamental.urls')),
    path('api/notifications/', include('apps.notifications.urls')),
    path('api/support/', include('apps.support.urls')),
]
