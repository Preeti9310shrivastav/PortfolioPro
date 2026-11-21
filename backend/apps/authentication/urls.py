"""
URL routing for PortfolioPro Authentication Module.
"""
from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from apps.authentication.views import (
    RegisterView,
    LoginView,
    LogoutView,
    ProfileView,
    PasswordChangeView,
    PasswordResetRequestView,
    PasswordResetConfirmView,
    CustomerDashboardAccessView,
    FinanceOfficerConsoleAccessView,
    UserManagementListView,
)

urlpatterns = [
    # Core Authentication Endpoints
    path('register/', RegisterView.as_view(), name='auth-register'),
    path('login/', LoginView.as_view(), name='auth-login'),
    path('logout/', LogoutView.as_view(), name='auth-logout'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),

    # Profile & Account Management
    path('profile/', ProfileView.as_view(), name='auth-profile'),
    path('password-change/', PasswordChangeView.as_view(), name='auth-password-change'),
    path('password-reset/request/', PasswordResetRequestView.as_view(), name='auth-password-reset-request'),
    path('password-reset/confirm/', PasswordResetConfirmView.as_view(), name='auth-password-reset-confirm'),

    # Role-Based Verification / Protected Endpoints
    path('portal/customer/', CustomerDashboardAccessView.as_view(), name='auth-customer-portal'),
    path('console/finance-officer/', FinanceOfficerConsoleAccessView.as_view(), name='auth-fo-console'),
    path('users/', UserManagementListView.as_view(), name='auth-users-list'),
]
