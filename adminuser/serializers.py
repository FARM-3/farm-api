# adminuser/serializers.py
from rest_framework import serializers
from .models import AdminUser, EmailVerification
import re


# ============================================
# ADMIN USER SERIALIZER (for returning admin user data)
# ============================================
class AdminUserSerializer(serializers.ModelSerializer):
    """
    Serializer for AdminUser model.
    Used to return admin user information in API responses.
    NEVER includes sensitive data like password.
    """

    # Make role human-readable (e.g., "Super Admin" instead of "superadmin")
    role_display = serializers.CharField(source='get_role_display', read_only=True)

    class Meta:
        model = AdminUser
        fields = [
            'id',
            'name',
            'email',
            'role',
            'role_display',
            'is_active',
            'is_email_verified',
            'created_at'
        ]
        read_only_fields = ['id', 'created_at', 'is_email_verified']


# ============================================
# ADMIN LOGIN SERIALIZER
# ============================================
class AdminLoginSerializer(serializers.Serializer):
    """
    Serializer for admin user login.
    Validates email and password format.
    """

    email = serializers.EmailField(
        required=True,
        help_text="Admin user's email address"
    )

    password = serializers.CharField(
        required=True,
        write_only=True,  # Never include password in response
        min_length=4,
        help_text="Admin user's password"
    )

    def validate_email(self, value):
        """
        Ensure email is in valid format.

        Args:
            value (str): The email to validate

        Returns:
            str: Validated email (normalized to lowercase)

        Raises:
            ValidationError: If email is invalid
        """
        # Normalize email to lowercase
        return value.lower()


# ============================================
# REQUEST PASSWORD RESET SERIALIZER
# ============================================
class RequestPasswordResetSerializer(serializers.Serializer):
    """
    Serializer for requesting password reset.
    Admin provides their email and receives OTP.
    """

    email = serializers.EmailField(
        required=True,
        help_text="Admin user's email address"
    )

    def validate_email(self, value):
        """Normalize email to lowercase."""
        return value.lower()


# ============================================
# VERIFY OTP SERIALIZER
# ============================================
class VerifyOTPSerializer(serializers.Serializer):
    """
    Serializer for verifying OTP code.
    Admin provides email and OTP code.
    """

    email = serializers.EmailField(
        required=True,
        help_text="Admin user's email address"
    )

    otp_code = serializers.CharField(
        required=True,
        min_length=6,
        max_length=6,
        help_text="6-digit OTP code"
    )

    def validate_email(self, value):
        """Normalize email to lowercase."""
        return value.lower()

    def validate_otp_code(self, value):
        """Ensure OTP is exactly 6 digits."""
        if not value.isdigit():
            raise serializers.ValidationError("OTP must be numeric")
        if len(value) != 6:
            raise serializers.ValidationError("OTP must be exactly 6 digits")
        return value


# ============================================
# RESET PASSWORD SERIALIZER
# ============================================
class ResetPasswordSerializer(serializers.Serializer):
    """
    Serializer for resetting password after OTP verification.
    Admin provides email, OTP code, and new password.
    """

    email = serializers.EmailField(
        required=True,
        help_text="Admin user's email address"
    )

    otp_code = serializers.CharField(
        required=True,
        min_length=6,
        max_length=6,
        help_text="6-digit OTP code"
    )

    new_password = serializers.CharField(
        required=True,
        write_only=True,
        min_length=6,
        help_text="New password (minimum 6 characters)"
    )

    confirm_password = serializers.CharField(
        required=True,
        write_only=True,
        min_length=6,
        help_text="Confirm new password"
    )

    def validate_email(self, value):
        """Normalize email to lowercase."""
        return value.lower()

    def validate_otp_code(self, value):
        """Ensure OTP is exactly 6 digits."""
        if not value.isdigit():
            raise serializers.ValidationError("OTP must be numeric")
        if len(value) != 6:
            raise serializers.ValidationError("OTP must be exactly 6 digits")
        return value

    def validate(self, data):
        """
        Validate that passwords match.
        """
        if data['new_password'] != data['confirm_password']:
            raise serializers.ValidationError({
                "confirm_password": "Passwords do not match"
            })
        return data


# ============================================
# ADMIN SIGNUP SERIALIZER
# ============================================
class AdminSignupSerializer(serializers.Serializer):
    """
    Serializer for admin user signup/registration.
    Creates a new admin user account.
    """

    name = serializers.CharField(
        required=True,
        max_length=100,
        help_text="Admin user's full name"
    )

    email = serializers.EmailField(
        required=True,
        help_text="Admin user's email address"
    )

    password = serializers.CharField(
        required=True,
        write_only=True,
        min_length=6,
        help_text="Password (minimum 6 characters)"
    )

    confirm_password = serializers.CharField(
        required=True,
        write_only=True,
        min_length=6,
        help_text="Confirm password"
    )

    role = serializers.ChoiceField(
        choices=AdminUser.ROLE_CHOICES,
        default="admin",
        required=False,
        help_text="Admin role (admin, superadmin, manager)"
    )

    def validate_email(self, value):
        """
        Ensure email is unique and normalize to lowercase.
        """
        email = value.lower()
        if AdminUser.objects.filter(email=email).exists():
            raise serializers.ValidationError("An admin user with this email already exists")
        return email

    def validate(self, data):
        """
        Validate that passwords match.
        """
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError({
                "confirm_password": "Passwords do not match"
            })
        return data

    def create(self, validated_data):
        """
        Create new admin user account.
        """
        # Remove confirm_password as it's not needed for creation
        validated_data.pop('confirm_password')

        # Create admin user
        admin_user = AdminUser.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
            name=validated_data.get('name', ''),
            role=validated_data.get('role', 'admin'),
            is_staff=True,
            is_superuser=False
        )

        return admin_user


# ============================================
# SEND VERIFICATION EMAIL SERIALIZER
# ============================================
class SendVerificationEmailSerializer(serializers.Serializer):
    """
    Serializer for sending verification email.
    Admin provides their email to receive verification link.
    """

    email = serializers.EmailField(
        required=True,
        help_text="Admin user's email address"
    )

    def validate_email(self, value):
        """Normalize email to lowercase."""
        return value.lower()


# ============================================
# CHECK VERIFICATION STATUS SERIALIZER
# ============================================
class CheckVerificationSerializer(serializers.Serializer):
    """
    Serializer for checking email verification status.
    """

    email = serializers.EmailField(
        required=True,
        help_text="Admin user's email address"
    )

    def validate_email(self, value):
        """Normalize email to lowercase."""
        return value.lower()


# ============================================
# VERIFY EMAIL TOKEN SERIALIZER
# ============================================
class VerifyEmailTokenSerializer(serializers.Serializer):
    """
    Serializer for verifying email with token.
    """

    token = serializers.UUIDField(
        required=True,
        help_text="Email verification token"
    )
