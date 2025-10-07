from rest_framework import serializers
from .models import Sale, Wage, Expense, Balancesheet

class WageSerializer(serializers.ModelSerializer):
    net_salary = serializers.ReadOnlyField(source='calculate_net_salary')

    class Meta:
        model = Wage
        fields = (
            'id', 
            'employee_name', 
            'days_worked', 
            'amount_paid', 
            'date_of_payment', 
            'monthly_pay', 
            'deduction', 
            'noted_reason', 
            'net_salary'  
        )
        
        read_only_fields = ('net_salary',)

class SaleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sale
        fields = [
            'id', 'customer_name', 'item', 'rate', 'quantity', 
            'total_amount', 'amount', 'date_of_payment', 
            'status', 'balance', 'method_of_payment'
        ]
    
        read_only_fields = ['total_amount', 'status', 'balance']

class ExpenseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Expense
        fields = '__all__'


class BalancesheetSerializer(serializers.ModelSerializer):
    # This field shows the full category name (e.g., "Asset")
    account_type_display = serializers.CharField(source='get_account_type_display', read_only=True)

    class Meta:
        model = Balancesheet
        fields = ['id', 'account_name', 'account_type', 'account_type_display', 'balance', 'last_updated']
        read_only_fields = ['last_updated']