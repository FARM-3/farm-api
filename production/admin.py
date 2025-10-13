from django.contrib import admin
<<<<<<< HEAD
=======
<<<<<<< HEAD

# Register your models here.
=======
>>>>>>> 447798b3a9fca5fed9ccfbdbfbdeb8a9db50aeb0
from django.utils.html import format_html
from .models import Harvests, Block

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


# Register your models here.
@admin.register(Block)
class BlockAdmin(admin.ModelAdmin):
    list_display = ['block_id', 'type_of_coffee', 'no_of_trees', 'date_planted', 'created_at']
    list_filter = ['use_pesticides', 'created_at']
    search_fields = ['block_id', 'type_of_coffee']
    readonly_fields = ['created_at', 'updated_at', 'created_by']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('block_id', 'no_of_trees', 'date_planted')
        }),
        ('Coffee Details', {
            'fields': ('type_of_coffee',)
        }),
        ('Seedling Information', {
            'fields': ('source_of_seedling', 'type_of_seedling', 'age_of_seedling')
        }),
        ('Farm Practices', {
            'fields': ('use_pesticides', 'pesticides_list', 'standard_practices')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at', 'created_by'),
            'classes': ('collapse',)
        }),
<<<<<<< HEAD
    )
=======
    )
>>>>>>> 32f5cd754438efd6bf2c5652d930d014e74a421b
>>>>>>> 447798b3a9fca5fed9ccfbdbfbdeb8a9db50aeb0
