from django.contrib import admin
from .models import AdminUser, PasswordResetOTP, EmailVerification


# ============================================
# ADMIN USER ADMIN
# ============================================
@admin.register(AdminUser)
class AdminUserAdmin(admin.ModelAdmin):
    """
    Admin configuration for AdminUser model.
    """
    list_display = ['email', 'name', 'role', 'is_active', 'is_email_verified', 'is_staff', 'created_at']
    list_filter = ['role', 'is_active', 'is_email_verified', 'is_staff', 'created_at']
    search_fields = ['email', 'name']
    ordering = ['-created_at']
    readonly_fields = ['created_at', 'updated_at']

    fieldsets = (
        ('Account Info', {
            'fields': ('email', 'name', 'password')
        }),
        ('Permissions', {
            'fields': ('role', 'is_active', 'is_staff', 'is_superuser', 'is_email_verified')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )


# ============================================
# PASSWORD RESET OTP ADMIN
# ============================================
@admin.register(PasswordResetOTP)
class PasswordResetOTPAdmin(admin.ModelAdmin):
    """
    Admin configuration for PasswordResetOTP model.
    """
    list_display = ['admin_user', 'otp_code', 'is_verified', 'is_used', 'created_at', 'expires_at']
    list_filter = ['is_verified', 'is_used', 'created_at']
    search_fields = ['admin_user__email', 'otp_code']
    ordering = ['-created_at']
    readonly_fields = ['created_at', 'expires_at']


# ============================================
# EMAIL VERIFICATION ADMIN
# ============================================
@admin.register(EmailVerification)
class EmailVerificationAdmin(admin.ModelAdmin):
    """
    Admin configuration for EmailVerification model.
    """
    list_display = ['admin_user', 'token', 'is_verified', 'created_at', 'expires_at']
    list_filter = ['is_verified', 'created_at']
    search_fields = ['admin_user__email', 'token']
    ordering = ['-created_at']
    readonly_fields = ['token', 'created_at', 'expires_at']
