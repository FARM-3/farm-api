from django.db import models

# Create your models here.

# users/models.py
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager


# ============================================
# CUSTOM USER MANAGER
# ============================================
# This handles creating users and superusers
class UserManager(BaseUserManager):
    """
    Manager for our custom User model.
    Provides methods to create regular users and superusers.
    """
    
    def create_user(self, phone, pin, name="", role="block_champion", security_question="", security_answer="", is_staff=False, is_superuser=False):
        """
        Creates and saves a regular user with phone, pin, and security details.

        Args:
            phone (str): User's phone number (acts as username)
            pin (str): 4-digit PIN for login
            name (str): User's full name
            role (str): User role (manager, block_champion, etc.)
            security_question (str): Question for PIN reset
            security_answer (str): Answer to security question

        Returns:
            User: The created user instance
        """
        if not phone:
            raise ValueError("Users must have a phone number")
        if not pin:
            raise ValueError("Users must have a PIN")

        # Create user instance
        user = self.model(
            phone=phone,
            name=name,
            role=role,
            security_question=security_question,
            is_staff=is_staff,
            is_superuser=is_superuser
        )

        # Hash and store PIN securely (never store raw PIN)
        user.set_password(pin)

        # Hash and store security answer securely
        if security_answer:
            user.set_security_answer(security_answer)

        user.save(using=self._db)
        return user
    

    def create_superuser(self, phone, **extra_fields):
        """
        Creates a superuser (admin) with full permissions.
        Converts Django's 'password' input into 'pin'.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        # Django creates a 'password' field by default; treat it as pin
        pin = extra_fields.pop('password', None)
        if pin is None:
            raise ValueError('Superuser must have a PIN (password field used as PIN)')

        return self.create_user(phone=phone, pin=pin, role="admin", **extra_fields)


# ============================================
# CUSTOM USER MODEL
# ============================================
class User(AbstractBaseUser):
    """
    Custom user model for farm management system.
    Uses phone number as username and 4-digit PIN for authentication.
    """
    
    # Role choices for different user types
    ROLE_CHOICES = [
        ("manager", "Farm Manager"),          # Web app user
        ("block_champion", "Block Champion"),  # Mobile app user
        ("admin", "Admin"),                    # System admin
        ("superadmin", "Super Admin"),         # Future use
    ]
    
    # ---- Core Fields ----
    name = models.CharField(
        max_length=100,
        blank=True,
        help_text="User's full name"
    )

    phone = models.CharField(
        max_length=20,
        unique=True,
        help_text="Phone number used for login"
    )

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default="block_champion",
        help_text="User's role in the system"
    )
    
    # ---- Security Fields ----
    security_question = models.CharField(
        max_length=200,
        blank=True,
        help_text="Question for PIN reset (e.g., 'What is your mother's name?')"
    )
    
    _security_answer_hash = models.CharField(
        max_length=128,
        blank=True,
        help_text="Hashed security answer (never stored in plain text)"
    )
    
    # ---- Django Required Fields ----
    is_active = models.BooleanField(
        default=True,
        help_text="User can login if active"
    )
    
    is_staff = models.BooleanField(
        default=False,
        help_text="User can access Django admin"
    )
    
    is_superuser = models.BooleanField(
        default=False,
        help_text="User has all permissions"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # ---- Manager and Settings ----
    objects = UserManager()
    
    USERNAME_FIELD = "phone"      # Login with phone instead of username
    REQUIRED_FIELDS = ["name"]    # Name required for createsuperuser
    
    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"
        ordering = ["-created_at"]
    
    def __str__(self):
        if self.name:
            return f"{self.name} - {self.phone} ({self.get_role_display()})"
        return f"{self.phone} ({self.get_role_display()})"
    
    # ---- Security Answer Methods ----
    def set_security_answer(self, raw_answer):
        """
        Hash and store the security answer securely.
        Similar to how Django hashes passwords.
        
        Args:
            raw_answer (str): Plain text security answer
        """
        from django.contrib.auth.hashers import make_password
        self._security_answer_hash = make_password(raw_answer)
    
    def check_security_answer(self, raw_answer):
        """
        Check if provided answer matches the stored hashed answer.
        
        Args:
            raw_answer (str): Plain text answer to check
        
        Returns:
            bool: True if answer matches, False otherwise
        """
        from django.contrib.auth.hashers import check_password
        if not self._security_answer_hash:
            return False
        return check_password(raw_answer, self._security_answer_hash)
    
    # ---- Permission Methods (required by Django) ----
    def has_perm(self, perm, obj=None):
        """Does the user have a specific permission?"""
        return self.is_superuser
    
    def has_module_perms(self, app_label):
        """Does the user have permissions to view the app?"""
        return self.is_superuser