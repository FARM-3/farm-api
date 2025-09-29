from rest_framework import serializers
from .models import Sale, Wage, Expense

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