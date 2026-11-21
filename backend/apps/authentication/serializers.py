"""
Serializers for PortfolioPro Authentication Module.
Adheres strictly to PEP 8, explicit field lists, and field/cross-field validation.
"""
from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str
from django.contrib.auth.tokens import default_token_generator
from rest_framework_simplejwt.tokens import RefreshToken
from apps.authentication.models import User, UserProfile
from apps.accounts.models import TradingAccount
from apps.portfolio.models import Portfolio
import re
import uuid

class UserProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for UserProfile entity.
    """
    class Meta:
        model = UserProfile
        fields = [
            'avatar_url',
            'bio',
            'city',
            'state',
            'country',
            'pincode',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['created_at', 'updated_at']


class UserDetailSerializer(serializers.ModelSerializer):
    """
    Complete user details serializer with nested profile.
    """
    profile = UserProfileSerializer(read_only=True)

    class Meta:
        model = User
        fields = [
            'id',
            'username',
            'email',
            'role',
            'first_name',
            'last_name',
            'phone_number',
            'is_active',
            'date_joined',
            'last_login',
            'profile',
        ]
        read_only_fields = ['id', 'role', 'is_active', 'date_joined', 'last_login']


class UserRegistrationSerializer(serializers.ModelSerializer):
    """
    Registration serializer enforcing password complexity, confirmation match,
    and strictly forbidding user self-promotion to privileged roles.
    """
    password = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'},
        min_length=8
    )
    password_confirm = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'},
        min_length=8
    )
    role = serializers.CharField(required=False, default=User.ROLE_CUSTOMER)

    class Meta:
        model = User
        fields = [
            'username',
            'email',
            'password',
            'password_confirm',
            'first_name',
            'last_name',
            'phone_number',
            'role',
        ]

    def validate_username(self, value):
        if not re.match(r'^[a-zA-Z0-9_.-]+$', value):
            raise serializers.ValidationError(
                "Username may only contain alphanumeric characters, underscores, dashes, and periods."
            )
        if User.objects.filter(username__iexact=value).exists():
            raise serializers.ValidationError("A user with this username already exists.")
        return value

    def validate_email(self, value):
        email_clean = value.lower().strip()
        if User.objects.filter(email__iexact=email_clean).exists():
            raise serializers.ValidationError("A user with this email address already exists.")
        return email_clean

    def validate_role(self, value):
        # Security Guardrail: Public registration CANNOT grant Finance Officer or Admin roles
        if value and value.upper() != User.ROLE_CUSTOMER:
            raise serializers.ValidationError(
                "Self-promotion to privileged roles (Finance Officer / Administrator) is strictly prohibited. "
                "All public signups are registered as Customers."
            )
        return User.ROLE_CUSTOMER

    def validate(self, data):
        if data.get('password') != data.get('password_confirm'):
            raise serializers.ValidationError({
                "password_confirm": ["Passwords do not match."]
            })
        
        # Django standard password complexity validation
        temp_user = User(
            username=data.get('username'),
            email=data.get('email'),
            first_name=data.get('first_name', ''),
            last_name=data.get('last_name', '')
        )
        validate_password(data.get('password'), temp_user)
        return data

    def create(self, validated_data):
        validated_data.pop('password_confirm', None)
        password = validated_data.pop('password')
        role = validated_data.get('role', User.ROLE_CUSTOMER)

        # Create user with properly hashed password
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=password,
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            phone_number=validated_data.get('phone_number', ''),
            role=role
        )

        # Create user profile
        UserProfile.objects.create(user=user)

        # If customer, auto-provision default TradingAccount and Portfolio
        if user.role == User.ROLE_CUSTOMER:
            account_num = f"PPRO-{user.id.hex[:6].upper()}"
            TradingAccount.objects.create(
                user=user,
                account_number=account_num,
                currency='INR'
            )
            Portfolio.objects.create(
                user=user,
                name='Primary Portfolio',
                is_default=True
            )

        return user


class LoginSerializer(serializers.Serializer):
    """
    Login serializer accepting username/email and password.
    """
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True, write_only=True)

    def validate(self, data):
        username_or_email = data.get('username')
        password = data.get('password')

        user = None
        # Check if email was provided instead of username
        if '@' in username_or_email:
            try:
                user_obj = User.objects.get(email__iexact=username_or_email)
                username_or_email = user_obj.username
            except User.DoesNotExist:
                user_obj = None

        user = authenticate(username=username_or_email, password=password)

        if not user:
            raise serializers.ValidationError({
                "credentials": ["Invalid username/email or password."]
            })

        if not user.is_active:
            raise serializers.ValidationError({
                "account": ["Your account has been deactivated. Please contact support."]
            })

        data['user'] = user
        return data


class LogoutSerializer(serializers.Serializer):
    """
    Logout serializer requiring refresh token to add to server blacklist.
    """
    refresh = serializers.CharField(required=True)

    def validate(self, data):
        self.token = data['refresh']
        return data

    def save(self, **kwargs):
        try:
            refresh_token = RefreshToken(self.token)
            refresh_token.blacklist()
        except Exception:
            raise serializers.ValidationError({
                "refresh": ["Invalid or already expired/blacklisted refresh token."]
            })


class PasswordChangeSerializer(serializers.Serializer):
    """
    Password change serializer for authenticated users.
    """
    old_password = serializers.CharField(required=True, write_only=True)
    new_password = serializers.CharField(required=True, write_only=True, min_length=8)
    new_password_confirm = serializers.CharField(required=True, write_only=True, min_length=8)

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Current password is incorrect.")
        return value

    def validate(self, data):
        if data['new_password'] != data['new_password_confirm']:
            raise serializers.ValidationError({
                "new_password_confirm": ["New passwords do not match."]
            })
        if data['old_password'] == data['new_password']:
            raise serializers.ValidationError({
                "new_password": ["New password must be different from current password."]
            })
        
        user = self.context['request'].user
        validate_password(data['new_password'], user)
        return data

    def save(self, **kwargs):
        user = self.context['request'].user
        user.set_password(self.validated_data['new_password'])
        user.save()
        return user


class PasswordResetRequestSerializer(serializers.Serializer):
    """
    Password reset request serializer accepting registered user email.
    """
    email = serializers.EmailField(required=True)

    def validate_email(self, value):
        return value.lower().strip()


class PasswordResetConfirmSerializer(serializers.Serializer):
    """
    Password reset confirmation serializer with uidb64, token, and new password.
    """
    uidb64 = serializers.CharField(required=True)
    token = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, write_only=True, min_length=8)
    new_password_confirm = serializers.CharField(required=True, write_only=True, min_length=8)

    def validate(self, data):
        if data['new_password'] != data['new_password_confirm']:
            raise serializers.ValidationError({
                "new_password_confirm": ["New passwords do not match."]
            })

        try:
            uid = force_str(urlsafe_base64_decode(data['uidb64']))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            raise serializers.ValidationError({
                "uidb64": ["Invalid user identifier."]
            })

        if not default_token_generator.check_token(user, data['token']):
            raise serializers.ValidationError({
                "token": ["Reset token is invalid or has expired."]
            })

        validate_password(data['new_password'], user)
        data['user'] = user
        return data

    def save(self, **kwargs):
        user = self.validated_data['user']
        user.set_password(self.validated_data['new_password'])
        user.save()
        return user


class UserProfileUpdateSerializer(serializers.Serializer):
    """
    Serializer to update both User and nested UserProfile attributes.
    """
    first_name = serializers.CharField(required=False, max_length=150)
    last_name = serializers.CharField(required=False, max_length=150)
    phone_number = serializers.CharField(required=False, max_length=20)
    avatar_url = serializers.URLField(required=False, allow_blank=True, max_length=500)
    bio = serializers.CharField(required=False, allow_blank=True)
    city = serializers.CharField(required=False, allow_blank=True, max_length=100)
    state = serializers.CharField(required=False, allow_blank=True, max_length=100)
    country = serializers.CharField(required=False, allow_blank=True, max_length=100)
    pincode = serializers.CharField(required=False, allow_blank=True, max_length=20)

    def update(self, instance, validated_data):
        # Update user fields
        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        instance.phone_number = validated_data.get('phone_number', instance.phone_number)
        instance.save()

        # Update profile fields
        profile = getattr(instance, 'profile', None)
        if not profile:
            profile = UserProfile.objects.create(user=instance)

        profile.avatar_url = validated_data.get('avatar_url', profile.avatar_url)
        profile.bio = validated_data.get('bio', profile.bio)
        profile.city = validated_data.get('city', profile.city)
        profile.state = validated_data.get('state', profile.state)
        profile.country = validated_data.get('country', profile.country)
        profile.pincode = validated_data.get('pincode', profile.pincode)
        profile.save()

        return instance
