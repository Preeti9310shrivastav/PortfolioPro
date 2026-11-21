"""
Views for PortfolioPro Authentication & Role-Based Access Control Module.
"""
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.conf import settings
from django.db import models
from rest_framework.views import APIView
from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from drf_spectacular.utils import extend_schema, OpenApiResponse

from apps.authentication.models import User
from apps.authentication.serializers import (
    UserRegistrationSerializer,
    LoginSerializer,
    LogoutSerializer,
    UserDetailSerializer,
    UserProfileUpdateSerializer,
    PasswordChangeSerializer,
    PasswordResetRequestSerializer,
    PasswordResetConfirmSerializer,
)
from apps.common.responses import api_success, api_error
from apps.common.permissions import IsCustomer, IsFinanceOfficer, IsAdminUser
import logging

logger = logging.getLogger(__name__)

class RegisterView(APIView):
    """
    Public endpoint for new customer registration.
    Enforces password complexity and restricts self-promotion to privileged roles.
    """
    permission_classes = [AllowAny]

    @extend_schema(
        request=UserRegistrationSerializer,
        responses={201: OpenApiResponse(description="User registered successfully.")}
    )
    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)
            user_data = UserDetailSerializer(user).data
            logger.info(f"New customer registered: {user.username} ({user.email})")

            return api_success(
                data={
                    "user": user_data,
                    "tokens": {
                        "access": str(refresh.access_token),
                        "refresh": str(refresh),
                    }
                },
                message="Account registered successfully. Welcome to PortfolioPro!",
                status_code=status.HTTP_201_CREATED
            )
        return api_error(
            message="Registration validation failed.",
            errors=serializer.errors,
            status_code=status.HTTP_400_BAD_REQUEST
        )


class LoginView(APIView):
    """
    Public endpoint to authenticate credentials and issue JWT tokens.
    """
    permission_classes = [AllowAny]

    @extend_schema(
        request=LoginSerializer,
        responses={200: OpenApiResponse(description="Login successful.")}
    )
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            refresh = RefreshToken.for_user(user)
            user_data = UserDetailSerializer(user).data
            logger.info(f"User logged in: {user.username} [Role: {user.role}]")

            return api_success(
                data={
                    "user": user_data,
                    "tokens": {
                        "access": str(refresh.access_token),
                        "refresh": str(refresh),
                    }
                },
                message="Logged in successfully."
            )
        return api_error(
            message="Invalid credentials.",
            errors=serializer.errors,
            status_code=status.HTTP_401_UNAUTHORIZED
        )


class LogoutView(APIView):
    """
    Protected endpoint to blacklist the current refresh token upon sign-out.
    """
    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=LogoutSerializer,
        responses={200: OpenApiResponse(description="Logout successful.")}
    )
    def post(self, request):
        serializer = LogoutSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            logger.info(f"User logged out: {request.user.username}")
            return api_success(message="Logged out successfully. Token blacklisted.")
        return api_error(
            message="Logout failed.",
            errors=serializer.errors,
            status_code=status.HTTP_400_BAD_REQUEST
        )


class ProfileView(APIView):
    """
    Protected endpoint to retrieve or update the authenticated user's profile.
    """
    permission_classes = [IsAuthenticated]

    @extend_schema(responses={200: UserDetailSerializer})
    def get(self, request):
        serializer = UserDetailSerializer(request.user)
        return api_success(
            data={"user": serializer.data},
            message="Profile retrieved successfully."
        )

    @extend_schema(request=UserProfileUpdateSerializer, responses={200: UserDetailSerializer})
    def put(self, request):
        return self._update_profile(request)

    @extend_schema(request=UserProfileUpdateSerializer, responses={200: UserDetailSerializer})
    def patch(self, request):
        return self._update_profile(request)

    def _update_profile(self, request):
        serializer = UserProfileUpdateSerializer(data=request.data)
        if serializer.is_valid():
            updated_user = serializer.update(request.user, serializer.validated_data)
            return api_success(
                data={"user": UserDetailSerializer(updated_user).data},
                message="Profile updated successfully."
            )
        return api_error(
            message="Profile update validation failed.",
            errors=serializer.errors,
            status_code=status.HTTP_400_BAD_REQUEST
        )


