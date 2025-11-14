# adminuser/serializers.py
from rest_framework import serializers
from .models import AdminUser
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
            'created_at'
        ]
        read_only_fields = ['id', 'created_at']


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
