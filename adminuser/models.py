from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.utils import timezone
import random
import string
import uuid
from datetime import timedelta


# ============================================
# ADMIN USER MANAGER
# ============================================
class AdminUserManager(BaseUserManager):
    """
    Manager for AdminUser model.
    Handles creating admin users with email and password.
    """

    def create_user(self, email, password, name="", role="admin", is_staff=False, is_superuser=False):
        """
        Creates and saves an admin user with email and password.

        Args:
            email (str): Admin user's email address
            password (str): Admin user's password
            name (str): Admin user's full name
            role (str): Admin role (admin, superadmin, etc.)
            is_staff (bool): Can access Django admin
            is_superuser (bool): Has all permissions

        Returns:
            AdminUser: The created admin user instance
        """
        if not email:
            raise ValueError("Admin users must have an email address")
        if not password:
            raise ValueError("Admin users must have a password")

        # Normalize email (lowercase domain)
        email = self.normalize_email(email)

        # Create admin user instance
        user = self.model(
            email=email,
            name=name,
            role=role,
            is_staff=is_staff,
            is_superuser=is_superuser
        )

        # Hash and store password securely
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """
        Creates a superuser (admin) with full permissions.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if password is None:
            raise ValueError('Superuser must have a password')

        return self.create_user(
            email=email,
            password=password,
            role="superadmin",
            **extra_fields
        )


# ============================================
# ADMIN USER MODEL
# ============================================
class AdminUser(AbstractBaseUser):
    """
    Custom admin user model for website administration.
    Uses email and password for authentication.
    """

    # Role choices for different admin types
    ROLE_CHOICES = [
        ("admin", "Admin"),                    # Regular admin
        ("superadmin", "Super Admin"),         # Full access admin
        ("manager", "Manager"),                # Manager level
    ]

    # ---- Core Fields ----
    name = models.CharField(
        max_length=100,
        blank=True,
        help_text="Admin user's full name"
    )

    email = models.EmailField(
        max_length=255,
        unique=True,
        help_text="Email address used for login"
    )

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default="admin",
        help_text="Admin user's role in the system"
    )

    # ---- Django Required Fields ----
    is_active = models.BooleanField(
        default=True,
        help_text="Admin user can login if active"
    )

    is_staff = models.BooleanField(
        default=True,
        help_text="Admin user can access Django admin"
    )

    is_superuser = models.BooleanField(
        default=False,
        help_text="Admin user has all permissions"
    )

    is_email_verified = models.BooleanField(
        default=False,
        help_text="Whether the admin user's email has been verified"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # ---- Manager and Settings ----
    objects = AdminUserManager()

    USERNAME_FIELD = "email"        # Login with email instead of username
    REQUIRED_FIELDS = ["name"]      # Name required for createsuperuser

    class Meta:
        verbose_name = "Admin User"
        verbose_name_plural = "Admin Users"
        ordering = ["-created_at"]

    def __str__(self):
        if self.name:
            return f"{self.name} - {self.email} ({self.get_role_display()})"
        return f"{self.email} ({self.get_role_display()})"

    # ---- Permission Methods (required by Django) ----
    def has_perm(self, perm, obj=None):
        """Does the admin user have a specific permission?"""
        return self.is_superuser

    def has_module_perms(self, app_label):
        """Does the admin user have permissions to view the app?"""
        return self.is_superuser or self.is_staff


# ============================================
# PASSWORD RESET OTP MODEL
# ============================================
class PasswordResetOTP(models.Model):
    """
    Model to store OTP codes for password reset.
    Each OTP is valid for 10 minutes and can only be used once.
    """

    admin_user = models.ForeignKey(
        AdminUser,
        on_delete=models.CASCADE,
        related_name='password_reset_otps',
        help_text="Admin user requesting password reset"
    )

    otp_code = models.CharField(
        max_length=6,
        help_text="6-digit OTP code"
    )

    is_verified = models.BooleanField(
        default=False,
        help_text="Whether OTP has been verified"
    )

    is_used = models.BooleanField(
        default=False,
        help_text="Whether OTP has been used for password reset"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(
        help_text="OTP expiration time (10 minutes from creation)"
    )

    class Meta:
        verbose_name = "Password Reset OTP"
        verbose_name_plural = "Password Reset OTPs"
        ordering = ["-created_at"]

    def __str__(self):
        return f"OTP for {self.admin_user.email} - {self.otp_code}"

    def save(self, *args, **kwargs):
        """
        Override save to auto-generate OTP and expiration time.
        """
        if not self.otp_code:
            # Generate 6-digit OTP
            self.otp_code = ''.join(random.choices(string.digits, k=6))

        if not self.expires_at:
            # Set expiration to 10 minutes from now
            from datetime import timedelta
            self.expires_at = timezone.now() + timedelta(minutes=10)

        super().save(*args, **kwargs)

    def is_valid(self):
        """
        Check if OTP is still valid (not expired, not used).
        """
        return (
            not self.is_used and
            timezone.now() < self.expires_at
        )

    def mark_as_used(self):
        """
        Mark OTP as used after successful password reset.
        """
        self.is_used = True
        self.save()


# ============================================
# EMAIL VERIFICATION MODEL
# ============================================
class EmailVerification(models.Model):
    """
    Model to store email verification tokens.
    Each token is valid for 24 hours and can only be used once.
    """

    admin_user = models.ForeignKey(
        AdminUser,
        on_delete=models.CASCADE,
        related_name='email_verifications',
        help_text="Admin user requesting email verification"
    )

    token = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        unique=True,
        help_text="Unique verification token"
    )

    is_verified = models.BooleanField(
        default=False,
        help_text="Whether email has been verified"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(
        help_text="Token expiration time (24 hours from creation)"
    )

    class Meta:
        verbose_name = "Email Verification"
        verbose_name_plural = "Email Verifications"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Email verification for {self.admin_user.email}"

    def save(self, *args, **kwargs):
        """
        Override save to auto-set expiration time.
        """
        if not self.expires_at:
            # Set expiration to 24 hours from now
            self.expires_at = timezone.now() + timedelta(hours=24)

        super().save(*args, **kwargs)

    def is_valid(self):
        """
        Check if token is still valid (not expired, not used).
        """
        return (
            not self.is_verified and
            timezone.now() < self.expires_at
        )

    def mark_as_verified(self):
        """
        Mark token as verified and update admin user's email verification status.
        """
        self.is_verified = True
        self.save()

        # Update admin user's email verification status
        self.admin_user.is_email_verified = True
        self.admin_user.save()