class PasswordChangeView(APIView):
    """
    Protected endpoint allowing users to change their account password.
    """
    permission_classes = [IsAuthenticated]

    @extend_schema(request=PasswordChangeSerializer)
    def post(self, request):
        serializer = PasswordChangeSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            logger.info(f"Password changed successfully for user: {request.user.username}")
            return api_success(message="Password changed successfully.")
        return api_error(
            message="Password change failed.",
            errors=serializer.errors,
            status_code=status.HTTP_400_BAD_REQUEST
        )


class PasswordResetRequestView(APIView):
    """
    Public endpoint to initiate password reset via email token.
    """
    permission_classes = [AllowAny]

    @extend_schema(request=PasswordResetRequestSerializer)
    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            user = User.objects.filter(email__iexact=email).first()

            reset_data = {}
            if user and user.is_active:
                token = default_token_generator.make_token(user)
                uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
                reset_link = f"{settings.FRONTEND_URL}/reset-password?uid={uidb64}&token={token}"

                subject = "PortfolioPro — Password Reset Request"
                message_body = (
                    f"Hello {user.first_name or user.username},\n\n"
                    f"A password reset request was received for your PortfolioPro account.\n"
                    f"Click the link below to set a new password:\n{reset_link}\n\n"
                    f"If you did not request this, please ignore this email.\n"
                )
                try:
                    send_mail(
                        subject,
                        message_body,
                        settings.DEFAULT_FROM_EMAIL,
                        [user.email],
                        fail_silently=False,
                    )
                except Exception as e:
                    logger.warning(f"Email sending failed: {e}")

                # For developer / testing evaluation when DEBUG is True
                if settings.DEBUG:
                    reset_data = {
                        "uidb64": uidb64,
                        "token": token,
                        "reset_link": reset_link
                    }

            # Return success even if email not found to prevent user enumeration
            return api_success(
                data=reset_data,
                message="If an account with that email exists, password reset instructions have been dispatched."
            )
        return api_error(
            message="Invalid request.",
            errors=serializer.errors,
            status_code=status.HTTP_400_BAD_REQUEST
        )


class PasswordResetConfirmView(APIView):
    """
    Public endpoint to confirm password reset with token and new password.
    """
    permission_classes = [AllowAny]

    @extend_schema(request=PasswordResetConfirmSerializer)
    def post(self, request):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return api_success(message="Password has been reset successfully. You may now log in.")
        return api_error(
            message="Password reset confirmation failed.",
            errors=serializer.errors,
            status_code=status.HTTP_400_BAD_REQUEST
        )


class CustomerDashboardAccessView(APIView):
    """
    Protected endpoint strictly restricted to Customer role.
    """
    permission_classes = [IsAuthenticated, IsCustomer]

    def get(self, request):
        return api_success(
            data={
                "username": request.user.username,
                "role": request.user.role,
                "account_number": getattr(getattr(request.user, 'trading_account', None), 'account_number', 'N/A'),
            },
            message="Access granted to Customer Trading Portal."
        )


class FinanceOfficerConsoleAccessView(APIView):
    """
    Protected endpoint strictly restricted to Finance Officer or Admin roles.
    """
    permission_classes = [IsAuthenticated, IsFinanceOfficer]

    def get(self, request):
        total_users = User.objects.count()
        total_customers = User.objects.filter(role=User.ROLE_CUSTOMER).count()
        return api_success(
            data={
                "officer_name": request.user.username,
                "role": request.user.role,
                "system_metrics": {
                    "total_users": total_users,
                    "total_customers": total_customers,
                }
            },
            message="Access granted to Finance Officer Supervisory Console."
        )


class UserManagementListView(APIView):
    """
    Protected supervisory view for Finance Officers to list, filter, and audit users.
    """
    permission_classes = [IsAuthenticated, IsFinanceOfficer]

    def get(self, request):
        role_filter = request.query_args = request.query_params.get('role')
        search_query = request.query_params.get('search')

        queryset = User.objects.all().select_related('profile')
        if role_filter:
            queryset = queryset.filter(role=role_filter.upper())
        if search_query:
            queryset = queryset.filter(
                models.Q(username__icontains=search_query) |
                models.Q(email__icontains=search_query) |
                models.Q(first_name__icontains=search_query) |
                models.Q(last_name__icontains=search_query)
            )

        serializer = UserDetailSerializer(queryset[:50], many=True)
        return api_success(
            data={
                "count": queryset.count(),
                "users": serializer.data
            },
            message="User accounts retrieved successfully."
        )
