from django.contrib import admin

# Register your models here.
# users/admin.py
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django import forms
from .models import User, SecurityQuestion, UserSecurityAnswer


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
        fields = ('name', 'phone', 'role', 'security_question')
    
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
            'name',
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
        'name',
        'phone',
        'role',
        'linked_staff',
        'is_active',
        'has_security_question',
        'has_security_answers_setup',
        'created_at'
    ]
    
    list_filter = [
        'role', 
        'is_active', 
        'is_staff',
        'created_at'
    ]
    
    search_fields = ['name', 'phone']
    
    ordering = ['-created_at']
    
    # ---- Detail View Configuration ----
    fieldsets = (
        # Basic Info Section
        ('User Information', {
            'fields': ('name', 'phone', 'password')
        }),

        # Role Section
        ('Role & Permissions', {
            'fields': ('role', 'is_active', 'staff')
        }),
        
        # Security Section
        ('PIN Reset Security (Legacy)', {
            'fields': ('security_question', 'security_answer_raw'),
            'description': 'Legacy single security question (now using 3-question system)'
        }),

        ('Security Answers Setup', {
            'fields': ('security_answers_set',),
            'description': 'Multi-question security setup (users answer 3 questions on first login)'
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
        ('User Information', {
            'classes': ('wide',),
            'fields': ('name', 'phone', 'pin1', 'pin2')
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
    @admin.display(description='Linked Staff')
    def linked_staff(self, obj):
        """Show linked staff member if any."""
        if obj.staff:
            return f"{obj.staff.get_full_name()} ({obj.staff.staff_id})"
        return "-"

    @admin.display(boolean=True, description='Has Security Question')
    def has_security_question(self, obj):
        """Show if user has set up security question."""
        return bool(obj.security_question)

    @admin.display(boolean=True, description='Security Answers Set')
    def has_security_answers_setup(self, obj):
        """Show if user has completed 3-question security setup."""
        return obj.security_answers_set
    
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
# SECURITY QUESTION ADMIN
# ============================================

@admin.register(SecurityQuestion)
class SecurityQuestionAdmin(admin.ModelAdmin):
    """
    Admin interface for managing security questions.
    Admins can add, edit, enable/disable questions.
    """

    list_display = ['text', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['text']
    readonly_fields = ['created_at', 'updated_at']

    fieldsets = (
        ('Question', {
            'fields': ('text', 'is_active')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    ordering = ['-created_at']


# ============================================
# USER SECURITY ANSWER ADMIN
# ============================================

@admin.register(UserSecurityAnswer)
class UserSecurityAnswerAdmin(admin.ModelAdmin):
    """
    Admin interface for viewing user security answers.
    Admins can view which users have answered which questions.
    Answers are always hashed - never displayed in plain text.
    """

    list_display = ['user', 'question', 'created_at']
    list_filter = ['user', 'question', 'created_at']
    search_fields = ['user__phone', 'user__name', 'question__text']
    readonly_fields = ['user', 'question', 'answer_hash', 'created_at', 'updated_at']

    fieldsets = (
        ('Information', {
            'fields': ('user', 'question')
        }),
        ('Answer', {
            'fields': ('answer_hash',),
            'description': 'Answer is stored securely hashed - never in plain text'
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    ordering = ['-created_at']

    def has_add_permission(self, request):
        """Prevent manual addition of answers - only via API."""
        return False

    def has_delete_permission(self, request, obj=None):
        """Prevent deletion of answers."""
        return False


# ============================================
# ADMIN SITE CUSTOMIZATION
# ============================================

# Customize admin site headers
admin.site.site_header = "Farm Management Admin"
admin.site.site_title = "Farm Admin"
admin.site.index_title = "Welcome to Farm Management System"