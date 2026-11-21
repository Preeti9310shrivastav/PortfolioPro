"""
Django Admin registration for User and UserProfile models.
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from apps.authentication.models import User, UserProfile


class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('username', 'email', 'role', 'is_active', 'date_joined')
    list_filter = ('role', 'is_active', 'is_staff')
    inlines = [UserProfileInline]
    fieldsets = BaseUserAdmin.fieldsets + (
        ('PortfolioPro', {'fields': ('role', 'phone_number')}),
    )
