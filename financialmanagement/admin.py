from django.contrib import admin
from .models import Staff

# Register your models here.
from .models import Wage
from .models import Sale, Expense, Balancesheet


class WageAdmin(admin.ModelAdmin):
    
    list_display = (
        'employee_name', 
        'date_of_payment', 
        'monthly_pay', 
        'deduction', 
        'amount_paid', 
        '__str__',
        'calculate_net_salary' 
    )

    list_filter = ('date_of_payment', 'employee_name')

    search_fields = ('employee_name', 'noted_reason')

class SaleAdmin(admin.ModelAdmin):
    list_display = (
        'first_name', 
        'item', 
        'rate', 
        'quantity', 
        'total_amount', 
        'amount', 
        'date_of_payment', 
        'status', 
        'balance', 
        'method_of_payment',
        '__str__'
    )

    list_filter = ('date_of_payment', 'first_name', 'status')

    search_fields = ('first_name', 'item', 'method_of_payment')

class ExpenseAdmin(admin.ModelAdmin):
    list_display = (
        'expense_name', 
        'amount', 
        'date', 
        'category', 
        '__str__'
    )

    list_filter = ('date', 'category')

    search_fields = ('expense_name', 'category')

class BalancesheetAdmin(admin.ModelAdmin):
    list_display = (
        'account_name', 
        'account_type', 
        'balance', 
        'last_updated',
        '__str__'
    )

    list_filter = ('account_type', 'last_updated')

    search_fields = ('account_name', 'account_type')

admin.site.register(Wage, WageAdmin)
admin.site.register(Sale, SaleAdmin)
admin.site.register(Expense, ExpenseAdmin)
admin.site.register(Balancesheet, BalancesheetAdmin)


@admin.register(Staff)
class StaffAdmin(admin.ModelAdmin):
    """
    Admin interface for Staff model
    """
    list_display = [
        'staff_id',
        'get_full_name', 
        'nin', 
        'employment_type', 
        'is_active', 
        'date_hired',
        'district'
    ]
    list_filter = [
        'employment_type', 
        'is_active', 
        'district',
        'date_hired'
    ]
    search_fields = [
        'staff_id',
        'first_name', 
        'last_name', 
        'nin',
        'district',
        'village'
    ]
    ordering = ['staff_id']
    
    fieldsets = (
        ('Staff ID', {
            'fields': ('staff_id',)
        }),
        ('Personal Information', {
            'fields': ('first_name', 'last_name', 'nin')
        }),
        ('Location Details', {
            'fields': ('district', 'sub_county', 'parish', 'village')
        }),
        ('Employment Details', {
            'fields': ('date_hired', 'employment_type', 'is_active')
        }),
        ('System Information', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['staff_id', 'created_at', 'updated_at']
    
    def get_full_name(self, obj):
        """Display full name in list view"""
        return obj.get_full_name()
    get_full_name.short_description = 'Full Name'
    get_full_name.admin_order_field = 'last_name'
    
    actions = ['activate_staff', 'deactivate_staff']
    
    def activate_staff(self, request, queryset):
        """Action to activate selected staff members"""
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} staff member(s) activated.')
    activate_staff.short_description = 'Activate selected staff'
    
    def deactivate_staff(self, request, queryset):
        """Action to deactivate selected staff members"""
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} staff member(s) deactivated.')
    deactivate_staff.short_description = 'Deactivate selected staff'