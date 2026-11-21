"""
Role-Based Access Control (RBAC) Permissions for PortfolioPro.
"""
from rest_framework.permissions import BasePermission
from apps.authentication.models import User

class IsCustomer(BasePermission):
    """
    Grants access only to authenticated users with the Customer role.
    """
    message = "Access restricted to Customer accounts only."

    def has_permission(self, request, view):
        return bool(
            request.user and
            request.user.is_authenticated and
            request.user.role == User.ROLE_CUSTOMER
        )


class IsFinanceOfficer(BasePermission):
    """
    Grants access only to Finance Officers or Administrators.
    Customers are strictly prohibited.
    """
    message = "Access restricted to Finance Officers and Compliance Administrators only."

    def has_permission(self, request, view):
        return bool(
            request.user and
            request.user.is_authenticated and
            (request.user.role == User.ROLE_FINANCE_OFFICER or request.user.is_staff or request.user.is_superuser)
        )


class IsAdminUser(BasePermission):
    """
    Grants access strictly to System Administrators.
    """
    message = "Access restricted to System Administrators only."

    def has_permission(self, request, view):
        return bool(
            request.user and
            request.user.is_authenticated and
            (request.user.role == User.ROLE_ADMIN or request.user.is_superuser)
        )
