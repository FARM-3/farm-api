from django.contrib import admin

# Register your models here.
from .models import Wage


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


admin.site.register(Wage, WageAdmin)
