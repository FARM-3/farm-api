from django.contrib import admin
from django.utils.html import format_html
from .models import Harvests

# Register your models here.

@admin.register(Harvests)
class HarvestsAdmin(admin.ModelAdmin):
    """
    Admin interface for Harvests model
    """
    list_display = [
        'harvest_id',
        'worker_name', 
        'block_id',
        'formatted_weight',
        'date_of_delivery',
        'formatted_amount',
        'get_paid_by_name',
        'created_at'
    ]
    list_filter = [
        'block_id',
        'date_of_delivery',
        'paid_by',
        'created_at'
    ]
    search_fields = [
        'harvest_id',
        'worker_name',
        'paid_by__first_name',
        'paid_by__last_name'
    ]
    readonly_fields = [
        'harvest_id',
        'created_at',
        'updated_at'
    ]
    ordering = ['-date_of_delivery', '-created_at']
    date_hierarchy = 'date_of_delivery'
    
    fieldsets = (
        ('Harvest Information', {
            'fields': (
                'harvest_id',
                'worker_name',
                'block_id',
                'weight_on_delivery',
                'date_of_delivery'
            )
        }),
        ('Payment Information', {
            'fields': (
                'amount_paid',
                'paid_by'
            )
        }),
        ('System Information', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def formatted_weight(self, obj):
        """Display weight with 2 decimal places and unit"""
        return f"{obj.weight_on_delivery:.2f} kg"
    formatted_weight.short_description = 'Weight'
    formatted_weight.admin_order_field = 'weight_on_delivery'
    
    def formatted_amount(self, obj):
        """Display amount with currency formatting"""
        return f"UGX {obj.amount_paid:,.2f}"
    formatted_amount.short_description = 'Amount Paid'
    formatted_amount.admin_order_field = 'amount_paid'
    
    def get_paid_by_name(self, obj):
        """Display the name of staff who processed payment"""
        if obj.paid_by:
            return obj.paid_by.get_full_name()
        return '-'
    get_paid_by_name.short_description = 'Paid By'
    get_paid_by_name.admin_order_field = 'paid_by__last_name'
    
    def get_queryset(self, request):
        """
        Optimize queries by selecting related staff data
        """
        queryset = super().get_queryset(request)
        queryset = queryset.select_related('paid_by')
        return queryset
    
    # Add some custom actions
    actions = ['export_selected_harvests']
    
    def export_selected_harvests(self, request, queryset):
        """
        Action to export selected harvests (placeholder)
        You can implement CSV/Excel export here
        """
        count = queryset.count()
        self.message_user(
            request, 
            f'{count} harvest(s) selected for export. (Export functionality to be implemented)'
        )
    export_selected_harvests.short_description = 'Export selected harvests'