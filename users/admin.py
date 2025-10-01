from django.contrib import admin

# Register your models here.
# users/admin.py
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django import forms
from .models import User


# ============================================
# CUSTOM FORMS FOR ADMIN
# ============================================

class UserCreationForm(forms.ModelForm):
    """
    Form for creating new users in Django admin.
    Includes password fields for PIN entry.
    """
    
    pin1 = forms.CharField(
        label='PIN',
        widget=forms.PasswordInput,
        help_text="Enter a 4-digit PIN",
        max_length=4,
        min_length=4
    )
    
    pin2 = forms.CharField(
        label='PIN confirmation',
        widget=forms.PasswordInput,
        help_text="Enter the same PIN again for verification",
        max_length=4,
        min_length=4
    )
    
    security_answer_raw = forms.CharField(
        label='Security Answer',
        required=False,
        help_text="Plain text answer (will be hashed automatically)"
    )
    
    class Meta:
        model = User
        fields = ('phone', 'role', 'security_question')
    
    def clean_pin2(self):
        """Check that the two PIN entries match."""
        pin1 = self.cleaned_data.get("pin1")
        pin2 = self.cleaned_data.get("pin2")
        
        if pin1 and pin2 and pin1 != pin2:
            raise forms.ValidationError("PINs don't match")
        
        return pin2
    
    def save(self, commit=True):
        """Save user with hashed PIN."""
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["pin1"])  # Hash the PIN
        
        # Hash security answer if provided
        security_answer = self.cleaned_data.get('security_answer_raw')
        if security_answer:
            user.set_security_answer(security_answer)
        
        if commit:
            user.save()
        return user


class UserChangeForm(forms.ModelForm):
    """
    Form for updating users in Django admin.
    Shows hashed PIN (read-only) with option to change it.
    """
    
    password = ReadOnlyPasswordHashField(
        label="PIN",
        help_text=(
            "PINs are stored securely hashed. "
            "You can change the PIN using "
            "<a href=\"../password/\">this form</a>."
        )
    )
    
    security_answer_raw = forms.CharField(
        label='New Security Answer',
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Leave blank to keep current'}),
        help_text="Enter new security answer (will be hashed automatically)"
    )
    
    class Meta:
        model = User
        fields = (
            'phone', 
            'password', 
            'role', 
            'security_question',
            'is_active', 
            'is_staff', 
            'is_superuser'
        )
    
    def save(self, commit=True):
        """Save user and update security answer if provided."""
        user = super().save(commit=False)
        
        # Update security answer if a new one was provided
        security_answer = self.cleaned_data.get('security_answer_raw')
        if security_answer:
            user.set_security_answer(security_answer)
        
        if commit:
            user.save()
        return user


# ============================================
# CUSTOM USER ADMIN
# ============================================

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """
    Custom admin interface for User model.
    Allows sysadmin to:
    - View all users
    - Create new users
    - Edit user details
    - Reset PINs
    - Manage security questions/answers
    """
    
    # The forms to add and change user instances
    form = UserChangeForm
    add_form = UserCreationForm

    filter_horizontal = []
    
    # ---- List View Configuration ----
    list_display = [
        'phone',
        'role', 
        'is_active',
        'has_security_question',
        'created_at'
    ]
    
    list_filter = [
        'role', 
        'is_active', 
        'is_staff',
        'created_at'
    ]
    
    search_fields = ['phone']
    
    ordering = ['-created_at']
    
    # ---- Detail View Configuration ----
    fieldsets = (
        # Basic Info Section
        ('Login Information', {
            'fields': ('phone', 'password')
        }),
        
        # Role Section
        ('Role & Permissions', {
            'fields': ('role', 'is_active')
        }),
        
        # Security Section
        ('PIN Reset Security', {
            'fields': ('security_question', 'security_answer_raw'),
            'description': 'Set security question and answer for PIN reset'
        }),
        
        # Admin Permissions (only for superusers)
        ('Admin Permissions', {
            'fields': ('is_staff', 'is_superuser'),
            'classes': ('collapse',),  # Collapsed by default
            'description': 'Only check these for admin users'
        }),
    )
    
    # ---- Add User View Configuration ----
    add_fieldsets = (
        ('Login Information', {
            'classes': ('wide',),
            'fields': ('phone', 'pin1', 'pin2')
        }),
        ('Role', {
            'fields': ('role',)
        }),
        ('PIN Reset Security (Optional)', {
            'fields': ('security_question', 'security_answer_raw'),
            'description': 'Set these so user can reset PIN if forgotten'
        }),
    )
    
    # ---- Custom Methods for List Display ----
    @admin.display(boolean=True, description='Has Security Question')
    def has_security_question(self, obj):
        """Show if user has set up security question."""
        return bool(obj.security_question)
    
    # ---- Permissions ----
    def has_delete_permission(self, request, obj=None):
        """
        Prevent deletion of users (for data integrity).
        Disable users instead by setting is_active=False.
        """
        return False
    
    def get_readonly_fields(self, request, obj=None):
        """Make phone number read-only after creation."""
        if obj:  # Editing existing user
            return ['phone']
        return []


# ============================================
# ADMIN SITE CUSTOMIZATION
# ============================================

# Customize admin site headers
admin.site.site_header = "Farm Management Admin"
admin.site.site_title = "Farm Admin"
admin.site.index_title = "Welcome to Farm Management System"