"""
Pytest Test Suite for PortfolioPro Authentication and RBAC Module.
Covers: Registration, Login, Logout, JWT Auth, Password Reset, Profile, and Role Permissions.
"""
import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken
from apps.authentication.models import User, UserProfile
from apps.accounts.models import TradingAccount

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def customer_user(db):
    user = User.objects.create_user(
        username='investor_aarav',
        email='aarav.sharma@test.in',
        password='StrongPassword123!',
        role=User.ROLE_CUSTOMER,
        first_name='Aarav',
        last_name='Sharma',
        phone_number='+91-9811122334'
    )
    UserProfile.objects.get_or_create(user=user, city='Mumbai', state='Maharashtra')
    TradingAccount.objects.get_or_create(user=user, account_number='PPRO-TESTAARAV')
    return user

@pytest.fixture
def finance_officer_user(db):
    user = User.objects.create_user(
        username='fo_deshmukh',
        email='suresh.deshmukh@portfoliopro.in',
        password='StrongPassword123!',
        role=User.ROLE_FINANCE_OFFICER,
        first_name='Suresh',
        last_name='Deshmukh',
        is_staff=True
    )
    UserProfile.objects.get_or_create(user=user, city='Mumbai')
    return user

@pytest.fixture
def customer_client(api_client, customer_user):
    refresh = RefreshToken.for_user(customer_user)
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {str(refresh.access_token)}')
    return api_client

@pytest.fixture
def fo_client(api_client, finance_officer_user):
    refresh = RefreshToken.for_user(finance_officer_user)
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {str(refresh.access_token)}')
    return api_client


# ==============================================================================
# 1. USER REGISTRATION TESTS (P15-US05, P15-US07)
# ==============================================================================

