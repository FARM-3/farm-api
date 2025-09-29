from django.contrib import admin

# Register your models here.
from .models import Wage
from .models import Sale, Expense


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
        'customer_name', 
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

    list_filter = ('date_of_payment', 'customer_name', 'status')

    search_fields = ('customer_name', 'item', 'method_of_payment')

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


admin.site.register(Wage, WageAdmin)
admin.site.register(Sale, SaleAdmin)
admin.site.register(Expense, ExpenseAdmin)

