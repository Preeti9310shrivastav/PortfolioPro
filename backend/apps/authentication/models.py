import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from apps.common.models import TimeStampedModel

class User(AbstractUser):
    """
    Custom user model supporting UUID primary keys and RBAC
    for Customer, Finance Officer, and Administrator roles.
    """
    ROLE_CUSTOMER = 'CUSTOMER'
    ROLE_FINANCE_OFFICER = 'FINANCE_OFFICER'
    ROLE_ADMIN = 'ADMIN'

    ROLE_CHOICES = (
        (ROLE_CUSTOMER, 'Customer / Retail Investor'),
        (ROLE_FINANCE_OFFICER, 'Finance Officer / Compliance'),
        (ROLE_ADMIN, 'System Administrator'),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True, db_index=True)
    role = models.CharField(max_length=30, choices=ROLE_CHOICES, default=ROLE_CUSTOMER, db_index=True)
    phone_number = models.CharField(max_length=20, blank=True, default='')
    updated_at = models.DateTimeField(auto_now=True)

    REQUIRED_FIELDS = ['email', 'first_name', 'last_name']

    class Meta:
        db_table = 'users'
        ordering = ['-date_joined']

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"

    @property
    def is_customer(self):
        return self.role == self.ROLE_CUSTOMER

    @property
    def is_finance_officer(self):
        return self.role == self.ROLE_FINANCE_OFFICER or self.is_superuser


class UserProfile(TimeStampedModel):
    """
    Extended profile storing personal details, bio, and geographic metadata.
    """
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='profile')
    avatar_url = models.URLField(max_length=500, blank=True, default='')
    bio = models.TextField(blank=True, default='')
    city = models.CharField(max_length=100, blank=True, default='')
    state = models.CharField(max_length=100, blank=True, default='')
    country = models.CharField(max_length=100, default='India')
    pincode = models.CharField(max_length=20, blank=True, default='')

    class Meta:
        db_table = 'user_profiles'
        ordering = ['-created_at']

    def __str__(self):
        return f"Profile of {self.user.username}"