@pytest.mark.django_db
class TestUserRegistration:
    url = reverse('auth-register')

    def test_successful_customer_registration(self, api_client):
        """Verify successful registration auto-creates profile, trading account, and JWT tokens."""
        payload = {
            "username": "new_investor_priya",
            "email": "priya.patel@test.in",
            "password": "SecurePassword123!",
            "password_confirm": "SecurePassword123!",
            "first_name": "Priya",
            "last_name": "Patel",
            "phone_number": "+91-9822233445"
        }
        response = api_client.post(self.url, payload, format='json')
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['status'] == 'success'
        assert 'tokens' in response.data['data']
        assert 'access' in response.data['data']['tokens']

        user = User.objects.get(username="new_investor_priya")
        assert user.role == User.ROLE_CUSTOMER
        assert hasattr(user, 'profile')
        assert hasattr(user, 'trading_account')
        assert user.trading_account.cash_balance == 500000.0

    def test_registration_password_mismatch(self, api_client):
        """Verify registration fails when password and confirmation do not match."""
        payload = {
            "username": "mismatch_user",
            "email": "mismatch@test.in",
            "password": "Password123!",
            "password_confirm": "DifferentPassword123!",
        }
        response = api_client.post(self.url, payload, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data['status'] == 'error'
        assert 'password_confirm' in response.data['errors']

    def test_registration_short_password(self, api_client):
        """Verify registration rejects passwords shorter than 8 characters."""
        payload = {
            "username": "short_pwd_user",
            "email": "short@test.in",
            "password": "short",
            "password_confirm": "short",
        }
        response = api_client.post(self.url, payload, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data['status'] == 'error'

    def test_registration_duplicate_username_and_email(self, api_client, customer_user):
        """Verify duplicate usernames and emails are rejected."""
        payload = {
            "username": customer_user.username,
            "email": "another.email@test.in",
            "password": "StrongPassword123!",
            "password_confirm": "StrongPassword123!",
        }
        response = api_client.post(self.url, payload, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'username' in response.data['errors']

        # Duplicate email test
        payload['username'] = 'completely_new_username'
        payload['email'] = customer_user.email
        response = api_client.post(self.url, payload, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'email' in response.data['errors']

    def test_forbid_self_promotion_to_finance_officer(self, api_client):
        """Security Mandate: Users cannot promote themselves to Finance Officer on public signup."""
        payload = {
            "username": "sneaky_admin_wannabe",
            "email": "sneaky@test.in",
            "password": "StrongPassword123!",
            "password_confirm": "StrongPassword123!",
            "role": "FINANCE_OFFICER"
        }
        response = api_client.post(self.url, payload, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data['status'] == 'error'
        assert 'role' in response.data['errors']
        assert not User.objects.filter(username="sneaky_admin_wannabe").exists()


# ==============================================================================
# 2. LOGIN & AUTHENTICATION TESTS (P15-US07)
# ==============================================================================

@pytest.mark.django_db
class TestUserLogin:
    url = reverse('auth-login')

    def test_successful_login_with_username(self, api_client, customer_user):
        """Verify successful login using username and password."""
        payload = {
            "username": customer_user.username,
            "password": "StrongPassword123!"
        }
        response = api_client.post(self.url, payload, format='json')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['status'] == 'success'
        assert 'tokens' in response.data['data']
        assert 'access' in response.data['data']['tokens']
        assert response.data['data']['user']['username'] == customer_user.username

    def test_successful_login_with_email(self, api_client, customer_user):
        """Verify successful login using email and password."""
        payload = {
            "username": customer_user.email,
            "password": "StrongPassword123!"
        }
        response = api_client.post(self.url, payload, format='json')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['status'] == 'success'
        assert response.data['data']['user']['email'] == customer_user.email

    def test_login_invalid_password(self, api_client, customer_user):
        """Verify login fails with wrong password."""
        payload = {
            "username": customer_user.username,
            "password": "WrongPassword123!"
        }
        response = api_client.post(self.url, payload, format='json')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.data['status'] == 'error'
        assert 'credentials' in response.data['errors']

    def test_login_non_existent_user(self, api_client):
        """Verify login fails for unknown account."""
        payload = {
            "username": "ghost_user_404",
            "password": "SomePassword123!"
        }
        response = api_client.post(self.url, payload, format='json')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.data['status'] == 'error'

    def test_login_deactivated_account(self, api_client, customer_user):
        """Verify deactivated accounts cannot log in."""
        customer_user.is_active = False
        customer_user.save()

        payload = {
            "username": customer_user.username,
            "password": "StrongPassword123!"
        }
        response = api_client.post(self.url, payload, format='json')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.data['status'] == 'error'


# ==============================================================================
# 3. LOGOUT & TOKEN INVALIDATION TESTS
# ==============================================================================

@pytest.mark.django_db
class TestLogoutAndTokenBlacklist:
    logout_url = reverse('auth-logout')
    refresh_url = reverse('token-refresh')

    def test_logout_blacklists_refresh_token(self, customer_user):
        client = APIClient()
        refresh = RefreshToken.for_user(customer_user)
        access_token = str(refresh.access_token)
        refresh_token_str = str(refresh)

        # Authenticate client
        client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')

        # Call logout
        response = client.post(self.logout_url, {"refresh": refresh_token_str}, format='json')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['status'] == 'success'

        # Attempt to use the blacklisted refresh token to obtain a new access token
        refresh_response = client.post(self.refresh_url, {"refresh": refresh_token_str}, format='json')
        assert refresh_response.status_code == status.HTTP_401_UNAUTHORIZED


# ==============================================================================
# 4. PROFILE RETRIEVAL & UPDATE TESTS (P15-US05)
# ==============================================================================

@pytest.mark.django_db
class TestUserProfile:
    url = reverse('auth-profile')

    def test_get_profile_authenticated(self, customer_client, customer_user):
        """Verify authenticated user can retrieve own profile."""
        response = customer_client.get(self.url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['status'] == 'success'
        assert response.data['data']['user']['username'] == customer_user.username
        assert response.data['data']['user']['profile']['city'] == 'Mumbai'

    def test_get_profile_unauthenticated(self, api_client):
        """Verify unauthenticated user receives 401 Unauthorized."""
        response = api_client.get(self.url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_update_profile(self, customer_client, customer_user):
        """Verify user can update personal details and location."""
        payload = {
            "first_name": "Aarav-Updated",
            "city": "Bengaluru",
            "bio": "Quantitative portfolio investor.",
            "pincode": "560001"
        }
        response = customer_client.patch(self.url, payload, format='json')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['data']['user']['first_name'] == "Aarav-Updated"
        assert response.data['data']['user']['profile']['city'] == "Bengaluru"


# ==============================================================================
# 5. PASSWORD CHANGE & RESET TESTS
# ==============================================================================

@pytest.mark.django_db
class TestPasswordWorkflows:
    change_url = reverse('auth-password-change')
    reset_request_url = reverse('auth-password-reset-request')
    reset_confirm_url = reverse('auth-password-reset-confirm')

    def test_password_change_success(self, customer_client, customer_user):
        """Verify authenticated user can change password with valid old password."""
        payload = {
            "old_password": "StrongPassword123!",
            "new_password": "BrandNewPassword2026!",
            "new_password_confirm": "BrandNewPassword2026!"
        }
        response = customer_client.post(self.change_url, payload, format='json')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['status'] == 'success'

        customer_user.refresh_from_db()
        assert customer_user.check_password("BrandNewPassword2026!")

    def test_password_change_wrong_old_password(self, customer_client):
        """Verify password change fails if old password is incorrect."""
        payload = {
            "old_password": "WrongOldPassword!",
            "new_password": "BrandNewPassword2026!",
            "new_password_confirm": "BrandNewPassword2026!"
        }
        response = customer_client.post(self.change_url, payload, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_password_reset_flow(self, api_client, customer_user):
        """Verify complete forgot password -> reset token -> confirm new password flow."""
        # 1. Request reset
        req_resp = api_client.post(self.reset_request_url, {"email": customer_user.email}, format='json')
        assert req_resp.status_code == status.HTTP_200_OK
        assert req_resp.data['status'] == 'success'

        token = req_resp.data['data']['token']
        uidb64 = req_resp.data['data']['uidb64']

        # 2. Confirm reset
        confirm_payload = {
            "uidb64": uidb64,
            "token": token,
            "new_password": "CompletelyResetPassword2026!",
            "new_password_confirm": "CompletelyResetPassword2026!"
        }
        confirm_resp = api_client.post(self.reset_confirm_url, confirm_payload, format='json')
        assert confirm_resp.status_code == status.HTTP_200_OK
        assert confirm_resp.data['status'] == 'success'

        customer_user.refresh_from_db()
        assert customer_user.check_password("CompletelyResetPassword2026!")


# ==============================================================================
# 6. ROLE-BASED ACCESS CONTROL (RBAC) TESTS (P15-US06, P15-US07)
# ==============================================================================

@pytest.mark.django_db
class TestRoleBasedAccessControl:
    customer_portal_url = reverse('auth-customer-portal')
    fo_console_url = reverse('auth-fo-console')
    users_list_url = reverse('auth-users-list')

    def test_customer_cannot_access_finance_officer_console(self, customer_client):
        """Security: Customers must be blocked from Finance Officer console with 403 Forbidden."""
        response = customer_client.get(self.fo_console_url)
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert response.data['status'] == 'error'

    def test_customer_cannot_access_users_audit_list(self, customer_client):
        """Security: Customers cannot view or audit platform user lists."""
        response = customer_client.get(self.users_list_url)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_customer_can_access_customer_portal(self, customer_client):
        """Customers can access customer-designated trading views."""
        response = customer_client.get(self.customer_portal_url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['status'] == 'success'

    def test_finance_officer_can_access_supervisory_console_and_users(self, fo_client):
        """Finance Officers can access console and audit user lists."""
        resp1 = fo_client.get(self.fo_console_url)
        assert resp1.status_code == status.HTTP_200_OK
        assert resp1.data['status'] == 'success'

        resp2 = fo_client.get(self.users_list_url)
        assert resp2.status_code == status.HTTP_200_OK
        assert 'users' in resp2.data['data']

    def test_unauthenticated_request_rejected(self, api_client):
        """Anonymous requests to protected endpoints return 401 Unauthorized."""
        resp1 = api_client.get(self.customer_portal_url)
        assert resp1.status_code == status.HTTP_401_UNAUTHORIZED
        assert resp1.data['status'] == 'error'

        resp2 = api_client.get(self.fo_console_url)
        assert resp2.status_code == status.HTTP_401_UNAUTHORIZED
